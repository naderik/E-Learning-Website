from django.urls import path
from myapp import views


app_name = 'myapp'

urlpatterns = [
    path(r'', views.index, name='index'),
    path(r'about/', views.about, name='about'),
    path(r'<int:topic_id>/', views.detail, name='detail'),
    path(r'findcourses/', views.findcourses, name='findcourses'),
    path(r'place_order/', views.place_order, name='place_order'),
    path(r'submit_review/', views.submit_review, name='submit_review'),
    path(r'login/', views.user_login, name='login'),
    path(r'logout/', views.user_logout, name='logout'),
    path(r'myaccount/', views.myaccount, name='myaccount'),
    path(r'myorders', views.myorders, name='myorders'),
    path(r'register', views.register, name='register'),
    path(r'forgot_password/', views.forgot_password, name='forgot_password')
]
