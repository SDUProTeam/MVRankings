import json

from .models import Comments, Fusion, Details, User
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from mongoengine.queryset.visitor import Q
from bson import ObjectId
from recsys.models import Recommander
import time


class UserView:
    def set_cookie(self, resp, id):
        resp.set_cookie('_id', id)
        return resp

    @api_view(['POST'])
    def signin(self, request):
        form = request.POST.dict()
        user = User.objects.filter(Q(name=form['name']) | Q(phone=form['name']))
        if len(user)==0:
            return JsonResponse({'success': False, 'msg': '不存在该用户'},
                                json_dumps_params={'ensure_ascii': False})
        if user[0]['pwd'] != form['pwd']:
            return JsonResponse({'success': False, 'msg': '密码错误'},
                                json_dumps_params={'ensure_ascii': False})
        return self.set_cookie(HttpResponse('success'), user[0]['_id']['$oid'])

    @api_view(['POST'])
    def signup(self, request):
        form = request.POST.dict()
        if len(User.objects.filter(name=form['name']))>0:
            return JsonResponse({'success': False, 'msg': '用户名已被注册'},
                                json_dumps_params={'ensure_ascii': False})
        if 'phone' in form and len(User.objects.filter(phone=form['phone']))>0:
            return JsonResponse({'success': False, 'msg': '手机号已被注册'},
                                json_dumps_params={'ensure_ascii': False})
        user = User(name=form['name'], pwd=form['pwd'])
        if 'phone' in form:
            user.phone = form['phone']
        user.save()
        user = User.objects.filter(name=form['name'], pwd=form['pwd'])[0]
        return self.set_cookie(JsonResponse({'success': True}), user['_id']['$oid'])

    @api_view(['GET'])
    def history(self, request):
        cookies = request.COOKIES
        user=User.objects.with_id(ObjectId(cookies['_id']))
        if len(user)==0:
            return JsonResponse({'success': False, 'msg': '登陆状态异常，请重新登录'},
                                json_dumps_params={'ensure_ascii': False})
        return JsonResponse({'success': True, 'history': json.loads(user[0]['history'].to_json())},
                            json_dumps_params={'ensure_ascii': False})


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
    for key in ['types', 'source', 'stars', 'directors', 'writers', 'country', 'language']:
        if params.get(key):
            filters[key] = params[key]
    if params.get("time_min"):
        filters['year'] = {"$gt": str(max(int(params['time_min']), 0))}
    if params.get("time_max"):
        filters['year'] = {"$lt": str(int(params['time_max']) + 1)}
    if 'rate_min' in params:
        filters['rating__gte'] = params['rate_min']
    if 'rate_max' in params and params['rate_max'] != "10":
        filters['rating__lte'] = params['rate_max']
    if 'insertStamp' in params:
        filters['insertStamp'] = params['insertStamp']
    offset = int(request.GET.get('offset', 0))
    movies = Details.objects.exclude('_id').filter(**filters)
    total = movies.count()
    if 'order' in params:
        movies = movies.order_by(params['order'])
    movies = movies.limit(limit).skip(offset)
    return JsonResponse({'data': json.loads(movies.to_json()), 'total': total},
                        json_dumps_params={'ensure_ascii': False})


@api_view(['GET'])
def movie(request, id):
    movie = Details.objects.exclude('_id').filter(sourceId=str(id))
    data = json.loads(movie.to_json())
    filters = {}
    filters['name'] = data[0]['name']
    filters['source'] = "mtime"
    movie = Details.objects.exclude('_id').filter(**filters)
    if len(json.loads(movie.to_json()))>0:
        filters.clear()
        filters['movieId'] = json.loads(movie.to_json())[0]['sourceId']
        comments = Comments.objects.exclude('_id').filter(**filters)
        data[0]['comments'] = json.loads(comments.to_json())
    else:
        data[0]['comments'] = []

    if '_id' in request.COOKIES:
        _id = request.COOKIES['_id']
        user = User.objects.with_id(ObjectId(_id))
        if user:
            if 'history' not in user:
                user.history = {}
            else:
                user.history[time.time()] = id

    request.session.set_expiry(3600)
    request.session.setdefault('sess', [])
    request.session['sess'] += [id]

    resp = JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})
    return resp


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
    return JsonResponse({'data': json.loads(movies.to_json()), 'total': total},
                        json_dumps_params={'ensure_ascii': False})
