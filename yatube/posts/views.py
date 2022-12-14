from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import PostForm, CommentForm


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all()
    paginator = Paginator(posts, settings.LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    post_count = author_posts.count()
    paginator = Paginator(author_posts, settings.LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user.id,
            author=author.id
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'post_count': post_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author_posts = Post.objects.filter(author=post.author).count()
    group_name = post.group
    form = CommentForm()
    template = 'posts/post_detail.html'
    comments = post.comments.filter(post=post_id)
    context = {
        'title': group_name,
        'post': post,
        'author_posts': author_posts,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST,
        files=request.FILES or None,
    )
    template = 'posts/create_post.html'
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    is_edit = True
    if post.author.username != request.user.username:
        return redirect('posts:post_detail', post_id=post.id)
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {'form': form, 'post': post, 'is_edit': is_edit}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post, settings.LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author_obj = get_object_or_404(User, username=username)
    user_obj = request.user
    if author_obj != user_obj:
        Follow.objects.get_or_create(
            user=user_obj, author=author_obj
        )
    return redirect('posts:profile', username=author_obj.username)


@login_required
def profile_unfollow(request, username):
    author_obj = get_object_or_404(User, username=username)
    user_obj = request.user
    Follow.objects.filter(
        user=user_obj,
        author=author_obj
    ).delete()
    return redirect('posts:profile', username=author_obj.username)
