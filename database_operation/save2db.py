import PyPDF2
import fitz
import pytesseract
import os
from PIL import Image
from tqdm import tqdm


def text_clean_consolidate(consolidated_text):
    return consolidated_text


def extract_text_from_pdf_consolidate(pdf_file):
    try:
        # Create an empty string to store the consolidated text
        consolidated_text = ""
        with open(pdf_file, "rb") as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Loop through each page in the PDF
            for page_num in tqdm(
                range(len(pdf_reader.pages)),
                desc=f"Extracting text from {pdf_file}",
            ):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                consolidated_text += text  # + "\n"  # Append page text with a newline

            print(len(consolidated_text))

            return text_clean_consolidate(consolidated_text)
    except FileNotFoundError:
        print(f"File not found: {pdf_file}")


def extract_text_from_pdf(pdf_file):
    try:
        # pdf_document = fitz.open(pdf_file)
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)

            extracted_text = ""

            for page_number in range(pdf_document.page_count):
                page = pdf_document.load_page(page_number)
                text = page.get_text()
                extracted_text += text

            pdf_document.close()
            return extracted_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def is_text_based_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            # If any page contains text, it's a text-based PDF
            if text:
                return True
        # If no text found in any page, it's likely an image-based PDF
        return False
    except Exception as e:
        # Handle exceptions (e.g., invalid PDF format)
        print(f"Error: {e}")
        return False


def extract_text_from_image_pdf(pdf_file):
    try:
        extracted_text = ""
        pages = fitz.open(pdf_file)

        for page_number in range(len(pages)):
            image_page = pages.load_page(page_number)
            image = image_page.get_pixmap()
            image_file = f"temp_image_page_{page_number}.png"
            image.save(image_file)

            image_text = pytesseract.image_to_string(image_file)
            extracted_text += image_text

            os.remove(image_file)  # Remove the temporary image file

        return extracted_text
    except Exception as e:
        print(f"Error extracting text from image-based PDF: {e}")
        return ""


def extract_text_from_image(img_file):
    image = Image.open(img_file)
    text = pytesseract.image_to_string(image)
    return text
