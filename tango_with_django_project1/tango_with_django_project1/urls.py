from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings ##settings allows us to access vars in our projs settings.py file
from registration.backends.simple.views import RegistrationView

class MyRegistration(RegistrationView):
    def get_success_url(self, request, user):
        return '/rango/'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django_project1.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
    url(r'^accounts/register/$', RegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),

    
)

if settings.DEBUG: ##Checks if the Django project is being run in DEBUG
	urlpatterns += patterns( ##if DEBUG is true, additional URL patterns are appended to the urlpatterns tuple
		'django.views.static',
		(r'^media/(?P<path>.*)', ##any file requested with a URL starting with media/
			'serve',
			{'document_root': settings.MEDIA_ROOT}), )