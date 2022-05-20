#导入所需要的包
from fastapi import FastAPI
from pydantic import BaseModel
from io import BytesIO
import uvicorn
import random
import os
import base64
import json
import time
import numpy as np

#导入封装好的模型
from predict_num import Predict_image

#模型测试
#p1 = Predict_image()

#lab1 = p1.Predict('work/example_6.jpg')

#print("本次预测的数字是：", lab1[0][-1])

#定义接受的数据结构
class Item(BaseModel):
    #图片字节流base64
    base64: bytes = None

app = FastAPI()

@app.post("/")
async def calculate(request_data: Item):
    
    img_base64 = request_data.base64

    #输出检测的时间和目标
    print("!Time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    p1 = Predict_image()

    lab1 = p1.Predict_web(img_base64)
    lab_info = lab1[0][-1]

    lab_info = int(lab_info)
    print(lab_info)
    print(type(lab_info))

    return lab_info



if __name__ == '__main__':
    print('Loaded face model!')
    print("Service start!")

    uvicorn.run(app=app,
                host = "172.168.0.110",
                port = 12455,
                workers = 1)


'''
img_path = 'work/example_6.jpg'

with open(img_path, 'rb') as f:
    
    base64_data = base64.b64encode(f.read())
    
    img = base64_data.decode()

p1 = Predict_image()

lab1 = p1.Predict_web(img)
lab_info = lab1[0][-1]

print(lab_info)
'''

