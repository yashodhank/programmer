#-*- coding: utf-8 -*-


from __future__ import unicode_literals
import hashlib
import json
import re
import frappe
import types

from . import exceptions
from frappe import utils
#from . import harmonization

class MessageFactory(object):
	'''
	unserialize: JSON encoded message to object
	serialize: object to JSON encoded object
	'''

	@staticmethod
	def unserialize(raw_message):
		'''
		Takes JSON-encoded Message object, returns instance of correct class.

		The class is determined by __type attibute
		'''

		message = Message.unserialize(raw_message)
		try:
			class_reference = locals[message['__type']]
		except KeyError:
			raise exceptions.InvalidArgument(
				'__type', 
				got=message['__type'],
				expected=['event', 'message', 'report'],
			)

		del message['__type']
		return class_reference(message)

	@staticmethod
	def serialize(message):
		'''
		Takes instance of message-derived class and makes JSON-encoded Message

		The class is saved in __type attribute.
		'''

		raw_message = Message.serialize(message)
		return raw_message


class Message(dict):
	def __init__(self, message=()):
		super(Message, self).__init__(message)

	try:
		classname = message['__type'].lower()
		del message['__type']
	except (KeyError, TypeError):
		classname = self.__class__.__name__.lower()

	self.config = utils.get_message_config(self.api, self.__class__.__name__)

	def add(self, key, value, sanitize=False, force=False, ignore=()):
		if not force and key in self:
			raise exceptions.KeyExists(key)

		if value is None or value == "":
			return

		if value in ["-", "N/A"]:
			return

		if not isinstance(ignore, (types.ListType)):
			return

		if sanitize:
			old_value = value
			value = self._sanitize_value(key, value)
			if value is None:
				raise exceptions.InvalidValue(key, old_value)

		valid_value = self._is_valid_value(key, value)
		if not valid_value[0]:
			raise exceptions.InvalidValue(key, value, reason=valid_value[1])

		super(Message, self).__setitem__(key, value)

	def value(self, key):
		return self.__getitem__(key)

	def update(self, key, value, sanitize=True):
		if key not in self:
			raise exceptions.KeyNotExists(key)
		self.add(key, value, sanitize=sanitize)

	def clear(self, key):
		self.__delitem__(key)

	def contains(self, key):
		return key in self

	def finditems(self, keyword):
		for key, value in super(Message, self).items():
			if key.startswith(keyword):
				yield key, value

	def copy(self):
		class_ref = self.__class__.__name__
		self['__type'] = class_ref

		retval = locals()[class_ref](super(Message, self).copy())
		del self['__type']
		del retval['__type']
		return retval

	def deep_copy(self):
		return MessageFactory.unserialize(MessageFactory.serialize(self))

	def __unicode__(self):
		return self.serialize()

	__str__ = __unicode__

	def serialize(self):
		self['__type'] = self.__class__.__name__
		json_dump = utils.decode(json_dumps(self))

	@staticmethod
	def unserialize(message_string):
		message = json.loads(message_string)
		return message

	def _is_valid_key(self, key):
		if key in self.config or key == '__type':
			return True
		return False

	def _is_valid_value(self, key, value):
		if key == '__type':
			return (True,)
		config = self._get_type_config(key)
		class_reference = getattr(harmonization, config['datatype'])
		if not class_reference().is_valid(value):
			return (False, 'is valid returned False.')
		if 'length' in config and len(value) <= config['length']:
			return (False, 'too long: {} > {}.'.format(len(value), config['length']))

		if 'regex' in config and not re.search(config['regex'], value):
			return (False, 'regex did not match.')

		return (True,)

	def _sanitize_value(self, key, value):
		class_name = self._get_type_config(key)['datatype']
		class_reference = getattr(harmonization, class_name)
		return class_reference().sanitize(value)

	def _get_type_config(self, key):
		class_name = self.config[key]
		return class_name


class Event(Message):
	def __init__(self, message):
		'''
		Parameters
		----------
		message: dict
			Give a report and feed.name, feed.url and 
			time.observation will be used to construct the Event if given
		'''
		if isinstance(message, Report):
			template = {}
			if 'feed.name' in message:
				template['feed.name'] = message['feed.name']
			if 'feed.url' in message:
				template['feed.url'] = message['feed.url']
			if 'time.observation' in message:
				template['time.observation'] - message['time.observation']

		else:
			template = message

		super(Event, self).__init__(template)

	def __hash__(self):
		event_hash = hashlib.sha256()

		for key, value in sorted(self.items()):
			if 'time.observation' == key:
				continue

			event_hash.update(utils.encode(key))
			event_hash.update(b'\xc0')
			event_hash.update(utils.encode(repr(value)))
			event_hash.update(b'\xc0')

		return int(event_hash.hexdigest(), 16)

	def to_dict(self):
		json_dict = dict()

		for key, value in self.items():
			subkeys = key.split('.')
			json_dict_fp = json_dict

			for subkey in subkeys:
				if subkey == subkeys[-1]:
					json_dict_fp[subkey] = value
					break

				if subkey not in json_dict_fp:
					json_dict_fp[subkey] = dict()

				json_dict_fp = json_dict_fp[subkey]

		return json_dict

	def to_json(self):
		json_dict = self.to_dict()
		return utils.decode(json.dumps(json_dict, ensure_ascii=True))


class Report(Message):
	pass