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