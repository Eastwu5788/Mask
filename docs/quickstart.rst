Quickstart
==============

Eager to get started? This page gives a good example to use `Mask`. It assumes you already have `Mask` installed
If you do not, head over to the Installation section.

Minimal Example
-------------------

`Mask` is based on `grpc` which use `protobuf` as the transfer protocol. therefore you must to define a `protobuf` file.

.. code-block:: text

    syntax="proto3";


    service Hello {
        rpc SayHello (HelloRequest) returns (HelloResponse) {}
    }

    message HelloRequest {
        string name = 1;
    }

    message HelloResponse {
        string message = 1;
    }

For more details about `protobuf` can be found at: https://github.com/protocolbuffers/protobuf
Now, you can write code with `Mask` to implement the protocol.

.. code-block:: python

    from mask import Mask

    app = Mask(__name__)

    @app.route(method="SayHello", service="Hello")
    def say_hello(request):
        """ Handler SayHello request
        """
        return HelloResponse(message="Hello Reply: %s" % request.name)

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=1020)


Request Parse
-----------------

`Mask` support parsing whether request parameters comply with specific rules.

.. code-block:: python

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


`Mask` use `pre-request` to parse request params. you can find more document about `pre-request` at:  https://github.com/Eastwu5788/pre-request

Service
-----------

`Mask` support `Service` to organize a group of route which is likely with `Blueprint` in `Flask`.

.. code-block:: python

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
