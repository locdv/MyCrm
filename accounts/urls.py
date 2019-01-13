from django.urls import path
from accounts.views import (AccountsListView, CreateAccountView, UpdateAccountView, DeleteAccountView, DetailAccountView)
from . import views

app_name  = 'accounts'
urlpatterns = [
    path('', views.index, name='index'),
    path('list/', AccountsListView.as_view(), name='list'),
    path('create/', CreateAccountView.as_view(), name='create'),
    path('<int:pk>/update/', UpdateAccountView.as_view(), name='update'),
    path('<int:pk>/delete/', DeleteAccountView.as_view(), name='delete'),
    path('<int:pk>/detail/', DetailAccountView.as_view(), name='detail'),
]