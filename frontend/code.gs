function onOpen() {
  DocumentApp.getUi().createMenu('AI Translate')
    .addItem('Open Translator', 'showSidebar')
    .addToUi();
}

function showSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('sidebar')
    .setTitle('AI Translation');
  DocumentApp.getUi().showSidebar(html);
}

function translateSelectedText(sourceLang, targetLang) {
  const selection = DocumentApp.getActiveDocument().getSelection();
  if (!selection) return 'No text selected.';
  
  let text = '';
  const elements = selection.getRangeElements();
  for (const e of elements) {
    if (e.getElement().editAsText) {
      text += e.getElement().asText().getText().substring(
        e.getStartOffset(), e.getEndOffsetInclusive() + 1
      );
    }
  }

  const response = UrlFetchApp.fetch('http://localhost:5000/translate', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({
      text: text,
      source_lang: sourceLang,
      target_lang: targetLang
    })
  });

  return JSON.parse(response.getContentText()).translated;
}
