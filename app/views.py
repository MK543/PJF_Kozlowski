from django.urls import reverse
from django.shortcuts import redirect, render
from app.forms import CommentForm, SubscribeForm
from django.http import HttpResponseRedirect
from app.models import Comment, Post, Profile, Subscribe, Tag, WebsiteMeta
from django.contrib.auth.models import User
from django.db.models import Count

# Create your views here.
def post_page(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post, parent=None)
    form = CommentForm()
    
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
        
    post.save()
    context = {'post': post, 'form': form, 'comments': comments}
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
                "website_info": website_info
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