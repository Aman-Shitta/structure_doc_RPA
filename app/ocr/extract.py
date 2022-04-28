from lib2to3.pytree import convert
from unittest import result
from urllib.request import DataHandler
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from PIL import Image
import os
from fuzzywuzzy import fuzz
from config import AZKEY1, DATA, AZKEY2, ENDPOINT, rearrange_output

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

DOCTR_MODEL = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

class Extractor:
    
    def __init__(self, document):
        
        self.document = document
        self.doc_words = []
        self.output = {}
    

    def generate_ngrams(self, words, n_range=2):
        ngrams = []
        for i in range(0, len(words)-(n_range-1)):
            ngram_words = words[i:i+n_range]
            ngram_text = " ".join([n_word[1] for n_word in ngram_words])
            n_x1, n_y1, n_x2, n_y2 =  ngram_words[0][0][0], ngram_words[0][0][1], ngram_words[-1][0][2], ngram_words[-1][0][3]
            # ngram_cs = sum([n_word[2] for n_word in ngram_words]) / len(ngram_words)
            ngrams.append((
                [n_x1, n_y1, n_x2, n_y2],
                ngram_text
            ))

        return ngrams

    def get_radius_text(self, cords, words):
        max_word_x = max([word[0][2] for word in words])

        left = cords[0] - int(max_word_x*0.02)
        top = cords[1] - int(max_word_x*0.02)
        right = cords[2] + int(max_word_x*0.2)
        bottom = cords[3] + int(max_word_x*0.08)
        
        from PIL import Image, ImageDraw
        img = Image.open('image.jpg')
        dr = ImageDraw.Draw(img)
        dr.rectangle((left, top, right, bottom), outline="green", width=2)
        img.save('rad.png')

        radius_words = []
        for word in words:
            if word[0][0] > left and \
                word[0][1] > top and  \
                    word[0][2] < right  and \
                        word[0][3] < bottom:
                        radius_words.append(word)

        return ' '.join(w[1] for w in radius_words)

    def find_key_value(self, key, words):
        matches = {}
        key_len = len(key.split())
        n_grams = self.generate_ngrams(words, key_len)
        for idx,label in enumerate(n_grams):
            if fuzz.ratio(label[1].lower().strip(), key.lower().strip()) > 85:
                matches.update({idx:label})

        if not matches:
            breakpoint()
            
        for index,matched_label in matches.items():
            radius_text = self.get_radius_text(matched_label[0], words[index:])     
            # breakpoint()

            print(radius_text)

    def extract(self, words):
        # self.doc_words = rearrange_output(ocr_data)
        self.find_key_value("First Name", words)
        # doc = self.document
        # self.get_radius_text()
        return self.output


if __name__ == "__main__":
    import time

    """ AZURE OCR CODE """

    subscription_key = AZKEY1
    computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(subscription_key))
    
    images_folder = "/home/attihs/Downloads"

    # Get image path
    read_image_path = os.path.join (images_folder, "image.jpg")
    # Open the image

    read_image = open(read_image_path, "rb")

    # Call API with image and raw response (allows you to get the operation location)
    read_response = computervision_client.read_in_stream(read_image, raw=True)

    # Get the operation location (URL with ID as last appendage)
    read_operation_location = read_response.headers["Operation-Location"]
    # Take the ID off and use to get results
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for the retrieval of the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower () not in ['notstarted', 'running']:
            break
        print ('Waiting for result...')
        time.sleep(10)

    # Print results, line by line
    pages_data = {}
    if read_result.status == OperationStatusCodes.succeeded:
        # data = read_result.analyze_result.read_results.as_dict
        for text_result in read_result.analyze_result.read_results:
            data = text_result.as_dict()
            # for line in text_result.lines:
            #     print(line.text)
            #     print(line.bounding_box)
            pages_data.update({data['page']:rearrange_output(data)})
    
    
    """ Draw box for words"""
    # from PIL import Image, ImageDraw
    # img = Image.open(read_image_path)
    # dr = ImageDraw.Draw(img)

    # for _,page_words in pages_data.items():
    #     for word in page_words:
    #         dr.rectangle(word[0], outline="red", width=3)
    # img.save('reg.png')


    """ TESTING FURTHER """
    # pages_data = {}
    # pages_data.update({DATA['page']:rearrange_output(DATA)})
    # breakpoint()
    ext = Extractor('path')
    for page, words in pages_data.items():
        print("[+] Finding at Page :: ", page)
        ext.find_key_value("First Name", words)