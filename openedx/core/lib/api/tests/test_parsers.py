from collections import namedtuple
from io import BytesIO

from django.test import TestCase
from rest_framework import exceptions
from rest_framework.test import APITestCase, APIRequestFactory

from openedx.core.lib.api import parsers

class TestImageUploadParser(APITestCase):
    def setUp(self):
        self.parser = parsers.ImageUploadParser()
    	self.factory = APIRequestFactory()
    	supported_image_types = {
	    	'image/png': ['.png'],
	    	'image/jpeg': ['.jpg'],
    	}
    	self.view = namedtuple('view', ('supported_image_types',))(supported_image_types)

    def test_parse_supported_image(self):
    	"""
    	Test that ImageUploadParser returns empty data and content stored in
    	files['file'].
    	"""
    	request = self.factory.post(
    		'/',
    		content_type='image/png',
    		HTTP_CONTENT_DISPOSITION='attachment; filename="file.png"',
    	)
    	context = {'view': self.view, 'request': request}
        result = self.parser.parse(
        	stream=BytesIO('abcdefgh'), media_type='image/png', parser_context=context
        )
        self.assertEqual(result.data, {})
        self.assertIn('file', result.files)
        self.assertEqual(result.files['file'].read(), 'abcdefgh')

    def test_parse_unsupported_image(self):
    	"""
    	Test that ImageUploadParser raises an exception when parsing an
    	unsupported image format.
    	"""
    	request = self.factory.post(
    		'/',
    		content_type='image/tiff',
    		HTTP_CONTENT_DISPOSITION='attachment; filename="file.tiff"',
    	)
    	context = {'view': self.view, 'request': request}
    	with self.assertRaises(exceptions.UnsupportedMediaType):
        	self.parser.parse(
        		stream=BytesIO('abcdefgh'), media_type='image/tiff', parser_context=context
        	)

    def test_parse_mismatched_filename_and_mimetype(self):
    	"""
    	Test that ImageUploadParser raises an exception when the specified
    	content-type doesn't match the filename extension in the
    	content-disposition header.

    	TODO: This should probably raise a 400 (BadRequest).
    	"""
    	request = self.factory.post(
    		'/',
    		content_type='image/png',
    		HTTP_CONTENT_DISPOSITION='attachment; filename="file.jpg"',
    	)
    	context = {'view': self.view, 'request': request}
    	with self.assertRaises(TypeError):
        	self.parser.parse(
        		stream=BytesIO('abcdefgh'), media_type='image/png', parser_context=context
        	)

