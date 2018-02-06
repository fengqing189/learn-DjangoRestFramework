
# Permission相关
class MyPermission1(object):
    '''匿名用户跟登录用户都能看到'''
    message = '无效访问'
    def has_permission(self,request,view):
        return True

class MyPermission2(object):
    '''需要用户登录之后才能看到'''
    message = '用户信息需要认证之后才能看到'
    def has_permission(self,request,view):
        print(request.user,'++++ has_permission +++++')
        if request.user:
            return True
        return False

class MyPermission3(object):
    '''是管理员的名字是bai的才能访问'''
    message = '工资信息只有bai才能查看'
    def has_permission(self,request,view):
        if request.user == 'bai':
            return True
        return False