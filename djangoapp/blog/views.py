from typing import Any, Dict
from django import http
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import ListView

PER_PAGE = 9

class PostListView(ListView):   
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    ordering = '-pk'    
    queryset = Post.objManager.get_published()  
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Home - ',
        })
        return context
    
def created_by(request, author_pk):
    user = User.objects.filter(pk=author_pk).first()

    if user is None:
        raise Http404    
    posts = (
        Post.objManager.get_published()
        .filter(created_by__pk=author_pk)
    )
    user_full_name = user.username

    if user.first_name:
        user_full_name = f'{user.first_name} {user.last_name}'

    page_title = 'Posts de ' + user_full_name + ' - '

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'page_title': page_title,
        }
    )

class CreatedByListView(PostListView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._temp_context: dict[str, Any] = {}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self._temp_context['user']
        user_full_name = user.username

        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        page_title = 'Posts de ' + user_full_name + ' - '

        ctx.update({
            'page_title': page_title,
        })

        return ctx

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(created_by__pk=self._temp_context['user'].pk)
        return  qs

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            author_pk = self.kwargs.get('author_pk')
            user = User.objects.filter(pk=author_pk).first()

            if user is None:
                raise Http404()
            self._temp_context.update({
                'author_pk': author_pk,
                'user': user,
            })

            return super().get(request, *args, **kwargs)
    
def category(request, slug):
    posts = (
        Post.objManager.get_published()
        .filter(category__slug=slug)
    )      

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if len(posts) == 0:
        raise Http404()
    page_title = f'{page_obj[0].category.name} - Categoria -'

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'page_title': page_title,
        }
    )

def tag(request, slug):
    posts = (
        Post.objManager.get_published()
        .filter(tags__slug=slug)
    )
    
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if len(posts) == 0:
        raise Http404()
    page_title = f'{page_obj[0].tags.first().name} - Tag - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'page_title': page_title,
        }
    )

def search(request):
    search_value = request.GET.get('search', '').strip()
    posts = (
        Post.objManager.get_published()
        .filter(
            Q(title__icontains=search_value) |
            Q(excerpt__icontains=search_value) |
            Q(content__icontains=search_value)
        )[:PER_PAGE]
    )

    page_title = f'{ search_value[:30] } - Search - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': posts,
            'search_value': search,
            'page_title': page_title,
        }
    )

def page(request, slug):
    page_obj = ( 
            Page.objects
            .filter(is_published=True)         
            .filter(slug=slug)
            .first()
        )
    
    if page_obj is None:
        raise Http404()
    page_title = f'{page_obj.title} - Página - '

    return render(
        request,
        'blog/pages/page.html',
        {
            'page': page_obj,
            'page_title': page_title,
        }
    )

def post(request, slug):
    post_obj = ( 
            Post.objManager.get_published() 
            .filter(slug=slug)
            .first()
        )
    
    if post_obj is None:
        raise Http404()
    page_title = f'{post_obj.title} - Post - '

    return render(
        request,
        'blog/pages/post.html',
        {
            'post': post_obj,
            'page_title': page_title,
        }
    )


