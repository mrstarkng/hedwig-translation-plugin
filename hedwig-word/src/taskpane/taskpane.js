import $ from "jquery";
import StateManager from "../utils/stateManager";
import { BASE_API_URL } from "../config/config";
import languages from "../constants/languages";

let stateUpdated = new Event("stateUpdate");
const stateManager = new StateManager(
  {
    sourceLang: "Auto detect",
    targetLang: "Vietnamese",
    text: "",
    modelName: "gemini-2.0-flash",
    temperature: 0.8,
    wrttingStyle: "general",
  },
  stateUpdated
);

let debounceTimer;

Office.onReady((info) => {
  if (info.host === Office.HostType.Word) {
    $("#app-load").hide();
    $("#app-body").show();

    // Giao diện ban đầu
    $("#source-lang").append(createOptionElm("Auto detect", true));
    languages.forEach((lang) => {
      $("#source-lang").append(createOptionElm(lang));
      $("#target-lang").append(createOptionElm(lang));
    });
    $("#target-lang>option[value=Vietnamese]")[0].selected = true;
    $("#temperature").val(0.8);

    // Sự kiện
    window.addEventListener("stateUpdate", onStateUpdated);
    $("#source-lang").on("change", onSourceLangChange);
    $("#target-lang").on("change", onTargetLangChange);
    $("#swap-btn").on("click", onSwapLang);
    $("#source").on("input", onTyping);
    $("#model-name").on("change", onModelChange);
    $("#temperature").on("input", onTempChange);
    $("#load-full-btn").on("click", loadFullDocumentText);

    Office.context.document.addHandlerAsync(
      Office.EventType.DocumentSelectionChanged,
      onSelectText
    );
  }
});

async function onStateUpdated() {
  if (debounceTimer) clearTimeout(debounceTimer);
  if (stateManager.state.text) {
    $("#source-lang").val(stateManager.state.sourceLang);
    $("#target-lang").val(stateManager.state.targetLang);
    $("#source").val(stateManager.state.text);
    $("#model-name").val(stateManager.state.modelName);
    $("#temperature").val(stateManager.state.temperature);

    const translation = await translate(stateManager.state);
    $("#target").val(translation);
  }
}

function onSourceLangChange(e) {
  stateManager.setState({ ...stateManager.state, sourceLang: e.target.value });
}
function onTargetLangChange(e) {
  stateManager.setState({ ...stateManager.state, targetLang: e.target.value });
}
function onSwapLang() {
  const currentSource = stateManager.state.sourceLang;
  const currentTarget = stateManager.state.targetLang;
  stateManager.setState({
    ...stateManager.state,
    sourceLang: currentTarget,
    targetLang: currentSource === "Auto detect" ? languages[0] : currentSource,
  });
}
function onTyping(e) {
  stateManager.setState({ ...stateManager.state, text: e.target.value });
}
function onModelChange(e) {
  stateManager.setState({ ...stateManager.state, modelName: e.target.value });
}
function onTempChange(e) {
  stateManager.setState({ ...stateManager.state, temperature: e.target.value });
}

async function onSelectText() {
  await Word.run(async (context) => {
    const range = context.document.getSelection();
    range.load("text");
    await context.sync();
    stateManager.setState({ ...stateManager.state, text: range.text.trim() });
  });
}

async function loadFullDocumentText() {
  try {
    await Word.run(async (context) => {
      const body = context.document.body;
      body.load("text");
      await context.sync();

      const fullText = body.text;
      console.log("📄 Full document text:", fullText);

      $("#source").val(fullText);
      stateManager.setState({ ...stateManager.state, text: fullText });
    });
  } catch (err) {
    console.error("❌ Failed to load full document text:", err);
  }
}

async function translate(state) {
  return new Promise((resolve) => {
    debounceTimer = setTimeout(async () => {
      try {
        const response = await fetch(`${BASE_API_URL}/translate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: state.text,
            sourceLang: mapLangToCode(state.sourceLang),
            targetLang: mapLangToCode(state.targetLang),
            temperature: parseFloat(state.temperature),
            model: state.modelName
          }),
        });

        const result = await response.json();
        console.log("🧠 API result:", result);
        resolve(result.translated_text || "[Translation failed]");
      } catch (e) {
        console.error("Translation failed:", e);
        resolve("[Error during translation]");
      }
    }, 500);
  });
}

function createOptionElm(value, selected = false) {
  const option = document.createElement("option");
  option.value = value;
  option.textContent = value;
  option.selected = selected;
  return option;
}

function mapLangToCode(lang) {
  const map = {
    "Auto detect": "auto",
    "Vietnamese": "vi",
    "Chinese": "zh",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Korean": "ko",
    "Russian": "ru",
    "Hindi": "hi",
    "Arabic": "ar",
  };
  return map[lang] || "auto";
}