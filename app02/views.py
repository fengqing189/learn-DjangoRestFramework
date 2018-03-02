from django.shortcuts import render,HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from app02 import models
from app02.utils.permission import MyPermission1,MyPermission2,MyPermission3
from app02.utils.throttle import MyThrottle
from rest_framework import exceptions


# 以下是视图类，处理请求相关

class LoginView(APIView):
    authentication_classes = []   # 这里不进行验证，因为是login页面
    throttle_classes = [MyThrottle,]
    def get(self,request):
        '''
        接收用户名和密码,跟数据库中的进行匹配，验证成功则再数据库中写入token
        :param request:
        :return:
        '''
        ret = {'code':1000,'msg':None}
        user = request.query_params.get('user')
        pwd = request.query_params.get('pwd')

        obj = models.Userinfo.objects.filter(username=user,pwd=pwd).first()
        if not obj:
            ret['code'] = 1001
            ret['msg'] = '用户名密码不匹配'
            return Response(ret)
        # 创建随机字符串，当做token
        import time
        import hashlib
        ctime = time.time()
        key = '%s|%s'%(user,ctime)
        m = hashlib.md5()
        m.update(key.encode('utf-8'))
        token = m.hexdigest()

        # 保存数据
        obj.token = token
        obj.save()
        ret['token'] = token
        return Response(ret)

    def throttled(self,request, wait):
        raise MyThrottle(wait)


class HostView(APIView):  # 匿名用户、登录用户都可以查看
    # 认证的类，这里直接使用settings中配置的
    permission_classes = [MyPermission1,]  # 权限的验证用MyPermission1这个类
    throttle_classes = []
    def get(self,request,*args,**kwargs):
        self.dispatch  # 如果当前类没有dispatch方法，则走APIView类中的dispatch方法。
        return Response('用户信息列表')

    def post(self,response,*args,**kwargs):
        pass


class Users(APIView):
    '''只有登录用户才可以查看'''

    permission_classes = [MyPermission2,]
    def get(self,request):
        return Response('用户信息')

# 这里是自定义salary视图类中，要是没认证，保错的提示，参照源码写的。
from rest_framework.exceptions import APIException
from rest_framework import status
class MyNotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = ('Authentication credentials were not provided，没有提供身份验证凭据。.')
    default_code = 'not_authenticated--没有被认证'


class Salary(APIView):

    permission_classes = [MyPermission3,]
    throttle_classes = []
    def get(self,request):
        return Response('工资信息')

    def permission_denied(self, request, message=None):
        '''如果当前请求的permission没有通过，则会调用视图类的当前方法'''
        if request.authenticators and not request.successful_authenticator:   # 如果当前有认证的类
            raise MyNotAuthenticated()
        raise exceptions.PermissionDenied(detail='xxxxxxxxxxxx')
        # 这里原来是detail=message，也可以改写，也可以直接自定义PermissionDenied类，


# 首页视图函数，用来测试限流，匿名用户每分钟5次访问，登录用户每分钟10次，
from app02.utils.throttle import AnonSimpleRateThrottle      # 限制匿名用户的类
from app02.utils.throttle import UserSimpleRateThrottle       # 限制登录用户的类

class IndexView(APIView):

    throttle_classes = [AnonSimpleRateThrottle,UserSimpleRateThrottle]

    def get(self,request,*args,**kwargs):
        ret = {
            'code':100,
            'msg':'首页的信息'
        }
        self.dispatch
        return Response(ret)


