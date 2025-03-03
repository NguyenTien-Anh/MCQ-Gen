# import fitz
# def read_pdf_with_images(pdf_file):
#     """
#     Đọc file PDF và trả về dữ liệu HTML dưới dạng chuỗi, giữ lại ảnh.

#     Args:
#         pdf_file (str): Đường dẫn đến file PDF đầu vào.

#     Returns:
#         str: Dữ liệu HTML của file PDF.
#     """
#     try:
#         doc = fitz.open(pdf_file)
#         html_content = ""
#         for page in doc:
#             text = page.get_text("html")
#             html_content += text
#         return html_content
#     except Exception as e:
#         print(f"Lỗi khi chuyển đổi: {e}")
#         return None