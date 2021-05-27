# -*- coding: utf-8 -*-
import grpc


class BaseResponse:
    """ PreRequest basic response class
    """

    def __call__(self, fuzzy=False, error=None, **options):
        """ Use __call__ function to generate response

        :param error: error
        :type error: ParamsValueError
        """
        if error:
            self.error = error

        return self.error.form_message(fuzzy)


class GlibResponse(BaseResponse):
    """ Handler response for glib framework
    """

    def __call__(self, fuzzy=False, formatter=None, error=None, **options):
        """ Use __call__ function to generate response
        """
        result = super().__call__(fuzzy, error)
        options["context"].abort(grpc.StatusCode.INVALID_ARGUMENT, result)
