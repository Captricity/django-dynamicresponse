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

class modelWithVersionedSerializeFields(models.Model):
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

        self.modelWithVersionedSerializeFieldsV1 = JsonResponse(modelWithVersionedSerializeFields(title='Hadouken',
                                                                            text='is said repeatedly in Street Fighter',
                                                                            _password='is secret'), version='v1')

        self.modelWithVersionedSerializeFieldsVNull = JsonResponse(modelWithVersionedSerializeFields(title='Hadouken',
                                                                            text='is said repeatedly in Street Fighter',
                                                                            _password='is secret'))


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
