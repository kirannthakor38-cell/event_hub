from django.db import models

from mongoengine import Document, StringField,IntField

class User(Document):
    username = StringField(required=True)
    rollno = StringField(required=True, unique=True)
    mobile = StringField(required=True)
    email = StringField(required=True,)
    password = StringField(required=True)   # hashed password

class TempUser(Document):
    username = StringField(required=True)
    rollno = StringField(required=True)
    email = StringField(required=True)     # ❌ do NOT add unique=True here
    mobile = StringField(required=True)
    password = StringField(required=True)
    otp = IntField(required=True)


    



from mongoengine import Document, StringField

class Event(Document):
    event_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    description = StringField()
    image = StringField()
    date = StringField()

from mongoengine import Document, StringField, IntField

class Registration(Document):
    event_id = StringField(required=True)
    rollno = StringField(required=True)
    username = StringField(required=True)
    score = StringField(default="")   # ⭐ ADD SCORE FIELD



from mongoengine import Document, StringField, ListField, EmbeddedDocument, EmbeddedDocumentField

class WinnerItem(EmbeddedDocument):
    rollno = StringField(required=True)
    name = StringField(required=True)
    image = StringField(default="https://img.icons8.com/ios-filled/100/user.png")

class Winner(Document):
    meta = {"collection": "winners"}
    event_id = StringField(required=True)
    event_title = StringField(required=True)
    event_date = StringField(required=True)
    winners = ListField(EmbeddedDocumentField(WinnerItem))

from mongoengine import Document, StringField, ListField, IntField

class Examiner(Document):
    username = StringField(required=True)
    password = StringField(required=True)
    event_id = StringField(required=True)   # examiner assigned event


from mongoengine import Document, StringField

class AdminRadhe(Document):
    username = StringField(required=True)
    password = StringField(required=True)





