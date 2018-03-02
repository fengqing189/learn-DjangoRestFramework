# 这里是限制客户端访问频率的类
from rest_framework.throttling import BaseThrottle,SimpleRateThrottle


# =================以下是模拟=========================
RECORD = {}  # 用来记录每个ip的时间

# 1.继承自最基本的内置限制的类
class MyThrottle(BaseThrottle):
    '''必须实现下边的allow_request,wait方法'''
    def allow_request(self,request,view):
        '''返回True，则表示不进行限制，返回False，表示要进行限制，调用wait()方法'''
        # 1.拿到请求的唯一标示
        # 2.判断当前请求在一定时间内请求的次数

        import time
        ctime = time.time()
        # ret = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = self.get_ident(request)  # 拿到当前发请求的客户端的ip地址，
        if ip not in RECORD:
            RECORD[ip] = [ctime,]
        else:
            time_list = RECORD[ip]
            while True:
                val = time_list[-1]   # 列表最后的时间，也就是最早的时间
                if (ctime - val) > 60:  # 现在的时间，减去最开始访问的时间，如果超出60秒，我就删除距离现在大于60的时间
                    time_list.pop()
                else:
                    break
            if len(time_list)>10:   # 如果经过循环之后，列表长度仍然大于10,则证明在60秒内，访问超过10次，需要限制，返回false
                return False
            time_list.insert(0,ctime)  # 反之，把这次的访问时间写入列表，然后return True,放行
        return True

    def wait(self,request):
        import time
        ctime = time.time()
        first_in_time = RECORD[self.get_ident(request)][-1]
        wt = 60 - (ctime-first_in_time)   # 得到还需要等多久才到60秒
        return wt


# 2.继承自内置的SimpleRateThrottle限制类(这里功能很多呀，)
class MySimpleRateThrottle(SimpleRateThrottle):
    scope = 'reta_name'   # 必须在这里定义scope子字段，用于

    # 实例化(注意在哪里实例化的)的时候,会执行SimpleRateThrottle的__init__方法，注意里边做的事情,
    # 完成__init__之后，就会执行self.allow_request方法，SimpleRateThrottle类中也已经实现了，请查看

    def get_cache_key(self, request, view):
        '''这里写对谁做限制的条件，相当于拿到请求的id'''
        if request.user:
            return None   # 放行
        else:
            return self.get_ident(request)   # 返回什么，就意味着根据什么做唯一值，


# ==============以下是运用==================
# 3. 运用：根据用户登录的状态来判断限流的措施，分为两个限制类来做

class AnonSimpleRateThrottle(SimpleRateThrottle):
    '''对于匿名用户的限流，每分钟5次'''
    scope = 'anon_rate'   # 这里配置限流的字段名,匿名用户频率

    def get_cache_key(self, request, view):
        '''

        :param request:
        :param view:
        :return: 返回None，表示不限制；其他返回值，表示用什么来做限制的唯一表示，是ip，还是用户名
        '''
        if request.user:
            return None
        return self.get_ident(request)   # 匿名用户，返回ip



class UserSimpleRateThrottle(SimpleRateThrottle):
    '''对于登录用户的限制,每分钟10次'''
    scope = 'user_rate'

    def get_cache_key(self, request, view):
        if request.user:
            return request.user



