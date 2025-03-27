# pdf_utils.py

import logging
from fpdf import FPDF
import os

# --- Font Configuration (ĐÃ THAY ĐỔI) ---
FONT_FILENAME = "NotoSans-Regular.ttf"       # <-- Đổi thành Noto Sans Regular
BOLD_FONT_FILENAME = "NotoSans-Bold.ttf"     # <-- Đổi thành Noto Sans Bold
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), FONT_FILENAME)
BOLD_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), BOLD_FONT_FILENAME)

# (Phần kiểm tra file tồn tại giữ nguyên)
if not os.path.exists(FONT_PATH):
    logging.error(f"CRITICAL: Font file '{FONT_FILENAME}' not found at '{FONT_PATH}'.")
bold_font_exists = os.path.exists(BOLD_FONT_PATH)
if not bold_font_exists:
    logging.warning(f"Bold font file '{BOLD_FONT_FILENAME}' not found at '{BOLD_FONT_PATH}'. Bold style will not be available.")


def create_pdf_from_text(original_text, translated_text, title="Translation Export"):
    try:
        pdf = FPDF()

        # --- Thêm Font Unicode (ĐÃ THAY ĐỔI TÊN FONT) ---
        try:
            # Thêm font thường
            pdf.add_font('NotoSans', '', FONT_PATH, uni=True) # <-- Đổi tên thành 'NotoSans'
            logging.info(f"Successfully added NotoSans regular font.")

            # Thêm font bold NẾU tồn tại file
            if bold_font_exists:
                pdf.add_font('NotoSans', 'B', BOLD_FONT_PATH, uni=True) # <-- Đổi tên thành 'NotoSans', đăng ký kiểu 'B'
                logging.info(f"Successfully added NotoSans bold font.")
            else: pass # Bỏ qua nếu không có font bold

        except Exception as font_err:
            logging.exception(f"Failed to add NotoSans font(s). Error: {font_err}")
            logging.warning("Falling back to default FPDF font (limited Unicode support).")
            pdf.set_font("Arial", size=12)

        # Đặt font mặc định (ĐÃ THAY ĐỔI TÊN FONT)
        pdf.set_font('NotoSans', '', 12) # <-- Đổi thành 'NotoSans'

        pdf.add_page()

        # --- Thêm nội dung (ĐÃ THAY ĐỔI TÊN FONT) ---
        if title:
            title_style = 'B' if bold_font_exists else ''
            pdf.set_font('NotoSans', title_style, 16) # <-- Đổi thành 'NotoSans'
            pdf.cell(0, 10, title, ln=1, align='C')
            pdf.ln(10)

        heading_style = 'B' if bold_font_exists else ''

        # Văn bản gốc
        pdf.set_font('NotoSans', heading_style, 14) # <-- Đổi thành 'NotoSans'
        pdf.cell(0, 10, "Original Text:", ln=1)
        pdf.set_font('NotoSans', '', 12) # <-- Đổi thành 'NotoSans'
        pdf.multi_cell(0, 5, original_text)
        pdf.ln(8)

        # Văn bản đã dịch
        pdf.set_font('NotoSans', heading_style, 14) # <-- Đổi thành 'NotoSans'
        pdf.cell(0, 10, "Translated Text:", ln=1)
        pdf.set_font('NotoSans', '', 12) # <-- Đổi thành 'NotoSans'
        pdf.multi_cell(0, 5, translated_text)

        # --- Xuất PDF ra dạng bytes ---
        pdf_bytes = pdf.output()
        logging.info(f"Successfully generated PDF ({len(pdf_bytes)} bytes).")
        return pdf_bytes

    # (Phần except giữ nguyên)
    except FileNotFoundError as fnf_err:
         logging.error(f"PDF generation failed due to missing font during processing: {fnf_err}")
         return None
    except Exception as e:
        logging.exception("An error occurred during PDF generation:")
        return None

# (Phần if __name__ == "__main__": giữ nguyên nếu có)