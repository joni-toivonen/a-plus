from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    url(r'^login/$', views.login,
        name="login"),
    url(r'^logout/$', auth_views.logout,
        { "template_name": "userprofile/logout.html" },
        name="logout"),
    url(r'^privacy-policy/$', views.PrivacyPolicyView.as_view(),
        name="privacy_policy"),
]
