from django.urls import path
from accounts.views import (AccountsListView)
from . import views

app_name  = 'accounts'
urlpatterns = [
    path('', views.index, name='index'),
    path('list/', AccountsListView.as_view(), name='list'),
]