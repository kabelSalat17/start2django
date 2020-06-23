from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView,CreateView,UpdateView, DeleteView
from .models import Post
from django.db.models import Count
import hashlib
from .utils import sendTransaction
from datetime import timedelta
from django.utils import timezone

# Json responses
def posts(request):
    response = []
    posts = Post.objects.filter().order_by("-date_posted")
    for post in posts:
        response.append(
            {
                'title': post.title,
                'content': post.content,
                'date_posted': post.date_posted,
                'author': post.author.username,
                'hash': post.hash,
                'txId': post.txId
            }
        )
    return JsonResponse(response, safe=False)



def last1HBlogs(request):
    response = []
    actual_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
    one_hour_later = actual_hour + timedelta(hours=1)
    posts = Post.objects.filter(date_posted__range=(actual_hour, one_hour_later)).order_by("-date_posted")

    for post in posts:
        response.append(
            {
                'title': post.title,
                'content': post.content,
                'date_posted': post.date_posted,
                'author': post.author.username,
                'hash': post.hash,
                'txId': post.txId
            }
        )
    return JsonResponse(response, safe=False)


# <app>/<model>_<viewtype>.html #
###############################
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts' #context
    ordering = ['-date_posted']

    def get_context_data(self, **kwargs):
        if not self.request.session.get('LastIP'):
            self.request.session['LastIP'] = ''
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        context = super().get_context_data(**kwargs)
        if x_forwarded_for:
            if self.request.session['LastIP'] == '':
                context['is_Same'] = True
            else:
                ip = self.request.META.get('REMOTE_ADDR')
                is_Same = self.request.session['LastIP'] == ip
                self.request.session['LastIP'] = ip

                context['is_Same'] = is_Same
        else:
            print(self.request.session.get('LastIP'))
            if self.request.session['LastIP'] == '':
                context['is_Same'] = True
            else:
                print(self.request.session.get('LastIP'))
                ip = self.request.META.get('REMOTE_ADDR')
                is_Same = self.request.session['LastIP'] == ip
                self.request.session['LastIP'] = ip
                context['is_Same'] = is_Same
                print(self.request.session.get('LastIP'))
        return context

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        forbiddenword = "hack"
        if not forbiddenword in self.request.POST['content']:
            form.instance.author = self.request.user
            form.instance.hash = hashlib.sha256(((self.request.POST['content'])).encode('utf-8')).hexdigest()
            form.instance.txId = sendTransaction(form.instance.hash)
            return super().form_valid(form)
        else:
            return render(self.request, 'blog/post_form_forbidden.html', {})

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        forbiddenword = "hack"
        if not forbiddenword in self.request.POST['content']:
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            return render(self.request, 'blog/post_form_forbidden.html', {})
    #only author can update the post
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    #only author can delete the post
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class AdminPageView (LoginRequiredMixin,UserPassesTestMixin, ListView):
    model = Post
    template_name = "blog/admin-page.html"
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the user_posts
        context['user_posts'] = User.objects.annotate(total_posts=Count('post'))
        return context

    def test_func(self):
        return self.request.user.is_superuser

@login_required
def statistics(request):
    if request.GET:
        word = request.GET.get('word').capitalize()
        posts = Post.objects.filter(content__contains=word)
        times = len(posts)
        context={
            'times': times,
            'word': word
        }
    else:
        context={}
    return render(request, 'blog/statistics.html' , context)


