import pandas as pd
from os.path import dirname
def load_fruits():
    return pd.read_csv(dirname(__file__) + '/test/data/fruits.txt',sep=" ",header=None,names=['layer1', 'layer2'])
def load_countrys():
    return pd.read_csv(dirname(__file__) + "/test/data/countrys.txt",sep="\t",header=None,names=['layer1', 'layer2','layer3'])

