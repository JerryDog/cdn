'''
Created on 2014-4-25

@author: zzh
'''
import unittest

class CommonTest(unittest.TestCase):
    Host = "xxxx"
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testVar(self):
        print "-----start---"
        strs = self.returnWrong()
        print strs
        
    def returnWrong(self):
        if 1 > 10:
            return "GodWrong"