import json

from .models import Comments, Fusion, Details, User, Movie
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from mongoengine.queryset.visitor import Q
import time
import urllib
from bson import ObjectId
from recsys.models import pool
from recsys import views as recviews
from crawler import views as craviews


def set_cookie(resp, _id, origin, name=None):
    if name:
        resp.set_cookie('name', name)
    resp.set_cookie('_id', _id, domain=origin)
    return resp

@api_view(['POST'])
def signin(request):
    form = request.POST.dict()

    user = User.objects.filter(Q(name=form['name']) | Q(phone=form['name'])).first()
    if user is None:
        return JsonResponse({'success': False, 'msg': '不存在该用户'},
                            json_dumps_params={'ensure_ascii': False})
    if user['pwd'] != form['pwd']:
        return JsonResponse({'success': False, 'msg': '密码错误'},
                            json_dumps_params={'ensure_ascii': False})
    return set_cookie(JsonResponse({'success': True}), user.pk, request.META.get("ORIGIN"), name=user.name)


@api_view(['POST'])
def signup(request):
    form = request.POST.dict()
    if len(User.objects.filter(name=form['name'])) > 0:
        return JsonResponse({'success': False, 'msg': '用户名已被注册'},
                            json_dumps_params={'ensure_ascii': False})
    if 'phone' in form and len(User.objects.filter(phone=form['phone'])) > 0:
        return JsonResponse({'success': False, 'msg': '手机号已被注册'},
                            json_dumps_params={'ensure_ascii': False})
    user = User(name=form['name'], pwd=form['pwd'])
    if 'phone' in form:
        user.phone = form['phone']
    user = User.objects.insert(user)
    return set_cookie(JsonResponse({'success': True}), user.pk, request.META.get("ORIGIN"))


# 将历史记录按照时间戳排序
def historySortOrder(h):
    return h['timestamp']


@api_view(['GET'])
def history(request):
    cookies = request.COOKIES

    user = User.objects.with_id(cookies['_id'])
    if user is None:
        return JsonResponse({'success': False, 'msg': '登陆状态异常，请重新登录'},
                            json_dumps_params={'ensure_ascii': False})
    #    return JsonResponse({'success': True, 'history': json.loads(user.to_json())['history']},
    #                        json_dumps_params={'ensure_ascii': False})

    history_ids = json.loads(user.to_json())['history']
    result = []
    for h in history_ids:
        result.append(getHistoryMovieById(h['id']))

    return JsonResponse({'success': True, 'history': result}, json_dumps_params={'ensure_ascii': False})

@api_view(['GET'])
def question(request):
    cookies=request.COOKIES
    if "country" not in cookies:
        pipeline=[{"$unwind":"$country"},
                  {"$group":{"_id":"$country","count":{"$sum":1}}},
                  {"$sort":{"count":-1}}]
        result=list(Movie._get_collection().aggregate(pipeline))[:12]
        return JsonResponse({'result': result}, json_dumps_params={'ensure_ascii': False})
    if "types" not in cookies:
        country=urllib.parse.unquote(cookies['country']).split(",")
        pipeline = [{"$match":{"country":{"$in":country}}},
                    {"$unwind": "$types"},
                    {"$group": {"_id": "$types", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}]
        result = list(Movie._get_collection().aggregate(pipeline))[:12]
        return JsonResponse({'result': result}, json_dumps_params={'ensure_ascii': False})
    if "stars" not in cookies:
        country=urllib.parse.unquote(cookies['country']).split(",")
        types = urllib.parse.unquote(cookies['types']).split(",")
        pipeline = [{"$match": {"country": {"$in": country},"types":{"$in": types}}},
                    {"$unwind": "$stars"},
                    {"$group": {"_id": "$stars", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}]
        result = list(Movie._get_collection().aggregate(pipeline))[:12]
        return JsonResponse({'result': result}, json_dumps_params={'ensure_ascii': False})
    if "movies" not in cookies:
        country=urllib.parse.unquote(cookies['country']).split(",")
        types = urllib.parse.unquote(cookies['types']).split(",")
        stars = urllib.parse.unquote(cookies['stars']).split(",")
        filters = {}
        filters['country__in'] = country
        filters['types__in'] = types
        filters['stars__in'] = stars
        result = Movie.objects.exclude('_id').filter(**filters)
        result = result.order_by("-source__douban__rating").limit(12)
        return JsonResponse({'result': json.loads(result.to_json())}, json_dumps_params={'ensure_ascii': False})

    movieIds=urllib.parse.unquote(cookies['movies']).split(",")
    for i in range(len(movieIds)):
        movieIds[i] = int(movieIds[i])
    _id=cookies['_id']
    user = User.objects.with_id(_id)
    items=[]
    if "question" not in user:
        items=recviews.init_emb(movieIds, _id)
        user.question=1
    elif user.question==0:
        items=recviews.init_emb(movieIds, _id)
        user.question = 1
    else:
        items=recviews.init_emb(movieIds, _id, False)
    User.objects.filter(_id=ObjectId(_id)).update_one(question=user.question)
    return JsonResponse({'success': True,'result':items})



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
    for key in ['types', 'stars', 'directors', 'writers', 'country', 'language']:
        if params.get(key):
            filters[key] = params[key]
    if params.get("time_min"):
        filters['year'] = {"$gt": str(max(int(params['time_min']), 0))}
    if params.get("time_max"):
        filters['year'] = {"$lt": str(int(params['time_max']) + 1)}
    if 'rate_min' in params:
        filters['source__douban__rating__gte'] = params['rate_min']
        filters['source__mtime__rating__gte'] = params['rate_min']
        filters['source__maoyan__rating__gte'] = params['rate_min']
    if 'rate_max' in params and params['rate_max'] != "10":
        filters['source__douban__rating__lte'] = params['rate_max']
        filters['source__mtime__rating__lte'] = params['rate_max']
        filters['source__maoyan__rating__lte'] = params['rate_max']
    if 'insertStamp' in params:
        filters['insertStamp'] = params['insertStamp']
    offset = int(request.GET.get('offset', 0))
    movies = Movie.objects.exclude('_id').filter(**filters)
    total = movies.count()
    if params['order']=="-year":
        movies = movies.order_by("-year","-source__douban__rating")
    else:
        movies = movies.order_by("-source__douban__rating")
    movies = movies.limit(limit).skip(offset)
    return JsonResponse({'data': json.loads(movies.to_json()), 'total': total},
                        json_dumps_params={'ensure_ascii': False})


def getHistoryMovieById(id):
    movie = Movie.objects.exclude('_id').filter(movieId=id).first()
    if movie is not None:
        movie = movie.to_mongo()

    return movie


@api_view(['GET'])
def movie(request, id):
    movie = Movie.objects.exclude('_id').filter(movieId=id).first()
    if movie is None:
        return JsonResponse({'data': None, 'msg': '不存在该电影'}, json_dumps_params={'ensure_ascii': False})
    movie = movie.to_mongo()
    movie['comments']=[]
    if "mtime" in movie['source']:
        comments = Comments.objects.exclude('_id').filter(movieId=id)
        movie['comments'] = json.loads(comments.to_json()) if comments else []

    if '_id' in request.COOKIES:
        _id = request.COOKIES['_id']
        user = User.objects.with_id(_id)
        if user:
            # history = {}
            if 'history' not in user:
                user.history = []

            flag = True
            for history in user.history:
                if history['id'] == id:
                    history['timestamp'] = int(time.time())
                    flag = False
            if flag:
                user.history.append({'id': id, 'timestamp': int(time.time())})
            user.history.sort(key=historySortOrder, reverse=True)
            if len(user.history) > 19:
                user.history.pop()

            User.objects.filter(_id=ObjectId(_id)).update_one(history=user.history)

    request.session.set_expiry(3600)
    request.session.setdefault('sess', [])
    request.session['sess'] += [id]

    resp = JsonResponse({'data': movie}, json_dumps_params={'ensure_ascii': False})
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


@api_view(['POST'])
def add_comment(request):
    uid = request.COOKIES.get('_id')
    name = request.COOKIES.get('name')
    form = request.POST.dict()
    comment = Comments(userId=uid, content=form['content'], user=name, movieId=form['movieId'],
                       rating=form['rating'], time=time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())))
    comment = Comments.objects.insert(comment)
    return JsonResponse({'success': True})

