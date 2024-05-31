from django.views.generic import ListView, DetailView
from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy

from blogapp.models import Article


class ArticleListView(ListView):
    model = Article
    context_object_name = 'articles'
    queryset = (
        Article.objects
        .select_related('author')
        .select_related('category')
        .prefetch_related('tags')
        .filter(pub_date__isnull=False)
        .order_by("-pub_date")
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticleFeed(Feed):
    title = "Latest Article Feed"
    description = "Updates on changes and addition blog Articles"

    link = reverse_lazy('blogapp:article-list')

    def items(self):
        return (
            Article.objects
            .select_related('author')
            .select_related('category')
            .prefetch_related('tags')
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:100]

