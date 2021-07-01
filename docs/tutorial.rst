Tutorial
=============

本教程将向大家详细介绍 `Mask` 的相关特性，帮助大家快速入手 `Mask` .


Layout
---------

`Mask` 支持单文件形式的目录结构，但是在大型项目中依然需要遵循相关最佳实践.
`Demo` 项目中使用的目录结构是我们在实践过程中不断总结的一种结构，希望对大家的应用有所帮助.

.. code-block:: text

    ├── app
    │   ├── __init__.py
    │   ├── controllers
    │   │   ├── __init__.py
    │   │   └── test
    │   │       ├── __init__.py
    │   │       ├── base.py
    │   │       └── info.py
    │   ├── core
    │   │   └── __init__.py
    │   ├── middleware
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── log.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── test_db
    │   │       ├── __init__.py
    │   │       ├── entity.py
    │   │       └── test_info.py
    │   ├── protos
    │   │   ├── __init__.py
    │   │   └── test
    │   │       ├── __init__.py
    │   │       ├── test.proto
    │   │       ├── test_pb2.py
    │   │       └── test_pb2_grpc.py
    │   └── utils
    │       └── __init__.py
    ├── config
    │   ├── __init__.py
    │   └── example.yml
    ├── manage.py
    └── requirements.txt


* 项目结构应依据需求做特定适配，此目录仅供参考。


ProtoBuf
------------

`Mask` 依赖 `gRpc` 构建通信服务，所以默认使用 `ProtoBuf` 作为传输协议。
`Mask` 在启动时会自动扫描项目中的所有`.proto`文件生成的`*_pb2.py`和`*_pb2_grpc.py`文件，发现其中定义的`Service`并注册进`gRpc`服务中。

所以您仅需要将项目中需要使用的`ProtoBuf`文件进行编译即可，其它的事情都交由`Mask`来完成。

* TODO: 支持手动添加`Service`替代自动扫描。
* TODO: 提供多样性的`ProtoBuf`判别规则，用于忽略特定的文件和文件夹扫描。
* TODO: 提供`cli`命令行用于自动编译`.proto`文件。


Application Setup
--------------------

`Mask` 支持多种方式从配置对象中读取配置，目前提供的方法如下:

=================== ===============================================
    Method              Intro
=================== ===============================================
 def from_object          Load config items from object attribute
 def from_dict            Load config items from dict instance
 def from_json            Load config items from json string
=================== ===============================================

.. code-block:: python

    from mask import Mask

    app = Mask(__name__)

    app.config.from_object(obj)
    app.config.from_dict(dict)
    app.config.from_json(json)


目前`Mask`支持的配置项目如下:

============================ ======================================== ===================
Key                             Intro                                   Default Value
============================ ======================================== ===================
DEBUG                           Debug mode                                  False
MAX_WORKERS                     Max worker quantity                         10
REFLECTION                      Open reflection service                     False
TLS_SERVER_KEY                  TLS server key file path                    None
TLS_SERVER_CERT                 TLS server cert file path                   None
CA_CERT                         TLS CA file path                            None
MAX_SEND_MESSAGE_LENGTH         Max send message length                     10MB
MAX_RECEIVE_MESSAGE_LENGTH      Max receive message content length          10MB
GRPC_OPTIONS                    gRpc setup Options                          None
HEALTH                          Enable health checking feature              None
============================ ======================================== ===================

特别说明:

* `gRpc` 原生提供大量配置参数用于控制`gRpc`服务的表现，在`Mask`中可以通过`GRPC_OPTIONS`参数提供, 例如: `[("grpc.so_reuseport", True)]`。
* 关于 `TLS` 相关说明，请详细参考下方 `TLS Support` 模块。


参考链接:

* `gRpc` 支持的配置列表: https://github.com/grpc/grpc/blob/v1.37.x/include/grpc/impl/codegen/grpc_types.h
* `gRpc` 反射相关知识: https://github.com/grpc/grpc/blob/master/doc/server-reflection.md


Routes And Services
--------------------------

`Mask` 支持简单的 `route` 定义，此时需要同时填写此函数对应的 `ProtoBuf` 文件中的服务和方法名称.

.. code-block:: python


    @app.route(service="User", method="SayHello")
    def user_say_hello_handler(request):
        return



当项目较大时需要实现的 `Service` 和 `Method` 通常较多，此时万不可以将所有的实现函数都写入同一个 `.py` 文件中，需要依据需求做特定的模块划分。
`Mask` 支持 `Flask` 中的蓝图概念用于将接口进行分组，但是这里叫做 `Service` 并与 `ProtoBuf` 中的 `Service` 一一对应。

.. code-block:: python

    service = Service(name="Hello")

    @service.route(method="SayHello")
    def say_hello_handler(request, context):
        return

    # 将子服务注册进入 `Mask` 应用中
    app.register_service(service)

使用 `Service` 后可以将接口文件放到不同的模块中，由核心模块统一注册进入 `app` 即可。

通过 `Mask` 路由函数注册的响应函数支持 `request` 和 `context` 两个入参。`request` 表示当前请求的参数，`context` 为当前请求的上下文。
当然这两个参数为可选项，路由函数会判断函数的入参是否接受相关参数智能注入。

`Mask` 也同样支持 `Flask` 中的 `g` 、`request` 等概念，用户也可以通过导入获取

.. code-block:: python

    from mask import g, request, current_app


Middleware
-----------------

`Mask` 通过 `gRpc` 提供的拦截器 `interceptor` 实现了中间件功能，包括请求中间件和响应中间件，帮助用户对请求和响应做统一处理。

.. code-block:: python

    def before_request(request, context):
        print(request.name)


    def after_request(response):
        print(response.message)
        return response


    app.before_request(before_request)
    app.after_request(after_request)


与 `Flask` 一样，`before_request` 和 `after_request` 是可以多次调用添加中间件的， 其响应顺序也是一致的。

当然，除了经过封装的中间件，用户也可以直接添加自定义的 `gRPC` 拦截器。根据 `gRPC` 的要求，拦截器必须是 `grpc.ServerInterceptor` 的子类
并且实现 `intercept_service` 方法.


.. code-block::

    from mask import Mask
    app = Mask()

    class CustomInterceptor(grpc.ServerInterceptor):
        """ 自定义拦截器的一个空白实现，无任何业务逻辑
        """

        def intercept_service(self, continuation, handler_call_details):
            return continuation(handler_call_details)

    # 将自定义拦截器注册进入 `Mask` 中
    app.register_interceptor(CustomInterceptor())

    if __name__ == "__main__":
        app.run()


Stream
-----------

`Mask` 支持 `双向流式RPC` , 您只需要在 `ProtoBuf` 文件中标识请求入参或者响应类型为 `stream` 即可。
如果您使用 `mask.pre` 来校验流式请求参数的话，推荐使用 `pre.parse` 函数来解析迭代后的单个 `request`。

.. code-block:: python

    # 3p
    from mask.parse import pre, Rule


    rule = {
        "userId": Rule(required=True, type=int, lte=200, trim=True, dest="user_id")
    }


    @app.route(method="UserInfo", service="User")
    def user_info_handler(request, context):
        """ 查询用户信息
        """
        for item in request:
            item = pre.parse(rule=rule, request=item, context=context)
            yield HelloResponse(message="Hello %s" % item["user_id"])



当然 `pre.catch` 同样支持自动化的将可迭代的 `request` 进行校验，但是它会一次性处理所有的请求参数，如果您的入参较多的话，建议使用 `pre.parse`.

.. code-block:: python

    # 3p
    from mask.parse import pre, Rule


    rule = {
        "userId": Rule(required=True, type=int, lte=200, trim=True, dest="user_id")
    }


    @app.route(method="UserInfo", service="User")
    @pre.catch(rule=rule)
    def user_info_handler(params):
        """ 查询用户信息
        """
        # 这里的params是交验完所有入参的数组(不建议用于处理实时数据流)
        for item in params:
            yield HelloResponse(message="Hello %s" % item["user_id"])


Exception
------------

当意外情况发生时，`Mask` 会将异常的错误信息输出，并给出合适的响应到请求客户端，但是我们也提供了自定义异常响应的处理的钩子。

.. code-block:: python

    @app.exception_handler(ZeroDivisionError)
    def zero_division_error_handler(request, context):
        context.abort(grpc.StatusCode.INTERNAL, "自定义错误说明")


需要注意的是，针对同一种类型的错误，不能多次注册钩子，后注册的钩子会覆盖掉前面注册的回调函数。因为一旦异常被处理，就应该给出响应
其它的函数就不需要被执行了。

除了装饰器类型的异常捕获钩子注册方式之外，我们也提供了函数形式的注册方式，方便其它插件系统添加异常捕获回调。

.. code-block:: python

    def zero_division_error_handler(request, context):
        context.abort(grpc.StatusCode.INTERNAL, "自定义错误说明")

    # 通过函数的方式添加异常钩子
    app.register_exception_handler(ZeroDivisionError, zero_division_error_handler)


Context
-----------

`Mask` 参考(抄袭)了 `Flask` 全局变量的优秀设计，同样实现了全局的 `request` , `g` , `current_app` 参数。

`Mask` 会自动判断用户实现的函数中是否有 `request` 和 `context` 参数，如果没有这两个参数的话在实际调用时将不会传入，用户需要使用全局变量进行获取

.. code-block:: python

    # 线程安全的全局参数
    from mask import g, request, current_app


Extensions
---------------

`Mask` 的插件实现机制与 `Flask` 基本一致，用户可根据自己的需求实现响应的插件。

目前提供的插件如下:


==================== ================================ ====================================================
   Project Name                         Intro                              Links
==================== ================================ ====================================================
Mask-SQAlchemy        Mask extension for SQLAlchemy
Mask-Redis            Mask extension for Redis
==================== ================================ ====================================================


Reflection
---------------

`Mask` 支持 `gRPC` 反射功能的快速开启，仅需要在配置中设置 `REFLECTION=True` 即可


TLS Support
--------------

关于 SSL/TLS 的相关知识点较多，请自行查阅相关文档，下面提供几个创建自签名证书的实例命令，请根据实际情况使用！

* 私有证书签发机构 `CA` 生成自签证书

.. code-block:: shell

    # 使用 `genrsa` 创建 `CA` 私钥 `ca.key` , 长度为4096bit
    openssl genrsa -passout pass:1234 -des3 -out ca.key 4096
    # 创建 `CA` 自签名证书
    # 使用 `req` 只能生成签署请求，需要加 `-x509` 实现自己发出请求、自己签署
    openssl req -passin pass:1111 -new -x509 -days 365 -key ca.key -out ca.crt -subj  "/C=CN/ST=ZJ/L=HZ/O=Attractor/OU=www/CN=*"

* 创建服务器端相关证书

.. code-block:: shell

    # 创建服务端证书私钥
    openssl genrsa -passout pass:1111 -des3 -out server.key 4096
    # 创建证书签署请求 （签发证书后，即可删除）
    openssl req -passin pass:1111 -new -key server.key -out server.csr -subj  "/C=CN/ST=ZJ/L=HZ/O=Attractor/OU=www/CN=localhost"
    # 使用 `x509` 协议对证书申请文件进行签署 (此步骤一般由CA服务器执行)
    openssl x509 -req -passin pass:1111 -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt
    # 创建私钥时使用了加密存储，需要提取后，显示在server.key中，如果不是加密存储，则不需要此步骤
    openssl rsa -passin pass:1111 -in server.key -out server.key

* 创建客户端相关证书

.. code-block:: shell

    # 创建客户端证书私钥
    openssl genrsa -passout pass:1111 -des3 -out client.key 4096
    # 创建证书申请请求 （签发证书后，即可删除）
    openssl req -passin pass:1111 -new -key client.key -out client.csr -subj  "/C=CN/ST=ZJ/L=HZ/O=Attractor/OU=www/CN=localhost"
    # 签发客户端证书
    openssl x509 -passin pass:1111 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out client.crt
    # 提取加密的私钥文件，存储在client.key中，如果不是加密存储，则不需要此步骤
    openssl rsa -passin pass:1111 -in client.key -out client.key


Deploy to Production
----------------------------

运行 `Mask` 非常简单，直接调用 `app.run()` 即可。
在生产环境中推荐使用 `supervisor` 或者 `docker-compose` 等工具监听服务的运行状态。

* TODO: `Prometheus` 指标接口实现
