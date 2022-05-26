from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('connpass_member/', views.connpass_member, name='connpass_member'),
    path('youtube_subscriber/', views.youtube_subscriber, name='youtube_subscriber'),
    path('connpass_registration/', views.connpass_registration, name='connpass_registration'),
    path('tweet/', views.tweet, name='tweet'),
    path('qiita_post/', views.qiita_post, name='qiita_post'),
    path('qiita_organization_member/', views.qiita_organization_member, name='qiita_organization_member'),
    path('zenn_post/', views.zenn_post, name='zenn_post'),
    path('connpass_new_event/', views.connpass_new_event, name='connpass_new_event'),
    path('youtube_video/', views.youtube_video, name='youtube_video'),
    path('add_leader/', views.add_leader, name='add_leader'),
    path('zenn_member_all/', views.zenn_member_all, name='zenn_member_all'),
    path('do_all_job/', views.do_all_job, name='do_all_job'),
]