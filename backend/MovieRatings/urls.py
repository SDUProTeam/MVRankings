"""MovieRatings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import include, url
from django.views.generic.base import TemplateView
from django.http import HttpResponse
import api.views as views
import recsys.views as recviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/search', view=views.search),
    path('api/fusion', view=views.search_fusion),
    path('api/movie/<int:id>/', view=views.movie),
    path('api/signin', view=views.signin),
    path('api/signup', view=views.signup),
    path('api/history', view=views.history),
    path('api/comment', view=views.add_comment),
    path('api/question', view=views.question),
    path('api/recommend', view=recviews.recommend)
]
