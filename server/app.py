# -*- coding: utf-8 -*-
# app.py - Backend Flask cho Plugin Dịch thuật Hedwig
# Hỗ trợ dịch đa ngôn ngữ (nguồn) sang tiếng Việt (đích mặc định)
# Sử dụng asyncio và aiohttp để xử lý bất đồng bộ
# *** Phiên bản đầy đủ với logging chi tiết để debug lỗi Vi->En ***
import base64 # Để mã hóa sang Base64
from pdf_utils import create_pdf_from_text # Import hàm từ file mới tạo
from flask import Flask, request, jsonify
import os
import re
import asyncio
import aiohttp # Thư viện HTTP bất đồng bộ
import logging # Thư viện logging

# Các thư viện khác
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory, LangDetectException # Thêm LangDetectException
from flask_cors import CORS

# Đảm bảo kết quả langdetect nhất quán giữa các lần chạy
DetectorFactory.seed = 0

# Tải biến môi trường từ file .env (nếu có)
load_dotenv()

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Cấu hình CORS chặt chẽ hơn nếu cần
CORS(app) # Cho phép tất cả cross-origin requests (dễ cho development)

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s')
app.logger.setLevel(logging.INFO) # Đảm bảo logger của Flask cũng ở mức INFO

# --- Cấu hình và Hằng số ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = os.environ.get("GEMINI_API_URL")

if not GEMINI_API_KEY or not GEMINI_API_URL:
    app.logger.error("FATAL: GEMINI_API_KEY hoặc GEMINI_API_URL chưa được thiết lập trong biến môi trường!")
    # Có thể dừng ứng dụng ở đây nếu muốn
    # exit("API Key/URL not configured.")

# Giới hạn ký tự cho mỗi chunk
MAX_CHARS = 1800
# Giới hạn số lượng request đồng thời tới Gemini để tránh rate limit
MAX_CONCURRENT_REQUESTS = 5
# Timeout cho mỗi request tới Gemini (giây)
API_TIMEOUT = 90

# Dictionary tên ngôn ngữ cho prompt (Thêm/bớt tùy ý)
LANG_NAMES = {
    "auto": "Auto-detect", "en": "English", "vi": "Vietnamese", "es": "Spanish",
    "fr": "French", "de": "German", "zh": "Chinese", "ja": "Japanese",
    "ko": "Korean", "ru": "Russian", "hi": "Hindi", "ar": "Arabic"
    # Thêm các ngôn ngữ khác nếu cần, đảm bảo mã ISO 639-1 chính xác
}
# Danh sách các mã ngôn ngữ được hỗ trợ (dùng để kiểm tra sau khi detect)
# Bao gồm 'auto' không có ý nghĩa ở đây, chỉ lấy mã thực tế
SUPPORTED_LANG_CODES = [code for code in LANG_NAMES if code != 'auto']

# -------------------------- Chunking (Cải thiện) --------------------------
def chunk_text_improved(text, max_chars=MAX_CHARS):
    """
    Splits text into chunks, preserving paragraphs and trying to respect sentence boundaries.
    Handles paragraphs longer than max_chars by splitting sentences within them.
    Returns a list of non-empty text chunks.
    """
    if not isinstance(text, str): # Kiểm tra kiểu dữ liệu đầu vào
        app.logger.warning("chunk_text_improved received non-string input.")
        return []

    chunks = []
    # Chuẩn hóa ngắt dòng và tách đoạn văn
    paragraphs = re.split(r'\n\s*\n', text.strip()) # Tách bằng một hoặc nhiều dòng trống
    current_chunk = ""

    for i, paragraph in enumerate(paragraphs):
        paragraph_stripped = paragraph.strip()
        if not paragraph_stripped: # Bỏ qua đoạn trống
            continue

        # Kiểm tra xem thêm đoạn này vào chunk hiện tại có vượt quá giới hạn không
        # +2 để tính thêm \n\n tiềm năng nếu ghép đoạn
        needs_paragraph_break = bool(current_chunk) # Cần thêm ngắt đoạn nếu chunk hiện tại không rỗng
        projected_length = len(current_chunk) + len(paragraph_stripped) + (2 if needs_paragraph_break else 0)

        if len(paragraph_stripped) <= max_chars and projected_length <= max_chars:
            # Thêm vào chunk hiện tại
            if needs_paragraph_break:
                current_chunk += "\n\n"
            current_chunk += paragraph_stripped
        else:
            # Nếu chunk hiện tại có nội dung, lưu nó lại trước
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = "" # Reset chunk

            # Xử lý đoạn văn hiện tại (quá dài hoặc không vừa với chunk trước)
            if len(paragraph_stripped) <= max_chars:
                # Đoạn văn vừa đủ, bắt đầu chunk mới với nó
                current_chunk = paragraph_stripped
            else:
                # Đoạn văn dài hơn max_chars, cần tách nhỏ hơn nữa (theo câu)
                app.logger.debug(f"Paragraph {i+1} longer than {max_chars} chars. Splitting by sentence.")
                # Cải thiện regex tách câu để xử lý tốt hơn các trường hợp dấu chấm không phải cuối câu
                sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ỹ"\'(])', paragraph_stripped) # Tách câu, nhìn trước ký tự hoa đầu câu sau
                temp_chunk_for_long_paragraph = ""
                for j, sentence in enumerate(sentences):
                    sentence_stripped = sentence.strip()
                    if not sentence_stripped:
                        continue

                    # Xử lý câu quá dài (nếu có)
                    if len(sentence_stripped) > max_chars:
                         app.logger.warning(f"Single sentence in paragraph {i+1} exceeds max_chars ({max_chars}). Adding as its own chunk.")
                         if temp_chunk_for_long_paragraph.strip():
                             chunks.append(temp_chunk_for_long_paragraph.strip())
                             temp_chunk_for_long_paragraph = ""
                         chunks.append(sentence_stripped)
                         continue

                    # Kiểm tra thêm câu vào chunk tạm
                    needs_space = bool(temp_chunk_for_long_paragraph)
                    projected_temp_length = len(temp_chunk_for_long_paragraph) + len(sentence_stripped) + (1 if needs_space else 0)

                    if projected_temp_length <= max_chars:
                        if needs_space:
                            temp_chunk_for_long_paragraph += " "
                        temp_chunk_for_long_paragraph += sentence_stripped
                    else:
                        # Chunk tạm đầy, lưu lại
                        if temp_chunk_for_long_paragraph.strip():
                            chunks.append(temp_chunk_for_long_paragraph.strip())
                        # Bắt đầu chunk tạm mới
                        temp_chunk_for_long_paragraph = sentence_stripped

                # Lưu phần còn lại của chunk tạm
                if temp_chunk_for_long_paragraph.strip():
                    chunks.append(temp_chunk_for_long_paragraph.strip())
                # current_chunk đã được reset ở trên

    # Thêm chunk cuối cùng nếu còn
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Lọc các chunk rỗng cuối cùng
    final_chunks = [chunk for chunk in chunks if chunk and chunk.strip()]
    app.logger.debug(f"Split text into {len(final_chunks)} chunks.")
    return final_chunks


# -------------------------- Translation (Async - Cập nhật Prompt) --------------------------
async def translate_chunk_async(session, chunk_index, chunk, source_lang, target_lang, temperature):
    """
    Async function to translate a single chunk using aiohttp session.
    Includes chunk index for better logging and refined prompt.
    """
    source_lang_name = LANG_NAMES.get(source_lang, source_lang) # Lấy tên đầy đủ
    target_lang_name = LANG_NAMES.get(target_lang, target_lang) # Lấy tên đầy đủ
    task_name = f"Chunk-{chunk_index}" # Tên để logging

    # *** Prompt được nhấn mạnh và rõ ràng hơn ***
    prompt_text = (
    f"You are a translation engine. Translate the text below from {source_lang_name} to {target_lang_name}.\n\n"
    f"---\nInput ({source_lang_name}):\n{chunk}\n---\n\n"
    f"Output ({target_lang_name}):"
)


    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": temperature}
        # Cân nhắc thêm các tham số khác nếu cần: "topP": 0.95, "topK": 40
    }
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"} # Thêm Accept header

    app.logger.debug(f"[{task_name}] Sending request. Source='{source_lang}', Target='{target_lang}'. Prompt starts: {prompt_text[:150]}...")

    try:
        async with session.post(url, json=payload, headers=headers, timeout=API_TIMEOUT) as response:
            app.logger.debug(f"[{task_name}] Received status {response.status}")
            # Đọc nội dung trước khi kiểm tra status để có thể log lỗi nếu có
            response_text = await response.text()
            # Kiểm tra status sau khi đọc
            response.raise_for_status()

            # Phân tích JSON
            try:
                result = await response.json(content_type=None) # content_type=None để tránh lỗi content type nếu API trả về sai
            except Exception as json_err:
                 app.logger.error(f"[{task_name}] Failed to decode JSON response. Status: {response.status}. Response text: {response_text[:500]}...")
                 raise ValueError(f"Invalid JSON response from API: {json_err}")

            # Kiểm tra cấu trúc response cẩn thận
            if not isinstance(result, dict):
                 raise ValueError("API response is not a valid JSON object")

            candidates = result.get("candidates")
            # Kiểm tra lỗi trả về trong JSON body
            if not candidates and "error" in result:
                 error_details = result.get("error", {}).get("message", "Unknown error structure in response.")
                 app.logger.error(f"[{task_name}] API returned error in JSON: {error_details}")
                 raise ValueError(f"API Error: {error_details}")

            if not isinstance(candidates, list) or not candidates:
                 raise ValueError("No candidates found in API response")

            # Xử lý finishReason (nếu có) - ví dụ: SAFETY, RECITATION, OTHER
            finish_reason = candidates[0].get("finishReason")
            if finish_reason and finish_reason != "STOP":
                 app.logger.warning(f"[{task_name}] Gemini finishReason was '{finish_reason}'. Translation might be incomplete or blocked.")
                 # Có thể trả về lỗi hoặc chuỗi đặc biệt tùy theo finishReason
                 if finish_reason == "SAFETY":
                     raise ValueError("Translation blocked due to safety settings.")
                 # return f"[Translation stopped: {finish_reason}]" # Hoặc trả về thông báo

            content = candidates[0].get("content")
            if not isinstance(content, dict): raise ValueError("Candidate content is not valid")
            parts = content.get("parts")
            if not isinstance(parts, list) or not parts: raise ValueError("Content parts are missing")
            text_part = parts[0].get("text")
            if not isinstance(text_part, str): raise ValueError("Translated text part is missing or not a string")

            processed_text = text_part.strip()
            app.logger.debug(f"[{task_name}] Successfully translated. Result starts: {processed_text[:100]}...")
            return processed_text

    except aiohttp.ClientResponseError as e:
        # Lỗi HTTP status (4xx, 5xx)
        app.logger.error(f"[{task_name}] HTTP Error {e.status}: {e.message}. Response: {response_text[:500]}...")
        # Ném lại lỗi với thông điệp rõ ràng hơn
        raise ConnectionError(f"API request failed (Status {e.status})") from e
    except aiohttp.ClientError as e:
        # Lỗi kết nối, timeout client-side, etc.
        app.logger.error(f"[{task_name}] Connection/Client Error: {str(e)}")
        raise ConnectionError(f"API connection failed: {str(e)}") from e
    except asyncio.TimeoutError:
        app.logger.error(f"[{task_name}] API request timed out after {API_TIMEOUT}s.")
        raise TimeoutError(f"API request timed out ({API_TIMEOUT}s)")
    except ValueError as e: # Bắt lỗi phân tích JSON hoặc cấu trúc response
         app.logger.error(f"[{task_name}] Invalid API response or data: {e}")
         raise ValueError(f"Invalid API response/data: {e}")
    except Exception as e: # Bắt các lỗi không mong muốn khác
        app.logger.exception(f"[{task_name}] Unexpected error during translation!") # Ghi cả traceback
        raise Exception(f"Unexpected error processing chunk") from e


# -------------------------- Flask Endpoint (Async - Thêm Logging) --------------------------
@app.route('/translate', methods=['POST'])
async def translate(): # Đánh dấu endpoint là async
    # Kiểm tra API key/URL
    if not GEMINI_API_KEY or not GEMINI_API_URL:
         app.logger.error("Translate endpoint called but API Key/URL not configured.")
         return jsonify({"error": "API Key or URL not configured on server"}), 503

    # Lấy và kiểm tra dữ liệu đầu vào
    data = request.get_json()
    if not data or not isinstance(data, dict) or 'text' not in data:
        app.logger.warning("Invalid request format or missing 'text'.")
        return jsonify({"error": "Invalid request format or missing 'text'"}), 400

    user_text = data.get('text', '')
    source_lang_req = data.get("sourceLang", "auto")
    target_lang_req = data.get("targetLang", "vi")
    try:
        temperature = float(data.get("temperature", 0.7))
        if not (0.0 <= temperature <= 1.0): temperature = 0.7
    except (ValueError, TypeError): temperature = 0.7

    if not isinstance(user_text, str) or not user_text.strip():
        app.logger.warning("Request received with empty or invalid 'text'.")
        return jsonify({"error": "Text is empty or invalid"}), 400

    # *** Log ngay sau khi nhận và chuẩn hóa request ***
    app.logger.info(f"=== New Request === source='{source_lang_req}', target='{target_lang_req}', temp={temperature}, text length={len(user_text)}")

    # --- Xác định ngôn ngữ nguồn thực tế ---
    actual_source_lang = source_lang_req
    detection_method = "Provided by user"
    if actual_source_lang == "auto":
        detection_method = "Auto-detected"
        try:
            sample_text = user_text[:1500].strip() # Mẫu dài hơn và strip
            if not sample_text: raise LangDetectException("EMPTY", "Sample text for detection is empty") # Dùng exception của langdetect
            detected_lang = detect(sample_text)
            app.logger.info(f"Language detected as: '{detected_lang}'")
            # Chỉ chấp nhận nếu detect ra ngôn ngữ được hỗ trợ
            if detected_lang in SUPPORTED_LANG_CODES:
                actual_source_lang = detected_lang
            else:
                fallback_lang = 'en' if target_lang_req != 'en' else 'vi'
                app.logger.warning(f"Detected lang '{detected_lang}' not in supported list {SUPPORTED_LANG_CODES}. Falling back to source '{fallback_lang}'.")
                actual_source_lang = fallback_lang
                detection_method = f"Detected '{detected_lang}', Fell back to '{fallback_lang}'"
        except LangDetectException as e: # Bắt lỗi cụ thể của langdetect
            fallback_lang = 'en' if target_lang_req != 'en' else 'vi'
            app.logger.warning(f"Language detection failed ({e}). Falling back to source '{fallback_lang}'.")
            actual_source_lang = fallback_lang
            detection_method = f"Detection failed ({e}), Fell back to '{fallback_lang}'"
        except Exception as e: # Bắt lỗi không mong muốn khác
            fallback_lang = 'en' if target_lang_req != 'en' else 'vi'
            app.logger.exception(f"Unexpected error during language detection! Falling back to source '{fallback_lang}'.")
            actual_source_lang = fallback_lang
            detection_method = f"Detection error, Fell back to '{fallback_lang}'"

    # *** Log ngôn ngữ nguồn cuối cùng ***
    app.logger.info(f"Determined Source Language: '{actual_source_lang}' (Method: {detection_method})")
    app.logger.info(f"Target Language: '{target_lang_req}'")

    # --- Log ngay trước khi so sánh ---
    app.logger.info(f"Checking condition: actual_source_lang ('{actual_source_lang}') == target_lang_req ('{target_lang_req}') ?")

    # --- Kiểm tra nếu ngôn ngữ nguồn và đích trùng nhau ---
    if actual_source_lang == target_lang_req:
         app.logger.warning(f"RESULT: Source and target are the same! Returning original text.") # Log kết quả kiểm tra
         return jsonify({
             "translated_text": user_text,
             "detected_source_lang": actual_source_lang,
             "message": "Source and target languages are the same."
         }), 200
    else:
         app.logger.info("RESULT: Source and target differ. Proceeding with translation...") # Log kết quả kiểm tra

    # --- Chia chunks ---
    text_chunks = chunk_text_improved(user_text, MAX_CHARS)
    if not text_chunks:
         app.logger.warning("Input text resulted in zero chunks after processing.")
         return jsonify({"translated_text": "", "detected_source_lang": actual_source_lang}), 200

    app.logger.info(f"Translating {len(text_chunks)} chunks from '{actual_source_lang}' to '{target_lang_req}'...")

    # --- Tạo và chạy các task dịch bất đồng bộ ---
    tasks = []
    session = None
    try:
        # Tạo session trong try block
        session = aiohttp.ClientSession()
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def throttled_translate(chunk_idx, chunk_data):
             async with semaphore:
                 app.logger.debug(f"Task for Chunk-{chunk_idx} starting...")
                 # Truyền cả index để logging trong hàm dịch
                 return await translate_chunk_async(session, chunk_idx, chunk_data, actual_source_lang, target_lang_req, temperature)

        for i, chunk in enumerate(text_chunks):
             tasks.append(asyncio.create_task(throttled_translate(i, chunk), name=f"Chunk-{i}"))

        # Chạy đồng thời và chờ kết quả
        results = await asyncio.gather(*tasks, return_exceptions=True)

    except Exception as e:
         # Lỗi trong quá trình tạo session hoặc task (hiếm)
         app.logger.exception(f"Error setting up translation tasks: {e}")
         # Đóng session nếu đã tạo
         if session and not session.closed: await session.close()
         return jsonify({"error": f"Failed to initiate translation tasks: {e}"}), 500
    finally:
        # Đảm bảo session được đóng ngay cả khi gather lỗi
        if session and not session.closed:
            await session.close()
            app.logger.debug("aiohttp ClientSession closed.")

    # --- Xử lý kết quả và lỗi ---
    translated_content = []
    errors = []
    successful_chunks = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Lỗi trả về từ asyncio.gather
            error_message = f"{type(result).__name__}: {str(result)}"
            errors.append({"chunk_index": i, "error": error_message})
            app.logger.error(f"Error translating Chunk-{i}: {error_message}")
        elif isinstance(result, str): # Kết quả thành công là string
            translated_content.append(result)
            successful_chunks += 1
        else: # Trường hợp lạ (không nên xảy ra nếu gather hoạt động đúng)
             error_message = f"Unexpected result type for Chunk-{i}: {type(result).__name__}"
             errors.append({"chunk_index": i, "error": error_message})
             app.logger.error(error_message)


    # --- Ghép kết quả ---
    # Sử dụng "\n\n" để cố gắng giữ lại sự phân tách giữa các chunk
    final_translation = "\n\n".join(translated_content).strip()

    app.logger.info(f"Translation finished. Successful: {successful_chunks}/{len(text_chunks)}. Errors: {len(errors)}.")

    # --- Chuẩn bị và log kích thước response ---
    response_data = {
        "translated_text": final_translation,
        "detected_source_lang": actual_source_lang
    }
    if errors:
        response_data["errors_detail"] = errors

    try:
        final_json_string = jsonify(response_data).get_data(as_text=True)
        # Log kích thước byte của JSON ước tính
        json_bytes_len = len(final_json_string.encode('utf-8'))
        app.logger.info(f"Backend: Final translation length (chars): {len(final_translation)}")
        app.logger.info(f"Backend: Estimated response JSON length (bytes): {json_bytes_len}")
        # Cảnh báo nếu response quá lớn (ví dụ > 5MB, gần giới hạn UrlFetch ~10MB)
        if json_bytes_len > 5 * 1024 * 1024:
            app.logger.warning(f"Response JSON size is large ({json_bytes_len / (1024*1024):.2f} MB), might approach Apps Script limits.")
    except Exception as log_e:
        app.logger.error(f"Backend: Error estimating response size: {log_e}")

    # --- Trả về response ---
    # Luôn trả về 200 OK, lỗi (nếu có) nằm trong key "errors_detail"
    return jsonify(response_data), 200


# Endpoint GET để kiểm tra server có chạy không
@app.route('/', methods=['GET'])
def home():
    """Root endpoint to check if the server is running."""
    app.logger.info("Root path '/' accessed.")
    return "Hedwig Translation Backend is running!", 200

# -------------------------- PDF Export Endpoint --------------------------
@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    """
    Endpoint để nhận văn bản gốc và bản dịch, tạo PDF và trả về base64.
    """
    req_data = request.get_json()
    if not req_data or not isinstance(req_data, dict):
        app.logger.warning("Export PDF: Invalid or missing JSON data.")
        return jsonify({"error": "Invalid request format"}), 400

    original_text = req_data.get('original_text')
    translated_text = req_data.get('translated_text')

    if not original_text or not translated_text:
        app.logger.warning("Export PDF: Missing 'original_text' or 'translated_text'.")
        return jsonify({"error": "Missing required text fields"}), 400

    app.logger.info(f"Export PDF request received. Original length: {len(original_text)}, Translated length: {len(translated_text)}")

    try:
        # Gọi hàm tạo PDF từ pdf_utils.py
        pdf_bytes = create_pdf_from_text(original_text, translated_text)

        if pdf_bytes:
            # Mã hóa PDF bytes sang Base64 để gửi về dạng text trong JSON
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            filename = "hedwig_translation.pdf" # Đặt tên file mặc định

            app.logger.info(f"Export PDF: Successfully generated and encoded PDF ({filename}). Base64 length: {len(pdf_base64)}")

            # Trả về JSON chứa base64 và tên file
            return jsonify({
                "pdf_base64": pdf_base64,
                "filename": filename
            }), 200
        else:
            # Lỗi xảy ra trong create_pdf_from_text (đã được log bên trong)
            app.logger.error("Export PDF: create_pdf_from_text returned None.")
            return jsonify({"error": "Failed to generate PDF content."}), 500

    except Exception as e:
        # Bắt các lỗi không mong muốn khác trong quá trình xử lý request
        app.logger.exception("Export PDF: Unexpected error processing request!")
        return jsonify({"error": "Internal server error during PDF export.", "details": str(e)}), 500


# Chạy ứng dụng Flask
if __name__ == '__main__':
    # Lấy cổng từ biến môi trường hoặc dùng mặc định 5050
    port = int(os.environ.get("PORT", 5050))
    # Chạy debug=False và dùng WSGI server (như gunicorn, waitress) khi deploy thực tế
    # Ví dụ: waitress-serve --host=0.0.0.0 --port=5050 app:app
    # Hoặc: gunicorn --bind 0.0.0.0:5050 "app:app" --worker-class uvicorn.workers.UvicornWorker (nếu dùng ASGI)
    app.logger.info(f"Starting Flask server on port {port} with debug={app.debug}...")
    # Host '0.0.0.0' để có thể truy cập từ bên ngoài container/máy ảo nếu cần
    app.run(host='0.0.0.0', port=port, debug=True) # debug=True cho development