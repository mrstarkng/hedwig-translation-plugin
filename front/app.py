import streamlit as st
import requests

st.set_page_config(page_title="Gemini Translation", page_icon="🌐")

st.title("🌐 AI Translation with Gemini")
st.write("Translate text between languages using Gemini Flash 2.0")

source_lang = st.selectbox("Source Language", ["en", "vi", "zh", "fr", "de"], index=0)
target_lang = st.selectbox("Target Language", ["vi", "en", "zh", "fr", "de"], index=1)

text_input = st.text_area("Enter text to translate", height=150)

if st.button("Translate"):
    if not text_input.strip():
        st.warning("Please enter some text to translate.")
    else:
        with st.spinner("Translating..."):
            try:
                res = requests.post(
                    "http://127.0.0.1:5000/translate",
                    json={
                        "text": text_input,
                        "source_lang": source_lang,
                        "target_lang": target_lang
                    }
                )
                result = res.json()
                if "translated" in result:
                    st.success("Translated Text:")
                    st.text_area("Result", result["translated"], height=150)
                else:
                    st.error("Translation failed.")
            except Exception as e:
                st.error(f"Error: {e}")


