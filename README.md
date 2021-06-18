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
