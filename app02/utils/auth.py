from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
from rest_framework.exceptions import APIException
from app02 import models

# 这里是写入认证的类，在视图中引入(全局settings或者局部的view视图类中)

class MyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        '''对于用户、匿名用户都放行，但是如果是登录用户，需要在在request中设置信息'''
        token = request.query_params.get('token')
        obj = models.Userinfo.objects.filter(token=token).first()
        print('222--auth认证类中的 authenticate')
        if obj:
            # 这里请看源码，self.user, self.auth = user_auth_tuple  (self就是request对象，user_auth_tuple=(obj.username,obj))
            return (obj.username,obj)
        # raise APIException
        return None   # 不验证，开始放行