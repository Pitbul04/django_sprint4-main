from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserEditForm


User = get_user_model()


def get_paginator(request, values):
    paginator = Paginator(values, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request):
    template_name = 'blog/index.html'

    posts = Post.objects.all().filter(
        Q(is_published=True)
        & Q(pub_date__lt=timezone.now())
        & Q(category__is_published=True)
        & Q(location__is_published=True)
    ).annotate(
        comment_count=Count(
            'comment',
            filter=(
                Q(comment__is_published=True)
            )
        )
    ).order_by(
        '-pub_date'
    )

    page_obj = get_paginator(request, posts)

    context = {
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def post_detail(request, id):
    template_name = 'blog/detail.html'

    post = get_object_or_404(
        Post,
        pk=id
    )

    if (
        (not request.user.is_authenticated or post.author != request.user)
        and (
            not post.is_published
            or post.pub_date > timezone.now()
            or not post.category.is_published
            or not post.location.is_published
        )
    ):
        raise Http404()

    form = CommentForm()
    comments = Comment.objects.filter(
        Q(post=post)
        & Q(is_published=True)
    ).select_related(
        'author'
    ).order_by(
        'created_at'
    )

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
    posts = Post.objects.filter(
        Q(is_published=True)
        & Q(pub_date__lt=timezone.now())
        & Q(category__pk=category.pk)
        & Q(category__pk=category.pk)
    ).annotate(
        comment_count=Count(
            'comment',
            filter=(
                Q(comment__is_published=True)
            )
        )
    ).order_by(
        '-pub_date'
    )

    page_obj = get_paginator(request, posts)

    context = {
        'category': category,
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def profile(request, username):
    template_name = 'blog/profile.html'

    profile = get_object_or_404(User, username=username)

    conditions = (
        Q(author__username=username)
    )
    if not request.user.is_authenticated or profile != request.user:
        conditions &= Q(pub_date__lt=timezone.now()) & Q(is_published=True) & \
            Q(category__is_published=True) & Q(location__is_published=True)

    posts = Post.objects.all().filter(
        conditions
    ).order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count(
            'comment',
            filter=(
                Q(comment__is_published=True)
            )
        )
    ).order_by(
        '-pub_date'
    )

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
def create_post(request, id=None):
    template_name = 'blog/create.html'

    post = None
    if id is not None:
        post = get_object_or_404(
            Post,
            pk=id,
        )

        if post.author != request.user:
            return redirect('blog:post_detail', id=id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        post = form.save(commit=False)
        if id is None:
            post.author = request.user
            form.save()
            return redirect('blog:profile', username=request.user)
        else:
            form.save()
            return redirect('blog:post_detail', id=id)

    context = {
        'form': form
    }

    return render(request, template_name, context)


@login_required
def delete_post(request, id):
    template_name = 'blog/create.html'

    post = get_object_or_404(
        Post,
        pk=id,
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
def add_comment(request, post_id, comment_id=None):
    template_name = 'blog/comment.html'

    post = get_object_or_404(Post, pk=post_id)

    comment = None
    if comment_id:
        comment = get_object_or_404(
            Comment,
            pk=comment_id,
            post=post,
            author=request.user
        )

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        comment = form.save(commit=False)
        if not comment_id:
            comment.author = request.user
            comment.post = post
        comment.save()

        return redirect('blog:post_detail', id=post_id)

    context = {
        'form': form,
        'comment': comment,
    }

    return render(request, template_name, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'

    post = get_object_or_404(
        Post,
        pk=post_id
    )
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post=post,
        author=request.user
    )

    if request.method == 'POST':
        comment.delete()

        return redirect('blog:post_detail', id=post_id)

    context = {
        'comment': comment
    }

    return render(request, template_name, context)
