from mongoengine import Document, fields, DateTimeField , StringField , IntField
from django.utils import timezone
import datetime
import uuid



class SuperAdmin(Document):
    email = fields.StringField(required=True, unique=True)
    password = fields.StringField(required=True)
    is_active = fields.BooleanField(default=True)

    

class Activation_code(Document):
    key_created_by = fields.StringField()
    admin_id = fields.StringField()
    activation_code = fields.StringField(unique=True)
    using_times = fields.IntField(default=0)
    max_using = fields.IntField(default=1)
    created_at = fields.DateTimeField(default=timezone.now)
    activation_date = fields.DateTimeField(default=timezone.now)
    status = fields.StringField(default="Active")  # Active or Expired
    expiry_date = DateTimeField(default=timezone.now)
    
class Sender_Activation_code(Document):
    key_created_by = fields.StringField()
    admin_id = fields.StringField()
    activation_code = fields.StringField(unique=True)
    using_times = fields.IntField(default=0)
    max_using = fields.IntField(default=1)
    created_at = fields.DateTimeField(default=timezone.now)
    activation_date = fields.DateTimeField(default=timezone.now)
    status = fields.StringField(default="Active")  # Active or Expired
    expiry_date = DateTimeField(default=timezone.now)
    start_date = DateTimeField(default=timezone.now)
    


class Admin(Document):
    name = StringField()
    email = StringField()
    password = StringField()
    key_option = StringField()  # "Unlimited" or "Custom"
    custom_key_count = IntField(default=0)
    total_keys = IntField(default=0)
    used_keys = IntField(default=0)
    status = StringField()  # "Active" or "Inactive"
    otp = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
  

   

class ActivationKey(Document):
    key = fields.StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    status = fields.StringField(choices=["Active", "Expired", "Revoked"], default="Active")
    max_usage = fields.IntField(default=1)
    used_count = fields.IntField(default=0)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)
    expiry_date = fields.DateTimeField(default=timezone.now)
    


class User(Document):
    name = fields.StringField()
    email = fields.EmailField()
    password = fields.StringField()  # (for demo: plain text, but should hash in real apps)
    otp = fields.StringField() 

