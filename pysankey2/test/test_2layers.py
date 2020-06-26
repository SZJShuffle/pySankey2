import os
import sys
sys.path.append(os.path.realpath('.'))
import unittest
import pandas as pd
from pysankey2 import Sankey

class Test2layers(unittest.TestCase):
    def setUp(self):
        self.df = pd.read_csv("./test/data/fruits.txt",sep="\t")
    def test_auto_sankey(self):
        """
        Only passing the dataframe into Sankey, and let it automatically extract attributes(labels, colors, etc) 
        """
        sky_auto_global = Sankey(self.df,colorMode="global")
        sky_auto_layer = Sankey(self.df,colorMode="layer")

    def test_provided_layerLabels_sankey(self):
        """"""
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
        pass
    

    def tearDown(self):
        print("done")
if __name__ == "__main__":
    unittest.main()