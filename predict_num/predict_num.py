#!/usr/bin/env python
# coding: utf-8

# In[54]:


#导入所需要的包
import paddle
from paddle.nn import Linear
from paddle.nn import Conv2D, MaxPool2D
from paddle.io import Dataset
import paddle.nn.functional as F
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import os
import gzip
import json
import random
import numpy as np
import base64


# In[55]:


#创建异步读取数据类
class MnistDataset(paddle.io.Dataset):
    def __init__(self, mode):
        #读取数据
        datafile = './work/mnist.json.gz'
        #解压缩
        data = json.load(gzip.open(datafile))
        #将读取到的数据进行划分为训练集、验证集、测试集
        train_set, val_set, eval_set = data
        # 数据集相关参数，图片高度IMG_ROWS, 图片宽度IMG_COLS
        self.IMG_ROWS = 28
        self.IMG_COLS = 28

        if mode=='train':
            # 获得训练数据集
            imgs, labels = train_set[0], train_set[1]
        elif mode=='valid':
            # 获得验证数据集
            imgs, labels = val_set[0], val_set[1]
        elif mode=='eval':
            # 获得测试数据集
            imgs, labels = eval_set[0], eval_set[1]
        else:
            raise Exception("mode can only be one of ['train', 'valid', 'eval']")

        #校验数据
        imgs_length = len(imgs)
        assert len(imgs) == len(labels), "length of train_imgs({}) should be the same as train_labels({})".format(len(imgs), len(labels))

        self.imgs = imgs
        self.labels = labels
    
    def __getitem__(self, idx):
        #img = np.array(self.imgs[idx]).astype('float32')
        #labels = np.array(self.labels[idx]).astype('float32')
        img = np.reshape(self.imgs[idx], [1, self.IMG_ROWS, self.IMG_COLS]).astype('float32')
        label = np.reshape(self.labels[idx], [1]).astype('int64')

        return img, label
    
    def __len__(self):

        return len(self.imgs)


# In[56]:


#多层卷积化神经网络的实现
class MNIST(paddle.nn.Layer):
    def __init__(self):

        super(MNIST, self).__init__()

        # 定义卷积层，输出特征通道out_channels设置为20，卷积核的大小kernel_size为5，卷积步长stride=1，padding=2
        self.conv1 = Conv2D(in_channels=1, out_channels=20, kernel_size=5, stride=1, padding=2)
        # 定义池化层，池化核的大小kernel_size为2，池化步长为2
        self.max_pool1 = MaxPool2D(kernel_size=2, stride=2)
        # 定义卷积层，输出特征通道out_channels设置为20，卷积核的大小kernel_size为5，卷积步长stride=1，padding=2
        self.conv2 = Conv2D(in_channels=20, out_channels=20, kernel_size=5, stride=1, padding=2)
        # 定义池化层，池化核的大小kernel_size为2，池化步长为2
        self.max_pool2 = MaxPool2D(kernel_size=2, stride=2)
        # 定义一层全连接层，输出维度是1
        self.fc = Linear(in_features=980, out_features=10)
         
    # 定义网络前向计算过程，卷积后紧接着使用池化层，最后使用全连接层计算最终输出
    # 卷积层激活函数使用Relu，全连接层不使用激活函数
    def forward(self, inputs):
        x = self.conv1(inputs)
        x = F.relu(x)
        x = self.max_pool1(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = self.max_pool2(x)
        x = paddle.reshape(x, [x.shape[0], -1])
        x = self.fc(x)
        return x


# In[57]:


#手写数字模型训练和部署
class MNISTmodel(object):

    def evaluation(model, datasets):

        model.eval()#eval

        acc_set = list()
        for batch_id, data in enumerate(datasets()):
            images, labels = data
            images = paddle.to_tensor(images)
            labels = paddle.to_tensor(labels)
            pred = model(images)   # 获取预测值
            acc = paddle.metric.accuracy(input=pred, label=labels)
            acc_set.extend(acc.numpy())
    
        # #计算多个batch的准确率
        acc_val_mean = np.array(acc_set).mean()
        return acc_val_mean
    
    #仅修改计算损失的函数，从均方误差（常用于回归问题）到交叉熵误差（常用于分类问题）
    def train(self,model):
        #model.train()
        #调用加载数据的函数
        # train_loader = load_data('train')
        # val_loader = load_data('valid')
        opt = paddle.optimizer.SGD(learning_rate=0.01, parameters=model.parameters())
        # opt = paddle.optimizer.Momentum(learning_rate=0.01, momentum=0.9, parameters=model.parameters())
        EPOCH_NUM = 10
        for epoch_id in range(EPOCH_NUM):
            for batch_id, data in enumerate(train_loader()):
                #准备数据
                images, labels = data
                images = paddle.to_tensor(images)
                labels = paddle.to_tensor(labels)
                #前向计算的过程
                predicts = model(images)
            
                #计算损失，使用交叉熵损失函数，取一个批次样本损失的平均值
                loss = F.cross_entropy(predicts, labels)
                avg_loss = paddle.mean(loss)
            
                #每训练了200批次的数据，打印下当前Loss的情况
                if batch_id % 200 == 0:
                    print("epoch: {}, batch: {}, loss is: {}".format(epoch_id, batch_id, avg_loss.numpy()))
            
                #后向传播，更新参数的过程
                avg_loss.backward()
                # 最小化loss,更新参数
                opt.step()
                # 清除梯度
                opt.clear_grad()
        # acc_train_mean = evaluation(model, train_loader)
        # acc_val_mean = evaluation(model, val_loader)
        # print('train_acc: {}, val acc: {}'.format(acc_train_mean, acc_val_mean))   
        #保存模型参数
        paddle.save(model.state_dict(), 'mnist.pdparams')


# In[58]:


# 声明数据加载函数，使用训练模式，MnistDataset构建的迭代器每次迭代只返回batch=1的数据
#train_dataset = MnistDataset(mode='train')

# 使用paddle.io.DataLoader 定义DataLoader对象用于加载Python生成器产生的数据，
# DataLoader 返回的是一个批次数据迭代器，并且是异步的；

#train_loader = paddle.io.DataLoader(train_dataset, batch_size=100, shuffle=True, drop_last=True)
#val_dataset = MnistDataset(mode='valid')
#val_loader = paddle.io.DataLoader(val_dataset, batch_size=128,drop_last=True)

#运行测试
#model = MNIST()

#MNIST_model = MNISTmodel()
#MNIST_model.train(model)


# In[59]:


class Predict_image(object):
    
    #本地读取图片数据
    def load_image(self, img_path):
        #读取打开图片
        im = Image.open(img_path).convert('L')
        #转化为灰度图
        im = im.resize((28,28), Image.ANTIALIAS)

        im = np.array(im).reshape(1, 1, 28, 28).astype(np.float32)
        #图像归一化
        im = 1.0 - im / 255

        return im 
    def conversion_image(self, img_byte):
        #base64解码
        img_b64decode = base64.b64decode(img_byte)  # base64解码
        #将字节流转化为Image对象
        bytes_stream = BytesIO(img_b64decode)

        image = Image.open(bytes_stream)

        img_array = image.resize((28,28), Image.ANTIALIAS)

        im = np.array(img_array).reshape(1, 1, 28, 28).astype(np.float32)
        #图像归一化
        im = 1.0 - im / 255

        return im
    
    #网络接口
    def Predict_web(self, img_byte):

        model = MNIST()

        params_file_path = 'mnist.pdparams'
        #加载模型参数
        param_dict = paddle.load(params_file_path)
        model.load_dict(param_dict)
        #载入数据
        model.eval()
        #读取数据
        tensor_img = self.conversion_image(img_byte)
        #模型反馈10个分类标签
        result = model(paddle.to_tensor(tensor_img))
        #取概率最大的标签作为预测输出
        lab = np.argsort(result.numpy())

        return lab
    
    #本地调用   
    def Predict(self, img_path):

        model = MNIST()
        
        params_file_path = 'mnist.pdparams'
        #加载模型参数
        param_dict = paddle.load(params_file_path)
        model.load_dict(param_dict)
        #载入数据
        model.eval()
        #转化图片格式
        tensor_img = self.load_image(img_path)
        #模型反馈10个分类标签
        result = model(paddle.to_tensor(tensor_img))
        #取概率最大的标签作为预测输出
        lab = np.argsort(result.numpy())

        return lab


# In[60]:


#预测测试
#模型测试
#p1 = Predict_image()
#path1 = 'work/example_6.jpg'
#lab1 = p1.Predict(path1)

#print("本次预测的数字是：", lab1[0][-1])

