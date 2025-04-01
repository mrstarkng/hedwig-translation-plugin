
// --- Hằng số API ---
// !!! QUAN TRỌNG: Thay YOUR_NGROK_URL_HERE bằng URL ngrok hiện tại của bạn 
const NGROK_BASE_URL = "YOUR_NGROK_URL_HERE"; // ngrok
const TRANSLATE_API_URL = NGROK_BASE_URL + "/translate";
const PDF_API_URL = NGROK_BASE_URL + "/export-pdf"; // Endpoint mới cho PDF

// --- Hàm khởi tạo Add-on ---
function onOpen(e) {
  DocumentApp.getUi()
    .createMenu("Hedwig")
    .addItem("Open Translator", "showSidebar")
    .addToUi();
}

function showSidebar() {
  // Sử dụng createHtmlOutputFromFile thay vì createTemplateFromFile nếu Sidebar.html không dùng scriptlet <% ... %>
  // const html = HtmlService.createHtmlOutputFromFile("Sidebar");
  // Nếu Sidebar.html CÓ dùng scriptlet thì giữ nguyên createTemplateFromFile
  const html = HtmlService.createTemplateFromFile("Sidebar").evaluate();
  html.setTitle("Hedwig");
  DocumentApp.getUi().showSidebar(html);
}

// --- Hàm lấy văn bản từ Google Docs ---
function getSelectedText() {
  const selection = DocumentApp.getActiveDocument().getSelection();
  if (!selection) {
    Logger.log("getSelectedText: No selection found.");
    return "";
  }

  const elements = selection.getRangeElements();
  let selectedText = "";

  for (const el of elements) {
    // Chỉ xử lý nếu element có thể chỉnh sửa dưới dạng text
    if (el.getElement().editAsText) {
      const textElement = el.getElement().asText();
      let elementText = "";
      
      if (el.isPartial()) {
        const start = el.getStartOffset();
        const end = el.getEndOffsetInclusive();
        // Kiểm tra hợp lệ
        if (start !== -1 && end !== -1 && start <= end) {
          try {
            elementText = textElement.getText().substring(start, end + 1);
            Logger.log(`Partial text extracted: "${elementText}"`);
          } catch (e) {
            Logger.log("Error extracting partial text: " + e);
          }
        } else {
          Logger.log(`Skipping element with unusual offsets: start=${start}, end=${end}`);
        }
      } else {
        try {
          elementText = textElement.getText();
          Logger.log(`Full text extracted: "${elementText.substring(0, 50)}..."`);
        } catch (e) {
          Logger.log("Error extracting full text: " + e);
        }
      }
      // Nối thêm xuống dòng giữa các element để giữ định dạng
      selectedText += elementText + "\n";
    } else {
      Logger.log("Skipping non-text element of type: " + el.getElement().getType());
    }
  }

  selectedText = selectedText.trim(); // Xóa khoảng trắng dư thừa
  Logger.log("getSelectedText: Final Length = " + selectedText.length);
  return selectedText;
}

  

function getFullDocumentText() {
  const body = DocumentApp.getActiveDocument().getBody();
  const text = body.getText();
  Logger.log("getFullDocumentText: Length = " + text.length);
  return text;
}

// --- Hàm gọi API Dịch thuật ---
function doTranslation(text, sourceLang, targetLang, model, temperature) {
  if (!text || !text.trim()) {
    Logger.log("doTranslation: No text provided.");
    return { error: "No text provided." }; // Trả về lỗi rõ ràng hơn
  }

  const payload = {
    text: text,
    sourceLang: sourceLang, // Key đã sửa
    targetLang: targetLang, // Key đã sửa
    model: model,
    temperature: temperature
  };

  const options = {
    method: "post",
    contentType: "application/json",
    muteHttpExceptions: true, // Quan trọng để tự xử lý lỗi HTTP
    payload: JSON.stringify(payload),
    // Cân nhắc thêm thời hạn chờ (deadline) nếu cần, mặc định là 6 phút
    // deadline: 300 // ví dụ: 5 phút = 300 giây
  };

  Logger.log("doTranslation: Calling API: " + TRANSLATE_API_URL);
  // Logger.log("doTranslation: Payload keys: " + Object.keys(payload).join(', ')); // Debug payload keys

  try {
    const response = UrlFetchApp.fetch(TRANSLATE_API_URL, options);
    const responseCode = response.getResponseCode();
    const responseBody = response.getContentText();

    Logger.log("doTranslation: Response Code = " + responseCode);
    Logger.log("doTranslation: Received response body length: " + responseBody.length);
    // Logger.log("doTranslation: Response body tail: " + responseBody.substring(responseBody.length - 100)); // Log phần cuối để debug JSON

    // Xử lý cả 200 (OK) và 207 (Multi-Status - nếu backend trả về lỗi partial)
    if (responseCode === 200 || responseCode === 207) {
      try {
        const parsedResponse = JSON.parse(responseBody);
        Logger.log("doTranslation: Successfully parsed JSON response.");
        // Trả về toàn bộ object JSON nhận được từ backend
        return parsedResponse;
      } catch (e) {
         Logger.log("doTranslation: JSON.parse failed. Error: " + e);
         // Trả về lỗi chi tiết để frontend xử lý
         return {
           error: "Failed to parse response from backend.",
           error_details: e.toString(),
           response_preview: responseBody.substring(0, 500) + "..." // Gửi một phần response để debug
         };
      }
    } else {
      // Lỗi từ server backend (4xx, 5xx)
      Logger.log("doTranslation: Backend returned error code " + responseCode + ". Body: " + responseBody.substring(0, 500) + "...");
      // Cố gắng parse lỗi từ backend nếu là JSON
      let backendError = responseBody;
      try {
        const errorJson = JSON.parse(responseBody);
        if (errorJson && errorJson.error) {
          backendError = errorJson.error;
        }
      } catch(e) { /* Bỏ qua nếu không phải JSON */ }
      return {
          error: `Backend Error (${responseCode})`,
          error_details: backendError
        };
    }
  } catch (err) {
    // Lỗi từ UrlFetchApp (ví dụ: timeout, network error, invalid URL)
    Logger.log("doTranslation: UrlFetchApp failed. Error: " + err);
    return {
        error: "Failed to connect to backend service.",
        error_details: err.toString()
      };
  }
}


// --- Hàm mới: Gọi API Xuất PDF ---
function exportToPdf(originalText, translatedText) {
  if (!originalText || !translatedText || !originalText.trim() || !translatedText.trim()) {
      Logger.log("exportToPdf: Missing original or translated text.");
      // Trả về lỗi để handlePdfError xử lý
      throw new Error("Original or translated text is missing.");
  }

  const payload = {
    // Backend /export-pdf mong đợi key gì? Giả sử là:
    original_text: originalText,
    translated_text: translatedText
  };

  const options = {
    method: "post",
    contentType: "application/json",
    muteHttpExceptions: true,
    payload: JSON.stringify(payload),
    // Có thể cần deadline dài hơn cho việc tạo PDF
    // deadline: 120 // 2 phút
  };

  Logger.log("exportToPdf: Calling API: " + PDF_API_URL);
  // Logger.log("exportToPdf: Payload preview: " + JSON.stringify(payload).substring(0, 200) + "...");

  try {
    const response = UrlFetchApp.fetch(PDF_API_URL, options);
    const responseCode = response.getResponseCode();
    const responseBody = response.getContentText();

    Logger.log("exportToPdf: Response Code = " + responseCode);
    // Logger.log("exportToPdf: Received response body length: " + responseBody.length); // Base64 có thể rất dài

    if (responseCode === 200) {
       try {
        const parsedResponse = JSON.parse(responseBody);
        // Kiểm tra xem backend có trả về đúng key pdf_base64 không
        if (parsedResponse && parsedResponse.pdf_base64 && parsedResponse.filename) {
           Logger.log("exportToPdf: Successfully received PDF base64 data.");
           return parsedResponse; // Trả về { pdf_base64: "...", filename: "..." }
        } else {
           Logger.log("exportToPdf: Backend response missing pdf_base64 or filename key.");
           throw new Error("Invalid response format from PDF export service (missing keys).");
        }
      } catch (e) {
         Logger.log("exportToPdf: JSON.parse failed. Error: " + e);
         throw new Error("Failed to parse PDF response from backend.");
      }
    } else {
      // Lỗi từ server backend khi tạo PDF
      Logger.log("exportToPdf: Backend returned error code " + responseCode + ". Body: " + responseBody.substring(0, 500) + "...");
      let backendError = responseBody;
      try { const errorJson = JSON.parse(responseBody); if (errorJson && errorJson.error) backendError = errorJson.error; } catch(e) {}
      throw new Error(`PDF Generation Error (${responseCode}): ${backendError}`);
    }
  } catch (err) {
    // Lỗi từ UrlFetchApp
    Logger.log("exportToPdf: UrlFetchApp failed. Error: " + err);
    // Ném lỗi để withFailureHandler bắt được
    throw new Error("Failed to connect to PDF export service: " + err.message);
  }
}

// --- (Các hàm tiện ích khác nếu có) ---

// *** Thêm hàm này vào cuối file Code.gs ***

/**
 * Tạo và hiển thị một modal dialog chứa link tải file PDF.
 * Hàm này được gọi từ client-side JavaScript (handlePdfResponse).
 *
 * @param {string} base64Data Dữ liệu PDF đã được mã hóa Base64.
 * @param {string} filename Tên file gợi ý để tải về.
 */
function displayPdfDialog(base64Data, filename) {
  try {
    // Kiểm tra đầu vào cơ bản
    if (!base64Data || !filename) {
      throw new Error("Missing base64 data or filename for PDF dialog.");
    }

    const dataUri = "data:application/pdf;base64," + base64Data;
    const safeFilename = filename.replace(/[^a-z0-9._-]/gi, '_'); // Làm sạch tên file cơ bản

    // Tạo nội dung HTML cho dialog
    // Sử dụng target="_blank" và rel="noopener noreferrer" cho link an toàn hơn
    const downloadHtml = `
      <style> body { font-family: Arial, sans-serif; padding: 15px; } a { text-decoration: none; color: #1a73e8; } button { margin-top: 15px; } </style>
      <body>
        <p>PDF generated successfully!</p>
        <p><a href="${dataUri}" download="${safeFilename}" target="_blank" rel="noopener noreferrer">Click here to download ${safeFilename}</a></p>
        <button onclick="google.script.host.close()">Close</button>
        <script>
          // Tự động focus vào link khi dialog mở (cải thiện UX)
          window.onload = function() {
            const link = document.querySelector('a');
            if (link) link.focus();
          };
        </script>
      </body>
      `;

    // Tạo HtmlOutput và hiển thị dialog
    const htmlOutput = HtmlService.createHtmlOutput(downloadHtml)
        .setWidth(350)  // Tăng nhẹ chiều rộng
        .setHeight(150);
    DocumentApp.getUi().showModalDialog(htmlOutput, 'Download PDF');

    Logger.log("displayPdfDialog: Successfully shown PDF download dialog.");

  } catch (e) {
    Logger.log("displayPdfDialog: Error - " + e);
    // Ném lỗi lại để withFailureHandler phía client có thể bắt được nếu cần
    throw new Error("Could not display the PDF download dialog: " + e.message);
  }
}