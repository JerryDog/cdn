# -*- coding: utf-8 -*-
'''
Created on 2013-1-10

@author: sinlangxmu@gmail.com
'''

if __name__ == '__main__':
    pass

import hashlib, urlparse, httplib, time, logging, base64, hmac, sha, urllib, os
import sys
import logging, ConfigParser, xml.dom as dom, xml.dom.minidom as minidom

from rfc3339 import rfc3339
from datetime import datetime

X_CNC_REQUEST_ID = 'x-cnc-request-id'

def encodePassword(pw):
    ''' 此处的 password需要 先经过base64加密 '''
    return base64.b64encode(pw)

def hashPassword(data, key):
    ''' api 中密码使用的hash算法 '''
    h = hmac.new(key, data, sha)
    return base64.encodestring(h.digest()).strip()

def httpReqeust(url, body = None, headers = None, method = "POST"):
    ''' 进行http请求 
    :rtype : object
    '''
    urlList = urlparse.urlparse(url)
    
    logging.debug("url: " + str(urlList));
    logging.debug("header:" + str(headers))
    logging.debug("method: " + method);
    logging.debug("body: " + body)
    if not urlList.scheme or not urlList.netloc or not urlList.path:
        raise Exception("url 格式出错, " + url)
    if urlList.scheme == 'https':
        con = httplib.HTTPSConnection(urlList.netloc, timeout = 15)
    else:
        con = httplib.HTTPConnection(urlList.netloc, timeout = 15)
    path = urlList.path;
    
    if urlList.query:
        path = path + "?" + urlList.query
    con.request(method, path, body, headers)
    res =  con.getresponse()
    logging.debug("status:" + str(res.status) + ", reason:" + res.reason)
    return res

def getRFC3339Time(dateStr):
    date_object = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S");
    return rfc3339(date_object);

def parseRFC1123Time(dateStr):
    isoFormat = "%a, %d %b %Y %H:%M:%S %Z"
    return datetime.strptime(dateStr, isoFormat)

def getRFCTime():
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime());

def getCnCTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def getText(node):
    ''' get text conent of node '''
    rc = []
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def getChildNode(node, name):
    ''' 获取孩子节点 '''
    for node in node.childNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == name:
            return node
        
def getChildNodeList(node, name):
    ''' 获取孩子节点 '''
    resultList = []
    for node in node.childNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == name:
            resultList.append(node)
    
    return resultList
            
def getChildNodeText(node, name):
    child = getChildNode(node, name)
    if child is not None:
        return getText(child)

def addElement(doc, parent, name, text = None):
    ''' private function, add a element to the xml '''
    e = doc.createElement(name)
    if text:
        e.appendChild(doc.createTextNode(str(text)))
    parent.appendChild(e)
    return e;

class BaseResult(object):
    def __init__(self, ret, msg, xCncRequestId = None):
        self.ret = ret
        self.msg= msg
        self.xCncRequestId = xCncRequestId
        
    def isSuccess(self):
        ''' 判断请求是否成功'''
        return self.ret == 0
    
    def getRet(self):
        ''' 获取返回代码'''
        return self.ret
    
    def getMsg(self):
        ''' 获取返回消息'''
        return self.msg
    
    def getXCncRequestId(self):
        ''' 返回请求的编号 '''
        return self.xCncRequestId
    
def xmlToDefaultFailure(ret):
    ''' 返回xml 转换成 带错误信息的BaseResult对象'''
    msg = getReturnXmlMsg(ret)
    return BaseResult(ret.status, ret.reason + ":" + msg)

def xmlToDefaultSuccess(ret):
    ''' 返回xml 转换成 成功返回的ProcessResult对象'''
    global X_CNC_REQUEST_ID
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    
    msg= getReturnXmlMsg(ret)
    
    return BaseResult(0, msg, xCncRequestId = requestId)
    
def getReturnXmlMsg(ret):
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    xmlString = str(xmlString)
    doc = minidom.parseString(xmlString)
    responseNode = getChildNode(doc, 'response')
    msg = getChildNodeText(responseNode, 'message')
    return msg
