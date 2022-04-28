from PIL import Image, ImageDraw

def rearrange_output(data):
    words = []
    try:
        for line in data['lines']:
            for word in line['words']:
                # cords = [int(i) for i in word['bounding_box'].split(',')]
                cords = (word['bounding_box'][0], word['bounding_box'][1], word['bounding_box'][-4],word['bounding_box'][-3])
                WORD = word['text']
                conf = word["confidence"]*100
                words.append(((cords, WORD, conf)))
    except Exception as e:
        print(f"reaggrange_output :: Exception :: {str(e)}")
    
    return words



def draw_cord(cords, color, in_name, out_name):
    img = Image.open(in_name)
    dr = ImageDraw.Draw(img)
    dr.rectangle(cords, outline=color, width=2)
    img.save(out_name)