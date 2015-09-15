__author__ = 'liujiahua'
from models import Domain, CacheRules, AccessControl
import os

def getBool(str):
    if str == "1":
        return True
    else:
        return False


def saveDomainAndReturnId(domain_name,domain_cname,domain_type,
                          domain_status,disId, etag, project_id,
                          username, new_ip_list,test_url,ignore_param_req):
    domain = Domain(domain_name=domain_name,
                    domain_cname=domain_cname,
                    domain_type=domain_type,
                    domain_status=domain_status,
                    distribution_id=disId,
                    etag=etag,
                    project_id=project_id,
                    username=username,
                    ip_list=new_ip_list,
                    test_url=test_url,
                    ignore_param_req=ignore_param_req)
    domain.save()
    domain_id = Domain.objects.get(domain_name=domain_name).id
    return domain_id

def saveCacheRulesAndAcl(domain_id, cache_rules=None, acl=None):
    if cache_rules:
        cache_rules_list = cache_rules.split(';')
        for i in cache_rules_list:
            j = i.split(',')
            cache_type = j[0]
            is_cached = getBool(j[1])
            ignore_param_req = getBool(j[2])
            cache_time = j[3]
            cr = CacheRules(cache_type=cache_type,
                            is_cached=is_cached,
                            ignore_param_req=ignore_param_req,
                            cache_time=cache_time,
                            domain_id=domain_id)
            cr.save()

    if acl:
        acl_list = acl.split('%')
        for i in acl_list:
            j = i.split(',')
            url_type = j[0]
            white_list = j[1]
            black_list = j[2]
            deny_list = j[3]
            al = AccessControl(url_type=url_type,
                                white_list=white_list,
                                black_list=black_list,
                                deny_list=deny_list,
                                domain_id=domain_id)
            al.save()


def getJson4Xml(cache_rules=None, acl=None):
    json_str = {}
    json_str["CacheBehavior"] = [{"PathPattern":".*","NeverCache":"False","CacheControl":"Ignore","ForwardedValues":"False","CacheTime":"31536000"},]
    json_str["AclBehavior"] = []


    if cache_rules:
        cache_rules_list = cache_rules.split(';')
        for i in cache_rules_list:
            j = i.split(',')
            cache_type = j[0]
            is_cached = getBool(j[1])
            ignore_param_req = getBool(j[2])
            cache_time = j[3]
            unit_json = {
                "PathPattern": "%s" % cache_type,
                "NeverCache": "%s" % is_cached,
                "CacheControl": "Ignore",
                "ForwardedValues": "%s" % ignore_param_req,
                "CacheTime": "%s" % cache_time
            }
            json_str["CacheBehavior"].append(unit_json)

    if acl:
        acl_list = acl.split('%')
        for i in acl_list:
            j = i.split(',')
            url_type = j[0]
            white_list = j[1]
            black_list = j[2]
            deny_list = j[3]
            unit_json = {
                "PathPattern": "%s" % url_type,
                "WhiteList": "%s" % white_list,
                "BlackList": "%s" % black_list,
                "DenyIpList": "%s" % deny_list
            }
            json_str["AclBehavior"].append(unit_json)
    else:
        json_str.pop("AclBehavior")
    return  json_str

class LogObj(object):
    def __init__(self, url):
        self.url = url
        self.name = os.path.basename(url)