from django.urls import path
from .views import ThreadDetailView

app_name = "discussions"

urlpatterns = [
    path("thread/<int:pk>/", ThreadDetailView.as_view(), name="thread_detail"),
    # URLs for creating posts/replies are handled within ThreadDetailView's POST method for now.
    # If separate views were used:
    # path('thread/<int:thread_pk>/post/new/', PostCreateView.as_view(), name='post_create'),
    # path('post/<int:parent_pk>/reply/new/', ReplyCreateView.as_view(), name='reply_create'),
]
