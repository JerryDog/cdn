__author__ = 'Administrator'
from django.http import HttpResponseRedirect

class QtsAuthenticationMiddleware(object):
    def process_request(self, request):
        if request.path != '/login/':
             if "username" in request.COOKIES:
                 pass
             else:
                 return HttpResponseRedirect("/login/")
