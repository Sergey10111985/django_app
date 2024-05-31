from django.urls import path

from .views import ArticleListView, ArticleDetailView, LatestArticleFeed

app_name = 'blogapp'

urlpatterns = [
    path('article-list/', ArticleListView.as_view(), name='article-list'),
    path('article-detail/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('article/latest/feed/', LatestArticleFeed(), name='article-feed'),
]
