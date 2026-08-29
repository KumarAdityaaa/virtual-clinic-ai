from django.contrib import admin
from django.urls import include, re_path

admin.autodiscover()

urlpatterns = [
    re_path(r'^', include('server.urls', namespace='server')),
    re_path(r'^ai/', include('ai.urls')),
    re_path(r'^admin/', admin.site.urls),
]