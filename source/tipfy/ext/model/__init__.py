# -*- coding: utf-8 -*-
"""
    tipfy.ext.model
    ~~~~~~~~~~~~~~~

    Model utilities extension.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
import pickle
import hashlib
import re
import unicodedata

from google.appengine.ext import db
from google.appengine.datastore import entity_pb

from werkzeug.exceptions import NotFound


def model_to_protobuf(models):
    """Converts one or more db.Model instances to encoded Protocol Buffers.
    Borrowed from http://blog.notdot.net/2009/9/Efficient-model-memcaching
    """
    if not models:
        return None
    elif isinstance(models, db.Model):
        return db.model_to_protobuf(models).Encode()
    else:
        return [db.model_to_protobuf(x).Encode() for x in models]


def model_from_protobuf(data):
    """Converts one or more encoded Protocol Buffers to db.Model instances.
    Borrowed from http://blog.notdot.net/2009/9/Efficient-model-memcaching
    """
    if not data:
        return None
    elif isinstance(data, str):
        return db.model_from_protobuf(entity_pb.EntityProto(data))
    else:
        return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]


def get_key(entity, prop_name):
    """Returns a encoded key from a ReferenceProperty without fetching the
    referenced entity.
    """
    getattr(entity.__class__, prop_name).get_value_for_datastore(entity)


def populate_entity(entity, **kwargs):
    """Sets a batch of property values in an entity."""
    properties = entity.properties()
    for key, value in kwargs.iteritems():
        if key in properties:
            setattr(entity, key, value)


def get_or_insert_with_flag(model, key_name, **kwargs):
    """Same as Model.get_or_insert(), but also returns a boolean flag
    indicating if the entity was inserted.
    """
    entity = model.get_by_key_name(key_name, parent=kwargs.get('parent'))
    if entity:
        return (entity, False)

    def txn():
        entity = model.get_by_key_name(key_name, parent=kwargs.get('parent'))
        if entity:
            return (entity, False)

        entity = model(key_name=key_name, **kwargs)
        entity.put()
        return (entity, True)

    return db.run_in_transaction(txn)


# Nice idea borrowed from Kay. See AUTHORS.txt for details.
def get_by_key_name_or_404(model, key_name):
    """Returns a model instance by key name or raises a 404 Not Found error."""
    obj = model.get_by_key_name(key_name)
    if obj:
        return obj
    raise NotFound()


def get_by_id_or_404(model, id):
    """Returns a model instance by id or raises a 404 Not Found error."""
    obj = model.get_by_id(id)
    if obj:
        return obj
    raise NotFound()


def get_or_404(model, key):
    """Returns a model instance by key or raises a 404 Not Found error."""
    obj = model.get(key)
    if obj:
        return obj
    raise NotFound()


def slugify(string, max_length=None, default=None):
    """Converts a string to slug format."""
    s = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').lower()
    s = re.sub('-+', '-', re.sub('[^a-zA-Z0-9-]+', '-', s)).strip('-')
    if not s:
        return default

    if max_length:
        # Restrict lenght without breaking words.
        while len(s) > max_length:
            if s.find('-') == -1:
                s = s[:max_length]
            else:
                s = s.rsplit('-', 1)[0]

    return s


class EtagProperty(db.Property):
    """Automatically creates an ETag based on the value of another property.
    Note: the ETag is only set or updated after the entity is saved.
    """
    def __init__(self, prop, *args, **kwargs):
        self.prop = prop
        super(EtagProperty, self).__init__(*args, **kwargs)

    def get_value_for_datastore(self, model_instance):
        v = self.prop.__get__(model_instance, type(model_instance))
        if not v:
            return None

        return hashlib.sha1(v).hexdigest()


class SlugProperty(db.Property):
    """Automatically creates a slug based on the value of another property.
    Note: the slug is only set or updated after the entity is saved.
    """
    def __init__(self, prop, max_length=None, *args, **kwargs):
        self.prop = prop
        self.max_length = max_length
        super(SlugProperty, self).__init__(*args, **kwargs)

    def get_value_for_datastore(self, model_instance):
        v = self.prop.__get__(model_instance, type(model_instance))
        if not v:
            return self.default

        return slugify(v, max_length=self.max_length, default=self.default)


class PickleProperty(db.Property):
    """A property for storing complex objects in the datastore in pickled form.
    From aetycoon: http://github.com/Arachnid/aetycoon/

    Example usage:
    >>> class PickleModel(db.Model):
    ... data = PickleProperty()

    >>> model = PickleModel()
    >>> model.data = {"foo": "bar"}
    >>> model.data
    {'foo': 'bar'}
    >>> model.put() # doctest: +ELLIPSIS
    datastore_types.Key.from_path(u'PickleModel', ...)
    >>> model2 = PickleModel.all().get()
    >>> model2.data
    {'foo': 'bar'}
    """
    data_type = db.Blob

    def get_value_for_datastore(self, model_instance):
        value = self.__get__(model_instance, model_instance.__class__)
        if value is not None:
            return db.Blob(pickle.dumps(value))

    def make_value_from_datastore(self, value):
        if value is not None:
            return pickle.loads(str(value))
