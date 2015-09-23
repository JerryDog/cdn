#/usr/bin/python
__author__ = 'liujiahua'
import MySQLdb
import xml.etree.ElementTree as Etree
import httplib
import hashlib

def prefetchProgress(req_id):
        type = 'POST'
        rq_url = "/DnionCloud/cdnPrefetch/progress?RequestId=%s" % req_id
        rq_body = ''
        response, resp = req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        return (status, reason, resp)

def pushProgress(req_id):
        type = 'POST'
        rq_url = "/DnionCloud/cdnPush/progress?RequestId=%s" % req_id
        rq_body = ''
        response, resp = req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        return (status, reason, resp)

def hex_digest(algrithom, data_list):
        digest = None
        try:
            hash_obj = hashlib.new(algrithom)
            for item in data_list:
                    hash_obj.update(item)
            digest = hash_obj.hexdigest()
        except Exception, e:
            return None
        return digest

def calcSignature(algorithm, method, url, body=''):
        body_digest = hex_digest(algorithm, body)
        data_list = []
        data_list.append(method + '\n')
        data_list.append('1234567890abcdef' + '\n')
        data_list.append(url + '\n')
        data_list.append(body_digest + '\n')
        data_list.append('accesskeyidexample6/20150714233600/xnop015/dnioncloud')
        signature = hex_digest(algorithm, data_list)
        return signature

def req(type, rq_url, rq_body='', ETag=None):
        signature = calcSignature('md5', type, rq_url, rq_body)
        authorization = 'Algorithm=md5,Credential=' + 'accesskeyidexample6/20150714233600/xnop015/dnioncloud'  \
                        + ',Signature='+ signature
        rq_headers = {"Content-type": "application/xml", "Accept": "text/plain" ,"If-Match":ETag }
        rq_headers['Authorization'] = authorization
        try:
            httpClient = httplib.HTTPConnection('dcloud.dnion.com')
            httpClient.request(type , rq_url, rq_body, rq_headers)
            response = httpClient.getresponse()
            return (response, response.read())
        except Exception,e:
            print 'can not connect to dilian %s' % e
        finally:
            if httpClient:
                httpClient.close()

def get_cache_status():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from cdn.cdn_manage_tasklist')
    tasks = cur.fetchall()
    for i in tasks:
        if i["task_status"] != 'success' and i["task_status"] != 'failure':
            if i["task_type"] == '2':
                status, reason, resp = prefetchProgress(i["task_id"])
            else:
                status, reason, resp = pushProgress(i["task_id"])
            try:
                new_task_status = Etree.fromstring(resp).find("Status").text
            except:
                for i in Etree.fromstring(resp).findall("Item/Status"):
                    if i.text == 'failed':
                        new_task_status = 'failure'
                        break
                    else:
                        new_task_status = i.text
            if new_task_status != i["task_status"]:
                #update status
                cur.execute('update cdn.cdn_manage_tasklist set task_status="%s" where task_id="%s"'
                            % (new_task_status, i["task_id"]))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    get_cache_status()
