# -*- coding: utf-8 -*-
"""
    tipfy.ext.pyamf
    ~~~~~~~~~~~~~~~

    PyAMF Gateway for Google App Engine.

    This gateway allows you to expose functions in Google App Engine web
    applications to AMF clients and servers.

    :copyright: 2007-2009 The PyAMF Project.
    :copyright: 2010 tipfy.org.
    :license: MIT License, see LICENSE.txt for more details.
"""
from __future__ import absolute_import

from pyamf import remoting
from pyamf.remoting import gateway

from tipfy import Response, abort

__all__ = ['AmfRequestHandlerMixin']

class AmfRequestHandlerMixin(object):
    """Google App Engine Remoting Gateway."""
    def set_gateway(self, *args, **kwargs):
        self.gateway = gateway.BaseGateway(*args, **kwargs)

    def process_request(self):
        body = self.request.data
        stream = None
        timezone_offset = self.gateway._get_timezone_offset()

        # Decode the request
        try:
            request = remoting.decode(body, strict=self.gateway.strict,
                logger=self.gateway.logger, timezone_offset=timezone_offset)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            abort(400)

        if self.gateway.logger:
            self.gateway.logger.info("AMF Request: %r" % request)

        # Process the request
        try:
            response = self.get_response(request)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            abort(500)

        if self.gateway.logger:
            self.gateway.logger.info("AMF Response: %r" % response)

        # Encode the response
        try:
            stream = remoting.encode(response, strict=self.gateway.strict,
                logger=self.gateway.logger, timezone_offset=timezone_offset)
        except:
            abort(500)

        response = stream.getvalue()
        headers = {
            'Content-Type':   remoting.CONTENT_TYPE,
            'Content-Length': str(len(response)),
            'Server':         gateway.SERVER_NAME,
        }
        return Response(response, headers=headers)

    def get_response(self, request):
        """
        Processes the AMF request, returning an AMF response.

        @param request: The AMF Request.
        @type request: L{Envelope<pyamf.remoting.Envelope>}
        @rtype: L{Envelope<pyamf.remoting.Envelope>}
        @return: The AMF Response.
        """
        response = remoting.Envelope(request.amfVersion, request.clientType)

        for name, message in request:
            self.request.amf_request = message

            processor = self.gateway.getProcessor(message)
            response[name] = processor(message, http_request=self.request)

        return response
