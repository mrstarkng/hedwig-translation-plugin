from flask import Flask, request, jsonify
import requests # Vẫn giữ lại để phòng trường hợp cần gọi đồng bộ khác
import os
from dotenv import load_dotenv
from langdetect import detect
from flask_cors import CORS
import re
import asyncio
import aiohttp # Thư viện HTTP bất đồng bộ

load_dotenv()

app = Flask(__name__)
# Cấu hình CORS chặt chẽ hơn nếu cần, ví dụ chỉ cho phép origin từ Google Apps Script
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = os.environ.get("GEMINI_API_URL")

# Giảm nhẹ MAX_CHARS để an toàn hơn với token limits, có thể điều chỉnh
MAX_CHARS = 1800
# Giới hạn số lượng request đồng thời tới Gemini để tránh rate limit
MAX_CONCURRENT_REQUESTS = 5

# -------------------------- Chunking (Cải thiện) --------------------------
def chunk_text_improved(text, max_chars=MAX_CHARS):
    """
    Splits text into chunks, preserving paragraphs and trying to respect sentence boundaries.
    """
    chunks = []
    paragraphs = text.split('\n\n') # Tách đoạn văn trước
    current_chunk = ""

    for i, paragraph in enumerate(paragraphs):
        if not paragraph.strip(): # Bỏ qua đoạn trống
            if i < len(paragraphs) - 1: # Nếu không phải đoạn cuối, thêm dấu xuống dòng để giữ cấu trúc
                 current_chunk += "\n\n"
            continue

        # Nếu cả đoạn văn ngắn hơn max_chars và thêm vào chunk hiện tại không vượt quá
        if len(paragraph) <= max_chars and len(current_chunk) + len(paragraph) + 2 <= max_chars:
             current_chunk += paragraph
             if i < len(paragraphs) - 1: # Thêm ngắt đoạn nếu không phải cuối
                 current_chunk += "\n\n"

        # Nếu đoạn văn quá dài hoặc thêm vào sẽ vượt quá
        else:
            # Nếu chunk hiện tại có nội dung, thêm vào list chunks
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = "" # Reset chunk

            # Xử lý đoạn văn hiện tại (có thể dài hơn max_chars)
            if len(paragraph) <= max_chars:
                # Đoạn văn vừa đủ, bắt đầu chunk mới với nó
                current_chunk = paragraph
                if i < len(paragraphs) - 1:
                     current_chunk += "\n\n"
            else:
                # Đoạn văn dài hơn max_chars, cần tách nhỏ hơn nữa (theo câu)
                sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
                temp_chunk_for_long_paragraph = ""
                for sentence in sentences:
                    if len(temp_chunk_for_long_paragraph) + len(sentence) + 1 <= max_chars:
                        temp_chunk_for_long_paragraph += sentence + " "
                    else:
                        # Nếu chunk tạm đã đầy, thêm vào chunks chính
                        if temp_chunk_for_long_paragraph.strip():
                            chunks.append(temp_chunk_for_long_paragraph.strip())
                        # Bắt đầu chunk tạm mới bằng câu hiện tại (có thể vẫn dài hơn max_chars!)
                        # Xử lý câu quá dài: Nếu cần, có thể tách cứng nhắc hơn ở đây, nhưng tạm bỏ qua để đơn giản
                        temp_chunk_for_long_paragraph = sentence + " "

                # Thêm phần còn lại của chunk tạm (nếu có)
                if temp_chunk_for_long_paragraph.strip():
                    chunks.append(temp_chunk_for_long_paragraph.strip())

                # Sau khi xử lý đoạn dài, bắt đầu chunk mới hoàn toàn
                current_chunk = ""
                # Nếu đây không phải đoạn cuối cùng, và chunk trước đó đã được thêm vào list,
                # chúng ta cần đảm bảo ngắt đoạn được thêm vào cuối chunk trước đó hoặc đầu chunk tiếp theo
                # Cách đơn giản là không thêm \n\n tự động sau khi xử lý đoạn dài ở đây

    # Thêm chunk cuối cùng nếu còn
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Lọc các chunk rỗng có thể xuất hiện do logic tách
    return [chunk for chunk in chunks if chunk]


# -------------------------- Translation (Async) --------------------------
async def translate_chunk_async(session, chunk, source_lang, target_lang, temperature):
    """
    Async function to translate a single chunk using aiohttp session.
    """
    # Prompt được cải thiện để cố gắng giữ định dạng và rõ ràng hơn
    if source_lang == 'vi':
        prompt_text = (
            f"Translate the following Vietnamese text to English accurately. "
            f"Preserve paragraph breaks if present in the original text.\n"
            f"Output ONLY the translated text, without any introduction, commentary, or explanation.\n\n"
            f"Original Text:\n---\n{chunk}\n---\n\nTranslated Text:"
        )
    else: # Giả sử en -> vi
        prompt_text = (
            f"Translate the following English text to Vietnamese accurately. "
            f"Preserve paragraph breaks if present in the original text.\n"
            f"Output ONLY the translated text, without any introduction, commentary, or explanation.\n\n"
            f"Original Text:\n---\n{chunk}\n---\n\nTranslated Text:"
        )

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": temperature}
    }
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    try:
        # Sử dụng session đã tạo để gửi request
        async with session.post(url, json=payload, headers=headers, timeout=60) as response: # Thêm timeout
            response.raise_for_status() # Kiểm tra lỗi HTTP status
            result = await response.json() # Đọc JSON response

            # Kiểm tra cấu trúc response cẩn thận hơn
            if (result and "candidates" in result and
                len(result["candidates"]) > 0 and
                "content" in result["candidates"][0] and
                "parts" in result["candidates"][0]["content"] and
                len(result["candidates"][0]["content"]["parts"]) > 0 and
                "text" in result["candidates"][0]["content"]["parts"][0]):

                translated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                # Post-processing đơn giản: Chỉ lấy phần sau dấu hiệu kết thúc prompt nếu có
                processed_text = translated_text.split("Translated Text:")[-1].strip()
                return processed_text # Trả về kết quả đã xử lý
            else:
                # Log cấu trúc không mong đợi
                app.logger.error(f"Unexpected Gemini API response structure: {result}")
                raise ValueError("Unexpected response format from Gemini API")

    except aiohttp.ClientError as e:
        # Lỗi kết nối hoặc timeout từ aiohttp
        app.logger.error(f"aiohttp client error for chunk: {str(e)}")
        raise ConnectionError(f"API request failed: {str(e)}")
    except asyncio.TimeoutError:
        app.logger.error(f"API request timed out for chunk.")
        raise TimeoutError("API request timed out")
    except Exception as e:
        # Các lỗi khác (ví dụ JSON decode, raise_for_status, ValueError)
        app.logger.error(f"Error processing chunk: {str(e)}")
        # Ném lại lỗi để asyncio.gather bắt được
        raise

# -------------------------- Flask Endpoint (Async) --------------------------
@app.route('/translate', methods=['POST'])
async def translate(): # Đánh dấu endpoint là async
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing required parameter: text"}), 400

    user_text = data['text'] # Không cần strip() ngay, giữ nguyên xuống dòng
    source_lang_req = data.get("sourceLang", "auto") # Lấy từ request nếu có
    target_lang_req = data.get("targetLang", "vi") # Mặc định dịch sang tiếng Việt
    temperature = data.get("temperature", 0.7)

    if not user_text.strip(): # Kiểm tra nếu text toàn khoảng trắng
        return jsonify({"error": "Text is empty"}), 400

    # 1. Xác định ngôn ngữ nguồn
    actual_source_lang = source_lang_req
    if actual_source_lang == "auto":
        try:
            detected_lang = detect(user_text[:500]) # Chỉ detect phần đầu cho nhanh
            if detected_lang in ['vi', 'en']:
                actual_source_lang = detected_lang
            else:
                actual_source_lang = 'en' # Mặc định là tiếng Anh nếu không detect được vi/en
        except Exception as e:
            app.logger.warning(f"Language detection failed: {e}. Defaulting to 'en'.")
            actual_source_lang = 'en'

    # Đảm bảo target_lang hợp lệ (ví dụ: không dịch vi sang vi)
    if actual_source_lang == target_lang_req:
         # Nếu ngôn ngữ nguồn và đích giống nhau, không cần dịch
         # Hoặc chọn một ngôn ngữ đích mặc định khác, ví dụ:
         if actual_source_lang == 'vi':
             target_lang_req = 'en'
         else:
             target_lang_req = 'vi'
         app.logger.warning(f"Source and target language are the same ({actual_source_lang}). Forcing target to {target_lang_req}.")


    # 2. Chia chunks (sử dụng hàm cải thiện)
    text_chunks = chunk_text_improved(user_text, MAX_CHARS)
    if not text_chunks:
         return jsonify({"translated_text": ""}), 200 # Trả về rỗng nếu không có chunk nào

    app.logger.info(f"Translating {len(text_chunks)} chunks from {actual_source_lang} to {target_lang_req}...")

    # 3. Tạo các task dịch bất đồng bộ
    tasks = []
    # Sử dụng aiohttp.ClientSession để tái sử dụng kết nối
    async with aiohttp.ClientSession() as session:
        # Sử dụng asyncio.Semaphore để giới hạn số request đồng thời
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        async def throttled_translate(chunk):
             async with semaphore:
                 # Gọi hàm dịch bất đồng bộ
                 return await translate_chunk_async(session, chunk, actual_source_lang, target_lang_req, temperature)

        for chunk in text_chunks:
             tasks.append(throttled_translate(chunk))

        # 4. Chạy các task đồng thời và thu kết quả
        # return_exceptions=True để không dừng lại nếu có lỗi ở một task
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 5. Xử lý kết quả và lỗi
    translated_content = []
    errors = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Nếu kết quả là một exception, ghi nhận lỗi
            errors.append({"chunk_index": i, "error": str(result)})
            app.logger.error(f"Error translating chunk {i}: {str(result)}")
            # Có thể thêm một placeholder vào kết quả cuối nếu muốn
            # translated_content.append(f"[Error translating chunk {i+1}]")
        else:
            # Nếu thành công, thêm kết quả dịch
            translated_content.append(result)

    # 6. Ghép các phần đã dịch lại (dùng xuống dòng để giữ cấu trúc tốt hơn)
    # Giả sử các chunk được tạo bởi chunk_text_improved có thể kết thúc bằng \n\n
    # nên việc join bằng "" có thể phù hợp nếu chunking giữ được ngắt đoạn.
    # Hoặc join bằng "\n\n" nếu chunking chỉ tách câu. Cần kiểm tra kỹ logic chunking.
    # Thử join bằng "\n\n" để đảm bảo các đoạn văn được tách biệt.
    final_translation = "\n\n".join(translated_content).strip()

    app.logger.info(f"Translation finished. Successful chunks: {len(translated_content)}. Errors: {len(errors)}.")

    # Trả về kết quả, có thể kèm thông tin lỗi nếu muốn
    response_data = {"translated_text": final_translation}
    if errors:
        response_data["errors"] = errors
        # Trả về status 200 nhưng kèm thông tin lỗi, hoặc có thể chọn status khác (vd: 207 Multi-Status)
        return jsonify(response_data), 207 # Multi-Status indicates partial success

    return jsonify(response_data), 200

# Endpoint GET giữ nguyên
@app.route('/', methods=['GET'])
def home():
    return "Hello from Flask!", 200


if __name__ == '__main__':
    # Chạy debug=False khi deploy thực tế
    app.run(debug=True, port=5050)