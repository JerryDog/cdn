from celery import task, platforms
from models import TaskList
from CdnApi import DiLianManager
import xml.etree.ElementTree as Etree

platforms.C_FORCE_ROOT = True

@task
def getTaskStatus():
    all_tasks = TaskList.objects.all()
    obj = DiLianManager()
    for t in all_tasks:
        if t.task_status != 'success' and t.task_status != 'failure':
            if t.task_type == '2':
                status, reason, resp = obj.prefetchProgress(t.task_id)
            else:
                status, reason, resp = obj.pushProgress(t.task_id)
            try:
                new_task_status = Etree.fromstring(resp).find("Status").text
            except:
                for i in Etree.fromstring(resp).findall("Item/Status"):
                    if i.text != 'success':
                        new_task_status = 'failure'
                        break
                    else:
                        new_task_status = 'success'
            if new_task_status != t.task_status:
                task_obj = TaskList.objects.filter(task_id=t.task_id)
                task_obj.update(task_status=new_task_status)
