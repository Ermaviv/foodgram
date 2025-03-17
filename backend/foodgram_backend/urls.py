from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [

    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]

# handler403 = 'pages.views.csrf_failure'
# handler404 = 'pages.views.page_not_found'
# handler500 = 'pages.views.server_error'
