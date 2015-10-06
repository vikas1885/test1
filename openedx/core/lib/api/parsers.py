from rest_framework import exceptions
from rest_framework import parsers


# Figure out what to raise on no disposition header or mismatched filename

class ImageUploadParser(parsers.FileUploadParser):
    media_type = 'image/*'

    @property
    def image_types(self):
        if not getattr(self, '_image_types', None):
            self._image_types = set()
            for type_ in IMAGE_TYPES.values():
                self._image_types.update(type_['mimetypes'])
        return self._image_types

    def parse(self, stream, media_type=None, parser_context=None):
        supported_image_types = parser_context['view'].supported_image_types
        if media_type not in supported_image_types:
            raise exceptions.UnsupportedMediaType(media_type)
        filename = self.get_filename(stream, media_type, parser_context)

        ext = '.{}'.format(filename.rsplit('.', 1)[1])
        if ext not in supported_image_types[media_type]:
        	raise TypeError("Filename does not match requested content-type. Filename: {}, image_type: {}".format(filename, media_type))
        return super(ImageUploadParser, self).parse(stream, media_type, parser_context)


class MergePatchParser(parsers.JSONParser):
    """
    Custom parser to be used with the "merge patch" implementation (https://tools.ietf.org/html/rfc7396).
    """
    media_type = 'application/merge-patch+json'
