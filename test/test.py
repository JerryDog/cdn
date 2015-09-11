'''
Created on 2013-10-14

@author: Administrator
'''
from util.rfc3339 import rfc3339 

from datetime import datetime

import util.ApiUtil as util

date_object = datetime.strptime("2012-01-11 10:10:09", "%Y-%m-%d %H:%M:%S");
time = rfc3339(date_object);
print time;
 

EMUN_A = 1
EMUN_B = 2

class A(object):
    def __init__(self, a = 1):
        self.a = a
        print 'init A a is ', a
        pass
    
class B(A):
    def __init__(self, a, b):
        super(B, self).__init__(a)
        self.b = b
        print 'init B b is', b
        pass
    
    def getA(self):
        return self.a
    
    def getB(self):
        return self.b
    
    def getEnum(self):
        print 'get emun a is :', EMUN_A
        print 'get emun b is: ', EMUN_B
    
x = B(10, 20)
# print "a from B is ", x.getA()
# print "b from B is ", x.getB()

#x.getEnum()


#print "host is ", HOST

def hello():
    "xxxx"
    
chack = hello()
print chack
