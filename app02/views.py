from django.shortcuts import render,HttpResponse

from django.views import View
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from app02 import models



class LoginView(APIView):
    authentication_classes = []
    def get(self,request):
        '''
        接收用户名和密码
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
        # 创建随机字符串
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

class HostView(APIView):

    def get(self,request,*args,**kwargs):
        self.dispatch
        return HttpResponse('....')

    def post(self,response,*args,**kwargs):
        pass