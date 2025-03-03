from docx import Document as DocxDocument
def read_docx_file(file):
    file_content = ''
    doc = DocxDocument(file)
    for para in doc.paragraphs:
        file_content += " " + para.text
    return file_content


