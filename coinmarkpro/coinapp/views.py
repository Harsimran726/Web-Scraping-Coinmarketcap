from django.shortcuts import render
import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import *
from .tasks import scrape_coin  # Import the task
from uuid import uuid4
from celery.result import AsyncResult

class StartScrapingView(APIView):
    def post(self, request):
        """
        Starts a scraping job for 'TOR'.
        """
        job_id = str(uuid4())  # Generate a unique job ID
        tasks = [scrape_coin.delay('TOR')]  # Start a task for 'TOR'
        return Response({'job_id': job_id}, status=status.HTTP_202_ACCEPTED) 


class ScrapingStatusView(APIView):
    def get(self, request, job_id):
        """
        Returns the status of the scraping job.
        """
        task = AsyncResult(job_id)
        data = []
        if task.ready():
            print("Task ready")
            try:
                data.append({'coin': 'TOR', 'output': json.loads(task.result)})
            except json.JSONDecodeError:
                data.append({'coin': 'TOR', 'output': 'Error: Failed to decode JSON'})
        else:
            print("NOt ready")
            data.append({'coin': 'TOR', 'output': 'In progress'})
        print("DAata : -",data)
        return Response({'job_id': job_id, 'tasks': data}, status=status.HTTP_200_OK)


class DisplayData(APIView):
    def get(self, request, job_id):
        """
        Retrieves scraped data and renders it in a template.
        """
        task = AsyncResult(job_id)
        print("Task :- ",task)
        data = []
        print("Data before :- ",data)
        if task.ready():
            print("Ready")
            try:
                data.append({'coin': 'TOR', 'output': json.loads(task.result)})
            except json.JSONDecodeError:
                data.append({'coin': 'TOR', 'output': 'Error: Failed to decode JSON'})
        else:
            print("Not ready")
            data.append({'coin': 'TOR', 'output': 'In progress'})
        print("DAata : -",data)
        return render(request, 'coin_scraper/display_data.html', {'job_id': job_id, 'data': data})

def index(request):
    print("this is")
    return render(request,'index.html')