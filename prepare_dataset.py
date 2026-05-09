import os

# 1. الأكواد التي سيتعلمها الذكاء الاصطناعي ليتعامل مع ملفات PDF
pdf_knowledge = """
# كود لإنشاء ملف PDF
from fpdf import FPDF
def create_pdf(file_name, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=text, ln=True, align='C')
    pdf.output(file_name)

# كود لقراءة ملف PDF
import PyPDF2
def read_pdf(file_name):
    text = ""
    with open(file_name, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text
"""

def gather_all_code(directory, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # نحقن معرفة الـ PDF في عقله أولاً
        outfile.write(pdf_knowledge + "\n\n")
        
        # المرور على كل الملفات في المجلد ليتعلم كل شيء موجود في حاسوبك
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.html', '.js', '.c', '.cpp', '.txt')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(f"\n# --- File: {file} ---\n")
                            outfile.write(infile.read() + "\n")
                    except Exception:
                        pass
    print(f"✅ تم جمع كل الأكواد والمعلومات في {output_file} بنجاح!")

if __name__ == "__main__":
    # المسار الذي يحتوي على كل مشاريعك وأكوادك
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_directory = current_dir 
    output = os.path.join(current_dir, "training_data.txt")
    gather_all_code(target_directory, output)