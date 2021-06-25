<p align="center">
    <a href="#readme">
        <img alt="Mask logo" src="https://mask.readthedocs.io/en/latest/_images/logo.png">
    </a>
</p>
<p align="center">
    <a href="https://travis-ci.com/github/Eastwu5788/Mask"><img alt="Travis" src="https://travis-ci.com/Eastwu5788/Mask.svg?branch=master"></a>
    <a href="https://coveralls.io/github/Eastwu5788/Mask"><img alt="Coveralls" src="https://coveralls.io/repos/github/Eastwu5788/Mask/badge.svg?branch=master"></a>
    <a href="https://github.com/Eastwu5788/Mask/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/Eastwu5788/Mask?color=brightgr"></a>
    <a href="https://mask.readthedocs.io/en/latest"><img alt="Docs" src="https://readthedocs.org/projects/mask/badge/?version=latest"></a>
    <a href="https://pypi.org/project/Mask/"><img alt="PyPI" src="https://img.shields.io/pypi/v/Mask?color=brightgreen"></a>
    <a href="https://gitter.im/mask-cn/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge"><img alt="IM" src="https://badges.gitter.im/pre-request/community.svg"/></a>
</p>

## Mask

A gRpc server just like `Flask`.

### Install

`Mask` support pypi packages, you can simply install by:

```
pip install mask
```

### Document

`Mask` manual could be found at:  https://mask.readthedocs.io/en/latest


### A Simple Example

This is very easy to use `Mask` in your project.

```
from mask import Mask
from mask.parse import pre, Rule


app = Mask(__name__)


rule = {
    "name": Rule(type=str, gte=2, dest="Name")
}


@app.route(method="SayHello", service="Hello")
def say_hello(request, context):
    """ Handler SayHello request
    """
    params = pre.parse(rule=rule, request=request, context=context)
    return HelloResponse(message="Hello Reply: %s" % params["Name"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1020)
```

### Service

`Mask` support `Service` to organize a group of route which is likely with `Blueprint` in `Flask`.

```

    # 3p
    from mask import Mask, Service
    from mask.parse import pre, Rule
    # project
    from examples.protos.hello_pb2 import HelloResponse


    app = Mask(__name__)
    app.config["REFLECTION"] = True


    # Bind service to application
    service = Service(name="Hello")
    app.register_service(service)


    rule = {
        "name": Rule(type=str, gte=2, dest="Name")
    }

    # Service route
    @service.route(method="SayHello")
    def say_hello_handler(request, context):
        """ Handler SayHello request
        """
        params = pre.parse(rule=rule, request=request, context=context)
        return HelloResponse(message="Hello Reply: %s" % params["Name"])


    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=1020)

```

### Middleware 

`Mask` support middleware to hook before request and after request.

```
# 3p
from mask import Mask
# project
from examples.protos.hello_pb2 import HelloResponse


app = Mask(__name__)
app.config["REFLECTION"] = True


def before_request(request, context):
    print(request.name)


def after_request(response):
    print(response.message)


app.before_request(before_request)
app.after_request(after_request)


@app.route(method="SayHello", service="Hello")
def say_hello_handler(request, context):
    """ Handler SayHello request
    """
    return HelloResponse(message="Hello Reply: %s" % request.name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1020)
```



### Coffee

Please give me a cup of coffee, thank you!

BTC: 1657DRJUyfMyz41pdJfpeoNpz23ghMLVM3

ETH: 0xb098600a9a4572a4894dce31471c46f1f290b087

### Links

* Documentaion: https://mask.readthedocs.io/en/latest
* Release: https://github.com/Eastwu5788/Mask/releases
* Code: https://github.com/Eastwu5788/Mask
* Issue tracker: https://github.com/Eastwu5788/Mask/issues
* Test status: https://coveralls.io/github/Eastwu5788/Mask
