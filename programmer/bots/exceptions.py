#-*- coding: utf-8 -*-

from __future__ import unicode_literals
import traceback

class MQException(Exception):
	def __init__(self, message):
		super(MQException, self).__init__(message)


class InvalidArgument(MQException):
	def __init__(self, argument, got=None, expected=None, docs=None):
		message = 'Argument {} is invalid.'.format(repr(argument))
		if expected is list:
			message += " Should be one of {}.".format(expected)
		elif expected:
			message += " Should be of type {}.".format(expected)

		if got:
			message += " Got {}.".format(repr(got))
		if docs:
			message += " For more information see {}".format(docs)

		super(InvalidArgument, self).__init__(message)

class PipelineError(MQException):
	def __init__(self, argument):
		if type(argument) is type and issubclass(argument, Exception):
			message = "pipeline failed - {}".format(traceback.format_exc(argument))
		else:
			message = "pipeline failed - {}".format(repr(argument))

		super(PipelineError, self).__init__(message)

class PipelineFactoryError(MQException):
	pass

class MQHarmonizationException(MQException):
	def __init__(self, message):
		super(MQHarmonizationException, self).__init__(message)

class InvalidValue(MQHarmonizationException):
	def __init__(self, key, value, reason=''):
		if reason:
			reason = ' : ' + reason
		message = 'invalid value {value!r} ({type}) for key {key!r}{reason}'.format(
			value=value, type=type(value), key=key, reason=reason
		)

		super(InvalidValue, self).__init__(message)

class InvalidKey(MQHarmonizationException):
	def __init__(self, key):
		message = 'invalid key {}'.format(repr(key))

		super(InvalidKey, self).__init__(message)

class KeyExists(MQHarmonizationException):
	def __init__(self, key):
		message = 'Key {} already exists'.format(repr(key))

		super(KeyExists, self).__init__(message)

class KeyNotExists(MQHarmonizationException):
	def __init__(self, key):
		message = 'Key {} not exists'.format(repr(key))

		super(KeyNotExists, self).__init__(message)