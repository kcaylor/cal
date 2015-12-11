# sample.py
import falcon
import json
from wsgiref import simple_server
# from data import DataCollection, DataItem
import data
from config import Config
from connection import db

data_collection = data.DataCollection(db.data)
data_item = data.DataItem(db.data)

config = Config()


def _make_route(resource, obj=None):
    route = ('/' + config['VERSION'] + '/' + resource)
    if type(obj) is dict:
        try:
            route += '/' + str(obj['_id'])
        except KeyError:
            print "Missing object id"
    return route


def _make_uri(resource, obj=None):
    return (config['PROTOCOL'] + '://' + config['SERVER'] + ':' +
            str(config['PORT']) + _make_route(resource, obj))

from json import JSONEncoder


class MongoEncoder(JSONEncoder):

    def default(self, obj, **kwargs):
        from bson import ObjectId
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return JSONEncoder.default(obj, **kwargs)


class LinkMiddleWare(object):

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        for item in req.context['result']:
            item['links'] = {
                'self': _make_uri(resource.resource, item)
            }


class MetaMiddleWare(object):

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        for item in req.context['result']:
            item['meta'] = ['api meta goes here']


class JSONTranslator(object):

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest(
                'Empty request body',
                'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(
                body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'], cls=MongoEncoder)


class QuoteResource:

    def on_get(self, req, resp):
        """Handles GET requests"""
        quote = {
            'quote': 'I\'ve always been more interested in the future than'
            'in the past.',
            'author': 'Grace Hopper'
        }
        resp.body = json.dumps(quote)

    def on_post(self, req, resp):
        """Handles POST requests"""
        quote = {
            'quote': 'You made it.',
            'author': 'Me'
        }
        resp.body = json.dumps(quote)


class Loader:

    def on_get(self, req, resp):
        """ Handles GET requests """
        token = 'loaderio-215743917cdfb58267c0f164a98c9683'
        resp.body = token

api = application = falcon.API(
    middleware=[JSONTranslator(), LinkMiddleWare(), MetaMiddleWare()])

api.add_route(_make_route('quote'), QuoteResource())
api.add_route(_make_route('data'), data_collection)
api.add_route(_make_route('data') + '/{id}', data_item)
api.add_route('/loaderio-215743917cdfb58267c0f164a98c9683', Loader())

# Useful for debugging problems in your API; works with pdb.set_trace()
if __name__ == '__main__':
    print "Running server on %s with port %s" % (
        str(config['SERVER']), str(config['PORT'])
    )
    httpd = simple_server.make_server(config['SERVER'], config['PORT'], api)
    httpd.serve_forever()
