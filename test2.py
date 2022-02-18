import requests
from pprint import pprint
from PIL import Image, ExifTags, ImageOps
import json


def imageprocess(filename):
    regions = ['sg'] # Change to your country
    with open(filename, 'rb') as fp:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
             data=dict(regions=regions),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': 'Token 37649c697240c794ff946cce1c0132d8af2aaf54'})
    result = response.json()
    try:
        plate = result['results'][0]['plate']
        return(plate)
    except:
        return (result)



pic = Image.open('static/uploads/image.jpg')
pic = ImageOps.exif_transpose(pic)
pic.save('static/uploads/image.jpg',optimize=True,quality=30)
extracted_text = imageprocess('static/uploads/image.jpg').upper()
pprint(extracted_text)



