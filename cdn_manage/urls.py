from django.conf.urls import patterns, include, url
from cdn_manage import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cdn.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^switch_project/$', views.switchProject, name='switch_project'),
    url(r'^index/$', views.index, name='index'),
    url(r'^domain_manage/$', views.domainManage, name='domain_manage'),
    url(r'^delete_domain/$', views.deleteDomain, name='delete_domain'),
    url(r'^edit_domain/(\d+)/$', views.editDomain, name='edit_domain'),
    url(r'^update_domain/(\d+)/$', views.updateDomain, name='update_domain'),
    url(r'^get_domain/(\d+)/$', views.getDomainStatus, name='get_domain'),
    url(r'^handler_cache/$', views.handlerCache, name='handler_cache'),
    url(r'^bandwidth/$', views.bandwidth, name='bandwidth'),
    url(r'^analytics_server/$', views.analyticsServer, name='analytics_server'),
    url(r'^log_download_list/$', views.logDownloadList, name='log_download_list'),
    url(r'^flow_value/$', views.flowValue, name='flow_value'),
    url(r'^bandwidth_csv/$', views.bandwidth_csv, name='bandwidth_csv'),
)
