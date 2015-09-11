# -*- coding: utf-8 -*-
'''
Created on 2013-10-14

@author: zzh
@version: 1.0
'''

import sys, logging, openstack_dashboard.api.cdn.util.ApiUtil as util, xml.dom.minidom as minidom
import traceback, base64
from openstack_dashboard.api.cdn.util.ApiUtil import BaseResult
import datetime

logging.basicConfig(level = logging.ERROR)
logger = logging.getLogger('ws.request')

X_CNC_REQUEST_ID = 'x-cnc-request-id'

X_CNC_DATE = 'x-cnc-date'

class RequestApi(object):
    '''报表查询API'''
    HOST = 'https://cloudcdn.chinanetcenter.com';
    #HOST = 'http://localhost:8080/cloud-cdn.cdn_domain_manager';
    ''' api服务地址 '''
    
    def __init__(self, user, apiKey):
        ''' 
                    初始化ReportApi 用于缓存操作相关调用
        @type user: str
        @param user: 用户名
        @type apiKey: str
        @param apiKey: 用户的api key
        @rtype: ReportApi
        @return: instance of ReportApi
        '''
        self.user = user
        self.apiKey = apiKey
        self.headers = {'Accept' : 'application/xml', 'Content-Type' : 'application/xml'}
    
    def getRequest(self, requestId):
        ''' 对于客户每一次请求记录/任务，都会生成一个 cnc-request-id。客户可以通过该 id查询请求记录，如果是异步的任务(HTTP 响应状态码为 HTTP 202 Accepted 的任务)，也可以通过该接口查询任务最终执行结果。 
        @param requestId:  请求的标识Id
        @rtype: GetRequestResult
        @return: 通过GetRequestResult.getRequestLog() 获得查询后的请求记录
        '''
        url = self.HOST + "/api/request/" + str(requestId) 
        try:
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToSuccessResult(ret)
            else:
                return XmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return GetRequestProcessResult(-1, str(e))
        
    def makeHeaders(self):  
        ''' 组装头部 '''  
        global X_CNC_DATE
        headers = self.headers.copy()
        headers[X_CNC_DATE] = util.getRFCTime()
        key = util.hashPassword(headers[X_CNC_DATE], self.apiKey)
        headers['Authorization'] = "Basic " + base64.standard_b64encode(self.user + ':' + key)
        return headers

class RequestLog(object):
    '''请求记录'''
    def __init__(self, cncRequestId = None, timeStamp = None, asyncResult = None, asyncMessage = None):
        '''初始化
        @param asyncResult: WAIT, INPROGRESS, SUCCESS, FAIL 
        '''
        self.cncRequestId = cncRequestId
        self.timeStamp = timeStamp
        self.asyncResult = asyncResult
        self.asyncMessage = asyncMessage

def xmlToSuccessResult(ret):
    ''' 返回xml 转换成 带 RequestLog对象列表的GetRequestProcessResult对象 '''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)
   
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    requestLogNode = util.getChildNode(doc, 'request-log')
    cncRequestId = util.getChildNodeText(requestLogNode, 'cnc-request-id')
    timestamp = util.getChildNodeText(requestLogNode, 'timestamp')
    asyncResult = util.getChildNodeText(requestLogNode, 'async-result')
    asyncMessage = util.getChildNodeText(requestLogNode, 'async-message')
    rl = RequestLog(cncRequestId, timestamp, asyncResult, asyncMessage)
    return GetRequestProcessResult(ret.status, 'OK', xCncRequestId = requestId, requestLog = rl)

class GetRequestProcessResult(BaseResult):
    '''请求数查询结果'''
    def __init__(self, ret, msg, xCncRequestId = None, requestLog = None):
        '''
        @type hitPoints: list of HitPoint
        @param hitPoints: 返回请求数统计结果列表
        '''
        super(GetRequestProcessResult, self).__init__(ret, msg, xCncRequestId)
        self.requestLog = requestLog
    
    def getRequestLog(self):
        '''返回HitPoint列表'''
        return self.requestLog
        
def XmlToFailure(ret):
    msg = util.getReturnXmlMsg(ret)
    return GetRequestProcessResult(ret.status, ret.reason + ":" + msg)      
