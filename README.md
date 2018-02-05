# learn-DjangoRestFramework
今天主要学习了`DjangoRestFrame`认证部分的源码流程。

在源码中，主要涉及到了3个类，分别是：

1.`LoginView`类;

2.`APIView`类

3.`View`类

4.`MyAuthentication`类(自己定义的验证规则类)

---

## 请求流程

1.请求到达路由函数 `url` 函数之后,因为是CBV模式,所以 `url(r'login/',app02_view.LoginView.as_view())`,调用`.as_view()`函数，进而执行了`self.dispatch()`方法；

2.在执行视图类之前，先执行`self.dispatch()` 函数。

3.在dispatch方法中，主要执行了`request = self.initialize_request(request, *args, **kwargs)`以及`self.initial(request, *args, **kwargs)`两句话。

```
def dispatch(self, request, *args, **kwargs):
    """
    `.dispatch()` is pretty much the same as Django's regular dispatch,
    but with extra hooks for startup, finalize, and exception handling.
    """
    self.args = args
    self.kwargs = kwargs
    # 对于原始请求，做封装，并返回
    request = self.initialize_request(request, *args, **kwargs)
    self.request = request  # 这里已经是新的请求了
    self.headers = self.default_response_headers  # deprecate?

    try:
        self.initial(request, *args, **kwargs)

        # Get the appropriate handler method
        if request.method.lower() in self.http_method_names:
            # 用反射来找到本期请求的方式，并执行，也就是下面的handler(request, *args, **kwargs)
            handler = getattr(self, request.method.lower(),
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed

        response = handler(request, *args, **kwargs)

    except Exception as exc:
        response = self.handle_exception(exc)

    self.response = self.finalize_response(request, response, *args, **kwargs)
    return self.response
```

4.`self.initialize_request(request, *args, **kwargs)`做了什么？

```
def initialize_request(self, request, *args, **kwargs):
    """
    Returns the initial request object.
    """
    parser_context = self.get_parser_context(request)

    # 这里开始封装request,需要进去看里边做了什么
    return Request(
        request,  # 原始的请求
        parsers=self.get_parsers(),    # 返回一个列表，元素是几个对象
        authenticators=self.get_authenticators(),  # 用于认证的列表，元素是对象,这里是验证规则的类的对象
        negotiator=self.get_content_negotiator(),
        parser_context=parser_context
    )
```

这个函数，把原始的request请求，进行了一次封装，增加了其他的属性(注意这里额外新增的属性，后边会用得到)。

5.再接着执行`self.dispatch()`函数中的`self.initial(request, *args, **kwargs)`这里主要是干了如下的事情：

> ```
> # 2.认证
> self.perform_authentication(request)
> # 3.权限
> self.check_permissions(request)
> # 4.限制客户端访问次数
> self.check_throttles(request)
> ```

这里我们主要看认证这个函数:

6.`self.perform_authentication(request)`(这个参数request就是封装之后的厉害的request)

```
def perform_authentication(self, request):
    """
    Perform authentication on the incoming request.

    Note that if you override this and simply 'pass', then authentication
    will instead be performed lazily, the first time either
    `request.user` or `request.auth` is accessed.
    """
    request.user
```

这里调用了Request类的user方法(这里的user是用@property装饰的，伪装成了一个属性 )

7.request.user()

```
@property
def user(self):
    """
    Returns the user associated with the current request, as authenticated
    by the authentication classes provided to the request.
    """
    if not hasattr(self, '_user'):    # self，指当前请求的对象，是已经被Request封装的加强版请求，
        with wrap_attributeerrors():
            self._authenticate()      # 这里开始调用验证函数了
    return self._user   # 返回与当前请求相关联的用户
```

主要是开始执行 `self._authenticate()` 

8. 执行认证request对象的`._authenticate()`方法

```
def _authenticate(self):   # 这里的self是request对象
    """
    Attempt to authenticate the request using each authentication instance
    in turn.
    """
    for authenticator in self.authenticators:
        try:
            user_auth_tuple = authenticator.authenticate(self)  # 这里就是开始验证了
        except exceptions.APIException:
            self._not_authenticated()        # 没有通过验证
            raise

        if user_auth_tuple is not None:  # 如果验证之后返回的结果不为空
            self._authenticator = authenticator   # authenticator指当前验证规则类的实例化对象
            self.user, self.auth = user_auth_tuple  # 这里就是返回的结果，放到request对象中，
            return

    self._not_authenticated()
```

- 这里的`self.authenticators`就是封装request的那里额外添加的authenticators属性，也就是APIView类的get_authenticators()方法执行之后的结果，就是个列表，要是在自己的LoginView类中定义了`authentication_classes = [认证1的class,认证2的class]`,就会覆盖settings中配置的，如果没有的话，就是用settings中配置的。
- 这里就会调用自己的类来开始做验证，也就是我们在utils.py中的`MyAuthentication`类，注意，如果认证成功，返回值是一个元组，因为在上一步中 `self.user, self.auth = user_auth_tuple`，把认证之后的数据赋值到了request请求对象中了。
- 到这里，认证的内容基本上就完了，要是想起来再来补充吧。

