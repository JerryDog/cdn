#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom.minidom import Document
import os, sys, re
import getopt
import json
from django.conf import settings

try:
   xml_name = sys.argv[1]
   AliasesV = sys.argv[2]
   OriginSourceExV = sys.argv[3]
   TestUrlsV = sys.argv[4]
   NoUse = sys.argv[5]
except:
   print sys.argv[0]+"alex1.ztgame.com.cnadfasdf alex1.ztgame.com.cn 222.73.33.4 http://alex1.ztgame.com.cn/test.xml False -J {json}"
   sys.exit(1)

"""
json

{
    "CacheBehavior": [
        {
            "PathPattern": ".jpg",
            "NeverCache": "False",
            "CacheControl": "Ignore",
            "ForwardedValues": "False",
            "CacheTime": "3600"
        },
        {
            "PathPattern": ".txt",
            "NeverCache": "False",
            "CacheControl": "Ignore",
            "ForwardedValues": "False",
            "CacheTime": "5200"
        }
    ],
    "AclBehavior": [
        {
            "PathPattern": ".jpg",
            "WhiteList": "www.163.com",
            "BlackList": "www.baidu.com",
            "DenyIpList": "222.73.33.5"
        },
        {
            "PathPattern": ".txt",
            "WhiteList": "www.162.com",
            "BlackList": "www.baidu1.com",
            "DenyIpList": "222.73.33.5"
        }
    ]
}

{"CacheBehavior":[{"PathPattern":".jpg","NeverCache":"False","CacheControl":"Ignore","ForwardedValues":"False","CacheTime":"31536000"},{"PathPattern":".txt","NeverCache":"False","CacheControl":"Ignore","ForwardedValues":"False","CacheTime":"5200"}],"AclBehavior":[{"PathPattern":".jpg","WhiteList":"www.163.com","BlackList":"www.baidu.com","DenyIpList":"222.73.33.5"},{"PathPattern":".txt","WhiteList":"www.162.com","BlackList":"www.baidu1.com","DenyIpList":"222.73.33.5"}]}{"CacheBehavior":[{"PathPattern":".jpg","NeverCache":"False","CacheControl":"Ignore","ForwardedValues":"False","CacheTime":"3600"},{"PathPattern":".txt","NeverCache":"False","CacheControl":"Ignore","ForwardedValues":"False","CacheTime":"5200"}],"AclBehavior":[{"PathPattern":".jpg","WhiteList":"www.163.com","BlackList":"www.baidu.com","DenyIpList":"222.73.33.5"},{"PathPattern":".txt","WhiteList":"www.162.com","BlackList":"www.baidu1.com","DenyIpList":"222.73.33.5"}]}

"""

options,args = getopt.getopt(sys.argv[6:],"J:",["json"])
#print options,args
#aaaaab = options,args
#print type(aaaaab)
for name,value in options:
   if name in ("-J","--json"):
      jsonvalue=value

jsontxt = json.loads(jsonvalue)


#for i in jsontxt["DefaultBehavior"]:
#   DefaultBehaviorl = i


CacheBehaviorl = jsontxt["CacheBehavior"]


#for i in jsontxt["DefaultAclBehavior"]:
#   DefaultAclBehaviorl = i









#sys.exit(0)

#CacheBehaviorlist = [{'PathPattern':'.jpg', 'NeverCache':'False', 'CacheControl':'Ignore', 'ForwardedValues':'False'  ,'CacheTime':3600},{'PathPattern':'.txt', 'NeverCache':'False', 'CacheControl':'Ignore', 'ForwardedValues':'False'  ,'CacheTime':5200}]
AclBehaviorlist = [{'PathPattern':'a', 'WhiteList':'b', 'BlackList':'c', 'DenyIpList':'d'},{'PathPattern':'A', 'WhiteList':'B', 'BlackList':'C', 'DenyIpList':'D'}]


doc = Document()
Distribution = doc.createElement("Distribution")
doc.appendChild(Distribution)


Customer = doc.createElement("Customer")
Id = doc.createElement("Id")
Id.appendChild(doc.createTextNode('436bd48b'))
Customer.appendChild(Id)



Platform = doc.createElement("Platform")
Name = doc.createElement("Name")
Name.appendChild(doc.createTextNode('xnop015'))
Type = doc.createElement("Type")
Type.appendChild(doc.createTextNode('WEB'))
Platform.appendChild(Name)
Platform.appendChild(Type)

DistributionConfig = doc.createElement("DistributionConfig")



Comment = doc.createElement("Comment")
Comment.appendChild(doc.createTextNode('create'))



NotUse = doc.createElement("NotUse")
NotUse.appendChild(doc.createTextNode(NoUse))

Domains = doc.createElement("Domains")

Aliases = doc.createElement("Aliases")
Aliases.appendChild(doc.createTextNode(AliasesV))

TestUrls = doc.createElement("TestUrls")
TestUrls.appendChild(doc.createTextNode(TestUrlsV))

Domain = doc.createElement("Domain")
Domains.appendChild(Domain)


Domain.appendChild(Aliases)
Domain.appendChild(TestUrls)

Origin = doc.createElement("Origin")
OriginSource = doc.createElement("OriginSource")
OriginSource.appendChild(doc.createTextNode(OriginSourceExV.split(",")[0]))



AdvanceConfig = doc.createElement("AdvanceConfig")

BackToSourceType = doc.createElement("BackToSourceType")
BackToSourceType.appendChild(doc.createTextNode("RoundRobin"))
AdvanceConfig.appendChild(BackToSourceType)

Item = doc.createElement("Item")
AdvanceConfig.appendChild(Item)



CarrierCode = doc.createElement("CarrierCode")
CarrierCode.appendChild(doc.createTextNode('ANY'))

OriginSourceEx = doc.createElement("OriginSourceEx")
OriginSourceEx.appendChild(doc.createTextNode(OriginSourceExV))

Item.appendChild(CarrierCode)
Item.appendChild(OriginSourceEx)


Origin.appendChild(OriginSource)
Origin.appendChild(AdvanceConfig)

Domain.appendChild(Origin)


CacheBehaviorTop = doc.createElement("CacheBehaviorTop")
AclBehaviorsTop = doc.createElement("AclBehaviorsTop")
'''
DefaultBehavior = doc.createElement("DefaultBehavior")


NeverCache = doc.createElement("NeverCache")
NeverCache.appendChild(doc.createTextNode('False'))
CacheControl = doc.createElement("CacheControl")
CacheControl.appendChild(doc.createTextNode(DefaultBehaviorl["CacheControl"]))#
ForwardedValues = doc.createElement("ForwardedValues")


QueryString = doc.createElement("QueryString")
QueryString.appendChild(doc.createTextNode(DefaultBehaviorl["ForwardedValues"]))#
orwardedValues.appendChild(QueryString)

CacheTime = doc.createElement("CacheTime")
CacheTime.appendChild(doc.createTextNode(DefaultBehaviorl["CacheTime"]))#


DefaultBehavior.appendChild(NeverCache)
DefaultBehavior.appendChild(CacheControl)
DefaultBehavior.appendChild(ForwardedValues)
DefaultBehavior.appendChild(CacheTime)

CacheBehaviorTop.appendChild(DefaultBehavior)


'''
DefaultAclBehavior = doc.createElement("DefaultAclBehavior")
WhiteList = doc.createElement("WhiteList")
#WhiteList.appendChild(doc.createTextNode(DefaultAclBehaviorl["WhiteList"]))
DefaultAclBehavior.appendChild(WhiteList)
BlackList = doc.createElement("BlackList")
#BlackList.appendChild(doc.createTextNode(DefaultAclBehaviorl["BlackList"]))
DefaultAclBehavior.appendChild(BlackList)
DenyIpList = doc.createElement("DenyIpList")
#DenyIpList.appendChild(doc.createTextNode(DefaultAclBehaviorl["DenyIpList"]))
DefaultAclBehavior.appendChild(DenyIpList)



DefaultAclBehavior.appendChild(WhiteList)
DefaultAclBehavior.appendChild(BlackList)
DefaultAclBehavior.appendChild(DenyIpList)
AclBehaviorsTop.appendChild(DefaultAclBehavior)

Logging = doc.createElement("Logging")

Analytics = doc.createElement("Analytics")
Analytics.appendChild(doc.createTextNode('True'))
Format = doc.createElement("Format")
Format.appendChild(doc.createTextNode('Apache'))
SplitTime = doc.createElement("SplitTime")
SplitTime.appendChild(doc.createTextNode('1h'))

Logging.appendChild(Analytics)
Logging.appendChild(Format)
Logging.appendChild(SplitTime)


CacheBehaviors = doc.createElement("CacheBehaviors")
CacheBehaviorTop.appendChild(CacheBehaviors)


Distribution.appendChild(Customer)
Distribution.appendChild(Platform)
Distribution.appendChild(DistributionConfig)
DistributionConfig.appendChild(Comment)
DistributionConfig.appendChild(NotUse)
DistributionConfig.appendChild(Domains)
DistributionConfig.appendChild(CacheBehaviorTop)
DistributionConfig.appendChild(AclBehaviorsTop)
DistributionConfig.appendChild(Logging)


def fAclBehavior(lAclBehavior):
   AclBehaviors = doc.createElement("AclBehaviors")
   AclBehaviorsTop.appendChild(AclBehaviors)
   for i in ['PathPattern', 'WhiteList', 'BlackList', 'DenyIpList']:
      acldoc = AclBehaviors.appendChild(doc.createElement(i))
      acldoc.appendChild(doc.createTextNode(str(lAclBehavior[i])))


def fCacheBehaviors(lCacheBehaviors):
   CacheBehavior=doc.createElement("CacheBehavior")
   CacheBehaviors.appendChild(CacheBehavior)
   for i in ['PathPattern', 'NeverCache', 'CacheControl', 'ForwardedValues', 'CacheTime']:
      if i != "ForwardedValues":
         a = doc.createElement(i)
         a.appendChild(doc.createTextNode('%s' % lCacheBehaviors[i]))
         c = str(lCacheBehaviors[i])
         abc = CacheBehavior.appendChild(doc.createElement(i))
         abc.appendChild(doc.createTextNode(c))
      elif i == "ForwardedValues":
         a = doc.createElement(i)
         a.appendChild(doc.createTextNode('%s' % lCacheBehaviors[i]))
         c = str(lCacheBehaviors[i])
         abc = CacheBehavior.appendChild(doc.createElement(i))
         bbb = abc.appendChild(doc.createElement("QueryString"))
         bbb.appendChild(doc.createTextNode(c))


for i in CacheBehaviorl:
   fCacheBehaviors(i)

try:
    AclBehaviorl =  jsontxt["AclBehavior"]
    for i in AclBehaviorl:
        fAclBehavior(i)
except:
    pass
i = doc.toprettyxml().split('\n')
file_path = '/usr/local/cdn/cdn_manage/Xml/%s.xml' % xml_name
if os.path.exists(file_path):
    os.remove(file_path)
with open(file_path,'a+') as f:
    for j in range(len(i)):
        if j+2 >= len(i):
            f.write(i[j]+'\n')
            break
        if not re.match(r'\s*<', i[j+1]):
            i[j] = i[j] + i[j+1].strip() + i[j+2].strip()
        else:
            if not re.match(r'\s*<', i[j]):
                continue
            if not re.match(r'\s*<', i[j-1]):
                continue
        f.write(i[j]+'\n')

#a=os.popen('echo "%s" |tidy -utf8 -xml -w 255 -i -c -q -asxml' % doc.toprettyxml())
#os.system('echo "%s" |tidy -utf8 -xml -w 255 -i -c -q -asxml' % doc.toprettyxml())
#print type(a)
#print a.read()
#os.system(print doc.toprettyxml()"|tidy -utf8 -xml -w 255 -i -c -q -asxml")
