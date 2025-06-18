from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import DiscussionThread, Post
from .forms import PostForm
from core.notifications import create_bulk_notifications

User = get_user_model()


class ThreadDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = DiscussionThread
    template_name = "discussions/thread_detail.html"
    context_object_name = "thread"
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = self.object
        context["posts"] = thread.posts.filter(
            parent__isnull=True, is_active=True
        ).order_by("created_at")
        context["form"] = self.get_form()

        reply_to_pk_get = self.request.GET.get("reply_to")
        #  Add replying_to_post context if parent_post_instance was set in get_initial.
        #  Used for "Replying to X" message or to manage form action.
        if hasattr(self, "parent_post_instance") and self.parent_post_instance:
            context["replying_to_post"] = self.parent_post_instance
        elif reply_to_pk_get:  # If page loaded with reply_to
            try:
                context["replying_to_post"] = Post.objects.get(
                    pk=reply_to_pk_get, thread=self.object
                )
            except Post.DoesNotExist:
                pass
        return context

    def get_initial(self):
        initial = super().get_initial()
        reply_to_pk = self.request.GET.get("reply_to")
        quote = self.request.GET.get("quote")
        self.parent_post_instance = None

        if reply_to_pk:
            try:
                self.parent_post_instance = Post.objects.get(pk=reply_to_pk, thread=self.object)
                #  Hidden 'parent_id' in template's reply forms handles passing this.
                #  Main form for new top-level posts won't have parent_id.
                if quote == "true" and self.parent_post_instance:
                    quoted_text = "\n".join(
                        [f"> {line}" for line in self.parent_post_instance.body.splitlines()]
                    )
                    initial["body"] = f"{quoted_text}\n\n"
            except Post.DoesNotExist:
                messages.error(self.request, "Failed to find post for quote/reply.")
        return initial

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def _send_reply_notifications(self, post, replier):
        thread = post.thread
        #  Notify thread creator
        if thread.created_by and thread.created_by != replier:
            verb = (
                f"'{replier.username}' replied to your discussion thread "
                f"'{thread.title}'"
            )
            recipients_qs = User.objects.filter(pk=thread.created_by.pk)
            create_bulk_notifications(
                recipient_qs=recipients_qs,
                verb=verb,
                action_object=post,
                target=thread,
                actor=replier,
            )
        #  Notify parent post author (if different from thread creator and replier)
        if (
            post.parent
            and post.parent.author
            and post.parent.author != replier
            and post.parent.author != thread.created_by  # Avoid double notification
        ):
            verb = (
                f"'{replier.username}' replied to your post in thread "
                f"'{thread.title}'"
            )
            recipients_qs = User.objects.filter(pk=post.parent.author.pk)
            create_bulk_notifications(
                recipient_qs=recipients_qs,
                verb=verb,
                action_object=post,
                target=thread,  # Or target=post.parent for more specific link
                actor=replier,
            )

    def form_valid(self, form):
        post = form.save(commit=False)
        post.thread = self.object
        post.author = self.request.user

        parent_id = self.request.POST.get("parent_id")
        if parent_id:
            try:
                parent_post = Post.objects.get(id=int(parent_id), thread=self.object)
                if parent_post.parent is not None:
                    msg = "You cannot reply to a reply (nesting limit is one level)."
                    messages.error(self.request, msg)
                    form.add_error(None, msg)  # Add to form errors
                    return self.form_invalid(form)
                post.parent = parent_post
            except (Post.DoesNotExist, ValueError):
                msg = "Invalid parent post selected for reply."
                messages.error(self.request, msg)
                form.add_error(None, msg)  # Add to form non-field errors
                return self.form_invalid(form)

        try:
            post.full_clean()
            post.save()
            self._send_reply_notifications(post, replier=self.request.user)
            messages.success(self.request, "Your post has been added.")
        except ValidationError as e:
            error_list = []
            for field, errs in e.message_dict.items():
                for err_txt in errs:
                    field_name = field.capitalize() if field != "__all__" else ""
                    error_list.append(f"{field_name}: {err_txt}")
            messages.error(self.request, "Failed to save post: " + "; ".join(error_list))
            #  Populate form.errors from validation error for display
            for field, errors_list in e.message_dict.items():
                for error_message in errors_list:
                    form.add_error(field if field != "__all__" else None, error_message)
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("discussions:thread_detail", kwargs={"pk": self.object.pk})
