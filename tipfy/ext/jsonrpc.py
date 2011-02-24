# -*- coding: utf-8 -*-
"""
    tipfy.ext.jsonrpc
    ~~~~~~~~~~~~~~~~~

    Tipfy extension to create JSON-RPC services.

    :copyright: 2010 Rodrigo Moraes.
    :license: Apache, see LICENSE.txt for more details.
"""
from django.utils import simplejson

from lovely.jsonrpc.dispatcher import JSONRPCDispatcher

from tipfy import Response, cached_property


class JSONRPCMixin(object):
    """A RequestHandler mixin to set a JSON-RPC service. Example usage:

    .. code-block:: python

       from tipfy import RequestHandler
       from tipfy.ext.jsonrpc import JSONRPCMixin


       class MyJSONRPCService(object):
           def echo(self, value):
               return value


       class JsonHandler(RequestHandler, JSONRPCMixin):
           #: The service instance.
           jsonrpc_service = MyJSONRPCService()

           #: The service description.
           jsonrpc_name = 'JSONRPC Echo Service',
           jsonrpc_summary = 'This services echoes whatever it receives.'
    """
    #: The service instance.
    jsonrpc_service = None
    #: The service description.
    jsonrpc_name = 'JSONRPC Service',
    jsonrpc_summary = 'JSONRPC Service'
    jsonrpc_address = None
    jsonrpc_help = None

    @cached_property
    def json_rpc_dispatcher(self):
        return JSONRPCDispatcher(instance=self.jsonrpc_service,
                                 name=self.jsonrpc_name,
                                 summary=self.jsonrpc_summary,
                                 help=self.jsonrpc_help,
                                 address=self.jsonrpc_address,
                                 json_impl=simplejson)

    def post(self, **kwargs):
        res = self.json_rpc_dispatcher.dispatch(self.request.data)
        return Response(res, mimetype='application/json')