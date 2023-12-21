

import fitz
from glob import glob
import json
import os
from pdf2image import convert_from_path
from PIL import Image
from platform import system
from PyPDF2 import PdfReader
import pytesseract
import re
from tempfile import TemporaryDirectory
from tqdm.auto import tqdm
 

class PDF():
    def __init__(self, name:str=None):
        EXECUTABLE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        operating_system = system() 
        print(operating_system)

        if operating_system == "Windows":
            # We may need to do some additional downloading and setup...
            # Windows needs a PyTesseract Download
            # https://github.com/UB-Mannheim/tesseract/wiki/Downloading-Tesseract-OCR-Engine
        
            # If you don't have tesseract executable in your PATH, include the following:
            # Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
            pytesseract.pytesseract.tesseract_cmd = EXECUTABLE
        
            # Windows also needs poppler_exe
            path_to_poppler_exe = Path(r"C:\.....")
            
            # Put our output files in a sane place...
            out_directory = os.path.expanduser("~\Desktop")
        else:
            out_directory = os.path.expanduser("~")
        
        # Path of the Input pdf
        PDF_file = "d.pdf"
        
        # Store all the pages of the PDF in a variable
        image_file_list = []
        
        text_file = os.path.join(out_directory, "out_text.txt")
        
    def convert_to_images(self):
        
        ''' Main execution point of the program'''
        with TemporaryDirectory() as tempdir:
            # Create a temporary directory to hold our temporary images.
    
            """
            Part #1 : Converting PDF to images
            """
    
            # Read in the PDF file at 500 DPI
            if operating_system == "Windows":
                pdf_pages = convert_from_path(
                    PDF_file, 500, poppler_path=path_to_poppler_exe
                )
            else:
                pdf_pages = convert_from_path(PDF_file, 500)
                
    
            # Iterate through all the pages stored above
            for page_enumeration, page in enumerate(pdf_pages, start=1):
                # enumerate() "counts" the pages for us.
    
                # Create a file name to store the image
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg"
    
                # Declaring filename for each page of PDF as JPG
                # For each page, filename will be:
                # PDF page 1 -> page_001.jpg
                # ....
                # PDF page n -> page_00n.jpg
    
                # Save the image of the page in system
                page.save(filename, "JPEG")
                image_file_list.append(filename)
    
    def run_ocr(self):
    
            """
            Part #2 - Recognizing text from the images using OCR
            """

            # Simple image to string        
            print(pytesseract.image_to_string(Image.open('test.png')))
            
            '''
            # Example of adding any additional options
            custom_oem_psm_config = r'--oem 3 --psm 6'
            pytesseract.image_to_string(image, config=custom_oem_psm_config)

            # Example of using pre-defined tesseract config file with options
            cfg_filename = 'words'
            pytesseract.run_and_get_output(image, extension='txt', config=cfg_filename)
            
            Add the following config, if you have tessdata error like: “Error opening data file…”

            # Example config: r'--tessdata-dir "C:\Program Files (x86)\Tesseract-OCR\tessdata"'
            # It's important to add double quotes around the dir path.
            tessdata_dir_config = r'--tessdata-dir "<replace_with_your_tessdata_dir_path>"'
            pytesseract.image_to_string(image, lang='chi_sim', config=tessdata_dir_config)
            '''

            # In order to bypass the image conversions of pytesseract, just use relative or absolute image path
            # NOTE: In this case you should provide tesseract supported images or tesseract will return error
            print(pytesseract.image_to_string('test.png'))

            # List of available languages
            print(pytesseract.get_languages(config=''))

            # French text image to string
            print(pytesseract.image_to_string(Image.open('test-european.jpg'), lang='fra'))

            # Batch processing with a single file containing the list of multiple image file paths
            print(pytesseract.image_to_string('images.txt'))

            # Timeout/terminate the tesseract job after a period of time
            try:
                print(pytesseract.image_to_string('test.jpg', timeout=2)) # Timeout after 2 seconds
                print(pytesseract.image_to_string('test.jpg', timeout=0.5)) # Timeout after half a second
            except RuntimeError as timeout_error:
                # Tesseract processing is terminated
                pass

            # Get bounding box estimates
            print(pytesseract.image_to_boxes(Image.open('test.png')))

            # Get verbose data including boxes, confidences, line and page numbers
            print(pytesseract.image_to_data(Image.open('test.png')))

            # Get information about orientation and script detection
            print(pytesseract.image_to_osd(Image.open('test.png')))

            # Get a searchable PDF
            pdf = pytesseract.image_to_pdf_or_hocr('test.png', extension='pdf')
            with open('test.pdf', 'w+b') as f:
                f.write(pdf) # pdf type is bytes by default

            # Get HOCR output
            hocr = pytesseract.image_to_pdf_or_hocr('test.png', extension='hocr')

            # Get ALTO XML output
            xml = pytesseract.image_to_alto_xml('test.png')

    
            with open(text_file, "a") as output_file:
                # Open the file in append mode so that
                # All contents of all images are added to the same file
    
                # Iterate from 1 to total number of pages
                for image_file in image_file_list:
    
                    # Set filename to recognize text from
                    # Again, these files will be:
                    # page_1.jpg
                    # page_2.jpg
                    # ....
                    # page_n.jpg
    
                    # Recognize the text as string in image using pytesserct
                    text = str(((pytesseract.image_to_string(Image.open(image_file)))))
    
                    # The recognized text is stored in variable text
                    # Any string processing may be applied on text
                    # Here, basic formatting has been done:
                    # In many PDFs, at line ending, if a word can't
                    # be written fully, a 'hyphen' is added.
                    # The rest of the word is written in the next line
                    # Eg: This is a sample text this word here GeeksF-
                    # orGeeks is half on first line, remaining on next.
                    # To remove this, we replace every '-\n' to ''.
                    text = text.replace("-\n", "")
    
                    # Finally, write the processed text to the file.
                    output_file.write(text)
    
                # At the end of the with .. output_file block
                # the file is closed after writing all the text.
            # At the end of the with .. tempdir block, the
            # TemporaryDirectory() we're using gets removed!       
        # End of main function!

    def read(self, filename:str):
        pdf_reader = PdfReader(filename)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()      
        return text
        
    def extract_text(self, filename: str) -> list:
        # Open the PDF file of your choice
        with open(filename, 'rb') as f:
            reader = PdfReader(f, strict=False)
            number_of_pages = len(reader.pages)
            print(f'Document contains {number_of_pages} pages.')
            meta = reader.metadata
            print('The following informations area stored in the file: ')
            #print(json.dumps(meta, indent=4, sort_keys=True))
            '''
            for k in dir(meta):
                if not k.startswith('_'):
                    v = getattr(meta, k)
                    if v:
                        print(k, v)
            '''
            for x in [meta.author, meta.creator, meta.producer, meta.subject, meta.title]:
                if x is not None:
                    print(x)

            #text = []
            text = ''
            for page in reader.pages:
                content = page.extract_text()
                #text.append(content)
                text += content
            return text

    def check_all_files(self, folder:str):
        filenames = glob(os.path.join(folder, '*.pdf'))
        pbar = tqdm(filenames[:10])
        outcome = {}
        for filename in pbar:
            pbar.set_description(f'{filename: >80}')
            basename = os.path.basename(filename)
            outcome[basename] = is_text_document(filename)
        return outcome

    def is_text_document(self, filename:str) -> bool:
        """
        Calculate the percentage of document that is covered by (searchable) text.

        If the returned percentage of text is very low, the document is
        most likely a scanned PDF
        """
        total_image_area = 0.0
        total_text_area = 0.0

        with open(filename,"rb") as f:
            doc = fitz.open(f)
            res = []
            for page in doc:
                image_area = 0.0
                text_area = 0.0
                for b in page.get_text("blocks"):
                    if '<image:' in b[4]:
                        # rectangle where block text appears
                        r = fitz.Rect(b[:4])
                        image_area += + abs(r)
                    else:
                        r = fitz.Rect(b[:4])
                        text_area += abs(r)
                total_image_area += image_area
                total_text_area += text_area
            print(f'Total Text Area : {total_text_area}, Total Image Area : {total_image_area}')
            if total_text_area:
                outcome = True
            else:
                outcome = False
            return outcome

    def is_text_document_pdfplumber(self, filename:str) -> bool:
        import pdfplumber
        with pdfplumber.open(filename) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            print(text)
            if text:
                return True
            else:
                return False
