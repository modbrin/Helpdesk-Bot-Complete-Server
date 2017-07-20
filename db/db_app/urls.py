from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from db_app import views

urlpatterns = [
	url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^$', views.ArticleList.as_view(), name='article-list'),
    url(r'^contact_info/', views.ContactsDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^users/(?P<email>.+)/$', views.UserSearch.as_view()),
    url(r'^view_increment/(?P<pk>[0-9]+)/$', views.ViewIncrement.as_view()),
    url(r'^like_increment/(?P<pk>[0-9]+)/$', views.LikeIncrement.as_view()),
    url(r'^feedback/$', views.FeedbackList.as_view()),
    url(r'^feedback/(?P<pk>[0-9]+)/$', views.FeedbackDetail.as_view()),
    url(r'^invites/$', views.InviteList.as_view()),
    url(r'^invites/(?P<pk>[0-9]+)/$', views.InviteDetail.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', views.ArticleDetail.as_view(), name='article-detail'),
    url(r'^(?P<keyword>.+)/$', views.ArticleSearch.as_view()),
   
]

urlpatterns = format_suffix_patterns(urlpatterns)