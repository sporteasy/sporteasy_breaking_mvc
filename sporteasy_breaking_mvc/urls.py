from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    'sporteasy_breaking_mvc.apps.sites.frontend.views',
    url(r'^$', 'index', name='home'),
    url(r'^add-match/(?P<champ_id>\d+)/$', 'add_match', name='add_match'),
)
