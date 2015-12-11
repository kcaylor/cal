import falcon
from bson import ObjectId


class DataCollection(object):

    def __init__(self, collection):
        self.objects = collection
        self.resource = 'data'

    def on_get(self, req, resp):
        limit = req.get_param_as_int('limit') or 50

        try:
            result = self.objects.find({}).limit(limit)
        except Exception as ex:
            self.logger.error(ex)
            description = ('Something has gone terribly wrong')

            raise falcon.HTTPServiceUnavailable(
                'Service Outage',
                description,
                30)

        items = []
        [items.append(item) for item in result]
        req.context['result'] = items
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        try:
            doc = req.context['doc']
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing data object',
                'A data object must be submitted in the request body')

        result = self.objects.insert_one(doc)
        doc['_id'] = str(result.inserted_id)
        # doc['links'] = {'self': _make_uri(self.resource, doc)}
        resp.status = falcon.HTTP_201
        resp.location = '/data/%s' % (str(result.inserted_id))
        req.context['result'] = [doc]


class DataItem(object):

    def __init__(self, collection):
        self.objects = collection
        self.resource = 'data'

    def on_get(self, req, resp, id):
        try:
            _id = ObjectId(id)
        except:
            raise falcon.HTTPBadRequest(
                'Bad ObjectId',
                'You need to provide a valid ObjectId for item requests')
        content = self.objects.find_one({'_id': _id})
        if content:
            req.context['result'] = [content]
        else:
            raise falcon.HTTPNotFound()
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, id):
        self.objects.delete_one({'_id': ObjectId(id)})
        resp.status = falcon.HTTP_204
