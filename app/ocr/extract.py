from lib2to3.pytree import convert
from unittest import result
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from PIL import Image
import os

DOCTR_MODEL = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

class Extractor:
    
    def __init__(self, document):
        
        self.document = document
        self.output = {}
    
    def convert_tif_to_pages(self, doc):
        document_images = []
        try:
            img = Image.open(doc)
            total_pages = img.n_frames
            if total_pages > 0:
                # create directory for document
                images_path = os.path.splitext(doc)[0]
                filename_split = os.path.basename(doc).split(".")
                os.makedirs(images_path)

                for i in range(total_pages):
                    try:
                        img.seek(i)
                        out_file = ".".join(filename_split[:-1]) + "_" + str(i) + "." + filename_split[-1]
                        img_path = os.path.join(images_path, out_file)
                        img.save(img_path)
                        document_images.append(img_path)

                        # create a PNG version of tif file for frontend use
                        if filename_split[-1].lower() != 'png':
                            png_file = ".".join(filename_split[:-1]) + "_" + str(i) + ".png"
                            img_path = os.path.join(images_path, png_file)
                            img.save(img_path)
                    except EOFError:
                        break
        except Exception as e:
            print(e)

        return document_images

    def convert_doctr_to_words(self, json_output):
        op = {}
        for pi,page in enumerate(json_output['pages']):
            words = []
            for block in page['blocks']:
                for line in block['lines']:
                    for word in line['words']:
                        words.append((word['geometry'], word['value'], word['confidence']*100))
            op.update({pi:words}) 

        return op

    def doctr_ocr(self, doc, doc_type):
        # PDF
        pages = {}
        if doc_type == 'pdf':
            doc_file = DocumentFile.from_pdf(doc)
            result = DOCTR_MODEL(doc_file)
            json_output = result.export()
            page_words = self.convert_doctr_to_words(json_output)
            

        # Image
        elif doc_type in ['jpg', 'jpeg']:
            doc_file = DocumentFile.from_images(doc)
            result = DOCTR_MODEL(doc_file)
            json_output = result.export()
            page_words = self.convert_doctr_to_words(json_output)
            
        else:
            print(f"{doc_type} Format not supported yet !")
        # TIFF image
        # elif doc_type == 'tiff':
        #     pages = {}
        #     image_pages = self.convert_tif_to_pages(doc)
        #     for page,image in enumerate(image_pages):
        #         result = DocumentFile.from_images(image)
        #         json_output = result.export()
        #         page_words = self.convert_doctr_to_words(json_output)
        #         pages.update({page+1:page_words})

        self.output = page_words

    def identify_doc_type(self, doc):
        file_n = os.path.splitext(doc)[-1]
        if file_n.endswith('jpeg') or file_n.endswith('jpg'):
            return "jpeg"
        if file_n.endswith('pdf'):
            return "pdf"

    def extract(self):
        doc = self.document
        doc_type = self.identify_doc_type(doc)
        self.doctr_ocr(doc, doc_type=doc_type)
        return self.output

if __name__ == "__main__":
    path = "/home/aman/Downloads/sample.pdf"
    # path = "/home/aman/Downloads/Aman_Shitta_Resume_26-02-2022-22-13-48.pdf"

    e = Extractor(path)
    print(e.extract())
    # breakpoint()