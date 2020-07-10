import unittest
import os
import sys
sys.path.append(os.path.realpath('.'))
import utils
import numpy as np
class TestUtils(unittest.TestCase):
    def test_color_conf(self):
        # tab20 as test case
        colors_palette="tab20"
        groups = [10,20,30]
        for group in groups:
            colors = utils.setColorConf(group,colors = colors_palette)
            self.assertEqual(len(colors),group)
            if len(colors) >20:
                #print(colors[20:])
                self.assertEqual(colors[20:],["#808080" for i in np.arange(20,group)])
        
        # nonexistent colors as test case
        colors_palette="tab30"
        with self.assertRaises(ValueError):
            utils.setColorConf(group,colors = colors_palette)
        
    def test_remove_list(self):
        lst = ['a','b',np.nan,'c',1,2,3,np.nan,3.5,4.5]
        ret = utils.listRemoveNAN(lst)
        self.assertEqual(ret,['a','b','c',1,2,3,3.5,4.5])

if __name__ == "__main__":
    unittest.main()

