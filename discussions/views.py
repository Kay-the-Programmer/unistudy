from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin # To handle forms within DetailView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import DiscussionThread, Post
from .forms import PostForm # Assume PostForm will be created in discussions/forms.py

class ThreadDetailView(LoginRequiredMixin, FormMixin, DetailView): # Added FormMixin and LoginRequiredMixin
    model = DiscussionThread
    template_name = 'discussions/thread_detail.html'
    context_object_name = 'thread'
    form_class = PostForm # Form for new posts/replies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = self.object
        # Get top-level posts (not replies)
        context['posts'] = thread.posts.filter(parent__isnull=True, is_active=True).order_by('created_at')
        # The form for new post/reply will be added by FormMixin's context processing
        # We might want to pass initial data to the form, e.g., thread_id
        context['form'] = self.get_form() # Ensure form is in context
        return context

    def post(self, request, *args, **kwargs):
        # This method handles form submission for new posts/replies
        if not request.user.is_authenticated:
            return redirect('accounts:login') # Should be handled by LoginRequiredMixin usually

        self.object = self.get_object() # Get the thread object
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.thread = self.object
        post.author = self.request.user

        # Check if 'parent_id' is in form.data to determine if it's a reply
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            try:
                parent_post = Post.objects.get(id=int(parent_id), thread=self.object)
                # Check nesting level before assigning parent
                if parent_post.parent is not None:
                    messages.error(self.request, "You cannot reply to a reply (nesting limit is one level).")
                    # Redirect or render form with error instead of raising ValidationError directly here
                    return self.form_invalid(form) # Or redirect to avoid re-post on refresh
                post.parent = parent_post
            except (Post.DoesNotExist, ValueError):
                messages.error(self.request, "Invalid parent post selected for reply.")
                return self.form_invalid(form) # Or redirect

        try:
            post.full_clean() # Explicitly call clean method from model
            post.save()
            messages.success(self.request, "Your post has been added.")
        except ValidationError as e:
            # Add model validation errors to the form or messages framework
            # This is a basic way to handle it.
            error_list = []
            for field, errors in e.message_dict.items():
                for error_text in errors:
                    error_list.append(f"{field.capitalize() if field != '__all__' else ''}: {error_text}")
            messages.error(self.request, "Failed to save post: " + "; ".join(error_list))
            return self.form_invalid(form) # Render the form again with errors

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('discussions:thread_detail', kwargs={'pk': self.object.pk})

    # form_invalid is inherited from FormMixin, it re-renders the template with the form and errors.
    # We might want to add messages.error(self.request, "Please correct the errors below.") here too.

# Note: Need to create discussions/forms.py with PostForm
# PostForm should likely only include 'body' and handle 'parent_id' via a hidden input in template.
