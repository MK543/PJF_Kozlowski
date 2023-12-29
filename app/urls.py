"""
URL configuration for blogapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('post/<slug:slug>', views.post_page, name='post_page'),
    path('', views.index, name='index'),
    path('tag/<slug:slug>', views.tag_page, name='tag_page'),
    path('author/<slug:slug>', views.author_page, name='author_page'),
    path('search/', views.search_posts, name='search_page'),
    path('about/', views.about, name='about'),
    path('accounts/register', views.register_user, name='register'),
    path('bookmark_post/<slug:slug>', views.bookmark_post, name='bookmark'),
    path('like_post/<slug:slug>', views.like_post, name='like'),
    path('all_bookmarked_posts/', views.all_bookmarked_posts, name='all_bookmarked_posts'),
    path('all_posts/', views.all_posts, name='all_posts'),
    path('all_liked_posts/', views.all_liked_posts, name='all_liked_posts'),
]
