from falcon import testing as test
import falcon
from app.app import api, config
import json
from bson import ObjectId


class TestBase(test.TestBase):

    def setUp(self):
        self.config = config
        self.app = api
        self.srmock = test.StartResponseMock()

    def simulate_request(self, path, *args, **kwargs):

        env = test.create_environ(
            path=path, **kwargs)
        return self.app(env, self.srmock)

    def simulate_get(self, *args, **kwargs):
        kwargs['method'] = 'GET'
        return self.simulate_request(*args, **kwargs)

    def simulate_post(self, *args, **kwargs):
        kwargs['method'] = 'POST'
        return self.simulate_request(*args, **kwargs)

    def simulate_delete(self, *args, **kwargs):
        kwargs['method'] = 'DELETE'
        return self.simulate_request(*args, **kwargs)


class TestLinkMiddleWare(TestBase):

    def setUp(self):
        super(TestLinkMiddleWare, self).setUp()
        result = self.simulate_post('/v1/data', body='{"name":"dog"}')
        self.new_item = json.loads(result[0])[0]
        self.entry_path = '/v1/data/' + self.new_item['_id']

    def tearDown(self):
        self.simulate_delete('/v1/data/' + self.new_item['_id'])
        super(TestLinkMiddleWare, self).tearDown()

    def test_middleware_returns_links(self):
        result = self.simulate_get(self.entry_path)
        self.item = json.loads(result[0])[0]
        self.assertTrue('links' in self.item.keys())
        links = self.item['links']
        self.assertTrue(type(links) is dict)
        self.assertTrue('self' in links.keys())

    def test_middleware_uses_correct_protocol(self):
        result = self.simulate_get(self.entry_path)
        self.item = json.loads(result[0])[0]
        links = self.item['links']
        protocol = links['self'].split(':', 1)[0]
        self.assertTrue(protocol == self.config['PROTOCOL'])


class TestDataEntry(TestBase):

    def setUp(self):
        super(TestDataEntry, self).setUp()
        result = self.simulate_get('/v1/data')
        self.existing_item = json.loads(result[0])[0]
        result = self.simulate_post('/v1/data', body='{"name":"dog"}')
        self.new_item = json.loads(result[0])[0]
        self.entry_path = '/v1/data/' + self.new_item['_id']

    def tearDown(self):
        self.simulate_delete('/v1/data/' + self.new_item['_id'])
        super(TestDataEntry, self).tearDown()

    def test_get_returns_200_when_entry_exists(self):
        self.simulate_get(self.entry_path)
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

    def test_get_returns_404_when_entry_does_not_exist(self):
        path = '/v1/data/' + str(ObjectId())
        self.simulate_get(path)
        self.assertEqual(self.srmock.status, falcon.HTTP_404)

    def test_delete_returns_204_no_matter_what(self):
        path = '/v1/data/' + str(ObjectId())
        self.simulate_delete(path)
        self.assertEqual(self.srmock.status, falcon.HTTP_204)

    def test_post_returns_201_when_successful(self):
        path = '/v1/data'
        self.simulate_post(path, body='{"test":"data"}')
        self.assertEqual(self.srmock.status, falcon.HTTP_201)
