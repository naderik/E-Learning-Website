from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from myapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'myapp/', include('myapp.urls')),
]
