from django.urls import path
from cases.views import (CasesListView, CreateCaseView, UpdateCaseView, DeleteCaseView, DetailCaseView)
from . import views

app_name  = 'cases'
urlpatterns = [
    path('', views.index, name='index'),
    path('list/', CasesListView.as_view(), name='list'),
    path('create/', CreateCaseView.as_view(), name='create'),
    path('<int:pk>/update/', UpdateCaseView.as_view(), name='update'),
    path('<int:pk>/delete/', DeleteCaseView.as_view(), name='delete'),
    path('<int:pk>/detail/', DetailCaseView.as_view(), name='detail'),
]