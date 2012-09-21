from datetime import datetime
import unittest

from django.db import models
from django.http import HttpResponse
from django.utils import simplejson

from dynamicresponse.json_response import JsonResponse


class ModelWithSerializeFields(models.Model):
    title = models.CharField('Title', max_length=200)
    text = models.TextField('Text')
    _password = models.CharField('Password', max_length=100)

    def serialize_fields(self):
        return [
            'id',
            'title'
        ]

class ModelWithoutSerializeFields(models.Model):
    title = models.CharField('Title', max_length=200)
    text = models.TextField('Text')
    _password = models.CharField('Password', max_length=100)

class ModelWithVersionedSerializeFields(models.Model):
    title = models.CharField('Title', max_length=200)
    text = models.TextField('Text')
    _password = models.CharField('Password', max_length=100)

    def versioned_serialize_fields(self, version):
        if version == 'v1':
            return ['id']
        return [
            'id',
            'title'
        ]

class EmittableResource(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.text = 'always happy'

    def __emittable__(self):
        return dict([(k, getattr(self, k)) for k in ('id', 'title')])

class EmittableResource(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.text = 'always happy'

    def __emittable__(self):
        return dict([(k, getattr(self, k)) for k in ('id', 'title')])

class VersionedEmittableResource(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.text = 'always happy'

    def __versioned_emittable__(self, version):
        if version == 'v1':
            return dict([(k, getattr(self, k)) for k in ('id', 'title')])
        return dict([(k, getattr(self, k)) for k in ('id', 'title', 'text')])



class JsonResponseTest(unittest.TestCase):

    def setUp(self):
        self.testObj = { 'testval': 99, 'testStr': 'Ice Cone', 'today': datetime(2012, 5, 17) }
        self.jsonres = JsonResponse(self.testObj)

        self.modelWithSerializeFields = JsonResponse(ModelWithSerializeFields(title='Hadouken',
                                                                            text='is said repeatedly in Street Fighter',
                                                                            _password='is secret'))

        self.modelbaseWithoutSerializeFields = ModelWithoutSerializeFields(title='Hadouken',
                                                                        text='is said repeatedly in Street Fighter',
                                                                        _password='is secret')

        self.modelWithoutSerializeFields = JsonResponse(self.modelbaseWithoutSerializeFields)

        self.modelWithVersionedSerializeFieldsV1 = JsonResponse(ModelWithVersionedSerializeFields(title='Hadouken',
                                                                            text='is said repeatedly in Street Fighter',
                                                                            _password='is secret'), version='v1')

        self.modelWithVersionedSerializeFieldsVNull = JsonResponse(ModelWithVersionedSerializeFields(title='Hadouken',
                                                                            text='is said repeatedly in Street Fighter',
                                                                            _password='is secret'))

    def testEmittableResource(self):
        emittableResource = EmittableResource(1, 'test')
        resp = JsonResponse(emittableResource)
        result = simplejson.loads(resp.content)
        for key, value in result.items():
            self.assertEqual(getattr(emittableResource, key).__str__(), value.__str__())
        self.assert_('id' in result.keys())
        self.assert_('title' in result.keys())
        self.assert_('text' not in result.keys())

        # test that version is ignored
        resp = JsonResponse(emittableResource, version='v1')
        result = simplejson.loads(resp.content)
        for key, value in result.items():
            self.assertEqual(getattr(emittableResource, key).__str__(), value.__str__())
        self.assert_('id' in result.keys())
        self.assert_('title' in result.keys())
        self.assert_('text' not in result.keys())

    def testVersionedEmittableResource(self):
        versionedEmittableResource = VersionedEmittableResource(1, 'test')
        resp = JsonResponse(versionedEmittableResource)
        result = simplejson.loads(resp.content)
        for key, value in result.items():
            self.assertEqual(getattr(versionedEmittableResource, key).__str__(), value.__str__())
        self.assert_('id' in result.keys())
        self.assert_('title' in result.keys())
        self.assert_('text' in result.keys())

        resp = JsonResponse(versionedEmittableResource, version='v1')
        result = simplejson.loads(resp.content)
        for key, value in result.items():
            self.assertEqual(getattr(versionedEmittableResource, key).__str__(), value.__str__())
        self.assert_('id' in result.keys())
        self.assert_('title' in result.keys())
        self.assert_('text' not in result.keys())

    def testIsInstanceOfHttpResponse(self):
        self.assertTrue(isinstance(self.jsonres, HttpResponse), 'should be an instance of HttpResponse')
        self.assertTrue(isinstance(self.modelWithSerializeFields, HttpResponse), 'should be an instance of HttpResponse')
        self.assertTrue(isinstance(self.modelWithoutSerializeFields, HttpResponse), 'should be an instance of HttpResponse')

    def testSetsCorrectMimetype(self):
        self.assertEqual(self.jsonres['Content-Type'], 'application/json; charset=utf-8')
        self.assertEqual(self.modelWithSerializeFields['Content-Type'], 'application/json; charset=utf-8')
        self.assertEqual(self.modelWithoutSerializeFields['Content-Type'], 'application/json; charset=utf-8')

    def testDictContentConvertsToJson(self):
        result = simplejson.loads(self.jsonres.content)

        for key, value in result.items():
            self.assertEqual(self.testObj.get(key).__str__(), value.__str__())

    def testModelWithSerializeFieldsConvertsToJson(self):
        to_equal = { u'id': None, u'title': u'Hadouken' }
        result = simplejson.loads(self.modelWithSerializeFields.content)

        for key, value in result.items():
            self.assertEqual(to_equal.get(key).__str__(), value.__str__())

    def testModelWithVersionedSerializeFieldsConvertsToJson(self):
        v1_to_equal = { u'id': None }
        vnull_to_equal = { u'id': None, u'title': u'Hadouken' }
        v1_result = simplejson.loads(self.modelWithVersionedSerializeFieldsV1.content)
        vnull_result = simplejson.loads(self.modelWithVersionedSerializeFieldsVNull.content)

        for key, value in v1_result.items():
            self.assertEqual(v1_to_equal.get(key).__str__(), value.__str__())
        for key, value in vnull_result.items():
            self.assertEqual(vnull_to_equal.get(key).__str__(), value.__str__())


    def testModelWithoutSerializeFieldsConvertsToJson(self):
        to_equal = { u'text': u'is said repeatedly in Street Fighter', u'title': u'Hadouken', u'id': None }
        result = simplejson.loads(self.modelWithoutSerializeFields.content)

        for key, value in result.items():
            self.assertEqual(to_equal.get(key).__str__(), value.__str__())

    def testModelsWithDynamiclyAddedFieldsConvertsToJson(self):
        to_equal = { u'text': u'is said repeatedly in Street Fighter', u'title': u'Hadouken', u'id': None, u'dummy': u'blah' }

        self.modelbaseWithoutSerializeFields.dummy = "blah"
        self.modelbaseWithoutSerializeFields._dummy = "blah"
        result = simplejson.loads(JsonResponse(self.modelbaseWithoutSerializeFields).content)

        for key, value in result.items():
            self.assertEqual(to_equal.get(key).__str__(), value.__str__())
