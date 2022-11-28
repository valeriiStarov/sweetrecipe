from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

from sweetrecipe import settings
from recipe.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipe.urls')),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), # Для отображения media при DEBUG
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), # Для отображения media при DEBUG
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
handler404 = pageNotFound
handler403 = Forbidden