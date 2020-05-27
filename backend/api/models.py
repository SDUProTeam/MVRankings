from django.db import models
from mongoengine import *
import json

with open('api/setting.json') as f:
    setting = json.load(f)
connect('movie', host=setting['host'], username=setting['username'], password=setting['password'])

# Create your models here.

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


