from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import PostForm, CommentForm, UserEditForm
from .models import Post, Category, Comment



User = get_user_model()


def get_paginator(request, values):
    paginator = Paginator(values, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request):
    template_name = 'blog/index.html'

    posts = Post.objects.filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True,
        location__is_published=True
    ).annotate(
        comment_count=Count(
            'comment',
            filter=Q(comment__is_published=True)
        )
    ).order_by('-pub_date')

    page_obj = get_paginator(request, posts)

    context = {
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def post_detail(request, post_pk):
    template_name = 'blog/detail.html'

    post = get_object_or_404(Post, pk=post_pk)

    if (
        not request.user.is_authenticated
        or post.author != request.user
    ):
        post = get_object_or_404(
            Post,
            pk=post_pk,
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True,
            location__is_published=True
        )

    form = CommentForm()
    comments = post.comment_set.filter(
        is_published=True
    ).select_related('author').order_by('created_at')

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    posts = category.post_set.filter(
        is_published=True,
        pub_date__lt=timezone.now()
    ).annotate(
        comment_count=Count(
            'comment',
            filter=Q(comment__is_published=True)
        )
    ).order_by('-pub_date')

    page_obj = get_paginator(request, posts)

    context = {
        'category': category,
        'page_obj': page_obj
    }

    return render(request, template_name, context)


@login_required
def create_post(request, post_pk=None):
    template_name = 'blog/create.html'

    post = None
    if post_pk is not None:
        post = get_object_or_404(
            Post,
            pk=post_pk,
        )

        if post.author != request.user:
            return redirect('blog:post_detail', post_pk=post_pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        post = form.save(commit=False)
        if post_pk is None:
            post.author = request.user
            form.save()
            return redirect('blog:profile', username=request.user)
        else:
            form.save()
            return redirect('blog:post_detail', post_pk=post_pk)

    context = {
        'form': form
    }

    return render(request, template_name, context)


def profile(request, username):
    template_name = 'blog/profile.html'

    profile = get_object_or_404(User, username=username)

    conditions = Q(author__username=username)

    if not request.user.is_authenticated or profile != request.user:
        conditions &= Q(
            pub_date__lt=timezone.now(),
            is_published=True,
            category__is_published=True,
            location__is_published=True
        )

    posts = Post.objects.filter(conditions).annotate(
        comment_count=Count(
            'comment',
            filter=Q(comment__is_published=True)
        )
    ).order_by('-pub_date')

    page_obj = get_paginator(request, posts)

    context = {
        'profile': profile,
        'page_obj': page_obj,
    }

    return render(request, template_name, context)


@login_required
def edit_profile(request):
    template_name = 'blog/user.html'

    form = UserEditForm(request.POST or None, instance=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)

    context = {
        'form': form,
    }

    return render(request, template_name, context)


@login_required
def delete_post(request, post_pk):
    template_name = 'blog/create.html'

    post = get_object_or_404(
        Post,
        pk=post_pk,
        author=request.user,
    )

    form = PostForm(instance=post)

    if request.method == 'POST':
        post.delete()

        return redirect('blog:profile', username=request.user)

    context = {
        'form': form
    }

    return render(request, template_name, context)


@login_required
def add_comment(request, post_pk, comment_pk=None):
    template_name = 'blog/comment.html'

    post = get_object_or_404(Post, pk=post_pk)

    comment = None
    if comment_pk:
        comment = get_object_or_404(
            Comment,
            pk=comment_pk,
            post=post,
            author=request.user
        )

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        comment = form.save(commit=False)
        if not comment_pk:
            comment.author = request.user
            comment.post = post
        comment.save()

        return redirect('blog:post_detail', post_pk=post_pk)

    context = {
        'form': form,
        'comment': comment,
    }

    return render(request, template_name, context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    template_name = 'blog/comment.html'

    post = get_object_or_404(
        Post,
        pk=post_pk
    )
    comment = get_object_or_404(
        Comment,
        pk=comment_pk,
        post=post,
        author=request.user
    )

    if request.method == 'POST':
        comment.delete()

        return redirect('blog:post_detail', post_pk=post_pk)

    context = {
        'comment': comment
    }

    return render(request, template_name, context)
