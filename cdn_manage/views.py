#coding:utf8
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from CdnApi import DiLianManager
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import Domain, CacheRules, AccessControl, TaskList
from django.conf import settings
from ks_auth import getTokenFromKS
import xml.etree.ElementTree as Etree
import os, sys, json, datetime, re
import utils
import uuid
import logging
from cname import CName
#reload(sys)
#sys.setdefaultencoding('utf8')
# Create your views here.

LOG = logging.getLogger(__name__)

SUCCESS = '$(document).ready(function(){$("#succContent").html("%s");' \
          '$("#alertSucc").fadeIn();setTimeout("closeAlert(\'#alertSucc\')", 2000);});'

FAIL = '$(document).ready(function(){$("#failContent").html("%s");' \
          '$("#alertFail").fadeIn();setTimeout("closeAlert(\'#alertFail\')", 3000);});'

JS_DICT = {
    "succ_create": SUCCESS % "<strong>成功！</strong>添加域名成功",

    "succ_delete": SUCCESS % "<strong>成功！</strong>删除域名成功",

    "succ_update": SUCCESS % "<strong>成功！</strong>更新域名成功",

    "fail_create": FAIL % "<strong>错误！</strong>添加域名失败，原因：%s",

    "fail_update": FAIL % "<strong>错误！</strong>更新域名失败，原因：%s",
}

def index(req):
    if not req.session.has_key("project_id"):
        return HttpResponseRedirect('/login/')
    else:
        project_id = req.session['project_id']
    project_list = req.session['project_list']
    username = req.COOKIES.get('username')
    return render_to_response('index.html', locals())

@csrf_exempt
def login(req):
    if req.method == "POST":
        username = req.POST.get('username')
        password = req.POST.get('password')
        if username == settings.SUPERADMIN and password == settings.SUPERADMIN_PD:
            project_list = [["超级管理员", "1234567890"]]
        else:
            project_list = getTokenFromKS(username, password)
        if project_list and project_list != 'ConnError':
            LOG.info('User %s login!' % username)
            req.session['project_id'] = project_list[0][1]
            req.session['project_list'] = project_list
            response = HttpResponseRedirect('/domain_manage/')
            response.set_cookie('username', username, settings.COOKIES_TIMEOUT)
            return response
        else:
            if project_list == 'ConnError':
                error = '链接超时'
                LOG.error('User %s login timeout!' % username)
            else:
                LOG.info('User %s login wrong password' % username)
                error = '用户名密码错误'
            return render_to_response('login.html', locals())
    else:
        return render_to_response('login.html')

def logout(req):
    if req.COOKIES.get('username'):
        LOG.info('User %s logout!' % req.COOKIES.get('username'))
        response = HttpResponseRedirect('/login/')
        response.delete_cookie('username')
        return response
    else:
        return render_to_response('login.html')

@csrf_exempt
def switchProject(req):
    if req.method == "POST":
        new_project_id = req.POST.get('new_project_id')
        req.session['project_id'] = new_project_id
        return HttpResponse('1')

@csrf_exempt
def domainManage(req):
    if req.method == "POST":
        if not req.session.has_key("session_id"):
            req.session['current_js'] = JS_DICT["fail_create"] % 'Null session_id'
            return HttpResponseRedirect('/domain_manage/')
        s_id = req.POST.get('session_id')
        if req.session["session_id"] != s_id:
            req.session['current_js'] = JS_DICT["fail_create"] % '请勿重复提交'
            return HttpResponseRedirect('/domain_manage/')
        else:
            del req.session["session_id"]
        cache_rules = req.POST.get('cache_rules', None)
        acl = req.POST.get('acl', None)
        domain_name = req.POST.get('domain_name').strip()
        domain_type = 'dilian'
        domain_status = 'InProgress'
        ip_str = req.POST.get('ip_list').strip()
        test_url = req.POST.get('test_url').strip()
        ignore_param_req = req.POST.get('ignore_param_req', False)
        json_str = utils.getJson4Xml(cache_rules, acl)
        json_str = json.dumps(json_str)
        random = uuid.uuid1()
        xml_name = '%s%s' % (domain_name, random)

        project_id = req.session['project_id']
        username = req.COOKIES.get('username')
        if ignore_param_req:
            noUse = 'True'
        else:
            noUse = 'False'
        LOG.info('Create Domain: /usr/bin/python %s %s %s \'%s\'  %s %s -J \'%s\'' % (
            settings.CREATE_XML_PATH, xml_name, domain_name, ip_str, test_url, noUse, json_str))
        try:
            os.system('/usr/bin/python %s %s %s \'%s\' %s %s -J \'%s\'' % (
                settings.CREATE_XML_PATH, xml_name, domain_name, ip_str, test_url, noUse, json_str))
        except Exception,e:
            LOG.error('Create Domain Failed because of os.system')
            req.session['current_js'] = JS_DICT["fail_create"] % e
            return HttpResponseRedirect('/domain_manage/')
        create_obj = DiLianManager(domain_name, ip_str, test_url, xml_name)
        status, reason, resp = create_obj.create()
        cname_obj = CName()
        if status == 201:
            req.session['current_js'] = JS_DICT["succ_create"]
            disId = Etree.fromstring(resp).find("Id").text
            ETag = create_obj.md5_file(settings.XML_PATH % xml_name)
            domain_cname = domain_name + settings.DINON_CNAME
            domain_id = utils.saveDomainAndReturnId(domain_name, domain_cname, domain_type,
                                                    domain_status, disId, ETag, project_id, username,
                                                    ip_str,test_url,ignore_param_req)
            utils.saveCacheRulesAndAcl(domain_id, cache_rules, acl)
            cname_obj.insert_cname(domain_name, disId)
            os.remove(settings.XML_PATH % xml_name)
        else:
            req.session['current_js'] = JS_DICT["fail_create"] % Etree.fromstring(resp).find("Message").text
        return HttpResponseRedirect('/domain_manage/')
    else:
        if not req.session.has_key("project_id"):
            return HttpResponseRedirect('/login/')
        else:
            project_id = req.session['project_id']
        if req.session.has_key("current_js"):
            current_js = req.session.get('current_js')
            del req.session["current_js"]
        session_id = '%s' % uuid.uuid1()
        req.session['session_id'] = session_id
        username = req.COOKIES.get('username')
        if username == settings.SUPERADMIN:
            domains = Domain.objects.all()
        else:
            domains = Domain.objects.filter(project_id=project_id)
        project_list = req.session['project_list']
        return render_to_response('domain_manage.html', locals())

@csrf_exempt
def deleteDomain(req):
    if req.method == 'POST':
        ids = req.POST.get('domain_ids')
        id_list = ids.split(',')
        username = req.COOKIES.get('username')
        for i in id_list:
            if i:
                id_obj = Domain.objects.filter(id=i)
                domain_name = id_obj[0].domain_name
                delete_obj = DiLianManager()
                cname_obj = CName()
                status, reason, resp = delete_obj.delete(id_obj[0].distribution_id, id_obj[0].etag)
                if status == 200:
                    update_time = datetime.datetime.now()
                    id_obj.update(domain_status='Deleted', update_time=update_time)
                    cname_obj.del_cname(domain_name)
                    LOG.info('User %s delete domain %s' % (username, domain_name))
                    result = 1
                else:
                    result = Etree.fromstring(resp).find("Message").text
    return HttpResponse(result)

@csrf_exempt
def editDomain(req,domain_id):
    if req.method == 'POST':
        session_id = '%s' % uuid.uuid1()
        req.session['edit_session_id'] = session_id
        domain = Domain.objects.get(id=domain_id)
        ip_list = domain.ip_list.split(',')
        if domain.ignore_param_req == 1:
            ignore_param_req = "checked"
        try:
            domain_cache = CacheRules.objects.filter(domain_id=domain_id)
        except:
            domain_cache = ''

        try:
            domain_acl = AccessControl.objects.filter(domain_id=domain_id)
        except:
            domain_acl = ''
        return render_to_response('edit_domain_modal.html', locals(),context_instance=RequestContext(req))

@csrf_exempt
def updateDomain(req, domain_id):
    if req.method == "POST":
        s_id = req.POST.get('edit_session_id')
        if not req.session.has_key("edit_session_id"):
            req.session['current_js'] = JS_DICT["fail_update"] % 'Null edit_session_id'
            return HttpResponseRedirect('/domain_manage/')
        if req.session["edit_session_id"] != s_id:
            req.session['current_js'] = JS_DICT["fail_update"] % '请勿重复提交'
            return HttpResponseRedirect('/domain_manage/')
        else:
            del req.session["edit_session_id"]
        cache_rules = req.POST.get('cache_rules', None)
        acl = req.POST.get('acl', None)
        domain_status = 'InProgress'
        ip_str = req.POST.get('ip_list').strip()
        ignore_param_req = req.POST.get('ignore_param_req', False)

        d = Domain.objects.get(id=domain_id)
        domain_name = d.domain_name
        test_url = d.test_url
        disId = d.distribution_id
        etag = d.etag
        if ignore_param_req:
            noUse = 'True'
        else:
            noUse = 'False'

        json_str = utils.getJson4Xml(cache_rules, acl)
        json_str = json.dumps(json_str)
        random = uuid.uuid1()
        xml_name = '%s%s' % (domain_name, random)
        LOG.info('Update Domain: /usr/bin/python %s %s %s \'%s\' %s %s -J \'%s\'' % (
            settings.CREATE_XML_PATH, xml_name, domain_name, ip_str, test_url, noUse, json_str))
        try:
            os.system('/usr/bin/python %s %s %s \'%s\' %s %s -J \'%s\'' % (
                settings.CREATE_XML_PATH, xml_name, domain_name, ip_str, test_url, noUse, json_str))
        except Exception,e:
            req.session['current_js'] = JS_DICT["fail_update"] % e
            return HttpResponseRedirect('/domain_manage/')
        update_obj = DiLianManager(domain_name, ip_str, test_url, xml_name)
        status, reason, resp, ETag = update_obj.config(disId, etag)
        if status == 200:
            req.session['current_js'] = JS_DICT["succ_update"]
            update_time = datetime.datetime.now()
            domain = Domain.objects.filter(id=domain_id)
            domain.update(domain_status=domain_status,
                          ip_list=ip_str,
                          ignore_param_req=ignore_param_req,
                          etag=ETag,
                          update_time=update_time)
            #delete acl and cache rules of this domain
            CacheRules.objects.filter(domain_id=domain_id).delete()
            AccessControl.objects.filter(domain_id=domain_id).delete()
            utils.saveCacheRulesAndAcl(domain_id, cache_rules, acl)
            os.remove(settings.XML_PATH % xml_name)
        else:
            req.session['current_js'] = JS_DICT["fail_update"] % Etree.fromstring(resp).find("Message").text
        session_id = '%s' % uuid.uuid1()
        req.session['edit_session_id'] = session_id
        return HttpResponseRedirect('/domain_manage/')

def getDomainStatus(req, domain_id):
    if req.method == 'GET':
        id_obj = Domain.objects.get(id=domain_id)
        delete_obj = DiLianManager()
        status, reason, resp, Etag = delete_obj.getDomain(id_obj.distribution_id)
        if status == 200:
            domain_status = Etree.fromstring(resp).find("Status").text
            domain = Domain.objects.filter(id=domain_id)
            domain.update(domain_status=domain_status)
            result = domain_status
        else:
            result = Etree.fromstring(resp).find("Message").text
        return HttpResponse(result)

@csrf_exempt
def handlerCache(req):
    if req.method == 'POST':
        url = req.POST.get('url')
        url_type = req.POST.get('type')
        username = req.COOKIES.get('username')
        project_id = req.session['project_id']
        ############ 判断是否是当前项目下的域名###########
        pattern = re.compile('http:\/\/(.*?)\/')
        re_result = pattern.findall(url)
        if username == settings.SUPERADMIN:
            domains = Domain.objects.all().values_list('domain_name')
        else:
            domains = Domain.objects.filter(project_id=project_id).values_list('domain_name')
        this_domains = []
        for d in domains:
            this_domains.append(d[0])
        for r in re_result:
            if r not in this_domains:
                result = '请不要操作该项目以外的域名'
                return HttpResponse(result)
        #################################################
        obj = DiLianManager()
        status, reason, resp, req_id = obj.cdnPushAndPrefetch(url_type, url)
        if status == 200:
            try:
                task_status = Etree.fromstring(resp).find("result").text
            except:
                task_status = Etree.fromstring(resp).find("message").text
            t = TaskList(task_id=req_id,
                         task_type=url_type,
                         project_id=project_id,
                         task_user=username,
                         task_content=url,
                         task_status=task_status)
            t.save()
            result = '成功!'
        else:
            result = Etree.fromstring(resp).find("Message").text
        return HttpResponse(result)
    else:
        if not req.session.has_key("project_id"):
            return HttpResponseRedirect('/login/')
        else:
            project_id = req.session['project_id']
        username = req.COOKIES.get('username')
        if username == settings.SUPERADMIN:
            tasks = TaskList.objects.all()
        else:
            tasks = TaskList.objects.filter(project_id=project_id)
        project_list = req.session['project_list']
        os.system('./cron_get_cache_status.py \&')
        return render_to_response("refresh_cache.html", locals())

@csrf_exempt
def bandwidth(req):
    if req.method == 'POST':
        domain_name = req.POST.get('domain_name')
        start = req.POST.get('start')
        end = req.POST.get('end')
        obj = DiLianManager()
        status, reason, resp = obj.bandwidthMap(domain_name, start, end)
        if status == 200:
            random = uuid.uuid1()
            path = settings.MONITOR_IMG % random
            os.system('rm -f %s/*' % os.path.dirname(path))
            with open(path, 'wb') as f:
                f.write(resp)
            result = os.path.basename(path)
        else:
            result = Etree.fromstring(resp).find("Message").text
        return HttpResponse(result)
    else:
        if not req.session.has_key("project_id"):
            return HttpResponseRedirect('/login/')
        else:
            project_id = req.session['project_id']
        username = req.COOKIES.get('username')
        if username == settings.SUPERADMIN:
            domains = Domain.objects.all()
        else:
            domains = Domain.objects.filter(project_id=project_id)
        project_list = req.session['project_list']
        return render_to_response("bandwidth.html", locals())

@csrf_exempt
def analyticsServer(req):
    if req.method == 'POST':
        domain_name = req.POST.get('domain_name')
        start = req.POST.get('start')
        end = req.POST.get('end')
        req_type = req.POST.get('req_type')
        obj = DiLianManager()
        status, reason, resp = obj.analyticsServer(domain_name, start, end, req_type)
        if status == 200:
            local = utils.getTempAndLocals(resp, req_type)
            info = [utils.InfoObj(l) for l in local["info"]]
            return render_to_response(local["template_name"], locals())
        else:
            result = Etree.fromstring(resp).find("Message").text
            return HttpResponse(result)
    else:
        if not req.session.has_key("project_id"):
            return HttpResponseRedirect('/login/')
        else:
            project_id = req.session['project_id']
        username = req.COOKIES.get('username')
        if username == settings.SUPERADMIN:
            domains = Domain.objects.all()
        else:
            domains = Domain.objects.filter(project_id=project_id)
        project_list = req.session['project_list']
        return render_to_response("analytics_server.html", locals())

@csrf_exempt
def logDownloadList(req):
    if req.method == 'POST':
        domain_name = req.POST.get('domain_name')
        start = req.POST.get('start')
        end = req.POST.get('end')
        obj = DiLianManager()
        status, reason, resp = obj.logDownloadList(domain_name, start, end)
        if status == 200:
            logs = [utils.LogObj(l.text) for l in Etree.fromstring(resp).findall('item')]
            return render_to_response("log_list.html", locals())
        else:
            result = status
            return HttpResponse(result)
    else:
        if not req.session.has_key("project_id"):
            return HttpResponseRedirect('/login/')
        else:
            project_id = req.session['project_id']
        username = req.COOKIES.get('username')
        if username == settings.SUPERADMIN:
            domains = Domain.objects.all()
        else:
            domains = Domain.objects.filter(project_id=project_id)
        project_list = req.session['project_list']
        return render_to_response("log_downLoad_list.html", locals())

@csrf_exempt
def flowValue(req):
    if req.method == 'POST':
        domain_name = req.POST.get('domain_name')
        start = req.POST.get('start')
        end = req.POST.get('end')
        obj = DiLianManager()
        status, reason, resp = obj.flowValue(domain_name, start, end)
        if status == 200:
            flows = [utils.FlowObj(l) for l in Etree.fromstring(resp).findall('date/Product/flow')]
            date = []
            flow = []
            for f in flows:
                date.append(f.date)
                flow.append(f.flow)
            str = ','.join(date) + ';' + ','.join(flow)
            result = str
        else:
            result = status
        return HttpResponse(result)
    else:
        if not req.session.has_key("project_id"):
            return HttpResponseRedirect('/login/')
        else:
            project_id = req.session['project_id']
        username = req.COOKIES.get('username')
        if username == settings.SUPERADMIN:
            domains = Domain.objects.all()
        else:
            domains = Domain.objects.filter(project_id=project_id)
        all_domains = ''
        for d in domains:
            all_domains = all_domains + ',' +d.domain_name
        project_list = req.session['project_list']
        return render_to_response("flow_value.html", locals())