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
logger = logging.getLogger('ws.report')

X_CNC_REQUEST_ID = 'x-cnc-request-id'

X_CNC_DATE = 'x-cnc-date'

REPORT_TYPE_5_MINUTES = 'fiveminutes'
REPORT_TYPE_HOURLY = 'hourly'
REPORT_TYPE_DAILY = 'daily'

class ReportApi(object):
    '''报表查询API'''
    HOST = 'https://cloudcdn.chinanetcenter.com';
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
    
    def getLog(self, reportForm, domainId):
        ''' 获取某域名的日志下载链接 
        @type reportForm: ReportForm
        @param reportForm:  请求的起止时间
        @rtype: LogProcessResult
        @return: 通过LogProcessResult.getLogs() 获得查询后的Log对象实例列表
        '''
        url = self.HOST + "/api/report/" + str(domainId) + "/log" 
        try:
            url = appendParams(url, reportForm)
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToLogList(ret)
            else:
                return getLogXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return LogProcessResult(-1, str(e))
        
    def getFlowReport(self, reportForm, domainId = None):
        ''' 获取某域名流量报表 如果domainId 为None,表示 查汇总信息
        @type reportForm: ReportForm
        @param reportForm:  请求的起止时间和报表粒度
        @rtype: FlowRrocessResult
        @return: 通过FlowProcessResult.getFlowPoints() 获得流量查询结果
        '''
        if domainId == None:
            url = self.HOST + "/api/report/flow"
        else:
            url = self.HOST + "/api/report/" + str(domainId) + "/flow" 
        try:
            url = appendParams(url, reportForm)
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToFlowPointList(ret, reportForm.getReportType())
            else:
                return getFlowReportXmlToDefaultFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return FlowProcessResult(-1, str(e))
    
    def getHitReport(self, reportForm, domainId = None):
        ''' 获取某域名请求数报表 如果domainId 为None,表示 查汇总信息
        @type reportForm: ReportForm
        @param reportForm:  请求的时间和报表粒度
        @rtype: HitProcessResult
        @return: 通过HitProcessResult.getHitPoints() 获得返回的结果
        '''
        if domainId == None:
            url = self.HOST + "/api/report/hit"
        else:
            url = self.HOST + "/api/report/" + str(domainId) + "/hit" 
        try:
            url = appendParams(url, reportForm)
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToHitPointList(ret, reportForm.getReportType())
            else:
                return getHitReportXmlToDefaultFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return HitProcessResult(-1, str(e))
        
        
    def makeHeaders(self):  
        ''' 组装头部 '''  
        global X_CNC_DATE
        headers = self.headers.copy()
        headers[X_CNC_DATE] = util.getRFCTime()
        key = util.hashPassword(headers[X_CNC_DATE], self.apiKey)
        headers['Authorization'] = "Basic " + base64.standard_b64encode(self.user + ':' + key)
        return headers

def appendParams(url, reportForm):
    dateFrom = reportForm.getDateFrom()
    dateTo = reportForm.getDateTo()
    reportType = reportForm.getReportType()
    originUrl = url + "?" 
    if dateFrom or dateTo or type:
        url = url + "?"
    if dateFrom:
        url = url + "datefrom=" + util.getRFC3339Time(dateFrom).replace('+', '%2B') 
    if dateTo:
        if url == originUrl:
            url = originUrl + "dateto=" + util.getRFC3339Time(dateTo).replace('+', '%2B')
        else:
            url =  url + "&dateto=" + util.getRFC3339Time(dateTo).replace('+', '%2B')
    if reportType:
        if url == originUrl:
            url = originUrl + "type=" + reportType
        else:
            url = url + "&type=" + reportType
    return url

class ReportForm (object):
    '''查询的起止时间和粒度'''
    def __init__(self, dateFrom = None, dateTo = None, reportType = None):
        '''初始化
        @type reportType: str
        @param reportType: 模块中已经定义了常量,分别是模块变量:REPORT_TYPE_5_MINUTES, REPORT_TYPE_HOURLY, REPORT_TYPE_DAILY
        '''
        self.dateFrom = dateFrom
        self.dateTo = dateTo
        self.reportType = reportType
        pass

    def getDateFrom(self):
        ''' 获得开始时间'''
        return self.dateFrom

    def setDateFrom(self, dateFrom):
        '''设置开始时间'''
        self.dateFrom = dateFrom

    def getDateTo(self):
        '''获得结束时间'''
        return self.dateTo

    def setDateTo(self, dateTo):
        '''设置结束时间'''
        self.dateTo = dateTo

    def getReportType(self):
        '''获得报表粒度'''
        return self.reportType

    def setReportType(self, reportType):
        '''设置报表粒度'''
        self.reportType = reportType

class FlowPoint(object):
    '''流量统计结果'''
    def __init__(self, point = None, flow = None):
        '''初始化
        @param point: 流量统计时间点
        @param flow: 流量统计值,单位为M
        '''
        self.point = point
        self.flow = flow
    
    def getPoint(self):
        return self.point
    def setPoint(self, point):
        self.point = point
    def getFlow(self):
        return self.flow
    def setFlow(self, flow):
        self.flow = flow

class HitPoint(object):
    '''请求数统计结果'''
    def __init__(self, point = None, hit = None):
        '''
        @param point: 请求数统计时间点
        @param hit: 请求数统计值
        '''
        self.point = point
        self.hit = hit
    
    def getPoint(self):
        return self.point
    def setPoint(self, point):
        self.point = point
    def getHit(self):
        return self.hit
    def setHit(self, hit):
        self.hit = hit

class Log(object):
    '''原始日志下载链接'''
    def __init__(self, dateFrom = None, dateTo = None, url = None, fileSize = None):
        '''
        @param dateFrom: 该下载链接包含的请求开始时间
        @param dateTo: 该下载链接包含的请求结束时间
        @param url: 下载链接，需要注意的是，该下载链接12h内有效，如查过12h需要重新请求以获取新的链接
        @param fileSize: the unit is byte
        '''
        self.dateFrom = dateFrom
        self.dateTo = dateTo
        self.url = url
        self.fileSize = fileSize
 
def xmlToHitPointList(ret, reportType):
    ''' 返回xml 转换成 带 HitPoint对象列表的HitProcessResult对象 '''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    
    isoFormat = getDateFormat(reportType)
   
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    hitPointListNode = util.getChildNode(doc, 'hit-report')
    hitPointList = []
    hitDataList = util.getChildNodeList(hitPointListNode, 'hit-data')
    for hitNode in hitDataList:
        pointStr = util.getChildNodeText(hitNode, 'timestamp')
        point = datetime.datetime.strptime(pointStr, isoFormat)
        hit = util.getChildNodeText(hitNode, 'hit')
        hitPoint = HitPoint(point, hit)
        hitPointList.append(hitPoint)
    return HitProcessResult(ret.status, 'OK', xCncRequestId = requestId, hitPoints = hitPointList)


def xmlToFlowPointList(ret, reportType):
    ''' 返回xml 转换成 带 FlowPoint对象列表的FlowProcessResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)
   
    isoFormat = getDateFormat(reportType)
   
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    flowPointListNode = util.getChildNode(doc, 'flow-report')
    flowSummary = util.getChildNodeText(flowPointListNode, 'flow-summary')
    flowPointList = []
    flowDataList = util.getChildNodeList(flowPointListNode, 'flow-data')
    for flowNode in flowDataList:
        pointStr = util.getChildNodeText(flowNode, 'timestamp')
        point = datetime.datetime.strptime(pointStr, isoFormat)
        flow = util.getChildNodeText(flowNode, 'flow')
        flowPoint = FlowPoint(point, flow)
        flowPointList.append(flowPoint)
    return FlowProcessResult(ret.status, 'OK', xCncRequestId = requestId, flowPoints = flowPointList, flowSummary = flowSummary);

def xmlToLogList(ret):
    ''' 返回xml 转换成 带Log对象列表的LogProcessResult对象 '''
    global X_CNC_REQUEST_ID
    requestId = ret.getheader(X_CNC_REQUEST_ID)
   
    isoFormat = "%Y-%m-%d-%H%M"
    
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    logListNode = util.getChildNode(doc, 'logs')
    logList = []
    logDataList = util.getChildNodeList(logListNode, 'log')
    for logNode in logDataList:
        dateFromStr = util.getChildNodeText(logNode, 'datefrom')
        dateToStr = util.getChildNodeText(logNode, 'dateto')
        url = util.getChildNodeText(logNode, 'log-url')
        fileSize = util.getChildNodeText(logNode, 'file-size')
        
        dateFrom = datetime.datetime.strptime(dateFromStr, isoFormat)
        dateTo = datetime.datetime.strptime(dateToStr, isoFormat)
        
        log = Log(dateFrom, dateTo, url, fileSize)
        logList.append(log)
    return LogProcessResult(ret.status, 'OK', xCncRequestId = requestId, logs = logList);

def getDateFormat(reportType):
    if reportType == REPORT_TYPE_5_MINUTES:
        return "%Y-%m-%d %H:%M:%S"
    elif reportType == REPORT_TYPE_HOURLY:
        return "%Y-%m-%d %H:%M"
    else:
        return "%Y-%m-%d"

class FlowProcessResult(BaseResult):
    '''流量查询结果'''
    def __init__(self, ret, msg, xCncRequestId = None, flowPoints = None, flowSummary = None):
        '''
        @type flowPoints: list of FlowPoint
        @param flowPoints: 返回流量统计结果列表
        '''
        super(FlowProcessResult, self).__init__(ret, msg, xCncRequestId)
        self.flowPoints = flowPoints
        self.flowSummary = flowSummary
    
    def getFlowPoints(self):
        '''返回流量统计结果列表'''
        return self.flowPoints
        

class HitProcessResult(BaseResult):
    '''请求数查询结果'''
    def __init__(self, ret, msg, xCncRequestId = None, hitPoints = None):
        '''
        @type hitPoints: list of HitPoint
        @param hitPoints: 返回请求数统计结果列表
        '''
        super(HitProcessResult, self).__init__(ret, msg, xCncRequestId)
        self.hitPoints = hitPoints

    def getHitPoints(self):
        '''返回HitPoint列表'''
        return self.hitPoints
        
class LogProcessResult(BaseResult):
    ''' 原始日志查询结果'''
    def __init__(self, ret, msg, xCncRequestId = None, logs = None):
        '''
        @type logs: list of Log
        @param logs: 返回原始日志请求结果列表
        '''
        super(LogProcessResult, self).__init__(ret, msg, xCncRequestId)
        self.logs = logs
    
    def getLogs(self):
        '''返回log记录列表'''
        return self.logs

def getLogXmlToFailure(ret):
    msg = util.getReturnXmlMsg(ret)
    return LogProcessResult(ret.status, ret.reason + ":" + msg)      

def getFlowReportXmlToDefaultFailure(ret):
    msg = util.getReturnXmlMsg(ret)
    return FlowProcessResult(ret.status, ret.reason + ":" + msg)

def getHitReportXmlToDefaultFailure(ret):
    msg = util.getReturnXmlMsg(ret)
    return HitProcessResult(ret.status, ret.reason + ":" + msg)