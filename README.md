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

A simple grpc server just like flask.

### Install

`Mask` support pypi packages, you can simply install by:

```
pip install mask
```

### Document

`Mask` manual could be found at: 


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

### Coffee

Please give me a cup of coffee, thank you!

BTC: 1657DRJUyfMyz41pdJfpeoNpz23ghMLVM3

ETH: 0xb098600a9a4572a4894dce31471c46f1f290b087

### Links

* Documentaion: 
* Release:
* Code: https://github.com/Eastwu5788/Mask
* Issue tracker: https://github.com/Eastwu5788/Mask/issues
* Test status: https://coveralls.io/github/Eastwu5788/Mask
