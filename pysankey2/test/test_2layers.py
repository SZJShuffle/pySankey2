import os
import sys
sys.path.append(os.path.realpath('.'))
import pandas as pd
from collections import defaultdict
from pysankey2 import LabelMismatchError
from pysankey2 import Sankey
from pysankey2.utils import setColorConf,listRemoveNAN
import unittest



class TestTwolayers(unittest.TestCase):

    def test_attr_colnameMaps(self):
        for sky in testCase['sankeys'].keys():
            if sky !="provided_layer_labels":
                self.assertEqual(testCase['sankeys'][sky].colnameMaps,
                                    testCase['colnames']['colname_layer_map'])
            else:
                self.assertEqual(testCase['sankeys'][sky].colnameMaps,
                                    testCase['colnames']['layer_layer_map'])

    def test_attr_labels(self):
        for sky in testCase['sankeys'].keys():
            self.assertEqual(set(testCase['sankeys'][sky].labels),
                            set(testCase['labels']['global_labels']))            

    def test_attr_layerLabels(self):
        for sky in testCase['sankeys'].keys():
            #print(sky)
            #print(testCase['sankeys'][sky].layerLabels)
            if sky !="provided_layer_labels":
                labs = testCase['sankeys'][sky].layerLabels
                for lab in labs.keys():
                    self.assertEqual(set(labs[lab]),
                                        set(testCase['labels']['layer_labels'][lab]))
            else:
                self.assertEqual(testCase['sankeys'][sky].layerLabels,
                                    testCase['labels']['layer_labels_specified'])

    def test_attr_boxPos(self):
        for sky in testCase['sankeys'].keys():
            labs = testCase['sankeys'][sky].layerLabels
            bps = testCase['sankeys'][sky].boxPos
            for layer in labs.keys():
                layer_labs = labs[layer]

                for i,layer_lab in enumerate(layer_labs):
                    if i ==0:
                        assumed_bottom = 0
                        assumed_height = ((testCase['dfs']['df_layer'][testCase['dfs']['df_layer'].loc[:,layer] == layer_lab])
                                            .loc[:,layer]
                                            .count())
                        #print(assumed_height)
                    else:
                        # 0.02：default boxInterv setting
                        assumed_bottom = assumed_height + 0.02 * testCase['dfs']['df_layer'].loc[:,layer].count()
                        assumed_height = ((testCase['dfs']['df_layer'][testCase['dfs']['df_layer'].loc[:,layer] == layer_lab])
                                            .loc[:,layer]
                                            .count()) + assumed_bottom 

                    self.assertEqual(bps[layer][layer_lab]['bottom'],assumed_bottom)
                    self.assertEqual(bps[layer][layer_lab]['top'],assumed_height)

    def test_attr_layerPos(self):
        for sky in testCase['sankeys'].keys():
            lps = testCase['sankeys'][sky].layerPos
            labs = testCase['sankeys'][sky].layerLabels
            for i,layer in enumerate(labs.keys()):
                if i ==0:
                    assumed_start = 0
                    assumed_end = 2 # default boxWidth
                else:
                    assumed_start = assumed_end + 10 # default stripLen
                    assumed_end = assumed_start + 2 # default boxWidth
                
                self.assertEqual(lps[layer]['layerStart'],assumed_start) 
                self.assertEqual(lps[layer]['layerEnd'],assumed_end) 

    
    def test_attr_stripWidth(self):
        for sky in testCase['sankeys'].keys():
            lbs = testCase['sankeys'][sky].layerLabels
            layers = list(lbs.keys())
            stpw = testCase['sankeys'][sky].stripWidth 
            for i,layer in enumerate(layers):
                if i == len(layers) -1:
                    break
                leftLayer = layers[i]
                rightLayer = layers[i+1]

                for leftLabel in lbs[leftLayer]:
                    for rightLabel in lbs[rightLayer]:
                        width = len(testCase['dfs']['df_layer'][(testCase['dfs']['df_layer'].loc[:,leftLayer] == leftLabel) & (testCase['dfs']['df_layer'].loc[:,rightLayer] == rightLabel)])
                        if width >0:
                            self.assertEqual(stpw[leftLayer][leftLabel][rightLabel],width)
                
    def test_attr_colorDict(self):
        """only test provided color case"""
        for sky in testCase['sankeys'].keys():  
            if "provided" not in sky:
                continue
            if "layer_colors" in sky:
                self.assertEqual(testCase['colors']['layer_colors'],testCase['sankeys'][sky].colorDict)
            elif "global_colors" in sky:
                # global_colors
                self.assertEqual(testCase['colors']['global_colors'],testCase['sankeys'][sky].colorDict)
      
    def test_colorMode_Error(self):
        with self.assertRaises(ValueError):
            Sankey(df,colorMode="glb")

    def test_LabelMismatch_Error(self):
        mism_cls = {'blueberrys': '#1f77b4', 'abcs': '#aec7e8', 'lime': '#ff7f0e', 'orange': '#ffbb78', 'apple': '#2ca02c'}
        mism_lyr_cls = {'layer1': {'blueberry': '#1f77b4', 'banana': '#aec7e8', 'lime': '#ff7f0e', 'orange': '#ffbb78', 'apple': '#2ca02c'}, 
                            'layer2': {'blueberry': '#1f77b4', 'abcs': '#ff7f0e', 'lime': '#2ca02c', 'orange': '#d62728', 'apple': '#9467bd'}}
        # Color mismatch with Label
        with self.assertRaises(LabelMismatchError):
            Sankey(df,
            colorDict= mism_cls,
            colorMode="global")
        with self.assertRaises(LabelMismatchError):
            Sankey(df,
            colorDict=mism_lyr_cls,
            colorMode="global")

        # Layer mismatch with DF
        mism_labs = {'layer1':['apple','abs','blueberry', 'lime', 'orange'],
                     'layer2':['apple','banana','blueberry', 'lime', 'orange']}
        with self.assertRaises(LabelMismatchError):
            Sankey(df_layer,
                    colorMode="global",
                    layerLabels=mism_labs)


    def test_kws_Error(self):
        # box text strip
        with self.assertRaises(TypeError):
            Sankey(df_layer,colorMode="global").plot(box_kws =5)

        with self.assertRaises(TypeError):
            Sankey(df_layer,colorMode="global").plot(text_kws =[1,2])

        with self.assertRaises(TypeError):
            Sankey(df_layer,colorMode="global").plot(strip_kws ='strip')
    
if __name__ == "__main__":
    # provided some test case for 2 layers test
    df = pd.read_csv("./pysankey2/test/data/fruits.txt",sep=" ",header=None,names=['From', 'To'])
    df_layer = pd.read_csv("./pysankey2/test/data/fruits.txt",sep=" ",header=None,names=['layer1', 'layer2'])
    
    # labels
    global_labels =  list(set(df.From).union(set(df.To)))
    layer_labels = {"layer1":list(set(df_layer.layer1)),"layer2":list(set(df_layer.layer2))}
    layer_labels_specified = {'layer1':['apple','banana','blueberry', 'lime', 'orange'],
                            'layer2':['apple','banana','blueberry', 'lime', 'orange']}

    # colors
    global_colors = dict(zip(global_labels,setColorConf(len(global_labels))))
    layer_colors = {"From":dict(zip(set(df.From),
                                        setColorConf(len(set(df.From))))),
                    "To":dict(zip(set(df.To),
                                        setColorConf(len(set(df.From)),colors="tab10")))}

    # colnames mapping
    colmaps = {'From':'layer1','To':'layer2'}
    colmaps_layer = {'layer1':'layer1','layer2':'layer2'}

    # provided layerlabels 
    # auto mode
    sky_auto_global_colors = Sankey(df,colorMode="global")
    sky_auto_layer_colors = Sankey(df,colorMode="layer")

    # provided colors global & layer mode
    sky_provided_global_colors = Sankey(df,
                colorDict=global_colors,
                colorMode="global")
    sky_provided_layer_colors = Sankey(df,
                colorDict=layer_colors,
                colorMode="layer")

    # provided layerlabels 
    sky_provided_layer_labels = Sankey(df_layer,
                #colorDict=colors,
                colorMode="global",
                layerLabels=layer_labels_specified)

    # provided layerlabels 
    sky_provided_global_strip_color1 = Sankey(df,
                colorDict=global_colors,
                colorMode="global",
                stripColor="left")

    sky_provided_global_strip_color2 = Sankey(df,
                colorDict=global_colors,
                colorMode="global",
                stripColor="#aec7e8")

    sky_provided_layer_strip_color = Sankey(df_layer,
                colorDict=layer_colors,
                colorMode="layer",
                stripColor="left")

    sky_auto_global_colors.plot(savePath = "./pysankey2/test/fruits_auto_global_colors.pdf")
    sky_auto_layer_colors.plot(savePath = "./pysankey2/test/fruits_auto_layer_colors.pdf")
    sky_provided_global_colors.plot(savePath = "./pysankey2/test/fruits_provided_global_colors.pdf")
    sky_provided_layer_colors.plot(savePath = "./pysankey2/test/fruits_provided_layer_colors.pdf")
    sky_provided_layer_labels.plot(savePath = "./pysankey2/test/fruits_provided_layer_labels.pdf")
    sky_provided_global_strip_color1.plot(savePath = "./pysankey2/test/fruits_provided_global_strip_color1.pdf")
    sky_provided_global_strip_color2.plot(savePath = "./pysankey2/test/fruits_provided_global_strip_color2.pdf")
    sky_provided_layer_strip_color.plot(savePath = "./pysankey2/test/fruits_provided_layer_strip_color.pdf")
    
    testCase = defaultdict(dict)

    testCase['dfs']['df'] = df
    testCase['dfs']['df_layer'] = df_layer

    testCase['sankeys']['auto_global_colors'] = sky_auto_global_colors
    testCase['sankeys']['auto_layer_colors'] = sky_auto_layer_colors
    testCase['sankeys']['provided_global_colors'] = sky_provided_global_colors 
    testCase['sankeys']['provided_layer_colors'] = sky_provided_layer_colors
    testCase['sankeys']['provided_layer_labels'] = sky_provided_layer_labels

    testCase['sankeys']['provided_layer_labels'] = sky_provided_layer_labels
    testCase['sankeys']['provided_layer_labels'] = sky_provided_layer_labels
    testCase['sankeys']['provided_layer_labels'] = sky_provided_layer_labels
    
    testCase['labels']['global_labels'] = global_labels
    testCase['labels']['layer_labels'] = layer_labels
    testCase['labels']['layer_labels_specified'] = layer_labels_specified

    testCase['colors']['global_colors'] = global_colors
    testCase['colors']['layer_colors'] = layer_colors 

    testCase['colnames']['colname_layer_map'] = colmaps
    testCase['colnames']['layer_layer_map'] = colmaps_layer

    unittest.main()