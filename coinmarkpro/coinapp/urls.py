from django.contrib import admin
from django.urls import path
from coinapp import *
from . import views

urlpatterns = [
    path("",views.index, name="home"),
    path('api/taskmanager/start_scraping/', views.StartScrapingView.as_view(), name='start-scraping'),
    path('api/taskmanager/scraping_status/<str:job_id>/', views.ScrapingStatusView.as_view(), name='scraping-status'),
    path('api/taskmanager/display/<str:job_id>/', views.DisplayData.as_view(), name='display-data'),
     path('api/taskmanager/tor/', views.StartScrapingView.as_view(), name='scrape-tor'),
]   