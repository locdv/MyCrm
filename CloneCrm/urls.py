"""CloneCrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
   # path('', include('common.urls', namespace="Common")),
    path('', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls', namespace="accounts")),
    path('leads/', include('leads.urls', namespace="leads")),
    # path('contacts/', include('contacts.urls', namespace="contacts")),
    # path('opportunities/', include('opportunity.urls', namespace="opportunities")),
    # path('cases/', include('cases.urls', namespace="cases")),
]
