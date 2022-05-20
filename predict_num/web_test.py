import requests
import json
import base64

def test(img_path):
    with open(img_path, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        img = base64_data.decode()
        
    datas = json.dumps({'base64': img})
    
    rec = requests.post("http://172.168.0.110:12455", data=datas, headers={'Content-Type': 'application/json'})
    
    return rec.text

img_path = 'work/example_6.jpg'

result = test(img_path)

print("本次预测的数字是：", result)


