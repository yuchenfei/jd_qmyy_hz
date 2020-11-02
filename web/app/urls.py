from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signin/', views.signin, name="signin"),
    path('signout/', views.signout, name="signout"),
    path('help_home/', views.help_home, name="help_home"),
    path('help_cbd/', views.help_cbd, name="help_cbd"),
    path('help_tm/', views.help_tm, name="help_tm"),
    path('help_star/', views.help_star, name="help_star"),
]