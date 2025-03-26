function translateText() {
  var inputText = document.getElementById("inputText").value;
  if (!inputText) {
    alert("Please enter text to translate.");
    return;
  }

  // Show a loading indicator, etc.

  fetch("http://127.0.0.1:5000/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: inputText })
  })
  .then(response => response.json())
  .then(data => {
    if (data.translated_text) {
      // Display the translated text
    } else if (data.error) {
      // Display the error
    }
  })
  .catch(error => {
    // Handle fetch errors
  });
}
