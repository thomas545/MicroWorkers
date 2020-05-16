import six
import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.fields import SkipField


class Base64ImageField(serializers.ImageField):
    def to_representation(self, data):
        try:
            return data.url
        except:
            return ""

    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if "data:" in data and ";base64," in data:
                # Break out the header from the base64 content
                header, data = data.split(";base64,")

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_image")

            # Generate file name:
            # 12 characters are more than enough.
            file_name = str(uuid.uuid4())[:12]
            # Get the file name extension:

            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension,)

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == None else extension

        return extension


class Base64FieldMixin(object):
    def _decode(self, data):
        if isinstance(data, str) and data.startswith("data:"):
            # base64 encoded file - decode
            # format ~= data:image/X,
            format, datastr = data.split(";base64,")
            ext = format.split("/")[-1]  # guess file extension
            if ext[:3] == "svg":
                ext = "svg"

            data = ContentFile(
                base64.b64decode(datastr), name="{}.{}".format(uuid.uuid4(), ext)
            )

        elif isinstance(data, str) and data.startswith("http"):
            raise SkipField()

        return data

    def to_internal_value(self, data):
        data = self._decode(data)
        return super(Base64FieldMixin, self).to_internal_value(data)


class Base64ImageMixinField(Base64FieldMixin, serializers.ImageField):
    pass


class Base64FileMixinField(Base64FieldMixin, serializers.FileField):
    pass
