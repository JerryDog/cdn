__author__ = 'liujiahua'
#coding:utf8
import httplib
import json
from django.conf import settings

def getTokenFromKS(username, password):
    headers = {"Content-type":"application/json" }
    KEYSTONE = settings.KEYSTONE
    try:
        conn = httplib.HTTPConnection(KEYSTONE)
    except:
        return 'ConnError'
    params = '{"auth": {"passwordCredentials": {"username": "%s", "password": "%s"}}}' % (username, password)
    try:
        conn.request("POST","/v2.0/tokens", params, headers)
    except:
        return 'ConnError'
    response = conn.getresponse()
    data = response.read()
    dd = json.loads(data)
    try:
    	apitoken = dd['access']['token']['id']
    except:
	    return False
    user_id = dd['access']['user']['id']
    rq_headers = {"X-Auth-Token": "%s" % apitoken}
    conn.request('GET' , '/v3/users/%s/projects' % user_id, '', rq_headers)
    resp = conn.getresponse().read()
    result = json.loads(resp)
    project_list = []
    for p in result["projects"]:
	l = [p["name"], p["id"]]
	project_list.append(l)
    conn.close()
    return project_list
