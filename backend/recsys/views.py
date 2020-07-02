from django.shortcuts import render

# Create your views here.

import json
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
import mongoengine
from mongoengine.queryset.visitor import Q
from recsys.models import pool
import asyncio
from api.models import User, Movie
from bson import ObjectId
import torch

async def get_rec_items(id, seq, emb):
    iids, emb = await pool.ask_for_recall(id, seq, emb)
    return iids, emb

@api_view(['GET'])
def recommend(requests):
    emb = None
    _id = requests.COOKIES.get('_id')
    user = None
    if _id:
        user = User.objects.only('_id', 'emb').with_id(_id)
        if not user:
            return JsonResponse({'err': '用户不存在，请重新登录'},
                                json_dumps_params={'ensure_ascii': False})
        if user.emb:
            emb = user.emb
    else:
        _id = requests.session.session_key
    seq = requests.session.get('sess')
    if not seq:
        return JsonResponse({'rec': []},
                            json_dumps_params={'ensure_ascii': False})
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_rec_items(_id, seq, emb))
    loop.run_until_complete(future)
    iids, emb = future.result()
    # if user:
    #     User.objects.filter(_id=_id).update_one(emb=emb.tolist())
    items = []
    for iid in iids:
        if iid == seq[-1]:
            continue
        items.append(dict(Movie.objects.exclude('_id').filter(movieId=iid).first().to_mongo()))
    return JsonResponse({'rec': items},
                        json_dumps_params={'ensure_ascii': False})


def init_emb(preference: list, uid: str, init=True):
    """

    :param preference:  movieId list
    :param uid:         _id for user
    :param init:        When register, set True, default
    :return: movie detail list
    """
    if init:
        emb = None
    else:
        user = User.objects.only('_id', 'emb').with_id(uid)
        emb = user.emb
    iids, emb = pool.recall_one(preference, emb)
    # User.objects.filter(_id=ObjectId(uid)).update_one(emb=emb.tolist())
    items = []
    for iid in iids:
        items.append(dict(Movie.objects.exclude('_id').filter(movieId=iid).first().to_mongo()))
    return items