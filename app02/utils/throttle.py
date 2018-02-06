# 这里是限制客户端访问频率的类
from rest_framework.throttling import BaseThrottle,SimpleRateThrottle

RECORD = {}  # 用来记录每个ip的时间

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
        first_in_time = RECORD[self.get_ident(request=)][-1]
        wt = 60 - (ctime-first_in_time)   # 得到还需要等多久才到60秒
        return wt