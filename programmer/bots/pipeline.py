#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe

from . import exceptions
from frappe import utils

class PipelineFactory(object):
	@staticmethod
	def create(parameters):
		return Redis(parameters)

class Pipeline(object):
	def __init__(self, parameters):
		self.parameters = parameters
		self.destination_queues = set()
		self.internal_queue = None
		self.source_queue = None

	def connect(self):
		raise NotImplementedError

	def disconnect(self):
		raise NotImplementedError

	def sleep(self, interval):
		time.sleep(interval)

	def set_queues(self, queues, queues_type):
		if queues_type == 'source':
			self.source_queue = str(queues)
			self.internal_queue = str(queues) + '-internal'

		elif queues_type == 'destination':
			if queues and type(queues) is not list:
				queues = queues.split()
			self.destination_queues = queues
		else:
			raise exceptions.InvalidArgument(
				'queues_type', 
				got=queues_type,
				expected=['source', 'destination'])

class Redis(Pipeline):
	def connect(self):
		self.pipe = frappe.cache()

	def disconnect(self):
		pass

	def send(self, message):
		message = utils.encode(message)

		for destination_queue in self.destination_queues:
			try:
				self.pipe.lpush(destination_queue, message)
			except Exception as exc:
				raise exceptions.PipelineError(exc)

	def receive(self):
		try:
			if self.pipe.llen(self.internal_queue) > 0:
				return utils.decode(self.pipe.lindex(self.internal_queue, -1))
			return utils.decode(self.pipe.brpoplpush(self.source_queue, self.internal_queue, 0))
		except Exception as exc:
			raise exceptions.PipelineError(exc);

	def acknowledge(self):
		try:
			return self.pipe.rpop(self.internal_queue)
		except Exception as e:
			raise exceptions.PipelineError(e)

	def count_queued_messages(self, queues):
		queue_dict = dict()
		for queue in queues:
			try:
				queue_dict[queue] = self.pipe.llen(queue)
			except Exception as exc:
				raise exceptions.PipelineError(exc)
		return queue_dict

	def clear_queue(self, queue):
		'''
		Clear a queue by removing (deleting) the key,
		which is the same as an empty list in Redis
		'''
		try:
			return self.pipe.delete(queue)
		except Exception as exc:
			raise exceptions.PipelineError(exc)

# Algorithm
# ---------
# [Receive]     B RPOP LPUSH   source_queue ->  internal_queue
# [Send]        LPUSH          message      ->  destination_queue
# [Acknowledge] RPOP           message      <-  internal_queue

