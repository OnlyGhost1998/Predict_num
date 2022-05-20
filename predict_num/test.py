import requests
import json
import base64
from PIL import Image
from io import BytesIO
import numpy as np

img_path = 'work/example_6.jpg'

#with open(img_path, 'rb') as f:
#im = f.read()
#base64_data = base64.b64encode(f.read())
#img = base64_data.decode()

im = Image.open(img_path).convert('L')

#im = im.resize((28,28), Image.ANTIALIAS)

#im = bytes(im)

img_byte = BytesIO()

im.save(img_byte, format='JPEG')

img_bytes = img_byte.getvalue()

    
print(type(img_bytes))

base64_data = base64.b64encode(img_bytes)

img = base64_data.decode()

img_b64decode = base64.b64decode(img)  # base64解码

print(type(img_b64decode))

bytes_stream = BytesIO(img_b64decode)

image = Image.open(bytes_stream)

img_array = image.resize((28,28), Image.ANTIALIAS)

im = np.array(img_array).reshape(1, 1, 28, 28).astype(np.float32)
#图像归一化
im = 1.0 - im / 255

print(type(im))



