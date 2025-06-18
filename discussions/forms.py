from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    # parent_id will be a hidden field in the template, not part of the visible form
    # It will be populated by JavaScript when a user clicks a "reply" button.

    class Meta:
        model = Post
        fields = ["body"]  # User only directly enters the body
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Write your post or reply..."}
            ),
        }

    # No need to include 'thread' or 'author' as they will be set in the view.
    # 'parent' is also handled in the view based on 'parent_id' from POST data.
