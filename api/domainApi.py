# -*- coding: utf-8 -*-
'''
Created on 2013-1-10

@author: sinlangxmu@gmail.com
@version: 1.0
'''

import sys, logging, openstack_dashboard.api.cdn.util.ApiUtil as util, xml.dom as dom, xml.dom.minidom as minidom
import traceback, base64
from openstack_dashboard.api.cdn.util.ApiUtil import BaseResult


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('ws.cloundcdn')

X_CNC_REQUEST_ID = 'x-cnc-request-id'

X_CNC_DATE = 'x-cnc-date'

X_CNC_LOCATION = 'location'

X_CNC_CNAME = 'cname'
    
class DomainApi(object):
    ''' 域名操作API '''
    HOST = 'https://cloudcdn.chinanetcenter.com'
    #HOST = 'http://192.168.27.161:8080/cloudcdn'
    #HOST = 'http://localhost:8080/cloud-cdn.cdn_domain_manager'
    ''' api服务地址 '''

    def __init__(self, user, apiKey):
        ''' 
                    初始化DomainApi 用于域名管理相关调用
        @type user: str
        @param user: 用户名
        @type apiKey: str
        @param apiKey: 用户的api key
        @rtype: DomainApi对象
        @return: instance of DomainApi
        '''
        self.user = user
        self.apiKey = apiKey
        self.headers = {'Accept': 'application/xml', 'Content-Type' : 'application/xml'}
    
    def add(self, domain):
        ''' 创建加速域名 
        @param domain:  新增加速域名构建的Domain对象实例
        @rtype: ProcessResult对象
        @return: 通过ProcessResult.getLocation()新域名的url
        '''
        url = self.HOST + "/api/domain"
        try:
            post = domainToXml(domain)
            #print post
            ret = util.httpReqeust(url, post, self.makeHeaders(url), "POST")
            if ret.status == 202:
                return xmlToSuccess(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
    
    def listAll(self):
        ''' 获取加速所有域名列表
        @rtype: ProcessResult对象 
        @return: 通过ProcessResult.getDomainSummarys()获取DomainSummary对象的实例列表
        '''
        
        url = self.HOST + "/api/domain"
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(url), "GET")
            if ret.status == 200:
                return xmlToDomainList(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def find(self, domainId):
        ''' 获取加速域名配置  
        @type domainId: str
        @param domainId : 指定查找的域名ID
        @rtype: ProcessResult对象
        @return: 通过ProcessResult.getDomain()返回指定的域名信息的Domain实例
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(url), "GET")
            if ret.status == 200:
                return xmlToDomain(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def modify(self, domain):
        ''' 修改加速域名配置 
        @type domain: Domain
        @param domain : 构建需要修改的域名的Domain实例, domain中必须设置domanId字段
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        if domain.domainId is None:
            raise '请设置domainId字段'
        
        url = self.HOST + "/api/domain/" + str(domain.domainId)
        try:
            post = domainToXml(domain)
            #print post
            ret = util.httpReqeust(url, post, self.makeHeaders(url), "PUT")
            if ret.status == 202:
                return xmlToSuccess(ret)
            else:
                return xmlToFailure(ret)   
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def delete(self, domainId):
        ''' 删除加速域名 
        @param domainId : 指定待删除的域名ID
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(url), "DELETE")
            if ret.status == 202:
                return xmlToSuccess(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def disable(self, domainId):
        ''' 禁用加速域名 
        @param domainId : 指定待禁用的域名ID
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(url), "DISABLE")
            if ret.status == 202:
                return xmlToSuccess(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def enable(self, domainId):
        ''' 启用加速域名 
        @param domainId : 指定启用的域名ID
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(url), "ENABLE")
            if ret.status == 202:
                return xmlToSuccess(ret)
            else:
                return xmlToFailure(ret) 
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
        
    def makeHeaders(self, uri):
        ''' 组装头部  '''  
        global X_CNC_DATE
        headers = self.headers.copy()
        headers[X_CNC_DATE] = util.getRFCTime()
        key = util.hashPassword(headers[X_CNC_DATE], self.apiKey)
        headers['Authorization'] = "Basic " + base64.standard_b64encode(self.user + ':' + key)
        return headers


class Domain(object):
    '''表示为域名对象'''
    def __init__(self, domainName = None, serviceType = None,
                 domainId = None, comment = None, serviceAreas = None, status = None, enabled = None, cname = None,
                 originConfig = None, queryStringSettings = None, cacheBehaviors = None,
                 visitControlRules = None):
        ''' 初始化域名对象
        @param domainName: 设置域名名称
        @param serviceType: 服务类型,默认为web
        @param domainId: 指定域名id，修改域名时使用
        @param comment: 注释
        @param serviceAreas: 加速区域
        @param cname: 获取域名cname信息，只有将域名的dns解析cname到该地址后，流量才会导入到网宿cdn中
        @param status: 查询域名部署状态
        @param enabled: 查询域名是否启用
        @type originConfig: OriginConfig
        @param originConfig: 设置回源信息
        @type cacheBehaviors: list of CacheBehavior
        @param cacheBehaviors: 缓存规则列表, CacheBehavior对象实例的列表
        @type visitControlRules: list of VisitControlRule
        @param visitControlRules: 访问者控制规则列表, VisitControlRule对象实例的列表
        @rtype: Domain  
        '''
        self.domainName = domainName
        self.serviceType = serviceType
        self.domainId = domainId
        self.comment = comment
        self.serviceAreas = serviceAreas
        self.status = status
        self.enabled = enabled
        self.cname = cname
        self.originConfig = originConfig
        self.queryStringSettings = queryStringSettings
        self.cacheBehaviors = cacheBehaviors
        self.visitControlRules = visitControlRules

class QueryStringSetting(object):
    '''查询串控制'''
    def __init__(self, pathPattern = None, ignoreQueryString = None):
        '''初始化一个查询串控制规则
        @param pathPattern: 设置文件类型，支持多个文件类型,当有多个文件类型时，以,分割
        @type ignoreQueryString: True or False  
        '''
        self.pathPattern = pathPattern
        self.ignoreQueryString = ignoreQueryString

class VisitControlRule(object):
    '''访问者控制规则'''
    def __init__(self, pathPattern = None, allowNullReferer = None, validReferers = None, invalidReferers = None, forbiddenIps = None):
        '''初始化一个访问者控制规则
        @param pathPattern: 设置文件类型，支持多个文件类型,当有多个文件类型时，以,分割
        @type validReferers: list of str
        @param allowNullReferer: 允许请求referer为空?
        @type allowNullReferer: True or False  
        @param validReferers: referer白名单列表，支持泛域名（如.chinanetcenter.com）
        @type invalidReferers: list of str
        @param invalidReferers: referer黑名单列表，支持泛域名（如.chinanetcenter.com） 
        @type forbiddenIps: list of str
        @param forbiddenIps: ip黑名单列表
        '''
        self.pathPattern = pathPattern
        self.allowNullReferer = allowNullReferer
        self.validReferers = validReferers
        self.invalidReferers = invalidReferers
        self.forbiddenIps = forbiddenIps

class OriginConfig(object):
    ''' 回源配置'''
    
    def __init__(self, originIps = None, originDomainName = None, advOriginConfigs = None):
        ''' 初始化回源配置
        :rtype : object
        @type originIps: list of str
        @param originIps: 回源ip列表，平台支持多个回源ip b
        @param originDomainName: 设置回源域名，平台支持通过ip或者域名回源，但二者只能选一，不能同时提供
        @type advOriginConfigs: list of AdvOriginConfig
        @param advOriginConfigs: 复杂回源规则列表
        '''
        self.originIps = originIps
        self.originDomainName = originDomainName
        self.advOriginConfigs = advOriginConfigs
        
    
class AdvOriginConfig(object):
    '''复杂回源规则'''
    def __init__(self, isps = None, masterIps = None, backupIps = None, detectUrl = None, detectPeriod = None):
        ''' 初始化复杂回源规则
        @type isps: list of str
        @param isps: 设置isp信息,允许设定多个运营商;dx("中国电信"), wt("中国联通"), yidong("中国移动"), tt("中国铁通"), jyw("中国教育网"), changkuan("长城宽带"), gd("中国广电"), qita("其他"), all("全部");
        @type masterIps: list of str
        @param masterIps: 允许设定多个主IP
        @type backupIps: list of str
        @param backupIps: 允许设定多个备用IP，只有当主IP不可用时，才使用备IP
        @param detectUrl: 监控URL，用于判断源主机是否可用
        @param detectPeriod: 回源监控的频率，单位为S
        '''
        self.isps = isps
        self.masterIps = masterIps
        self.backupIps = backupIps
        self.detectUrl = detectUrl
        self.detectPeriod = detectPeriod

class CacheBehavior(object):
    ''' 缓存行为 '''
    
    def __init__(self, pathPattern = None, ignoreCacheControl = None, cacheTtl = None):
        '''

        :rtype : object
        @type priority: int
        @param pathPattern: 设置路径匹配格式，支持*通配符以及|、()等正则字符，举例如下： 所有jpg文件：*.jpg 所有jpg或者gif文件：*.(jpg|gif) a/b/c下所有文件：a/b/c/ a/b/c下的所有jpg或者gif文件：a/b/c/*.(jpg|gif)
        @type ignoreCacheControl: boolean
        @param ignoreCacheControl: 设置是否忽略http头中的cache-control
        @param cacheTtl: 设置缓存时间，单位为s 
        '''
        self.pathPattern = pathPattern
        self.ignoreCacheControl = ignoreCacheControl
        self.cacheTtl = cacheTtl

def parseAdvOriginConfigList(nodeList):
    advOriginConfigList = []
    for advOriginConfigNode in nodeList:
        ispsList = util.getChildNodeText(advOriginConfigNode, 'isp')
        masterIpsList = util.getChildNodeText(advOriginConfigNode, 'master-ips')
        backupIpsList = util.getChildNodeText(advOriginConfigNode, 'backup-ips')
        detectUrl = util.getChildNodeText(advOriginConfigNode, 'detect-url')
        detectPeriod = util.getChildNodeText(advOriginConfigNode, 'detect-period')
        isps = splitStr(ispsList)
        masterIps = splitStr(masterIpsList)
        backupIps = splitStr(backupIpsList)
        advOriginConfig = AdvOriginConfig(isps = isps, masterIps = masterIps, backupIps = backupIps, 
                                          detectUrl = detectUrl, detectPeriod = detectPeriod)
        advOriginConfigList.append(advOriginConfig)
    return advOriginConfigList

def parseQueryStringSettingListNode(nodeList):
    queryStringSettingList = []
    for queryStringSetting in nodeList:
        pathPattern = util.getChildNodeText(queryStringSetting, 'path-pattern')
        ignoreQueryStringStr = util.getChildNodeText(queryStringSetting, 'ignore-query-string')
        if ignoreQueryStringStr == "false":
            ignoreQueryString = False
        else:
            ignoreQueryString = True 
        queryStringSetting = QueryStringSetting(pathPattern, ignoreQueryString)
        queryStringSettingList.append(queryStringSetting)
    return queryStringSettingList

def parseCacheBehaviorList(nodeList):
    cacheBehaviorList = []
    for cacheBehavior in nodeList:
        pathPattern = util.getChildNodeText(cacheBehavior, 'path-pattern')
        priority = util.getChildNodeText(cacheBehavior, 'priority')
        ignoreCacheControlStr = util.getChildNodeText(cacheBehavior, 'ignore-cache-control')
        if ignoreCacheControlStr == "false":
            ignoreCacheControl = False
        else:
            ignoreCacheControl = True 
        cacheTTL = util.getChildNodeText(cacheBehavior, 'cache-ttl')
        cacheBehavior = CacheBehavior(pathPattern, ignoreCacheControl, cacheTTL)
        cacheBehaviorList.append(cacheBehavior)
    return cacheBehaviorList

def parseVisitControlRulesList(nodeList):
    vistControlRulesList = []
    for node in nodeList:
        pathPattern = util.getChildNodeText(node, 'path-pattern')
        allowNullReffer = util.getChildNodeText(node, 'allownullreferer')
        validReferRootNode = util.getChildNode(node, "valid-referers")
        validRNode = util.getChildNodeList(validReferRootNode, 'referer')
        validRefers = []
        for ref in validRNode:
            validRefers.append(util.getChildNodeText(ref, "referer"))
        
        invalidReferRootNode = util.getChildNode(node, "invalid-referers")
        invalidRNode = util.getChildNodeList(invalidReferRootNode, 'referer')
        invalidRefers = []
        for ref in invalidRNode:
            invalidRefers.append(util.getChildNodeText(ref, "referer"))
        
        forbiddenIps = splitStr(util.getChildNodeText(node, 'forbidden-ips'))
        
        visitControlRule = VisitControlRule(pathPattern, allowNullReffer, validRefers, invalidRefers, forbiddenIps)
        vistControlRulesList.append(visitControlRule)
        
    return vistControlRulesList

def splitStr(data):
    list1 = data.split(";")
    res = []
    for item in list1:
        res = item.split(",") + res
    return res

def xmlToDomain(ret):
    ''' 返回xml 转换成 带 Domain对象的ProcessResult对象, 在查询频道信息的时候使用'''
    
    global X_CNC_REQUEST_ID, X_CNC_LOCATION, logger
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    
    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    
    domainNode = util.getChildNode(doc, 'domain')
    domainName = util.getChildNodeText(domainNode, 'domain-name')
    domainId = util.getChildNodeText(domainNode, 'domain-id')
    serviceType = util.getChildNodeText(domainNode, 'service-type')
    comment = util.getChildNodeText(domainNode, 'comment')
    serviceAreas = util.getChildNodeText(domainNode, 'service-areas')
    enabled = util.getChildNodeText(domainNode, 'enabled')
    cname = util.getChildNodeText(domainNode, 'cname')
    status = util.getChildNodeText(domainNode, 'status')
    
    domain = Domain(domainName = domainName, 
                    serviceType = serviceType, 
                    domainId = domainId,
                    comment = comment, 
                    serviceAreas = serviceAreas,
                    enabled = enabled, 
                    cname = cname,
                    status = status)
    
    originConfigNode = util.getChildNode(domainNode, 'origin-config')
    if originConfigNode is not None:
        originIpsStr = util.getChildNodeText(originConfigNode, 'origin-ips')
        originIps = splitStr(originIpsStr)
        originDomainName = util.getChildNodeText(originConfigNode, 'origin-domain-name')
        advOriginConfigListRootNode = util.getChildNode(originConfigNode, 'adv-origin-configs')
        if advOriginConfigListRootNode is not None:
            advOriginConfigListNode = util.getChildNodeList(advOriginConfigListRootNode, 'adv-origin-config')
            advOriginConfigs = []
            if advOriginConfigListNode is not None:
                advOriginConfigs = parseAdvOriginConfigList(advOriginConfigListNode)
                originConfig = OriginConfig(originIps, originDomainName, advOriginConfigs)
                domain.originConfig = originConfig   
        else:
            originConfig = OriginConfig(originIps, originDomainName)
            domain.originConfig = originConfig   
    
    queryStringSettingListRootNode = util.getChildNode(domainNode, 'query-string-settings')
    if queryStringSettingListRootNode is not None:
        queryStringSettingListNode = util.getChildNodeList(queryStringSettingListRootNode, 'query-string-setting')
        if queryStringSettingListNode is not None:
            queryStringSettingList = parseQueryStringSettingListNode(queryStringSettingListNode)
            domain.queryStringSettings = queryStringSettingList
    
    cacheBehaviorListRootNode = util.getChildNode(domainNode, 'cache-behaviors')
    if cacheBehaviorListRootNode is not None:
        cacheBehaviorListNode = util.getChildNodeList(cacheBehaviorListRootNode, 'cache-behavior')
        if cacheBehaviorListNode is not None:
            cacheBehaviorList = parseCacheBehaviorList(cacheBehaviorListNode)
            domain.cacheBehaviors = cacheBehaviorList
    
    visitControlRulesListRootNode = util.getChildNode(domainNode, 'visit-control-rules')
    if visitControlRulesListRootNode is not None:
        visitControlRulesListNode = util.getChildNodeList(visitControlRulesListRootNode, 'visit-control-rule')
        if visitControlRulesListNode is not None:
            visitControlRulesList = parseVisitControlRulesList(visitControlRulesListNode)
            domain.visitControlRules = visitControlRulesList
        
    return ProcessResult(0, 'OK', xCncRequestId = requestId, domain = domain);

def domainToXml(domain):
    ''' Domain 对象 转换成 xml '''
    
    doc = dom.getDOMImplementation().createDocument('', 'domain', '')
    domainNode = util.getChildNode(doc, 'domain')
    util.addElement(doc, domainNode, 'version', "1.0.0")
    if domain.domainName is not None:
        util.addElement(doc, domainNode, 'domain-name',  domain.domainName)
    if domain.serviceType is not None:
        util.addElement(doc, domainNode, 'service-type',  domain.serviceType)
    if domain.comment is not None:
        util.addElement(doc, domainNode, 'comment',  domain.comment)
    
    if domain.serviceAreas is not None:
        util.addElement(doc, domainNode, 'service-areas', domain.serviceAreas)
    else:
        util.addElement(doc, domainNode, 'service-areas', 'cn')
    
    if domain.originConfig is not None:
        originConfigNode = util.addElement(doc, domainNode, 'origin-config')
        if domain.originConfig.originIps is not None:
            originIps = domain.originConfig.originIps
            util.addElement(doc, originConfigNode, 'origin-ips', ';'.join(originIps))
        if domain.originConfig.originDomainName is not None:
            util.addElement(doc, originConfigNode, 'origin-domain-name', domain.originConfig.originDomainName)
        if domain.originConfig.advOriginConfigs is not None:
            advOriginConfigsNode = util.addElement(doc, originConfigNode, 'adv-origin-configs')
            for advOriginConfig in domain.originConfig.advOriginConfigs:
                isps = advOriginConfig.isps
                advOriginConfigNode = util.addElement(doc, advOriginConfigsNode, 'adv-origin-config')
                util.addElement(doc, advOriginConfigNode, 'isp', ';'.join(isps))
                util.addElement(doc, advOriginConfigNode, 'master-ips', ';'.join(advOriginConfig.masterIps))
                util.addElement(doc, advOriginConfigNode, 'backup-ips', ';'.join(advOriginConfig.backupIps))
                util.addElement(doc, advOriginConfigNode, 'detect-url', advOriginConfig.detectUrl)
                util.addElement(doc, advOriginConfigNode, 'detect-period', advOriginConfig.detectPeriod)                
    
    if domain.queryStringSettings is not None:
        queryStringSettingsNode = util.addElement(doc, domainNode, 'query-string-settings')
        for queryStringSetting in domain.queryStringSettings:
            queryStringSettingNode = util.addElement(doc, queryStringSettingsNode, 'query-string-setting')
            util.addElement(doc, queryStringSettingNode, 'path-pattern', queryStringSetting.pathPattern)
            if queryStringSetting.ignoreQueryString == False:
                util.addElement(doc, queryStringSettingNode, 'ignore-query-string', "false")
            else:
                util.addElement(doc, queryStringSettingNode, 'ignore-query-string', "true")
    
    if domain.cacheBehaviors is not None:
        cacheBehaviorsNode = util.addElement(doc, domainNode, 'cache-behaviors')
        for cacheBehavior in domain.cacheBehaviors:
            cacheBehaviorNode = util.addElement(doc, cacheBehaviorsNode, 'cache-behavior')
            util.addElement(doc, cacheBehaviorNode, 'path-pattern', cacheBehavior.pathPattern)
            if cacheBehavior.ignoreCacheControl == False:
                util.addElement(doc, cacheBehaviorNode, 'ignore-cache-control', "false")
            else:
                util.addElement(doc, cacheBehaviorNode, 'ignore-cache-control', "true")
            util.addElement(doc, cacheBehaviorNode, 'cache-ttl', cacheBehavior.cacheTtl)
    
    if domain.visitControlRules is not None:
        visitControlRulesNode = util.addElement(doc, domainNode, 'visit-control-rules')
        for visitControl in domain.visitControlRules:
            visitControlNode = util.addElement(doc, visitControlRulesNode, "visit-control-rule")
            if visitControl.allowNullReferer == True:
                util.addElement(doc, visitControlNode, 'allownullreferer', "true")
            elif visitControl.allowNullReferer == False:
                util.addElement(doc, visitControlNode, 'allownullreferer', "false")
            
            util.addElement(doc, visitControlNode, 'path-pattern', visitControl.pathPattern)
            validRNode = util.addElement(doc, visitControlNode, 'valid-referers')
            validReferers = visitControl.validReferers
            if validReferers is not None and len(validReferers) > 0 :
                for referer in validReferers:
                    util.addElement(doc, validRNode, 'referer', referer)
            invalidRNode = util.addElement(doc, visitControlNode, 'invalid-referers')
            invalidReferers = visitControl.invalidReferers
            if invalidReferers is not None and len(invalidReferers) > 0 :
                for referer in invalidReferers:
                    util.addElement(doc, invalidRNode, 'referer', referer)
            util.addElement(doc, visitControlNode, 'forbidden-ips', ';'.join(visitControl.forbiddenIps))
    return doc.toprettyxml(indent = "", newl="", encoding = 'utf-8')

def xmlToDomainList(ret):
    ''' 返回xml 转换成 带 Domain对象列表的ProcessResult对象, 在查询用户下所有频道时候使用'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    domainListNode = util.getChildNode(doc, 'domain-list')
    domainList = []
    domainSummaryList = util.getChildNodeList(domainListNode, 'domain-summary')
    for domainNode in domainSummaryList:
        domainId = util.getChildNodeText(domainNode, 'domain-id')
        cname = util.getChildNodeText(domainNode, 'cname')
        domainName = util.getChildNodeText(domainNode, 'domain-name')
        status = util.getChildNodeText(domainNode, 'status')
        serviceType = util.getChildNodeText(domainNode, "service-type")
        enabled = util.getChildNodeText(domainNode, 'enabled') == 'true'
        cdnServiceStatus = util.getChildNodeText(domainNode, 'cdn-service-status') == 'true'
        domainSummary = DomainSummary(domainId, domainName, cname,
                  status, enabled,
                  serviceType, cdnServiceStatus)
        domainList.append(domainSummary)
    return ProcessResult(0, 'OK', xCncRequestId = requestId, domainSummarys = domainList);

class DomainSummary(object):
    ''' 查询域名列表 返回 的列表中 单个域名的信息 '''
    def __init__(self, domainId = None, domainName = None, cname = None,
                  status = None, enabled = None,
                  serviceType = None, cdnServiceStatus = None):
        '''
        @param domainName: 设置域名名称
        @param serviceType: 服务类型
        @param domainId: 指定域名id，修改域名时使用
        @param cname: 获取域名cname信息，只有将域名的dns解析cname到该地址后，流量才会导入到网宿cdn中
        @param cdnServiceStatus: 域名服务状态
        @param status: 查询域名部署状态
        @param enabled: 查询域名是否启用
        '''
        self.domainId = domainId
        self.domainName = domainName
        self.cname = cname
        self.status = status
        self.enabled = enabled
        self.serviceType = serviceType
        self.cdnServiceStatus = cdnServiceStatus
        
class ProcessResult(BaseResult):
    '''表示请求的返回结果'''
    def __init__(self, ret, msg, xCncRequestId = None, domain = None, domainSummarys = None, location = None,
                 cname = None):
        '''

        :rtype : object
        @param ret: HTTP响应状态码
        @param msg: 响应消息
        @param xCncRequestId: 每一次请求，都会被分配一个唯一的id
        @param domain: 查询域名 返回的域名Domain实例
        @type domainSummarys: list of DomainSummary
        @param domainSummarys:  查询域名列表,返回的 域名基本信息 列表
        @param location: 返回新域名的url, 只有新增域名时候才有, 
        @param cname: 返回新域名的cname
        '''
        super(ProcessResult, self).__init__(ret, msg, xCncRequestId)
        self.domainSummarys = domainSummarys
        self.location = location
        self.domain = domain
        self.cname = cname
    
    def getDomainSummarys(self):
        ''' 如果返回多个域名信息, 调用此方法获取'''
        return self.domainSummarys
    
    def getDomain(self):
        ''' 如果返回含有单个域名信息, 调用此方法获取'''
        return self.domain
   
    def getLocation(self):
        ''' 返回频道的location信息, 只有新增频道时候才有'''
        return self.location
    
    def getCname(self):
        ''' 返回频道的cname信息'''
        return self.cname
        
def xmlToSuccess(ret):
    ''' 返回xml 转换成 成功返回的ProcessResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION, X_CNC_CNAME
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    location = ret.getheader(X_CNC_LOCATION)
    cname = ret.getheader(X_CNC_CNAME)
    msg = util.getReturnXmlMsg(ret)
    return ProcessResult(ret.status, msg, xCncRequestId = requestId, location = location, cname = cname)
     
def xmlToFailure(ret):
    msg = util.getReturnXmlMsg(ret)
    return ProcessResult(ret.status, ret.reason + ":" + msg)
