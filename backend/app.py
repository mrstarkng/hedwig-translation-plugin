from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from langdetect import detect
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # This allows all cross-origin requests by default

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = os.environ.get("GEMINI_API_URL")

# Max characters per chunk. Adjust based on model limits or performance.
MAX_CHARS = 2000

def chunk_text(text, chunk_size=2000):
    """
    Splits the text into chunks of up to `chunk_size` characters.
    This avoids exceeding token limits or causing timeouts.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end
    return chunks

def translate_chunk(chunk, source_lang):
    """
    Builds a prompt for the given chunk and sends it to the Gemini API.
    Returns the cleaned (post-processed) translation.
    """
    if source_lang == 'vi':
        # Vietnamese -> English
        prompt_text = (
            "Translate from Vietnamese to English.\n"
            "Output ONLY the translated sentence, with no commentary or explanation.\n\n"
            f"{chunk}"
        )
    else:
        # English -> Vietnamese
        prompt_text = (
            "Translate from English to Vietnamese.\n"
            "Output ONLY the translated sentence, with no commentary or explanation.\n\n"
            f"{chunk}"
        )

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    # Make the request to Gemini
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Will raise an error for non-2xx responses
    result = response.json()

    # Extract the translated text
    translated_text = result["candidates"][0]["content"]["parts"][0]["text"]

    # Post-processing to remove leftover prompt lines
    lines = translated_text.split('\n')
    filtered_lines = []
    for line in lines:
        lower_line = line.strip().lower()
        if not (lower_line.startswith("translate") or "dịch" in lower_line):
            filtered_lines.append(line.strip())

    return " ".join(filtered_lines).strip()

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing required parameter: text"}), 400

    user_text = data['text'].strip()
    if not user_text:
        return jsonify({"error": "Text is empty"}), 400

    # 1. Detect language for the entire text
    try:
        source_lang = detect(user_text)
    except:
        return jsonify({"error": "Could not detect language"}), 400

    # 2. Fallback if detection isn't 'vi' or 'en'
    if source_lang not in ['vi', 'en']:
        source_lang = 'en'

    # 3. Split the text into manageable chunks
    text_chunks = chunk_text(user_text, MAX_CHARS)

    # 4. Translate each chunk and accumulate results
    translated_chunks = []
    for chunk in text_chunks:
        try:
            partial_translation = translate_chunk(chunk, source_lang)
            translated_chunks.append(partial_translation)
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Gemini API request failed: {str(e)}"}), 500
        except (KeyError, IndexError):
            return jsonify({"error": "Unexpected response format from Gemini API"}), 500

    # 5. Combine all partial translations into one final string
    final_translation = " ".join(translated_chunks)

    return jsonify({"translated_text": final_translation}), 200

if __name__ == '__main__':
    app.run(debug=True)
