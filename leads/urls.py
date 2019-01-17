from django.urls import path
from leads.views import (LeadsListView, CreateLeadView, UpdateLeadView, DeleteLeadView, DetailLeadView)
from . import views

app_name  = 'leads'
urlpatterns = [
    path('', views.index, name='index'),
    path('list/', LeadsListView.as_view(), name='list'),
    path('create/', CreateLeadView.as_view(), name='create'),
    path('<int:pk>/update/', UpdateLeadView.as_view(), name='update'),
    path('<int:pk>/delete/', DeleteLeadView.as_view(), name='delete'),
    path('<int:pk>/detail/', DetailLeadView.as_view(), name='detail'),
]