import os
import sys
sys.path.append(os.path.realpath('.'))
import unittest
import pandas as pd
from pysankey2 import Sankey
from utils import setColorConf,listRemoveNAN

class TestTwolayers(unittest.TestCase):
    def setUp(self):
        """
        不是必要的东西最好不要写在setup里，有几个test方法就会运行setup几次。
        """
        self.df = pd.read_csv("./test/data/fruits.txt",sep=" ",header=None,names=['From', 'To'])
        tot_labs = list(set(self.df.From) & set(self.df.To))
        #print(self.df)
        
        # provided colors
        self.globalColors = dict(zip(tot_labs,setColorConf(len(tot_labs))))

        
        self.layerColors = {"layer1":dict(zip(set(self.df.From),
                                            setColorConf(len(set(self.df.From))))),
                            "layer2":dict(zip(set(self.df.To),
                                            setColorConf(len(set(self.df.From)),colors="tab10")))}
        print(self.globalColors)
        print(self.layerColors)

        # provided layerlabels 
        self.layerLabels = {"layer1":list(set(self.df.From)),"layer2":list(set(self.df.To))}
        print(self.layerLabels)
        
        # auto mode
        self.sky_auto_global = Sankey(self.df,colorMode="global")
        self.sky_auto_layer = Sankey(self.df,colorMode="layer")

        # provided colors global & layer mode
        self.sky_provided_glbcolors = Sankey(self.df,
                    colorDict=self.globalColors,
                    colorMode="global")
        
        self.sky_provided_lyrcolors = Sankey(self.df,
                    colorDict=self.layerColors,
                    colorMode="layer")
        
        # provided layerlabels 
        self.sky_provided_lyrlabels = Sankey(self.df,
                    #colorDict=colors,
                    colorMode="global",
                    layerLabels=self.layerLabels)
        

        """
        需要测试的：

        """
    def test_auto_xxxx(self):
        """
        Only passing the dataframe into Sankey, and let it automatically extract attributes(labels, colors, etc) 
        """

    def test_provided_layerLabels_sankey(self):
        """
        
        """
        pass

    def test_provided_colorDict_sankey(self):
        """
        provided global/layer color
        provided layer order.
        """
        pass



    def test_init(self):
        pass

    def test_colorMode(self):
        """global/layer/provided global/provided layer"""
        pass


    
    def test_attr_columnMaps(self):
        pass
    
    def test_attr_labels(self):
        pass
    
    def test_attr_layerLabels(self):
        pass

    def test_attr_boxPos(self):
        pass

    def test_attr_layerPos(self):
        pass
    
    def test_attr_stripWidth(self):
        pass

    def test_attr_colorDict(self):
        pass    

    def test_error(self):
        """
        主要是一些异常抛出的测试
        """
        pass
    

    def tearDown(self):
        print("done")
if __name__ == "__main__":
    unittest.main()