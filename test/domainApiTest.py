# -*- coding: utf-8 -*-
'''
Created on 2013-1-10

@author: sinlangxmu@gmail.com
'''
import sys
import os
reload(sys)

File_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(File_PATH, '..'))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)
#sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    pass
import api.domainApi as domainApi, logging

logging.basicConfig(level=logging.DEBUG)

api = domainApi.DomainApi("{syscloudcdn}", "{491fbc7ac81e48544660}")
a = dir(api)
print a
'''
purgeLocation = "a79af3d0-7188-42bd-a5a9-472355b4dc4e"
createDomainRequstId = "42b50404-2db3-4802-966c-1b3c9ad42948"
domainId = "193382"
domainName = "2013071700211.4399.com"
detectUrl = "http://2013071700211.4399.com"

domain = domainApi.Domain()
domain.domainName = domainName
domain.domainId = domainId
domain.serviceType = "web"

originConfig = domainApi.OriginConfig()
originConfig.originIps = ["192.168.1.1", "192.168.1.2"]

advOriginConfigMult = domainApi.AdvOriginConfig()
advOriginConfigMult.isps = ["dx", "jyw"]
advOriginConfigMult.backupIps = ["192.168.1.4", "192.168.1.3"]
advOriginConfigMult.masterIps = ["192.168.1.6", "192.168.1.5"]
advOriginConfigMult.detectUrl = detectUrl
advOriginConfigMult.detectPeriod = 10

advOriginConfig = domainApi.AdvOriginConfig()
advOriginConfig.isps = ["wt"]
advOriginConfig.backupIps = ["192.168.0.4", "192.168.0.3"]
advOriginConfig.masterIps = ["192.168.0.6", "192.168.0.5"]
advOriginConfig.detectUrl = detectUrl
advOriginConfig.detectPeriod = 10

queryStringSetting = domainApi.QueryStringSetting()
queryStringSetting.ignoreQueryString = True
queryStringSetting.pathPattern = "/(a|b)/*.html"

domain.queryStringSettings = [queryStringSetting]

originConfig.advOriginConfigs = [advOriginConfigMult, advOriginConfig]
domain.originConfig = originConfig

cacheBehavior = domainApi.CacheBehavior()
cacheBehavior.priority = 1
cacheBehavior.cacheTtl = 10
cacheBehavior.pathPattern = "/(a|b)/*.html"
cacheBehavior.ignoreCacheControl = False
domain.cacheBehaviors = [cacheBehavior]

'''
'''
1. path-pattern必填
2. valid-referers、invalid-referers和forbidden-ips至少填写其中一个。
3. valid-referers和invalid-referers不得同时提交。
4. allowNullReferer只在validReferers不为空的时候有效
'''
'''
visitControlRule = domainApi.VisitControlRule()
visitControlRule.forbiddenIps = ["192.168.1.8", "192.168.1.7"]
visitControlRule.allowNullReferer = True
#visitControlRule.invalidReferers = ["www.a.com"]
visitControlRule.validReferers = ["www.b.com"]
visitControlRule.pathPattern = "/(a|b)/*.html"
domain.visitControlRules = [visitControlRule]


logging.debug("获取用户下的频道列表")
result = api.listAll()
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()
print 'domainSummarys:', result.getDomainSummarys()
   
logging.debug("获取指定频道信息")
result = api.find(domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'domain:', result.getDomain()
  
logging.debug("修改指定频道")
oriDomain = result.getDomain()
oriDomain.domainId = domainId
oriDomain.comment = "xxxxx_modify"
result = api.modify(oriDomain)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()
  
logging.debug("启用指定频道")
result = api.enable(domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
  
logging.debug("禁用指定频道")
result = api.disable(domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()

logging.debug("删除指定频道")
result = api.delete("196199")
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()

logging.debug("添加频道")
result = api.add(domain)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()
print result.cname
'''