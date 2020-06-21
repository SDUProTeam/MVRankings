from django.db import models
from mongoengine import *
import json

with open('api/setting.json') as f:
    setting = json.load(f)
connect('movie', host=setting['host'], username=setting['username'], password=setting['password'])


# Create your models here.

class Comments(Document):
    _id = ObjectIdField()
    movieId=StringField()
    user=StringField()
    userId=StringField()
    rating=StringField()
    content=StringField()
    time=StringField()

class Details(Document):
    source = StringField()
    sourceId = StringField()
    name = StringField()
    nameFrn = StringField()
    cover = StringField()
    directors = ListField(StringField())
    writers = ListField(StringField())
    stars = ListField(StringField())
    types = ListField(StringField())
    country = ListField(StringField())
    language = ListField(StringField())
    releaseDate = ListField(StringField())
    runtime = StringField()
    imdb = StringField()
    summary = StringField()
    rating = StringField()
    rateNum = StringField()
    insertStamp = StringField()
    year = StringField()
    _id = ObjectIdField()


class Profile(Document):
    name = StringField()
    rate = StringField()
    cover = StringField()
    source = StringField()
    url = StringField()
    casts = ListField(StringField())
    directors = ListField(StringField())
    id = StringField()
    type = ListField(StringField())
    time = StringField()
    rate_num = StringField()
    _id = ObjectIdField()


class Fusion(Document):
    name = StringField()
    casts = ListField(StringField())
    directors = ListField(StringField())
    id = StringField()
    type = ListField(StringField())
    time = StringField()
    rate_num = StringField()
    source = DictField()
    _id = ObjectIdField()


class User(Document):
    _id = ObjectIdField()
    phone = StringField()
    name = StringField()
    pwd = StringField()
    emb = ListField(FloatField)
    history = ListField(DictField(LongField))

