"""
Custom DRF request parsers.  These can be used by views to handle different
content types, as specified by `<Parser>.media_type`.

To use these in an APIView, set `<View>.parser_classes` to a list including the
desired parsers.  See http://www.django-rest-framework.org/api-guide/parsers/
for details.
"""

from rest_framework import exceptions
from rest_framework import parsers


class ImageUploadParser(parsers.FileUploadParser):
    """
    Handles upload of images, ensuring that the image type is supported, and
    that the uploaded filename matches the Content-type.

    Requirements:
        * The view must have a View.supported_image_types attribute whose keys
          are the mimetypes of the supported image formats, and whose values
          are lists of acceptable file extensions for each content type.

          Example:

              supported_image_types = {'image/jpeg': ['.jpeg', '.jpg']}

        * Content-type must be set to a supported subtype of image/* (as
          defined in View.supported_image_types above).

          Example:

              Content-type: image/jpeg

        * Content-disposition must include a filename with a valid extensions
          for the specified Content-type.

          Example

              Content-disposition: attachment; filename="profile.jpg"

    TODO:
        Figure out what to raise on no disposition header or mismatched
        filename
    """

    media_type = 'image/*'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parse the request, returning a DataAndFiles object with the data dict
        left empty, and the body of the request placed in files['file'].
        """

        supported_image_types = parser_context['view'].supported_image_types
        if media_type not in supported_image_types:
            raise exceptions.UnsupportedMediaType(media_type)
        filename = self.get_filename(stream, media_type, parser_context)

        ext = '.{}'.format(filename.rsplit('.', 1)[1])
        if ext not in supported_image_types[media_type]:
            msg = "Filename does not match requested content-type. Filename: {}, image_type: {}"
            raise TypeError(msg.format(filename, media_type))
        return super(ImageUploadParser, self).parse(stream, media_type, parser_context)


class MergePatchParser(parsers.JSONParser):
    """
    Custom parser to be used with the "merge patch" implementation (https://tools.ietf.org/html/rfc7396).
    """
    media_type = 'application/merge-patch+json'
