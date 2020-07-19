# pySankey2
Static sankey diagrams with matplotlib. 



## Example1:Two-layer 

Using a 2-layer demo `fruits.txt`:

| From      | To        |
| --------- | --------- |
| blueberry | blueberry |
| apple     | blueberry |
| ...       | ...       |
| orange    | orange    |

and with a simple code:

```
import matplotlib.pyplot as plt
import pandas as pd
from pysankey2.datasets import load_fruits
from pysankey2 import Sankey

df = load_fruits()
sky = Sankey(df,colorMode="global")
fig,ax = sky.plot()
```

we get:

![fruits](./example/fruit_1.png)

Setting the strip color to be the same with left box is also allowed:

```
import matplotlib.pyplot as plt
import pandas as pd
from pysankey2.datasets import load_fruits
from pysankey2.utils import setColorConf
from pysankey2 import Sankey

df = load_fruits()
fruits = list(set(df.layer1).union(set(df.layer2)))

# Specified the colors.
# Here, we use 'Pastel1' colormaps(a shy bust fresh colormap :)).
# See matplotlib cmap for more colormaps:
# https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

colors = setColorConf(len(fruits),colors='Pastel1')
cls_map = dict(zip(fruits,colors))

sky = Sankey(df,colorDict=cls_map,colorMode="global",stripColor='left')

# set a bigger font size 
fig,ax = sky.plot(text_kws={'size':20})
```

we get:

![fruits2](./example/fruit_2.png)





## Example2:Multi-layer

Using a 3-layer demo `countrys.txt`:

| layer1  | layer2 | layer3 |
| ------- | ------ | ------ |
| China   | Canada | USA    |
| England | China  | Japan  |
| ...     | ...    | ...    |
| Senegal | Spain  | USA    |

and with a simple code:

```
import matplotlib.pyplot as plt
import pandas as pd
from pysankey2 import Sankey

df  = pd.read_csv("./pysankey2/test/data/countrys.txt",sep="\t",header=None,names=['First', 'Mid','Last'])
sky = Sankey(df,colorMode="global")
fig,ax = sky.plot()
plt.show()
```

we get:

![countrys](./example/country_1.png)



## Contact

Any  questions, bugs and suggestions are welcome, please feel free to contact:szjshuffle@foxmail.com