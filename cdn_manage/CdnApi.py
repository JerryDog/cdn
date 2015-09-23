#coding:utf8
__author__ = 'liujiahua'
import logging
import httplib
import hashlib
from django.conf import settings
import os, sys

LOG = logging.getLogger(__name__)

REQ_DICT = {
    "bandwidthmap":{
        "rq_url":"/DnionCloud/Bandwidth/bandwidthMap?domain=%s&beginDate=%s&endDate=%s",
        #domain&beginDate&endDate
        "type":"POST",
        "postfile":"n",
    },
    "bandwidthvalue":{
        "rq_url":"/DnionCloud/Bandwidth/bandwidthValue?domain=%s&date=%s",#domain&date
        "type":"POST",
        "postfile":"n",
    },
    "config":{
        "rq_url":"/DnionCloud/distribution/%s/config_update",#distributionID
        "type":"POST",
        "postfile":"y",
    },
    "create":{
        "rq_url":"/DnionCloud/distribution/create",
        "type":"POST",
        "postfile":"y",
    },
    "del":{
        "rq_url":"/DnionCloud/distribution/%s/delete", #distributionID
        "type":"POST",
        "postfile":"n",
    },
    "get":{
        "rq_url":"/DnionCloud/distribution/%s/get", #distributionID
        "type":"GET",
        "postfile":"n",
    },
    "list":{
        "rq_url":"/DnionCloud/distribution/list",
        "type":"GET",
        "postfile":"n",
    },
    "prefetch_progress":{
        "rq_url":"/DnionCloud/cdnPrefetch/progress?RequestId=%s", #RequestId
        "type":"POST",
        "postfile":"n",
    },
    "prefetch":{
        "rq_url":"/DnionCloud/cdnPrefetch/cdnBodyPrefetch",
        "type":"POST",
        "postfile":"n",
    },
    "progress":{
         "rq_url":"/DnionCloud/cdnPush/progress?RequestId=%s", #RequestId
         "type":"POST",
         "postfile":"n",
    },
    "push":{
        "rq_url":"/DnionCloud/cdnPush/cdnUrlPush?type=%s&url=%s&decode=y", #tftype & url
        "type":"POST",
        "postfile":"n",
    },
    "query":{
        "rq_url":"/DnionCloud/PutOnRecord/query?domain=%s", #domain
        "type":"POST",
        "postfile":"n",
    },
    "bandwidthRatio":{
        "rq_url":"/DnionCloud/Bandwidth/bandwidthRatio?domain=%s&beginDate=%s&endDate=%s",
        #domain&beginDate&endDate
        "type":"POST",
        "postfile":"n",
    },
    "staticRatio":{
        "rq_url":"/DnionCloud/Bandwidth/staticRatio?domain=%s&date=%s", #domain & date
        "type":"POST",
        "postfile":"n",
    },
    "flowValue":{
        "rq_url":"/DnionCloud/Bandwidth/flowValue?domain=%s&beginDate=%s&endDate=%s&province=%s&isp=%s",
        #domain & beginDate & endDate & url_escape(province) & url_escape(isp)
        "type":"POST",
        "postfile":"n",
    },
    "logDownLoad":{
        "rq_url":"/DnionCloud/DCC/logDownLoad?domain=%s&date=%s", #domain & date & hour
        "type":"POST",
        "postfile":"n",
    },
    "logDownLoadList":{
        "rq_url":"/DnionCloud/DCC/logDownLoadList?domain=%s&beginDate=%s&endDate=%s",
        #domain & beginDate & endDate
        "type":"POST",
        "postfile":"n",
    },
    "analyticsServer":{
        "rq_url":"/DnionCloud/Analytics/analyticsServer?domain=%s&beginDate=%s&endDate=%s&type=%s",
        #domain & beginDate & endDate & Type,
        "type":"POST",
        "postfile":"n",
    },
}

class DiLianManager(object):
    def __init__(self, domain_name=None, domain_ip=None, test_url=None, xml_name=None):
        self.domain_name = domain_name
        self.domain_ip = domain_ip
        self.test_url = test_url
        self.xml_path = settings.XML_PATH % xml_name
        self.key = settings.DINON_KEY
        self.credential = settings.DINON_CREDIT

    def hex_digest(self, algrithom, data_list):
        digest = None
        try:
            hash_obj = hashlib.new(algrithom)
            for item in data_list:
                    hash_obj.update(item)
            digest = hash_obj.hexdigest()
        except Exception, e:
            return None
        return digest


    def calcSignature(self, algorithm, method, url, body=''):
        body_digest = self.hex_digest(algorithm, body)
        data_list = []
        data_list.append(method + '\n')
        data_list.append(self.key + '\n')
        data_list.append(url + '\n')
        data_list.append(body_digest + '\n')
        data_list.append(self.credential)
        signature = self.hex_digest(algorithm, data_list)
        return signature

    def load_file(self):
        data = None
        try:
            fp =open(self.xml_path)
            data = fp.read()
            fp.close()
        except Exception, e:
            print e
            return None
        return data

    def md5_file(self, name):
        m = hashlib.md5()
        a_file = open(name, 'rb')    #需要使用二进制格式读取文件内容
        m.update(a_file.read())
        a_file.close()
        return m.hexdigest()

    def req(self, type, rq_url, rq_body='', ETag=None):
        signature = self.calcSignature('md5', type, rq_url, rq_body)
        authorization = 'Algorithm=md5,Credential=' + self.credential  \
                        + ',Signature='+ signature
        rq_headers = {"Content-type": "application/xml", "Accept": "text/plain" ,"If-Match":ETag }
        rq_headers['Authorization'] = authorization
        try:
            httpClient = httplib.HTTPConnection('dcloud.dnion.com')
            httpClient.request(type , rq_url, rq_body, rq_headers)
            response = httpClient.getresponse()
            return (response, response.read())
        except Exception,e:
            LOG.error('can not connect to dilian %s' % e)
        finally:
            if httpClient:
                httpClient.close()

    def create(self):
        type = REQ_DICT['create']['type']
        rq_url = REQ_DICT['create']['rq_url']
        rq_body = self.load_file()
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        ETag = response.getheader("ETag")
        LOG.info("Create Request Url: %s" % rq_url)
        LOG.info("Create status:%s, ETag: %s, reason:%s, resp:%s" % (status, ETag, reason, resp))
        return (status, reason, resp)

    def config(self, disId, etag):
        type = REQ_DICT['config']['type']
        rq_url = REQ_DICT['config']['rq_url'] % disId
        rq_body = self.load_file()
        response, resp = self.req(type, rq_url, rq_body, etag)
        status = response.status
        reason = response.reason
        ETag = response.getheader("ETag")
        LOG.info("Update Request Url: %s" % rq_url)
        LOG.info("Update status:%s, ETag: %s, reason:%s, resp:%s" % (status, ETag, reason, resp))
        return (status, reason, resp, ETag)

    def delete(self, disId, etag):
        type = REQ_DICT['del']['type']
        rq_url = REQ_DICT['del']['rq_url'] % disId
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body, etag)
        status = response.status
        reason = response.reason
        ETag = response.getheader("ETag")
        LOG.info("Delete Request Url: %s" % rq_url)
        LOG.info("Delete status:%s, etag: %s, reason:%s, resp:%s" % (status, ETag, reason, resp))
        return (status, reason, resp)

    def logDownload(self, domain_name, date, hour):
        type = REQ_DICT['config']['type']
        rq_url = REQ_DICT['config']['rq_url'] % (domain_name, date, hour)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        LOG.info("Download Request Url: %s" % rq_url)
        LOG.info("Download status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)

    def getDomain(self, disId):
        type = REQ_DICT['get']['type']
        rq_url = REQ_DICT['get']['rq_url'] % disId
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        ETag = response.getheader("ETag")
        LOG.info("Get Request Url: %s" % rq_url)
        LOG.info("Get status:%s, ETag: %s, reason:%s, resp:%s" % (status, ETag, reason, resp))
        return (status, reason, resp, ETag)

    def cdnPushAndPrefetch(self, url_type, url):
        if url_type == "2":
            type = REQ_DICT['prefetch']['type']
            rq_url = REQ_DICT['prefetch']['rq_url']
            rq_body = url
        else:
            url_list = url.split('\n')
            url_str = ','.join(url_list)
            type = REQ_DICT['push']['type']
            rq_url = REQ_DICT['push']['rq_url'] % (url_type, url_str)
            rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        req_id = response.getheader("x-dnion-request-id")
        LOG.info("UrlPush Request Url: %s" % rq_url)
        LOG.info("UrlPush status:%s, req_id: %s, reason:%s, resp:%s" % (status, req_id, reason, resp))
        return (status, reason, resp, req_id)

    def pushProgress(self, req_id):
        type = REQ_DICT['progress']['type']
        rq_url = REQ_DICT['progress']['rq_url'] % req_id
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        LOG.info("UrlProgerss Request Url: %s" % rq_url)
        LOG.info("UrlProgress status:%s, req_id: %s, reason:%s, resp:%s" % (status, req_id, reason, resp))
        return (status, reason, resp)

    def prefetchProgress(self, req_id):
        type = REQ_DICT['prefetch_progress']['type']
        rq_url = REQ_DICT['prefetch_progress']['rq_url'] % req_id
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        LOG.info("PrefetchProgress Request Url: %s" % rq_url)
        LOG.info("PrefetchProgress status:%s, req_id: %s, reason:%s, resp:%s" % (status, req_id, reason, resp))
        return (status, reason, resp)

    def bandwidthMap(self, domain_name, start, end):
        type = REQ_DICT['bandwidthmap']['type']
        rq_url = REQ_DICT['bandwidthmap']['rq_url'] % (domain_name, start, end)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        LOG.info("BankwidthMap Request Url: %s" % rq_url)
        LOG.info("BandwidthMap status:%s, reason:%s" % (status, reason))
        return (status, reason, resp)

    def analyticsServer(self, domain_name, start, end, req_type):
        type = REQ_DICT['analyticsServer']['type']
        rq_url = REQ_DICT['analyticsServer']['rq_url'] % (domain_name, start, end, req_type)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        LOG.info("AnalyticsServer Request Url: %s" % rq_url)
        LOG.info("AnalyticsServer status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)

    def logDownloadList(self, domain_name, start, end):
        type = REQ_DICT['logDownLoadList']['type']
        rq_url = REQ_DICT['logDownLoadList']['rq_url'] % (domain_name, start, end)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        LOG.info("LogDownload Request Url: %s" % rq_url)
        LOG.info("LogDownload status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)

    def flowValue(self, domain_name, start, end, prov='', isp=''):
        type = REQ_DICT['flowValue']['type']
        rq_url = REQ_DICT['flowValue']['rq_url'] % (domain_name, start, end, prov, isp)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        LOG.info("flowValue Request Url: %s" % rq_url)
        LOG.info("flowValue status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)