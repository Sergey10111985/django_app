from django.views.generic import ListView

from blogapp.models import Article


class ArticleListView(ListView):
    model = Article
    context_object_name = 'articles'
    queryset = (
        Article.objects
        .select_related('author')
        .select_related('category')
        .prefetch_related('tags')
    )