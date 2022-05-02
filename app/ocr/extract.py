import re
import os
import time
import json
from PIL import Image, ImageDraw
from fuzzywuzzy import fuzz
from .config import AZKEY1, DATA, AZKEY2, ENDPOINT
from .helper import rearrange_output, draw_cord

# Azure OCR imports
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes



subscription_key = AZKEY1
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(subscription_key))

class Extractor:
    
    def __init__(self):
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

        left = cords[0] - int(max_word_x*0.2)
        top = cords[1] - int(max_word_x*0.02)
        right = cords[2] + int(max_word_x*0.25)
        bottom = cords[3] + int(max_word_x*0.08)

        radius_words = []
        for word in words:
            if word[0][0] > left and \
                word[0][1] > top and  \
                    word[0][2] < right  and \
                        word[0][3] < bottom:
                        radius_words.append(word)
        # draw_cord((left,top,right,bottom), "red", "/home/aman/Documents/ocr_test/aadh2.png", "/home/aman/Documents/ocr_test/dob_2.png")
        return ' '.join(w[1] for w in radius_words)

    def find_key_value(self, key, words):
        matches = {}
        radius_text = ""
        key_len = len(key.split())
        n_grams = self.generate_ngrams(words, key_len)
        for idx,label in enumerate(n_grams):
            if fuzz.ratio(label[1].lower().strip(), key.lower().strip()) > 85:
                matches.update({idx:label})
            
        for index,matched_label in matches.items():
            radius_text = self.get_radius_text(matched_label[0], words[index:])     
        
            print("Possible Text :: ", radius_text)
        return radius_text

def get_ocr_data_azure(file_path):
    """ AZURE OCR CODE """
    pages_data = {}

    try:
        # Open the image
        read_image = open(file_path, "rb")

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
    except Exception as e:
        print(f"Azure OCR error :: Exception :: {str(e)}")
  
    return pages_data
   
def extract_attribute(key, file_path, regex):
    # Get image path
    file_loc = os.path.split(file_path)[0]
    ocr_folder = "/json_data/"
    # breakpoint()
    res = ""
    # folder = "/home/aman/Documents/ocr_test/"
    json_folder = file_loc+ocr_folder
    # file_path = os.path.join (folder, "aadh2.png")
    file_name = os.path.split(file_path)[-1]
    json_file_name = file_name.split('.')[0]+".json"
    
    if json_file_name not in os.listdir(json_folder):
        print("OCRING...")
        pages_data =  get_ocr_data_azure(file_path)
    else:
        print("Reading Existing ")
        fr = open(json_folder + json_file_name)
        pages_data = json.load(fr)
        fr.close()

    if json_file_name not in os.listdir(json_folder):
        print("Writing....")
        fp = open(json_folder+json_file_name, 'w')
        json.dump(pages_data,fp)
        fp.close()
    
    """ TESTING FURTHER """
    ext = Extractor()
    for page, words in pages_data.items():
        print("[+] Finding at Page :: ", page)
        res = ext.find_key_value(key, words)
    # breakpoint()
    all_text = ' '.join(i[1] for i in [j for j in list(pages_data.values())[0]])

    if not res and regex:
        found = re.search(regex, all_text)
        if found:
            res = found.group() 
        

    return res