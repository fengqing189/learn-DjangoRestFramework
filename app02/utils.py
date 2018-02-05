from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
from rest_framework.exceptions import APIException
from app02 import models

class MyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.query_params.get('token')
        obj = models.Userinfo.objects.filter(token=token).first()
        if obj:
            return (obj.username,obj)
        raise APIException