from collections import defaultdict
from collections import OrderedDict
from copy import deepcopy
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

import numpy as np
import pandas as pd
import seaborn as sns
import math

class SankeyException(Exception):
    pass

class NullsInFrame(SankeyException):
    pass

class LabelMismatchError(SankeyException):
    pass

def setColorConf(ngroups,colors="tab20",alternative="grey")->list:
    """
    Parameters:
    ----------
    ngroups:int
        Number of tags need to be colored.
    
    colors:str
        Built-in colormaps accessible in the matplotlib.
        See more:https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    
    alternative:
        If <ngroups> is greater than the maximum number of colorPalette, the rest tags would be colored with <alternative>.
    
    Returns:
    --------
    colors_list:list
        a list of colors(hex).
    """ 
    if colors == "hcl":
        try:
            from colorspace import sequential_hcl
            color_repo = sequential_hcl(h=[15,375],l=65,c=70)
            colors_list =  color_repo.colors(ngroups + 1)
        except ImportError:
            print('hcl colorspace package has not being installed.')
            print('please try the following command:')
            print('pip install git+https://github.com/retostauffer/python-colorspace') 
    else:
        colors = list(plt.get_cmap(colors).colors)
        colors_list = [to_hex(color) for color in colors]
        colors_list = colors_list[:ngroups]

        # if len of colors_list less than ngroups, use grey to fullfill.
        if len(colors_list) < ngroups:
            for i in range(ngroups - len(colors_list)):
                colors_list.append(to_hex(alternative))
    return colors_list

def listRemoveNAN(list_):
    """
    Remove NaN in the list.
    list_:list-like object.
    """
    list_new = []
    for i,val in enumerate(list(list_)):
        # float/nan
        if isinstance(val,float): 
            if math.isnan(val):
                continue
            else:
                list_new.append(val)
        # int,str,etc.
        else:
            list_new.append(val)
    return list_new

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
                e.g {'layer1':[cs1,cs2,cs4],'layer2':[cs2,cs4,cs2]}
            If not passing, layerLabels would be extracted from the dataFrame.
        
        colorDict:dict
            There are 2 modes can be passing, see colorMode for details.

        colorMode:str, Can only take option in ["global","layer"].
            If choosing "global", a colorPalette dict that merged the same label in different layers would be taken.
            If choosing "layer", a colorPalette dict that treat the same label in different layers as independent label would be taken.
            For example, a layerLabels was: 
                layerLabels = ['layer1':['cs1','cs2','cs3'],'layer2':['cs1','cs4']].
            If choosing "global", colorPalette(aka colorDict) like:
                {'cs1':'some color','cs2':'some color','cs3':'some color','cs4':'some color'} would be taken. 
            If choosing "layer", colorPalette(aka colorDict) like:
                {'layer1':{'cs1':'some color','cs2':'some color','cs3':'some color'},
                 'layer2':{'cs1':'some color','cs4':'some color'}} would be taken. 
        
        
        """

        self.dataFrame = dataFrame
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
        opts=["global","layer"]
        if colorMode not in opts:
            raise ValueError("colorMode options don't support:{0}".format(colorMode))       
        if colorDict is None:
            self._colorDict = self._setColorDict(self._layerLabels,mode = colorMode)
        else:
            self._checkColorMatchLabels(colorDict,mode = colorMode)
            self._colorDict = colorDict
        
        # set box position
        self._boxPos = self._setboxPos(self.dataFrame,self._layerLabels)
        # set layer position
        self._layerPos = self._setLayerPos(self._layerLabels)
        # set strip width
        self._stripWidths = self._setStripWidth(self._layerLabels,self.dataFrame)


    def _getColnamesMapping(self,dataFrame):
        """
        Maintains a mapping relationship between old and new names.
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
            e.g {'layer1':[cs2,cs3,cs4],'layer2':[cs2,cs3,cs5]}
        """
        layerLabels = OrderedDict()
        for layer_label in dataFrame.columns:
            layer_labels = list(df.loc[:,layer_label].unique()) # may contain NaN
            layer_labels = listRemoveNAN(layer_labels)
            layerLabels[layer_label] = layer_labels
        return layerLabels

    def _checkLayerLabelsMatchDF(self,dataFrame,layerLabels,colnameMaps):
        """
        check whether the provided layer-specific labels match dataframe column names.
        
        Parameters:
        ----------
        dataFrame:pd.DataFrame.

        layerLabels:dict
            User provided lay-specific labels(keys corresponding to the old name of dataFrame columns).
                e.g:{'day1':[1,2,3],'day3':[3,4,5]}
        
        colnameMaps:dict
            Mapping between old and new dataFrame names.
                e.g {'day1':'layer1','day3':'layer2'}
        
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
        check if labels in the provided colorDict are the same as those in the dataFrame.
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
                new_layer = self.colnameMaps[old_layer]
                df_set = set(self.layerLabels[new_layer])
                if provided_set !=df_set:
                    msg_provided = "Provided Color Labels:" + ",".join([str(i) for i in provided_set]) + "\n"
                    msg_df = "dataFrame Labels:" + ",".join([str(i) for i in df_set]) + "\n"
                    raise LabelMismatchError('{0} do not match with {1}'.format(msg_provided, msg_df))            
    
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

    def _setboxPos(self,dataFrame,layerLabels,boxInterv=0.02):
        """
        Set y-axis coordinate position for each box.
        Parameters:
        ----------        
        boxInterv:int/float,
            Determine the vertical interval distance between boxes in the same layer.

        Returns:
        -------
        boxPos:dict, contain y-axis position of each box:
            boxPos[<layer>][<label>]['bottom']:bottom position of <label> in <layer>.
            boxPos[<layer>][<label>]['top']:top position of <label> in <layer>.
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
                    layerPos[label]['bottom'] = prevLabelTop + boxInterv * dataFrame.loc[:,layer].sum()
                    layerPos[label]['top'] = layerPos[label]['bottom'] + labelHeight
            boxPos[layer] = layerPos
        
        return boxPos    
    
    def _setLayerPos(self,layerLabels,boxWidth=1,stripLen=5):
        """
        Set x-axis coordinate position for each layer.
        Parameters:
        ----------   
        boxWidth:int/float,
            the width of layer.
        
        stripLen:int/float,
            the length of strip.
        
        Returns:
        --------
        layerPos:dict, contain x-axis position of each layer:
            layerPos[<layer>]['layerStart']:start position of x-axis for <layer>.
            layerPos[<layer>]['layerEnd']:end position of x-axis for <layer>.
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
        stripWidths:nested dict, stripWidths[layer][leftLabel][rightLabel] = width: 
           <leftLabel> in <layer> has a link with <rightLabel>(in the next layer) , where the size/width of link equals <width>.

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

 
            
    def _setStripPos(self,leftBottom,rightBottom,leftTop,rightTop,kernelSize=20):
        """
        Using onvolution to make the curve smooth:
        Create array of y values for each strip, half at left value,half at right.
        
        Param:
            kernelSize: control the smooth degree of strip.
        """
        ys_bottom = np.array(50 * [leftBottom] + 50 * [rightBottom])
        ys_bottom = np.convolve(ys_bottom, 0.05 * np.ones(kernelSize), mode='valid')
        ys_bottom = np.convolve(ys_bottom, 0.05 * np.ones(kernelSize), mode='valid')
        
        ys_top = np.array(50 * [leftTop] + 50 * [rightTop])
        ys_top = np.convolve(ys_top, 0.05 * np.ones(kernelSize), mode='valid')
        ys_top = np.convolve(ys_top, 0.05 * np.ones(kernelSize), mode='valid')    

        return ys_bottom,ys_top

    def _plotBox(self,ax,boxPos,layerPos,layerLabels,colorDict,fontSize,box_kws,text_kws):
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
                ax.text(
                    (layerStart + layerEnd)/2,
                    (labelBot + labelTop)/2,
                    label,
                    {'ha': 'right', 'va': 'center'},
                    fontsize=fontSize,
                    **text_kws)

    def _plotStrip(self,ax,dataFrame,layerLabels,boxPos,layerPos,stripWidths,strip_kws):
        """
        Render the strip according to box-position(boxPos), layer-position(layerPos) and strip width(stripWidths).
        """
        layers = list(layerLabels.keys())
        for i,layer in enumerate(layers):
            # the last layer does not need strip.stripWidths
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

                        ys_bottom,ys_top = self._setStripPos(leftBottom,rightBottom,leftTop,rightTop)
                        
                        # Update bottom edges at each label so next strip starts at the right place
                        boxPosProxy[leftLayer][leftLabel]['bottom'] = leftTop
                        boxPosProxy[rightLayer][rightLabel]['bottom'] = rightTop
                        
                        # X axis of layer.
                        x_start = layerPos[leftLayer]['layerEnd']
                        x_end = layerPos[rightLayer]['layerStart']
                        # TODO: params control
                        ax.fill_between(
                            np.linspace(x_start, x_end, len(ys_top)), ys_bottom, ys_top, alpha=0.3,
                            color='grey',
                            edgecolor='black',lw=2,
                            **strip_kws
                        )

    def plot(self,figSize=(10,10),fontSize=10,
                    box_kws=None,text_kws=None,strip_kws=None,savePath=None):
        """
        
        """
        plt.rc('text', usetex=False)
        plt.rc('font', family='Arial')
        fig = plt.figure(figsize = figSize)
        ax = fig.subplots()

        # plot box
        if box_kws is None:box_kws = {} 
        if text_kws is None:text_kws = {}
        self._plotBox(ax,self._boxPos,self._layerPos,self._layerLabels,self._colorDict,fontSize = fontSize,
                        box_kws = box_kws,text_kws = text_kws)

        # plot strip
        if strip_kws is None:strip_kws = {}
        self._plotStrip(ax,self.dataFrame,self._layerLabels,self._boxPos,self._layerPos,self._stripWidths,strip_kws)
        plt.gca().axis('off')

        if savePath != None:
            plt.savefig(savePath, bbox_inches='tight', dpi=600)
        
        return fig,ax

    @property
    def colnameMaps(self):
        return self._colnameMaps
    
    @property
    def labels(self):
        return self._allLabels

    @property
    def layerLabels(self):
        return self._layerLabels
    
    @property
    def boxPos(self):
        return self._boxPos

    @property
    def layerPos(self):
        return self._layerPos
    
    @property
    def stripWidth(self):
        return self._stripWidths
    

    @property
    def colorDict(self):
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


    print('boxPos:',sk.boxPos)
    print('boxPos[layer1]:',sk.boxPos['layer1'])
    print('boxPos[layer2]:',sk.boxPos['layer2'])
    print('boxPos[layer3]:',sk.boxPos['layer3'])
    
    print('layerPos:',sk.layerPos)

    print('stripWidth:',sk.stripWidth)
    print('stripWidth[layer1]:',sk.stripWidth['layer1'])
    print('stripWidth[layer2]:',sk.stripWidth['layer2'])


    
    
    ax = sk2.plot()
    plt.show()
    print("done")
