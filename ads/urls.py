from django.urls import path
from ads.views import AdView, AdCreateView, AdDetailView, AdSearchView

urlpatterns = [
    path('list', AdView.as_view()),
    path('create', AdCreateView.as_view()),
    path('search', AdSearchView.as_view()),
    path('detail/ <int:pk>', AdDetailView.as_view()),
]
