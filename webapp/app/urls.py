from django.contrib import admin
from django.urls import path
from django.views.generic import base


urlpatterns = [
	path('', base.TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin-ctihq/', admin.site.urls),
]
