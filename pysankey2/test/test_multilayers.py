import os
import sys
sys.path.append(os.path.realpath('.'))
import pandas as pd
from collections import defaultdict
from pysankey2 import LabelMismatchError
from pysankey2 import Sankey
from utils import setColorConf,listRemoveNAN
import unittest
import matplotlib.pyplot as plt

# provided some test case for 2 layers test
#df = pd.read_csv("./test/data/countrys.txt",sep="\t")
df = pd.read_csv("./test/data/fruits.txt",sep=" ")
sky_auto_global_colors = Sankey(df,colorMode="global")
fig,ax = sky_auto_global_colors.plot()
plt.show()