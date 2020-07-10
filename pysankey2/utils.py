from matplotlib.colors import to_hex
import matplotlib.pyplot as plt
import math
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