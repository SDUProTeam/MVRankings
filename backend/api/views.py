import json

from django.shortcuts import render
from .models import Profile, Fusion
from django.views.generic import View
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.core import serializers
from mongoengine.queryset.visitor import Q

# Create your views here.


@api_view(['GET'])
def search(request):
    limit = 10  # max_num per page
    params = request.GET.dict()
    filters = {}
    if 'limit' in params:
        limit = int(params['limit'])
        limit = min(30, limit)
    if params.get('name'):
        filters['name__contains'] = params['name']
    for key in ['type', 'source', 'casts', 'directors']:
        if params.get(key):
            filters[key] = params[key]
    if params.get("time_min"):
        filters['time__gt'] = str(max(int(params['time_min']), 0))
    if params.get("time_max"):
        filters['time__lt'] = str(int(params['time_max']) + 1)
    if 'rate_min' in params:
        filters['rate__gte'] = params['rate_min']
    if 'rate_max' in params and params['rate_max'] != "10":
        filters['rate__lte'] = params['rate_max']
    offset = int(request.GET.get('offset', 0))
    movies = Profile.objects.exclude('_id').filter(**filters)
    total = movies.count()
    if 'order' in params:
        movies = movies.order_by(params['order'])
    movies = movies.limit(limit).skip(offset)
    return JsonResponse({'data': json.loads(movies.to_json()), 'total': total}, json_dumps_params={'ensure_ascii': False})


@api_view(['GET'])
def search_fusion(request):
    limit = 10  # max_num per page
    params = request.GET.dict()
    filters = {}
    if params.get("limit"):
        limit = int(params['limit'])
        limit = min(30, limit)
    if params.get("name"):
        filters['name__contains'] = params['name']
    for key in ['type', 'casts', 'directors']:
        if params.get(key):
            filters[key] = params[key]
    if params.get("time_min"):
        filters['time__gte'] = str(max(int(params['time_min']), 0))
    if params.get("time_max"):
        filters['time__lte'] = str(int(params['time_max']) + 1)
    q = Q(**filters)
    if 'rate_min' in params:
        for source in ['douban', 'mtime', 'maoyan']:
            q &= Q(**{'source__' + source + '__rate__gte': params['rate_min']})
    if 'rate_max' in params and params['rate_max'] != "10":
        for source in ['douban', 'mtime', 'maoyan']:
            q &= Q(**{'source__' + source + '__rate__lte': params['rate_max']})
    offset = int(request.GET.get('offset', 0))
    movies = Fusion.objects.exclude('_id').filter(q)
    total = movies.count()
    if params.get("order"):  # e.g. -rate_douban
        if "rate" in params['order']:
            if params['order'][0] == '-':
                order = '-source__' + params['order'][6:] + '__rate'
            else:
                order = 'source__' + params['order'][5:] + '__rate'
        else:
            order = params["order"]
        movies = movies.order_by(order)
    movies = movies.limit(limit).skip(offset)
    return JsonResponse({'data': json.loads(movies.to_json()), 'total': total}, json_dumps_params={'ensure_ascii': False})
