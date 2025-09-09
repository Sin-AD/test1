from django.urls import path
from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_quote, name="add_quote"),
    path("vote/<int:pk>/", views.vote, name="vote"),
    path("top10/", views.top10, name="top10"),
    path('popular/', views.popular_quotes, name='popular_quotes'),
]
