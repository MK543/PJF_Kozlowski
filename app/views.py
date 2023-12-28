from django.urls import reverse
from django.shortcuts import redirect, render
from app.forms import CommentForm
from django.http import HttpResponseRedirect
from app.models import Comment, Post

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
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, "app/index.html", context)