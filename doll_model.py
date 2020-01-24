# Keras
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping # コールバック関数
from keras.optimizers import SGD # 最適化関数
from keras.initializers import glorot_uniform, orthogonal, TruncatedNormal # 初期化関数
from keras.preprocessing.image import load_img, array_to_img, img_to_array # 画像の取り扱い
from keras.utils import np_utils, plot_model # ?
from keras.layers import Dense, Activation, Dropout, LSTM, Conv2D, MaxPooling2D, Flatten, BatchNormalization # レイヤー
from keras.layers.advanced_activations import PReLU # 応用活性化関数
from keras.layers.recurrent import GRU, SimpleRNN # RNN系関数
from keras import backend as K

# ファインチューニング
from keras.applications.vgg16 import VGG16
from keras.applications.vgg19 import VGG19
from keras.applications.resnet50 import ResNet50
from keras.applications.inception_resnet_v2 import InceptionResNetV2

# 計算
import pandas as pd #行列計算
import numpy as np #行列計算
import math #数値計算
import itertools #順列・組み合わせ

# 図・画像
#import matplotlib.pyplot as plt #グラフ
#import seaborn as sns
from PIL import Image, ImageFilter

# その他
import glob
import re
import gc
import cv2
import os
from datetime import datetime, timedelta

import tensorflow as tf

BATCH_SIZE = 512
EPOCHS = 100
VERBOSE = 1
VALIDATION_SPLIT = 0.2
MODEL = 'CNN'#'ResNet50'#'CNN' #'MyVGG16'
IMG_CHANNELS = 3
#KAITEN_MIZUMASHI = #range(0, 360, 30) # range(0, 1, 90)
KAITEN_MIZUMASHI = range(0, 1, 90)
img_size = 128

model = load_model('model_doll_cnn', compile=False)
graph = tf.get_default_graph()

# 余白を追加
def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

# 余白を追加して正方形に変形
def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result

def pred_price(x):
    x = Image.fromarray(np.uint8(x))
    x = expand2square(x, (255, 255, 255)) # 正方形に整形して
    x = x.resize((img_size, img_size)) # サイズを調整する
    X = []
    X.append(np.array(x))

    global graph
    with graph.as_default():
        pred = model.predict(np.array(X)).flatten()
        
    return pred