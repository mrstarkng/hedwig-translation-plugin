// Ensure Office is ready before running any code
Office.onReady(function(info) {
  // Once Office is ready, attach event handler to the button
  document.getElementById("translateButton").onclick = translateText;
});

function translateText() {
  // Retrieve text from the textarea
  var inputText = document.getElementById("inputText").value;
  if (!inputText) {
    alert("Please enter text to translate.");
    return;
  }

  // Show loading indicator
  document.getElementById("loading").style.display = "block";
  document.getElementById("result").innerHTML = "";

  // Make an asynchronous call using fetch
  fetch("http://127.0.0.1:5000/translate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: inputText })
  })
  .then(response => response.json())
  .then(data => {
    // Hide loading indicator once response is received
    document.getElementById("loading").style.display = "none";

    // Display the translated text or an error message
    if (data.translated_text) {
      document.getElementById("result").innerHTML = data.translated_text;
    } else if (data.error) {
      document.getElementById("result").innerHTML = "Error: " + data.error;
    }
  })
  .catch(error => {
    document.getElementById("loading").style.display = "none";
    document.getElementById("result").innerHTML = "Fetch error: " + error;
  });
}
