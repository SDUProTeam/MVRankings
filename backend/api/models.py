from django.db import models
from mongoengine import *
import json

with open('api/setting.json') as f:
    setting = json.load(f)
connect('movie', host=setting['host'], username=setting['username'], password=setting['password'])


# Create your models here.
class Movie(Document):
    movieId=IntField()
    source=DictField()
    name = StringField()
    nameFrn = StringField()
    directors = ListField(StringField())
    writers = ListField(StringField())
    stars = ListField(StringField())
    types = ListField(StringField())
    country = ListField(StringField())
    language = ListField(StringField())
    releaseDate = ListField(StringField())
    runtime = IntField()
    imdb = StringField()
    summary = StringField()
    timestamp = LongField()
    year = StringField()
    _id = ObjectIdField(primary_key=True)

class Comments(Document):
    sourceId = StringField()
    _id = ObjectIdField()
    movieId=IntField()
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
    runtime = IntField()
    imdb = StringField()
    summary = StringField()
    rating = StringField()
    rateNum = LongField()
    timestamp = LongField()
    year = StringField()
    _id = ObjectIdField(primary_key=True)


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
    _id = ObjectIdField(primary_key=True)
    phone = StringField()
    name = StringField()
    pwd = StringField()
    emb = ListField(FloatField())
    history = ListField(DictField())
    question = IntField()

