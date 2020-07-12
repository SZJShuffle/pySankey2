from collections import defaultdict
from collections import OrderedDict
from copy import deepcopy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

import numpy as np
import pandas as pd
import seaborn as sns
import math
from utils import setColorConf,listRemoveNAN

class SankeyException(Exception):
    pass

class NullsInFrame(SankeyException):
    pass

class LabelMismatchError(SankeyException):
    pass

class Sankey:
    """
    Sankey workflow:
        1. check whether the input OK. 
        2. create sankey-plot dataframe.
    """
    def __init__(self,dataFrame,layerLabels=None,colorDict=None,colorMode="global"):
        """
        Parameters:
        -----------
        dataFrame:pd.DataFrame
            Each row of the dataFrame represents a trans-entity,
        
        layerLabels:dict
            If passing, the provided layerLabels would determine the drawing order of each layer.
            If passing, dict keys must be named corresponding to column names of dataFrame.
                e.g {'layer1':['label1','label2','label4'],'layer2':['label2','label5','label6']}
            If not passing, layerLabels would be extracted from the dataFrame.
        
        colorDict:dict
            There are 2 modes can be passing, see colorMode for details.

        colorMode:str, Can only take option in ["global","layer"].
            If choosing "global", a colorPalette dict that merged the same label in different layers would be taken.
            If choosing "layer", a colorPalette dict that treat the same label in different layers as independent label would be taken.
            For example, a layerLabels was: 
                layerLabels = ['layer1':['label1','label2','label3'],'layer2':['label1','label4']].
            If choosing "global", colorPalette(aka colorDict) like:
                {'label1':'some color','label2':'some color','label3':'some color','label4':'some color'} would be taken. 
            If choosing "layer", colorPalette(aka colorDict) like:
                {'layer1':{'label1':'some color','label2':'some color','label3':'some color'},
                 'layer2':{'label1':'some color','label4':'some color'}} would be taken. 
        
        
        """

        self.dataFrame = deepcopy(dataFrame)
        # get mapping between old and new column names & rename columns.
        self._colnameMaps = self._getColnamesMapping(self.dataFrame)
        self.dataFrame.columns = ['layer%d'%(i+1) for i in range(dataFrame.shape[1])] 

        # labels
        self._allLabels = self._getAllLabels(self.dataFrame)
        if layerLabels is None:
            self._layerLabels = self._getLayerLabels(self.dataFrame)
        else:
            self._checkLayerLabelsMatchDF(self.dataFrame,layerLabels,self._colnameMaps)
            self._layerLabels = layerLabels
        
        # colors
        self.colorMode = colorMode
        _opts=["global","layer"]
        if colorMode not in _opts:
            raise ValueError("colorMode options must be one of:{0} ".format(",".join([i for i in _opts])))       
        if colorDict is None:
            self._colorDict = self._setColorDict(self._layerLabels,mode = colorMode)
        else:
            self._checkColorMatchLabels(colorDict,mode = colorMode)
            if colorMode == "layer":
                colorDict = self._renameColorDict(colorDict)
            self._colorDict = colorDict

    def _getColnamesMapping(self,dataFrame):
        """
        Returns:
        -------
        dict: mapping relationship between old and new names.
        """
        return dict(zip(dataFrame.columns,['layer%d'%(i+1) for i in range(dataFrame.shape[1])]))
    
    def _getAllLabels(self,dataFrame):
        """
        Returns:
        -------
        allLabels:list
            a global unique label list.
        """
        uniqLabels = list(set(dataFrame.unstack().values))
        allLabels = listRemoveNAN(uniqLabels)
        return allLabels

    def _getLayerLabels(self,dataFrame):
        """
        Returns:
        -------
        layerLabels:dict
            a layer-specific unique label dict(same labels in different layers would be treated as independent labels).
        """
        layerLabels = OrderedDict()
        for layer_label in dataFrame.columns:
            layer_labels = list(dataFrame.loc[:,layer_label].unique()) # may contain NaN
            layer_labels = listRemoveNAN(layer_labels)
            layerLabels[layer_label] = layer_labels
        return layerLabels

    def _checkLayerLabelsMatchDF(self,dataFrame,layerLabels,colnameMaps):
        """
        check whether the provided layer-specific labels match dataframe column names.
        """
        for oldname,newname in colnameMaps.items():
            df_list = listRemoveNAN(dataFrame.loc[:,newname].unique())
            provided_list = listRemoveNAN(layerLabels[oldname])
            df_set = set(df_list)
            provided_set = set(provided_list)

            if df_set != provided_set:
                msg_df = "dataFrame Labels:" + ",".join([str(i) for i in df_set]) + "\n"
                msg_provided = "Provided Labels:" + ",".join([str(i) for i in provided_set]) + "\n"
                raise LabelMismatchError('{0} do not match with {1}'.format(msg_provided, msg_df))
            

    def _checkColorMatchLabels(self,colorDict,mode):
        """
        check if labels in provided colorDict are identical to those in dataFrame.
        """
        if mode == "global":
            provided_set = set(colorDict.keys())
            df_set = set(self.labels)
            if provided_set !=df_set:
                msg_provided = "Provided Color Labels:" + ",".join([str(i) for i in provided_set]) + "\n"
                msg_df = "dataFrame Labels:" + ",".join([str(i) for i in df_set]) + "\n"
                raise LabelMismatchError('{0} do not match with {1}'.format(msg_provided, msg_df))     
        elif mode == "layer":
            # whether layer-specific labels match layerLabels
            for old_layer,layer_labels_map in colorDict.items():
                provided_set = set(layer_labels_map.keys())
                new_layer = self._colnameMaps[old_layer]
                df_set = set(self.layerLabels[new_layer])
                if provided_set !=df_set:
                    msg_provided = "Provided Color Labels:" + ",".join([str(i) for i in provided_set]) + "\n"
                    msg_df = "dataFrame Labels:" + ",".join([str(i) for i in df_set]) + "\n"
                    raise LabelMismatchError('In {0},{1} do not match with {1}'.format(new_layer,msg_provided, msg_df))            
    
    def _setColorDict(self,layerLabels,mode):
        """
        Set color for each label, return a color palette(dict). 
        """

        if mode =="global":
            ngroups = len(self.labels)
            colorPalette = setColorConf(ngroups=ngroups)
            colorDict = {}
            for i, label in enumerate(self.labels):
                colorDict[label] = colorPalette[i]
        elif mode =="layer":
            all_layer_labels = []
            for layer,layer_labels in self.layerLabels.items():
                all_layer_labels +=layer_labels
            
            ngroups = len(all_layer_labels)
            colorPalette = setColorConf(ngroups=ngroups)
            colorDict = defaultdict(dict)
            i=0
            for layer,layer_labels in self.layerLabels.items():
                for layer_label in layer_labels:
                    colorDict[layer][layer_label] = colorPalette[i]
                    i+=1
        return colorDict

    def _renameColorDict(self,colorDict):
        """rename keys of colordict from old column names to 'layer'"""

        for old_name,new_name in self.colnameMaps.items():
            colorDict[new_name]=colorDict[old_name]
            del colorDict[old_name]
        return colorDict

    def _setboxPos(self,dataFrame,layerLabels,boxInterv):
        """
        Set y-axis coordinate position for each box.
 
        Returns:
        -------
        boxPos:dict, contain y-axis position of each box.
        """
        boxPos = OrderedDict()
        for layer,labels in layerLabels.items():
            layerPos = defaultdict(dict)
            for i,label in enumerate(labels):
                labelHeight = ((dataFrame[dataFrame.loc[:,layer] == label])
                            .loc[:,layer]
                            .count())
                if i ==0:
                    layerPos[label]['bottom'] = 0
                    layerPos[label]['top'] = labelHeight
                else:
                    prevLabelTop = layerPos[labels[i-1]]['top']
                    layerPos[label]['bottom'] = prevLabelTop + boxInterv * dataFrame.loc[:,layer].count()
                    layerPos[label]['top'] = layerPos[label]['bottom'] + labelHeight
            boxPos[layer] = layerPos
        
        return boxPos    
    
    def _setLayerPos(self,layerLabels,boxWidth,stripLen):
        """
        Set x-axis coordinate position for each layer.
        
        Returns:
        --------
        layerPos:dict, contain x-axis position of each layer.
        """
        layerPos = defaultdict(dict) 
        layerStart = 0
        layerEnd = 0 + boxWidth

        for layer in layerLabels.keys():
            layerPos[layer]['layerStart'] = layerStart
            layerPos[layer]['layerEnd'] = layerEnd     

            layerStart = (layerEnd + stripLen)     
            layerEnd = (layerStart + boxWidth)
        return layerPos

    def _setStripWidth(self,layerLabels,dataFrame):
        """
        Set the width of strip(i.e. the size of a transfer pair).
        Returns:
        -------
        stripWidths:nested dict, stripWidths['layer'][leftLabel][rightLabel] = width: 
           <leftLabel> in 'layer' has a link with <rightLabel>(in the next layer) , where the size/width of link equals <width>.

        """
        layers = list(layerLabels.keys())
        # nested dict,see more:https://stackoverflow.com/questions/19189274/nested-defaultdict-of-defaultdict
        stripWidths = defaultdict(lambda: defaultdict(dict))

        for i,layer in enumerate(layers):
            # the last layer
            if i == len(layers) -1:
                break
            
            leftLayer = layers[i]
            rightLayer = layers[i+1]
            for leftLabel in layerLabels[leftLayer]:
                for rightLabel in layerLabels[rightLayer]:
                    width = len(dataFrame[(dataFrame.loc[:,leftLayer] == leftLabel) & (dataFrame.loc[:,rightLayer] == rightLabel)])
                    if width >0:
                        stripWidths[leftLayer][leftLabel][rightLabel] = width

        return stripWidths
            
    def _setStripPos(self,leftBottom,rightBottom,leftTop,rightTop,kernelSize,stripShrink):
        """
        Smooth the strip by convolution, and create array of y values for each strip.


        """
        ys_bottom = np.array(50 * [leftBottom] + 50 * [rightBottom])
        ys_bottom = np.convolve(ys_bottom + stripShrink, (1/kernelSize) * np.ones(kernelSize), mode='valid')
        ys_bottom = np.convolve(ys_bottom + stripShrink, (1/kernelSize) * np.ones(kernelSize), mode='valid')
        
        ys_top = np.array(50 * [leftTop] + 50 * [rightTop])
        ys_top = np.convolve(ys_top - stripShrink, (1/kernelSize) * np.ones(kernelSize), mode='valid')
        ys_top = np.convolve(ys_top - stripShrink,(1/kernelSize) * np.ones(kernelSize), mode='valid')    

        return ys_bottom,ys_top

    def _plotBox(self,ax,boxPos,layerPos,layerLabels,colorDict,fontSize,fontPos,box_kws,text_kws):
        """
        Render the box according to box-position(boxPos) and layer-position(layerPos).

        """    

        for layer,labels in layerLabels.items():
            for label in labels:
                labelBot = boxPos[layer][label]['bottom']
                labelTop = boxPos[layer][label]['top']
                layerStart = layerPos[layer]['layerStart']
                layerEnd = layerPos[layer]['layerEnd']

                if self.colorMode == "global":color = colorDict[label]
                elif self.colorMode == "layer":color = colorDict[layer][label]
                # fill the box
                ax.fill_between(
                    x = [layerStart,layerEnd],
                    y1 = labelBot,
                    y2 = labelTop,
                    facecolor = color,
                    alpha = 0.9,
                    **box_kws
                )
                # text annotation of each box
                distToBoxLeft = fontPos[0]
                distToBoxBottom = fontPos[1]
                ax.text(
                    (layerStart + distToBoxLeft),
                    (labelBot + (labelTop - labelBot)* distToBoxBottom),
                    label,
                    {'ha': 'right', 'va': 'center'},
                    fontsize=fontSize,
                    **text_kws)

    def _plotStrip(self,ax,dataFrame,layerLabels,boxPos,layerPos,stripWidths,kernelSize,stripShrink,strip_kws):
        """
        Render the strip according to box-position(boxPos), layer-position(layerPos) and strip width(stripWidths).
        """
        layers = list(layerLabels.keys())
        for i,layer in enumerate(layers):
            # the last layer does not need strip.
            if i == len(layers) -1:
                break
            leftLayer = layers[i]
            rightLayer = layers[i+1]
            # deepcopy:https://zhuanlan.zhihu.com/p/61904991
            # Update the box position when iterated to the next layer,
            # to make sure operation in the last layer would not affect the next layer.
            boxPosProxy = deepcopy(boxPos)
            for leftLabel in layerLabels[leftLayer]:
                for rightLabel in layerLabels[rightLayer]:
                    width = len(dataFrame[(dataFrame.loc[:,leftLayer] == leftLabel) & (dataFrame.loc[:,rightLayer] == rightLabel)])
                    if width > 0:
                        leftBottom = boxPosProxy[leftLayer][leftLabel]['bottom']
                        leftTop = leftBottom + stripWidths[layer][leftLabel][rightLabel] 

                        rightBottom = boxPosProxy[rightLayer][rightLabel]['bottom']
                        rightTop = rightBottom + stripWidths[layer][leftLabel][rightLabel] 

                        ys_bottom,ys_top = self._setStripPos(leftBottom,rightBottom,leftTop,rightTop,kernelSize = kernelSize,stripShrink = stripShrink)
                        
                        # Update bottom edges at each label so next strip starts at the right place
                        boxPosProxy[leftLayer][leftLabel]['bottom'] = leftTop
                        boxPosProxy[rightLayer][rightLabel]['bottom'] = rightTop
                        
                        # X axis of layer.
                        x_start = layerPos[leftLayer]['layerEnd']
                        x_end = layerPos[rightLayer]['layerStart']
                        # TODO: params control
                        ax.fill_between(
                            np.linspace(x_start, x_end, len(ys_top)), ys_bottom, ys_top, alpha=0.4,
                            color='grey',
                            #edgecolor='black',
                            **strip_kws
                        )

    def plot(self,figSize=(10,10),
                    fontSize=10,fontPos=(-0.15,0.5),
                    boxInterv=0.02,
                    boxWidth=2,stripLen=10,
                    kernelSize=25,stripShrink=0,
                    box_kws=None,text_kws=None,strip_kws=None,
                    savePath=None):
        """
        Draw a Sankey diagram.

        Parameters:
        ----------   
        figSize:(float, float), default=(10,10).
            Width, height of figure in inches.

        fontSize:float, default=10.
            Size of font.

        fontPos:(float, float), default=(-0.15,0.5).
            Distance(calculated as a percentage) to the left/bottom of box.
            For example, -0.15 means that the real distance to the left of the box is -0.15 * boxWidth, and 
            the real distance to the bottom of the box is 0.5 * boxHeight.

        boxInterv:float, default=0.02.
            Vertical interval distance between boxes in the same layer.

        boxWidth:float, default=2.
            Width of layer.
        
        stripLen:float, default=10.
            Length of strip.
        
        kernelSize:int, default=25.
            Convolution kernel size, used to control the smoothness of strip, 
        
        stripShrink:float,default=0.
            Shrink extend of strip, used to compress the strip width.
        
        box_kws:
            Additional keyword arguments, which would be passed to plt.fill_between().

        text_kws:
            Additional keyword arguments, which would be passed to plt.text().
        
        strip_kws:
            Additional keyword arguments, which would be passed to plt.fill_between().

        savePath:
            name to save the figure.
        
        Returns:
        --------
        fig:matplotlib Figure.
            The Figure object containing the plot.
        
        ax:matplotlib Axes
            The Axes object containing the plot.
        """
        # set box position
        self._boxPos = self._setboxPos(self.dataFrame,
                                        self._layerLabels,
                                        boxInterv = boxInterv)
        # set layer position
        self._layerPos = self._setLayerPos(self._layerLabels,
                                            boxWidth = boxWidth , 
                                            stripLen = stripLen)
        # set strip width
        self._stripWidths = self._setStripWidth(self._layerLabels,
                                                self.dataFrame)

        plt.rc('text', usetex=False)
        plt.rc('font', family='Arial')
        fig = plt.figure(figsize = figSize)
        ax = fig.subplots()

        # plot box
        if box_kws is None:box_kws = {} 
        if text_kws is None:text_kws = {}
        if not isinstance(box_kws,dict):
            raise TypeError("box_kws must be dict.")
        if not isinstance(text_kws,dict):
            raise TypeError("text_kws must be dict.")
        
        distToBoxLeft = boxWidth * fontPos[0]
        distToBoxBottom = fontPos[1]
        self._plotBox(ax,
                      self._boxPos,
                      self._layerPos,
                      self._layerLabels,
                      self._colorDict,
                      fontSize = fontSize,
                      fontPos = (distToBoxLeft,distToBoxBottom),
                      box_kws = box_kws,
                      text_kws = text_kws)

        # plot strip
        if strip_kws is None:strip_kws = {}
        if not isinstance(strip_kws,dict):
            raise TypeError("strip_kws must be dict.")
        self._plotStrip(ax,s
                        self.dataFrame,
                        self._layerLabels,
                        self._boxPos,
                        self._layerPos,
                        self._stripWidths,
                        kernelSize,
                        stripShrink,
                        strip_kws)
        plt.gca().axis('off')

        if savePath != None:
            plt.savefig(savePath, bbox_inches='tight', dpi=800)
        
        return fig,ax

    @property
    def colnameMaps(self):
        """
        dict, mapping between old and new dataFrame names(e.g. {'old_colname1':'layer1','old_colname2':'layer2'})        
        """

        return self._colnameMaps
    
    @property
    def labels(self):
        """
        list, set of labels in the data.
        """
        return self._allLabels

    @property
    def layerLabels(self):
        """
        dict, set of layer specific labels in the data.(e.g. {'layer1':['label1','label2','label4'],'layer2':['label1','label3','label5']})
        """
        return self._layerLabels
    
    @property
    def boxPos(self):
        """
        dict, contain y-axis position of each box:
            boxPos['layer']['label']['bottom']:bottom position of 'label' in 'layer'.
            boxPos['layer']['label']['top']:top position of 'label' in 'layer'.        
        """
        return self._boxPos

    @property
    def layerPos(self):
        """
        dict, contain x-axis position of each layer:
            layerPos['layer']['layerStart']:start position of x-axis for 'layer'.
            layerPos['layer']['layerEnd']:end position of x-axis for 'layer'.       
        """
        return self._layerPos
    
    @property
    def stripWidth(self):
        """
        dict, stripWidths['layer'][leftLabel][rightLabel] = width: 
           <leftLabel> in 'layer' has a link with <rightLabel>(in the next layer) , where the size/width of link equals <width>.        
        """
        return self._stripWidths
    

    @property
    def colorDict(self):
        """
        dict, see doc strings of colorMode in __init__ for details.
        """
        return self._colorDict        


if __name__ == "__main__":
    df = pd.DataFrame({'layer1':[1,1,1,1,1,2,2,2,2,2,2,4,4],'layer2':[3,3,3,3,3,3,3,3,3,3,3,6,6],
                  'layer3':[np.nan,np.nan,np.nan,np.nan,np.nan,1,1,1,1,1,1,5,6]})
    sk2_layerlabs = {'layer1':[1,2,4],'layer2':[3,6],'layer3':[1,5,6]}
    sk = Sankey(df)
    sk2 = Sankey(df,layerLabels=sk2_layerlabs)
    

    print("Mapping:",sk.colnameMaps)
    print("labels:",sk.labels)
    print('layerLabels:',sk.layerLabels)
    print('layerLabels:',sk2.layerLabels)

    ### colors 
    print("ColorMap(global)",sk.colorDict)
    sk = Sankey(df,colorMode="layer")
    print("ColorMap(layer)",sk.colorDict)
    # user specific
    sk2_glbcolors = {1:'grey',2:'grey',3:'grey',4:'grey',5:'grey',6:'grey'}
    sk2 = Sankey(df,layerLabels=sk2_layerlabs,colorDict= sk2_glbcolors)
    print("ColorMap(User global)",sk2.colorDict)
    sk2_lycolors = {'layer1':{1:'#1f77b4',2:'grey',4:'#aec7e8'},'layer2':{3:'#8c564b',6:'grey'},'layer3':{1:'#ff9896',5:'grey',6:'grey'}}
    sk2 = Sankey(df,layerLabels=sk2_layerlabs,colorDict= sk2_lycolors,colorMode = "layer")
    print("ColorMap(User layer)",sk2.colorDict)

    fig,ax = sk.plot(#boxInterv=0,
                    box_kws={'edgecolor':'black'})
    print('boxPos:',sk.boxPos)
    print('boxPos[layer1]:',sk.boxPos['layer1'])
    print('boxPos[layer2]:',sk.boxPos['layer2'])
    print('boxPos[layer3]:',sk.boxPos['layer3'])
    
    print('layerPos:',sk.layerPos)

    print('stripWidth:',sk.stripWidth)
    print('stripWidth[layer1]:',sk.stripWidth['layer1'])
    print('stripWidth[layer2]:',sk.stripWidth['layer2'])


    
    
    
    plt.show()
    print("done")
