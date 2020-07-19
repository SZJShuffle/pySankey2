import os
import sys
sys.path.append(os.path.realpath('.'))
import pandas as pd

def load_fruits():
    return pd.read_csv('./test/data/fruits.txt',sep=" ",header=None,names=['layer1', 'layer2'])
def load_countrys():
    return pd.read_csv("./test/data/countrys.txt",sep="\t",header=None,names=['layer1', 'layer2','layer3'])