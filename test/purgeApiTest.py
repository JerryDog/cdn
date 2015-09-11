# -*- coding: utf-8 -*-
'''
Created on 2013-10-18

@author: zzh
'''
import sys
reload(sys)
#sys.setdefaultencoding('utf8')

import logging
import api.purgeApi as purgeApi

logging.basicConfig(level = logging.DEBUG)

api = purgeApi.PurgeApi("{username}", "{API_KEY}")
dateFrom = "2013-09-01 01:00:00"
dateTo = "2013-09-18 12:00:00"

domainId = "193382"

logging.debug("批量清除某域名下缓存")
dirs = ['http://20130925001.4399.com/a/']
urls = ['http://20130925001.4399.com/a.jpg']
purgeBatch = purgeApi.PurgeBatch(urls, dirs)
result = api.purge(purgeBatch)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()


logging.debug("根据purgeId查缓存")
purgeId = result.getXCncRequestId()
#purgeId = "b918184b-74f9-4587-b0f3-92a27dc82836"
result = api.purgeQueryByPurgeId(purgeId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'purgeResult is ', result.getPurgeList()[0]
