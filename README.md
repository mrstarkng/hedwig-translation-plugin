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
    * **(Mới)** Nút "Paste" để thay thế nhanh văn bản đang chọn trong tài liệu bằng kết quả dịch.
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
    Server Flask sẽ khởi chạy (thường ở cổng 5050).

### Cài đặt ngrok

1.  Mở một cửa sổ terminal **khác**.
2.  Chạy ngrok để expose cổng mà Flask đang chạy (ví dụ 5050):
    ```bash
    ngrok http 5050
    ```
3.  **Copy URL HTTPS** từ output của ngrok.

### Cài đặt Frontend (Google Apps Script Add-on)

1.  Mở một tài liệu Google Docs.
2.  Vào `Extensions` > `Apps Script`.
3.  **Copy/Paste** nội dung các file `Code.gs` và `Sidebar.html` vào trình soạn thảo.
4.  **Cập nhật `NGROK_BASE_URL`** trong `Code.gs` bằng URL HTTPS từ ngrok.
5.  **Cấu hình `appsscript.json`**:
    * Hiển thị file manifest (Project Settings ⚙️).
    * Copy/Paste nội dung file `appsscript.json` của dự án vào. Đảm bảo `urlFetchWhitelist` chứa **URL gốc** của ngrok (có dấu `/` ở cuối).
    * **Lưu Project** (💾).
6.  **Đặt tên Project** Apps Script.

### Chạy và Thử nghiệm Add-on

1.  Trong trình soạn thảo Apps Script, `Deploy` > `Test deployments` > `Install` > `Done`. (Cấp quyền nếu được yêu cầu).
2.  Quay lại Google Docs, **tải lại trang**.
3.  Mở sidebar từ `Extensions > Hedwig > Open Translator`.

## Cách sử dụng chi tiết

1.  **Mở Sidebar:**
    * Đi tới menu `Tiện ích mở rộng` (Extensions) trên thanh công cụ Google Docs.
    * Chọn `Hedwig` > `Open Translator`. Sidebar Hedwig sẽ xuất hiện ở bên phải màn hình.

2.  **Nhập Văn bản Nguồn (Văn bản cần dịch):** Có 3 cách:
    * **Gõ/Dán trực tiếp:** Nhập hoặc dán văn bản bạn muốn dịch vào ô lớn có nhãn "Text to Translate".
    * **Load văn bản đang chọn:** Bôi đen (chọn) một đoạn văn bản trong tài liệu Google Docs của bạn, sau đó nhấn nút **`Load Selected`** trong sidebar. Đoạn văn bản đó sẽ được nạp vào ô "Text to Translate".
    * **Load toàn bộ văn bản:** Nhấn nút **`Load Full Doc`**. Toàn bộ nội dung văn bản trong tài liệu sẽ được nạp vào ô "Text to Translate" (hữu ích cho việc dịch cả tài liệu, nhưng hãy cẩn thận với các tài liệu rất dài).

3.  **Chọn Ngôn Ngữ:**
    * **`From` (Nguồn):** Chọn ngôn ngữ gốc của văn bản bạn vừa nhập. Nếu không chắc chắn, hãy để ở chế độ `Auto-detect`, plugin sẽ cố gắng tự động nhận diện.
    * **`To` (Đích):** Chọn ngôn ngữ bạn muốn dịch sang từ danh sách thả xuống. Tiếng Việt được đặt làm mặc định.
    * **Nút `Swap` (Mũi tên đổi chiều):** Nhấn nút này để nhanh chóng hoán đổi ngôn ngữ đã chọn ở ô "From" và "To".

4.  **Tùy chọn Nâng cao (Tùy chọn):**
    * **`Translation Engine`:** Chọn mô hình AI để dịch. Hiện tại, `Gemini` là lựa chọn hoạt động chính.
    * **`Temperature`:** Điều chỉnh thanh trượt hoặc nhập giá trị từ 0.0 đến 1.0. Giá trị thấp hơn (gần 0.0) cho kết quả dịch chính xác và sát nghĩa hơn. Giá trị cao hơn (gần 1.0) cho phép AI "sáng tạo" hơn, nhưng có thể kém chính xác. Mặc định là 0.7.

5.  **Thực hiện Dịch:**
    * Sau khi đã nhập văn bản và chọn ngôn ngữ, nhấn nút **`Translate`**.
    * Nút sẽ hiển thị trạng thái "Translating..." cùng với biểu tượng spinner. Quá trình dịch có thể mất vài giây đến vài phút tùy thuộc vào độ dài văn bản và tải của API.
    * Kết quả dịch sẽ xuất hiện trong ô "Translation Result" bên dưới.

6.  **Sử dụng Kết quả Dịch:**
    * **Đọc:** Xem bản dịch trong ô "Translation Result".
    * **Sao chép:** Nhấn nút **`Copy`** (biểu tượng 2 tờ giấy chồng lên nhau) ở góc dưới bên phải ô kết quả để sao chép toàn bộ nội dung bản dịch vào clipboard của bạn.
    * **Thay thế văn bản gốc:**
        * **Trước tiên, hãy bôi đen (chọn) lại đoạn văn bản gốc** trong tài liệu Google Docs mà bạn muốn thay thế.
        * Sau đó, nhấn nút **`Paste`** trong sidebar. Nội dung bạn vừa chọn trong Docs sẽ được thay thế bằng bản dịch từ ô "Translation Result". *Lưu ý: Hãy cẩn thận chọn đúng đoạn văn bản trước khi nhấn Paste.*

7.  **Xuất PDF:**
    * Nút **`Export PDF`** hiện có sẵn nhưng chức năng này đang trong quá trình phát triển và sẽ được hoàn thiện trong các phiên bản tương lai.

## Vấn đề đã biết / Hạn chế

* Thời gian dịch toàn bộ tài liệu rất dài có thể vượt quá giới hạn thực thi của Google Apps Script (~6 phút), gây lỗi timeout phía Apps Script ngay cả khi backend đã xử lý xong.
* Chất lượng bản dịch phụ thuộc hoàn toàn vào mô hình Gemini và có thể thay đổi giữa các cặp ngôn ngữ.
* Phiên bản development yêu cầu chạy song song server Flask và ngrok.
* Phát hiện ngôn ngữ tự động có thể không chính xác với các đoạn text quá ngắn hoặc chứa nhiều ngôn ngữ lẫn lộn.

## Hướng phát triển tương lai

* Hoàn thiện chức năng "Export PDF".
* Hỗ trợ thêm các mô hình AI khác (GPT-4, ...).
* Cải thiện giao diện người dùng và trải nghiệm người dùng.
* Đóng gói và phát hành lên Google Workspace Marketplace (yêu cầu quy trình review của Google).
* Phát triển phiên bản cho Microsoft Word / LibreOffice Writer.