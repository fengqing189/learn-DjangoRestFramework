# learn-DjangoRestFramework
������Ҫѧϰ��`DjangoRestFrame`��֤���ֵ�Դ�����̡�

��Դ���У���Ҫ�漰����3���࣬�ֱ��ǣ�

1.`LoginView`��;

2.`APIView`��

3.`View`��

4.`MyAuthentication`��(�Լ��������֤������)

---

## ��������

1.���󵽴�·�ɺ��� `url` ����֮��,��Ϊ��CBVģʽ,���� `url(r'login/',app02_view.LoginView.as_view())`,����`.as_view()`����������ִ����`self.dispatch()`������

2.��ִ����ͼ��֮ǰ����ִ��`self.dispatch()` ������

3.��dispatch�����У���Ҫִ����`request = self.initialize_request(request, *args, **kwargs)`�Լ�`self.initial(request, *args, **kwargs)`���仰��

```
def dispatch(self, request, *args, **kwargs):
    """
    `.dispatch()` is pretty much the same as Django's regular dispatch,
    but with extra hooks for startup, finalize, and exception handling.
    """
    self.args = args
    self.kwargs = kwargs
    # ����ԭʼ��������װ��������
    request = self.initialize_request(request, *args, **kwargs)
    self.request = request  # �����Ѿ����µ�������
    self.headers = self.default_response_headers  # deprecate?

    try:
        self.initial(request, *args, **kwargs)

        # Get the appropriate handler method
        if request.method.lower() in self.http_method_names:
            # �÷������ҵ���������ķ�ʽ����ִ�У�Ҳ���������handler(request, *args, **kwargs)
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

4.`self.initialize_request(request, *args, **kwargs)`����ʲô��

```
def initialize_request(self, request, *args, **kwargs):
    """
    Returns the initial request object.
    """
    parser_context = self.get_parser_context(request)

    # ���￪ʼ��װrequest,��Ҫ��ȥ���������ʲô
    return Request(
        request,  # ԭʼ������
        parsers=self.get_parsers(),    # ����һ���б�Ԫ���Ǽ�������
        authenticators=self.get_authenticators(),  # ������֤���б�Ԫ���Ƕ���,��������֤�������Ķ���
        negotiator=self.get_content_negotiator(),
        parser_context=parser_context
    )
```

�����������ԭʼ��request���󣬽�����һ�η�װ������������������(ע������������������ԣ���߻��õõ�)��

5.�ٽ���ִ��`self.dispatch()`�����е�`self.initial(request, *args, **kwargs)`������Ҫ�Ǹ������µ����飺

> ```
> # 2.��֤
> self.perform_authentication(request)
> # 3.Ȩ��
> self.check_permissions(request)
> # 4.���ƿͻ��˷��ʴ���
> self.check_throttles(request)
> ```

����������Ҫ����֤�������:

6.`self.perform_authentication(request)`(�������request���Ƿ�װ֮���������request)

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

���������Request���user����(�����user����@propertyװ�εģ�αװ����һ������ )

7.request.user()

```
@property
def user(self):
    """
    Returns the user associated with the current request, as authenticated
    by the authentication classes provided to the request.
    """
    if not hasattr(self, '_user'):    # self��ָ��ǰ����Ķ������Ѿ���Request��װ�ļ�ǿ������
        with wrap_attributeerrors():
            self._authenticate()      # ���￪ʼ������֤������
    return self._user   # �����뵱ǰ������������û�
```

��Ҫ�ǿ�ʼִ�� `self._authenticate()` 

8. ִ����֤request�����`._authenticate()`����

```
def _authenticate(self):   # �����self��request����
    """
    Attempt to authenticate the request using each authentication instance
    in turn.
    """
    for authenticator in self.authenticators:
        try:
            user_auth_tuple = authenticator.authenticate(self)  # ������ǿ�ʼ��֤��
        except exceptions.APIException:
            self._not_authenticated()        # û��ͨ����֤
            raise

        if user_auth_tuple is not None:  # �����֤֮�󷵻صĽ����Ϊ��
            self._authenticator = authenticator   # authenticatorָ��ǰ��֤�������ʵ��������
            self.user, self.auth = user_auth_tuple  # ������Ƿ��صĽ�����ŵ�request�����У�
            return

    self._not_authenticated()
```

- �����`self.authenticators`���Ƿ�װrequest�����������ӵ�authenticators���ԣ�Ҳ����APIView���get_authenticators()����ִ��֮��Ľ�������Ǹ��б�Ҫ�����Լ���LoginView���ж�����`authentication_classes = [��֤1��class,��֤2��class]`,�ͻḲ��settings�����õģ����û�еĻ���������settings�����õġ�
- ����ͻ�����Լ���������ʼ����֤��Ҳ����������utils.py�е�`MyAuthentication`�࣬ע�⣬�����֤�ɹ�������ֵ��һ��Ԫ�飬��Ϊ����һ���� `self.user, self.auth = user_auth_tuple`������֤֮������ݸ�ֵ����request����������ˡ�
- �������֤�����ݻ����Ͼ����ˣ�Ҫ����������������ɡ�

