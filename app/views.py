from ctypes.wintypes import tagSIZE
from multiprocessing import context
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from app.forms import CommentForm, NewUserForm, SubscribeForm
from django.http import HttpResponseRedirect
from app.models import Comment, Post, Profile, Subscribe, Tag, WebsiteMeta
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth import login

# Create your views here.
def post_page(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post, parent=None)
    form = CommentForm()
    
    
    is_liked = False
    if post.likes.filter(id = request.user.id).exists():
        is_liked = True
    likes = post.likes.all().count()
    
    is_bookmarked = False
    if post.bookmarks.filter(id = request.user.id).exists():
        is_bookmarked = True
        
    if request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid:
            if request.POST.get('parent'):
                parent = Comment.objects.get(id=request.POST.get('parent'))
                if parent:
                    comment_reply = comment_form.save(commit=False)
                    comment_reply.parent = parent
                    comment_reply.post = post
                    comment_reply.save()
                    return redirect(reverse('post_page', kwargs={'slug': slug}))
            else:
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.save()
                return redirect(reverse('post_page', kwargs={'slug': slug}))
                #return HttpResponseRedirect(reverse("post_page", kwargs={"slug":slug}))
            
    if post.view_count is None:
        post.view_count = 1
    else:
        post.view_count += 1
    
    recent_posts = Post.objects.exclude(id = post.id).order_by("-last_updated")[0:3]
    top_authors = User.objects.annotate(number = Count('post')).filter(profile__isnull=False).order_by('-number')[0:3]
    tags = Tag.objects.all()
    related_posts = Post.objects.exclude(id = post.id).filter(author = post.author)[0:3]
    
    post.save()
    context = {'post': post,
               'form': form,
               'comments': comments,
               "is_bookmarked": is_bookmarked,
               "is_liked": is_liked,
               "likes": likes,
               "recent_posts": recent_posts,
               "top_authors": top_authors,
               "tags": tags,
               "related_posts": related_posts
               }
    return render(request, "app/post.html", context)

def index(request):
    
    website_info = None
    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]
        
    featured_blog = Post.objects.filter(is_featured = True).order_by('-last_updated')
    if featured_blog:
        featured_blog = featured_blog[0]
    
    top_posts = Post.objects.all().order_by('-view_count')[0:3]
    recent_posts = Post.objects.all().order_by('-last_updated')[0:3]
    subscribe_succesful = None
    
    if request.POST:
        subscribe_form = SubscribeForm(request.POST)
        if subscribe_form.is_valid():
            subscribe_form.save()
            request.session['subscribed'] = True
            subscribe_succesful = "Thank you for subscribing!"
    
    #posts = Post.objects.all()
    #context = {'posts': posts}
    subscribe_form = SubscribeForm()
    context = {
                'top_posts': top_posts,
                'recent_posts':  recent_posts,
                "subscribe_form": subscribe_form,
                "subscribe_succesful": subscribe_succesful,
                "featured_blog": featured_blog,
                "website_info": website_info,
                }
    return render(request, "app/index.html", context)

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    tags = Tag.objects.all()
    top_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[0:2]
    recent_posts = Post.objects.all().order_by('-last_updated')[0:3]
    featured_posts = Post.objects.filter(is_featured = True).order_by('-last_updated')
    if featured_posts:
        featured_posts = featured_posts[0:3]
    context = {'tag': tag, 
               'top_posts': top_posts, 
               'recent_posts': recent_posts, 
               'featured_posts': featured_posts, 
               'tags': tags
               }
    return render(request, "app/tag.html", context)

def author_page(request, slug):
    author = Profile.objects.get(slug=slug)
    tags = Tag.objects.all()
    top_posts = Post.objects.filter(author=author.user).order_by('-view_count')[0:2]
    recent_posts = Post.objects.filter(author=author.user).order_by('-last_updated')[0:3]
    featured_posts = Post.objects.filter(is_featured = True).order_by('-last_updated')
    top_authors = User.objects.annotate(number=Count('post')).order_by('number')[0:3]
    if featured_posts:
        featured_posts = featured_posts[0:3]
    context = {'author': author,
               'top_posts': top_posts, 
               'recent_posts': recent_posts, 
               'featured_posts': featured_posts, 
               'tags': tags,
               'top_authors': top_authors
               }
    return render(request, "app/author.html", context)

def search_posts(request):
    search_query=''
    if request.GET.get('q'):
        search_query=request.GET.get('q')
    print(f"Search: {search_query}")
    posts = Post.objects.filter(title__contains=search_query)
    context = {'posts': posts, 'search_query': search_query}
    return render(request, "app/search.html", context)

def about(request):
    website_info = None
    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]
        
    context = {'website_info': website_info}
    return render(request, "app/about.html", context)


def register_user(request):
    form = NewUserForm()
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")

    context = {'form': form}
    return render(request, "app/register.html", context)

def bookmark_post(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.bookmarks.filter(id = request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    return redirect(reverse('post_page', args=[str(slug)]))

def like_post(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id = request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(reverse('post_page', args=[str(slug)]))

def all_bookmarked_posts(request):
    if request.user.is_authenticated:
        all_bookmarked_posts = Post.objects.filter(bookmarks = request.user)
        context = {'all_bookmarked_posts': all_bookmarked_posts}
        return render(request, "app/all_bookmarked_posts.html", context)
    else:
        return redirect("/")

def all_posts(request):
    all_posts = Post.objects.all()
    context = {'all_posts': all_posts}
    return render(request, "app/all_posts.html", context)

def all_liked_posts(request):
    if request.user.is_authenticated:
        all_liked_posts = Post.objects.filter(likes = request.user)
        context = {'all_liked_posts': all_liked_posts}
        return render(request, "app/all_liked_posts.html", context)
    else:
        return redirect("/")