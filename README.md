# Hedwig Translation Plugin

Hedwig là một plugin dịch thuật mạnh mẽ tích hợp trí tuệ nhân tạo, được thiết kế để hoạt động bên trong các trình soạn thảo văn bản phổ biến như Google Docs. Dự án này cho phép dịch thuật liền mạch bằng cách sử dụng các mô hình ngôn ngữ lớn (LLM) hiện đại như Gemini của Google, trực tiếp trong tài liệu của bạn.

Đây là một dự án trong khuôn khổ môn học Xử lý Ngôn ngữ Tự nhiên (NLP).

## Tính năng chính

* **Dịch văn bản:** Dịch đoạn văn bản bạn đang chọn (selected text) hoặc toàn bộ nội dung tài liệu (full document).
* **Hỗ trợ đa ngôn ngữ:**
    * Tự động phát hiện ngôn ngữ nguồn (Auto-detect).
    * Cho phép chọn ngôn ngữ nguồn và **ngôn ngữ đích** từ danh sách các ngôn ngữ phổ biến (ví dụ: Anh, Việt, Tây Ban Nha, Pháp, Đức, Trung, Nhật, Hàn, Nga, Hindi, Ả Rập...). Hỗ trợ dịch hai chiều giữa các ngôn ngữ này.
* **Tùy chọn mô hình AI:**
    * Hiện tại sử dụng **Gemini** làm engine dịch chính.
    * Có placeholder cho các mô hình khác như GPT-4 hoặc mô hình chuyên biệt (chưa tích hợp).
* **Kiểm soát Temperature:** Cho phép điều chỉnh tham số `temperature` để kiểm soát mức độ sáng tạo/ngẫu nhiên của bản dịch.
* **Giao diện Sidebar:** Tích hợp trực quan dưới dạng sidebar trong Google Docs để dễ dàng thao tác.
* **Tiện ích:**
    * Nút "Load Selected Text" và "Load Full Document" để nạp nhanh văn bản vào ô input.
    * Nút "Swap Languages" để hoán đổi nhanh ngôn ngữ nguồn và đích.
    * Nút "Copy" để sao chép kết quả dịch vào clipboard.
* **Xử lý văn bản dài:** Backend được thiết kế để chia nhỏ văn bản dài thành các phần (chunks) và dịch bất đồng bộ, giảm thiểu lỗi timeout và xử lý hiệu quả hơn.
* **Xuất PDF (Sẽ hoàn thiện sau):** Chức năng xuất văn bản gốc và bản dịch ra file PDF đang được phát triển và sẽ hoàn thiện trong tương lai.

## Nền tảng hỗ trợ

* **Hiện tại:** Google Docs (thông qua Google Apps Script Add-on).
* *Dự định tương lai:* Word, LibreOffice Writer.

## Công nghệ sử dụng

* **Frontend (Google Docs Add-on):** Google Apps Script (HTML, CSS, JavaScript)
* **Backend:** Python 3, Flask, aiohttp, asyncio
* **API Dịch thuật:** Google Gemini API
* **Thư viện phụ trợ (Backend):**
    * `Flask-Cors`: Xử lý Cross-Origin Resource Sharing.
    * `python-dotenv`: Quản lý biến môi trường.
    * `requests`: Gửi yêu cầu HTTP (dự phòng).
    * `langdetect`: Phát hiện ngôn ngữ tự động.
    * `fpdf2`: Tạo file PDF (cho chức năng tương lai).
    * `aiohttp`: Gửi yêu cầu HTTP bất đồng bộ.
    * `asgiref` (thông qua `Flask[async]`): Hỗ trợ view async trong Flask.
* **Tunneling (Development):** ngrok (Để expose server Flask local ra internet cho Apps Script gọi).

## Cấu trúc dự án
Here's a thinking process for generating the documentation for the Hedwig plugin based on the user's request and the development history:

Understand the Goal: The user wants comprehensive documentation (README style) for their "Hedwig" translation plugin. They provided a very basic skeleton and specified:

Target Platforms: Google Docs (primary focus of interaction), potentially Word/LibreOffice (mentioned in skeleton but not implemented/discussed).
Core Functionality: AI-powered translation (specifically mentioning OpenAI/Gemini models used during development).
Features to Include: Translate selected text, translate full document, choose source/target languages (multi-language support implemented), model selection, temperature control.
Features to Exclude/Defer: Paste/Replace function (Priority 2, deferred), PDF export (partially implemented but deferred completion).
Structure: Mention frontend/, backend/, docs/.
Tone: Standard documentation style (informative, clear).
Review Development History & Current State:

Frontend (Sidebar.html, Code.gs): Implemented for Google Docs using Apps Script. Includes UI elements for text input, language selection (source: auto + 10 langs, target: 10 langs), model selection (Gemini, placeholder GPT-4, Specialized), temperature control, "Load Selected", "Load Full Doc", "Translate", "Swap Languages", "Copy Result", "Export PDF" buttons. The "Paste/Replace" button was added but its associated functionality is excluded from this documentation version. The "Export PDF" button exists, but the user wants to mention it's not fully ready.
Backend (app.py, pdf_utils.py): Flask server using asyncio/aiohttp to handle long text via chunking. Connects to Gemini API (using environment variables for key/URL). Handles /translate endpoint with dynamic source/target languages. Has /export-pdf endpoint using fpdf2 and Noto Sans font (though PDF functionality is deferred). Uses langdetect.
Supported Languages: English, Vietnamese, Spanish, French, German, Chinese, Japanese, Korean, Russian, Hindi, Arabic (and auto-detect for source). Target can be any of these.
Models: Currently configured for Gemini, placeholders for GPT-4/Specialized.
Outline the Documentation (README.md structure):

Project Title: Hedwig Translation Plugin (Use the chosen name).
Badges (Optional): Build status, license, etc. (Skip for now as it's a student project).
Introduction/Overview: Briefly describe what the plugin does (AI translation within word processors, focusing on Google Docs for now) and the primary AI model used (Gemini). Mention it's an NLP course project.
Features: List the key functionalities currently working based on the request (Translate selection/full doc, multi-language source/target, model/temp controls). Explicitly mention PDF export is planned for the future. Do not mention the Paste/Replace feature.
Supported Platforms: State clearly "Currently supports Google Docs." Mentioning Word/LibreOffice as future goals is okay if desired, but clarify the current state.
Technology Stack: List the main technologies used (Frontend: Google Apps Script (HTML/CSS/JS); Backend: Python, Flask, aiohttp, Gemini API, langdetect, fpdf2; Other: ngrok for development).
Project Structure: Briefly explain the frontend/, backend/, docs/ directories as requested. (Even if these aren't literal directories in the Apps Script/Flask setup, use them conceptually).
Installation / Setup: This is crucial. Break it down:
Prerequisites: Google Account, Python 3.x, pip, Conda (optional, but user used it), ngrok account/executable, Google Cloud Project (for Gemini API Key), Gemini API enabled.
Backend Setup:
Clone repository (if applicable, otherwise "Set up backend files").
Create/activate Python environment (e.g., conda).
Install dependencies: pip install -r requirements.txt (Need to list the requirements: Flask, Flask-Cors, python-dotenv, requests, langdetect, aiohttp, fpdf2, Flask[async]). Create a hypothetical requirements.txt.
Environment Variables: Create .env file, add GEMINI_API_KEY and GEMINI_API_URL. Explain how to get the API key.
Font Setup: Explain downloading NotoSans-Regular.ttf and NotoSans-Bold.ttf and placing them in the backend directory.
Running the Backend: python app.py.
ngrok Setup:
Run ngrok: ngrok http <your_flask_port> (e.g., 5050).
Note the HTTPS URL.
Frontend (Google Apps Script) Setup:
Create a new Apps Script project bound to a Google Doc OR standalone.
Copy/Paste Code.gs content.
Copy/Paste Sidebar.html content (Create HTML file named "Sidebar").
Update NGROK_BASE_URL in Code.gs with the current ngrok HTTPS URL.
Configure appsscript.json (Manifest):
Show the complete manifest structure.
Emphasize setting timeZone, oauthScopes, and especially urlFetchWhitelist (using the ngrok base URL with /).
Explain saving the manifest.
Testing: Explain using "Deploy" > "Test deployments" to install and run the add-on in a Google Doc.
Usage: Briefly describe how to use the sidebar: Open via Extensions menu, select text/load doc, choose languages/options, click Translate, use Copy/Export buttons.
Features (Detailed - Optional): Could expand on each feature if needed.
Known Issues / Limitations: Mention potential timeouts for extremely long documents (Apps Script limit), dependency on ngrok for development, variable translation quality.
Future Work: Explicitly mention completing the PDF export feature. Add the Paste/Replace feature. Mention potential Word/LibreOffice support. Other ideas? (More models, customization, etc.)
Contributing (Optional): Standard contribution guidelines (skip for now).
License (Optional): Choose a license (e.g., MIT) or state "Educational project".
Draft the Content (in Vietnamese as requested): Write each section based on the outline and gathered information. Use Markdown formatting. Pay attention to the specific exclusions (Paste function) and deferrals (PDF function). Ensure setup instructions are clear and step-by-step.

Review and Refine: Read through the generated documentation.

Completeness: Does it cover all requested aspects?
Accuracy: Does it reflect the current state of the plugin (multi-language target, Gemini backend, etc.)? Are setup instructions correct?
Clarity: Is the language clear and easy to understand? Are instructions unambiguous?
Exclusions: Has the Paste function been omitted? Is PDF export correctly described as planned/deferred?
Formatting: Is Markdown used effectively for readability (headings, code blocks, lists)?
Tone: Is it professional and informative?
This systematic process ensures all requirements are met and results in comprehensive documentation reflecting the project's status.

Ok, đây là bản tài liệu documentation hoàn chỉnh hơn cho plugin Hedwig của bạn, dựa trên mô tả và các tính năng đã phát triển, đồng thời bỏ qua chức năng "Paste" và ghi chú về "Export PDF".

Markdown

# Hedwig Translation Plugin

Hedwig là một plugin dịch thuật mạnh mẽ tích hợp trí tuệ nhân tạo, được thiết kế để hoạt động bên trong các trình soạn thảo văn bản phổ biến như Google Docs. Dự án này cho phép dịch thuật liền mạch bằng cách sử dụng các mô hình ngôn ngữ lớn (LLM) hiện đại như Gemini của Google, trực tiếp trong tài liệu của bạn.

Đây là một dự án trong khuôn khổ môn học Xử lý Ngôn ngữ Tự nhiên (NLP).

## Tính năng chính

* **Dịch văn bản:** Dịch đoạn văn bản bạn đang chọn (selected text) hoặc toàn bộ nội dung tài liệu (full document).
* **Hỗ trợ đa ngôn ngữ:**
    * Tự động phát hiện ngôn ngữ nguồn (Auto-detect).
    * Cho phép chọn ngôn ngữ nguồn và **ngôn ngữ đích** từ danh sách các ngôn ngữ phổ biến (ví dụ: Anh, Việt, Tây Ban Nha, Pháp, Đức, Trung, Nhật, Hàn, Nga, Hindi, Ả Rập...). Hỗ trợ dịch hai chiều giữa các ngôn ngữ này.
* **Tùy chọn mô hình AI:**
    * Hiện tại sử dụng **Gemini** làm engine dịch chính.
    * Có placeholder cho các mô hình khác như GPT-4 hoặc mô hình chuyên biệt (chưa tích hợp).
* **Kiểm soát Temperature:** Cho phép điều chỉnh tham số `temperature` để kiểm soát mức độ sáng tạo/ngẫu nhiên của bản dịch.
* **Giao diện Sidebar:** Tích hợp trực quan dưới dạng sidebar trong Google Docs để dễ dàng thao tác.
* **Tiện ích:**
    * Nút "Load Selected Text" và "Load Full Document" để nạp nhanh văn bản vào ô input.
    * Nút "Swap Languages" để hoán đổi nhanh ngôn ngữ nguồn và đích.
    * Nút "Copy" để sao chép kết quả dịch vào clipboard.
* **Xử lý văn bản dài:** Backend được thiết kế để chia nhỏ văn bản dài thành các phần (chunks) và dịch bất đồng bộ, giảm thiểu lỗi timeout và xử lý hiệu quả hơn.
* **Xuất PDF (Sẽ hoàn thiện sau):** Chức năng xuất văn bản gốc và bản dịch ra file PDF đang được phát triển và sẽ hoàn thiện trong tương lai.

## Nền tảng hỗ trợ

* **Hiện tại:** Google Docs (thông qua Google Apps Script Add-on).
* *Dự định tương lai:* Word, LibreOffice Writer.

## Công nghệ sử dụng

* **Frontend (Google Docs Add-on):** Google Apps Script (HTML, CSS, JavaScript)
* **Backend:** Python 3, Flask, aiohttp, asyncio
* **API Dịch thuật:** Google Gemini API
* **Thư viện phụ trợ (Backend):**
    * `Flask-Cors`: Xử lý Cross-Origin Resource Sharing.
    * `python-dotenv`: Quản lý biến môi trường.
    * `requests`: Gửi yêu cầu HTTP (dự phòng).
    * `langdetect`: Phát hiện ngôn ngữ tự động.
    * `fpdf2`: Tạo file PDF (cho chức năng tương lai).
    * `aiohttp`: Gửi yêu cầu HTTP bất đồng bộ.
    * `asgiref` (thông qua `Flask[async]`): Hỗ trợ view async trong Flask.
* **Tunneling (Development):** ngrok (Để expose server Flask local ra internet cho Apps Script gọi).

## Cấu trúc dự án (Tham khảo)

hedwig-plugin/
│
├── backend/           # Chứa code server Flask
│   ├── app.py         # File Flask chính (routes, xử lý request)
│   ├── pdf_utils.py   # Logic tạo PDF (cho chức năng tương lai)
│   ├── .env           # File chứa API keys (KHÔNG commit lên Git)
│   ├── requirements.txt # Danh sách thư viện Python cần cài đặt
│   └── NotoSans-Regular.ttf  # File font (ví dụ)
│   └── NotoSans-Bold.ttf     # File font (ví dụ)
│
├── frontend/          # Chứa code Apps Script cho Google Docs Add-on
│   ├── Code.gs        # Logic Apps Script (gọi backend, xử lý UI)
│   ├── Sidebar.html   # Giao diện HTML của sidebar
│   └── appsscript.json # File Manifest cấu hình add-on
│
└── docs/              # Thư mục chứa tài liệu hướng dẫn
└── README.md      # File này

## Hướng dẫn cài đặt và chạy (Development)

### Yêu cầu cài đặt

* Tài khoản Google.
* Python 3.8+ và pip.
* Tài khoản ngrok và đã tải/cài đặt ngrok CLI.
* Google Cloud Project để lấy API Key cho Gemini API (hoặc API Key từ Google AI Studio). Đảm bảo Gemini API đã được kích hoạt.

### Cài đặt Backend (Server Flask)

1.  **Clone Repository (Nếu có):**
    ```bash
    git clone <your-repo-url>
    cd hedwig-plugin/backend
    ```
    Hoặc tạo thư mục `backend` và copy các file `app.py`, `pdf_utils.py` vào.
2.  **Tạo và kích hoạt môi trường ảo (Khuyến nghị):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # MacOS/Linux
    source venv/bin/activate
    ```
    Hoặc sử dụng Conda nếu bạn quen thuộc.
3.  **Cài đặt thư viện Python:**
    Tạo file `requirements.txt` với nội dung sau:
    ```txt
    Flask>=2.0.0
    Flask-Cors
    python-dotenv
    requests
    langdetect
    aiohttp
    fpdf2
    Flask[async]
    ```
    Sau đó chạy:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Tải Font:** Tải về các file font `NotoSans-Regular.ttf` và `NotoSans-Bold.ttf`. Đặt chúng vào trong cùng thư mục `backend`.
5.  **Thiết lập biến môi trường:**
    * Tạo file tên là `.env` trong thư mục `backend`.
    * Thêm nội dung sau vào file `.env`, thay thế bằng giá trị thực tế của bạn:
        ```env
        GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
        GEMINI_API_URL=[https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent](https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent) # Hoặc URL model Gemini bạn dùng
        # PORT=5050 # Tùy chọn: Đặt cổng khác nếu muốn
        ```
6.  **Chạy Backend:**
    ```bash
    python app.py
    ```
    Server Flask sẽ khởi chạy (thường ở cổng 5050). Ghi nhớ cổng này.

### Cài đặt ngrok

1.  Mở một cửa sổ terminal **khác**.
2.  Chạy ngrok để expose cổng mà Flask đang chạy (ví dụ 5050):
    ```bash
    ngrok http 5050
    ```
3.  Ngrok sẽ hiển thị thông tin, trong đó có một URL dạng `https://<random-string>.ngrok-free.app`. Hãy **copy URL HTTPS** này. Đây là địa chỉ công khai của backend Flask của bạn.

### Cài đặt Frontend (Google Apps Script Add-on)

1.  Mở một tài liệu Google Docs bất kỳ (hoặc tạo mới).
2.  Vào `Extensions` > `Apps Script`. Trình soạn thảo Apps Script sẽ mở ra.
3.  **Xóa** toàn bộ code mặc định trong file `Code.gs`.
4.  **Copy** toàn bộ nội dung file `Code.gs` của dự án và **dán** vào trình soạn thảo.
5.  **Cập nhật URL ngrok trong `Code.gs`:** Tìm dòng `const NGROK_BASE_URL = "..."` và thay thế URL trong dấu ngoặc kép bằng **URL HTTPS bạn đã copy từ ngrok** ở bước trên. Đảm bảo URL kết thúc bằng dấu `/`.
6.  **Tạo file Sidebar HTML:**
    * Trong trình soạn thảo Apps Script, nhấp vào dấu `+` bên cạnh "Files".
    * Chọn "HTML".
    * Đặt tên file là `Sidebar` (chính xác chữ hoa/thường) và nhấn Enter.
    * Xóa nội dung mặc định trong file `Sidebar.html` mới tạo.
    * **Copy** toàn bộ nội dung file `Sidebar.html` của dự án và **dán** vào đây.
7.  **Cấu hình Manifest (`appsscript.json`):**
    * Trong trình soạn thảo Apps Script, nhấp vào biểu tượng "Project Settings" (⚙️) ở menu bên trái.
    * Check vào ô "Show 'appsscript.json' manifest file in editor".
    * Quay lại phần "Editor" (</>), file `appsscript.json` sẽ xuất hiện.
    * **Copy** toàn bộ nội dung file `appsscript.json` **đã sửa lỗi whitelist** (chứa URL gốc của ngrok có dấu `/` ở cuối) và **dán** thay thế nội dung hiện có trong trình soạn thảo. Đảm bảo các `oauthScopes` cần thiết đều có mặt.
    * **Quan trọng:** Nhấn nút **Save project** (💾).
8.  **Lưu tất cả các file** (`Code.gs`, `Sidebar.html`). Đặt tên cho Project Apps Script của bạn (ví dụ: "Hedwig Add-on").

### Chạy và Thử nghiệm Add-on

1.  Trong trình soạn thảo Apps Script, đi tới menu `Deploy` > `Test deployments`.
2.  Một cửa sổ sẽ hiện ra. Nhấp vào **Install** > **Done**. (Lần đầu có thể yêu cầu cấp quyền, hãy xem xét và chấp nhận các quyền cần thiết).
3.  Quay lại cửa sổ Google Docs của bạn. **Tải lại (Refresh)** trang Google Docs.
4.  Vào menu `Extensions`. Bạn sẽ thấy menu "Hedwig" xuất hiện.
5.  Chọn "Hedwig" > "Open Translator". Sidebar sẽ mở ra.
6.  Thử các chức năng: Chọn text, load text, chọn ngôn ngữ, dịch, copy.

## Cách sử dụng

1.  Mở sidebar thông qua menu `Extensions > Hedwig > Open Translator`.
2.  **Nhập văn bản:**
    * Gõ hoặc dán trực tiếp vào ô "Text to Translate".
    * Hoặc bôi đen văn bản trong Google Docs rồi nhấn "Load Selected".
    * Hoặc nhấn "Load Full Doc" để lấy toàn bộ văn bản.
3.  **Chọn ngôn ngữ:** Chọn ngôn ngữ nguồn ("From") và ngôn ngữ đích ("To"). Chọn "Auto-detect" nếu muốn tự động phát hiện ngôn ngữ nguồn.
4.  **Tùy chỉnh (Tùy chọn):** Chọn "Translation Engine" (hiện tại là Gemini) và điều chỉnh "Temperature".
5.  **Dịch:** Nhấn nút "Translate". Kết quả sẽ xuất hiện ở ô "Translation Result".
6.  **Sao chép:** Nhấn nút copy (📄) bên dưới ô kết quả để sao chép bản dịch.
7.  **Xuất PDF (Tương lai):** Nút "Export PDF" hiện có nhưng chức năng sẽ được hoàn thiện sau.

## Vấn đề đã biết / Hạn chế

* Thời gian dịch toàn bộ tài liệu rất dài có thể vượt quá giới hạn thực thi của Google Apps Script (~6 phút), gây lỗi timeout phía Apps Script ngay cả khi backend đã xử lý xong.
* Chất lượng bản dịch phụ thuộc hoàn toàn vào mô hình Gemini và có thể thay đổi giữa các cặp ngôn ngữ.
* Phiên bản development yêu cầu chạy song song server Flask và ngrok.
* Phát hiện ngôn ngữ tự động có thể không chính xác với các đoạn text quá ngắn hoặc chứa nhiều ngôn ngữ lẫn lộn.

## Hướng phát triển tương lai

* Hoàn thiện chức năng "Export PDF".
* Triển khai chức năng "Paste/Replace Selected Text" (Ưu tiên 2).
* Hỗ trợ thêm các mô hình AI khác (GPT-4, ...).
* Cải thiện giao diện người dùng và trải nghiệm người dùng.
* Đóng gói và phát hành lên Google Workspace Marketplace (yêu cầu quy trình review của Google).
* Phát triển phiên bản cho Microsoft Word / LibreOffice Writer.