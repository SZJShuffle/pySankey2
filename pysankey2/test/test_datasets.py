import os
import sys
sys.path.append(os.path.realpath('.'))
import pandas as pd
import pandas.testing as pdt
from datasets import load_countrys,load_fruits
if __name__ == "__main__":
    tmp = pd.DataFrame({'test':range(1000)})
    pdt.assert_index_equal(load_countrys().index,tmp.index)
    pdt.assert_index_equal(load_fruits().index,tmp.index)