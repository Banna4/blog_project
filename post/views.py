from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


from django.http import Http404
from django.views import generic
from django.contrib import messages,redirects


from braces.views import SelectRelatedMixin

from . import models
from . import forms

from django.contrib.auth import get_user_model
User = get_user_model() 

class PostList(SelectRelatedMixin,generic.ListView):
    model = models.Post
    select_related = ('user','group')
    template_name = 'posts/post_list.html'

class UserPost(generic.ListView):
    model = models.Post
    template_name = 'posts/user_post_list.html'
    
    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))
        except User.DoesNotExist:
            raise Http404
        else:
             return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_user"] = self.post_user
        return context
    
class PostDetail(SelectRelatedMixin,generic.DetailView):
    model = models.Post
    select_related = ('user','group')
    template_name = 'posts/post_detail.html'
   
    

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))

class CreatePost(LoginRequiredMixin,SelectRelatedMixin,generic.CreateView):
    fields = ('message','group')
    model = models.Post
    template_name = 'posts/post_form.html'

    def form_valid(self, form):
        message = form.cleaned_data.get('message')
        existing_post = models.Post.objects.filter(user=self.request.user, message=message).first()
        if existing_post:
            existing_post.message = message  
            existing_post.save()
            messages.success(self.request, 'Post updated successfully.')
            return redirect(existing_post.get_absolute_url())  
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

class DeletePost(LoginRequiredMixin,SelectRelatedMixin,generic.DeleteView):
    model = models.Post
    select_related = ('user','group')
    success_url = reverse_lazy('posts:all')
    template_name = 'posts/post_confirm_delete.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id = self.request.user.id)

    def delete(self,*args,**kwargs):
        messages.success(self.request,'Post Deleted')
        return super().delete(*args,**kwargs)

        
    
    