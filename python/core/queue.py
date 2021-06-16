from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import threading
from typing import List, Tuple, Dict, Callable
import time


class DelayedElement():

	def __init__(self, *, element: object, delay_datetime: datetime):

		self.__element = element
		self.__delay_datetime = delay_datetime

	def get_element(self) -> object:
		return self.__element

	def get_delay_datetime(self) -> datetime:
		return self.__delay_datetime


class DelayedElementQueue():

	def __init__(self):

		self.__queue = []  # type: List[DelayedElement]
		self.__queue_semaphore = threading.Semaphore()

	def add(self, *, delayed_element: DelayedElement):

		self.__queue_semaphore.acquire()

		if len(self.__queue) == 0:
			self.__queue.append(delayed_element)
		else:
			_is_inserted = False
			for _delayed_element_index, _delayed_element in enumerate(self.__queue):
				if _delayed_element.get_delay_datetime() > delayed_element.get_delay_datetime():
					self.__queue.insert(_delayed_element_index, delayed_element)
					_is_inserted = True
					break
			if not _is_inserted:
				self.__queue.append(delayed_element)

		self.__queue_semaphore.release()

	def try_get(self) -> Tuple[bool, DelayedElement]:

		_delayed_element = None

		self.__queue_semaphore.acquire()

		_now = datetime.utcnow()
		if len(self.__queue) != 0:
			if _now >= self.__queue[0].get_delay_datetime():
				_delayed_element = self.__queue.pop()

		self.__queue_semaphore.release()

		return _delayed_element is not None, _delayed_element


class ExecutableElement(ABC):

	@abstractmethod
	def execute(self, *args, **kwargs) -> object:
		raise NotImplementedError()


class DefaultExecutableElement(ExecutableElement):

	def __init__(self, *, default_output: object):

		self.__default_output = default_output

	def execute(self, *args, **kwargs) -> object:
		return self.__default_output


class DelegatedExecutableElement(ExecutableElement):

	def __init__(self, *, delegate_function: Callable[[...], object]):

		self.__delegate_function = delegate_function

	def execute(self, *args, **kwargs) -> object:
		return self.__delegate_function(*args, **kwargs)


class ExecutableQueueInterface(ABC):

	@abstractmethod
	def insert_at_front_immediately(self, *, executable_element: ExecutableElement):
		"""
		Inserts this executable element at the front of the queue.
		:param executable_element: The element to be inserted at the front of the queue.
		:return: None
		"""
		raise NotImplementedError()

	@abstractmethod
	def append_to_end_immediately(self, *, executable_element: ExecutableElement):
		"""
		Appends this executable element to the back of the queue.
		:param executable_element: The executable element to be executed.
		:return: None
		"""
		raise NotImplementedError()

	@abstractmethod
	def insert_at_front_after_datetime(self, *, executable_element: ExecutableElement, delay_datetime: datetime):
		"""
		Inserts the executable element at the front of the queue after the datetime has passed.
		:param executable_element: The executable element to be executed.
		:param delay_datetime: The datetime that needs to be passed before the executable element is inserted at the front of the queue.
		:return: None
		"""
		raise NotImplementedError()

	@abstractmethod
	def append_to_end_after_datetime(self, *, executable_element: ExecutableElement, delay_datetime: datetime):
		"""
		Appends the executable element to the end of the queue after the datetime has passed.
		:param executable_element: The executable element to be executed.
		:param delay_datetime: The datetime that needs to be passed before the executable element is append to the end of the queue.
		:return: None
		"""
		raise NotImplementedError()

	@abstractmethod
	def insert_at_front_after_elapsed_seconds(self, *, executable_element: ExecutableElement, seconds_total: int):
		"""
		Inserts the executable element at the front of the queue after the total number of seconds have passed.
		:param executable_element: The executable element to be executed.
		:param seconds_total: The total number of seconds that need to pass before the executable element is inserted at the front of the queue.
		:return: None
		"""
		raise NotImplementedError()

	@abstractmethod
	def append_to_end_after_elapsed_seconds(self, *, executable_element: ExecutableElement, seconds_total: int):
		"""
		Appends the executable element to the end of the queue after the total number of seconds have passed.
		:param executable_element: The executable element to be executed.
		:param seconds_total: The total number of seconds that need to pass before the executable element is inserted to the end of the queue.
		:return: None
		"""
		raise NotImplementedError()

	@abstractmethod
	def wait_until_empty(self):
		"""
		Blocks the current thread until the queue has been emptied.
		:return: None
		"""
		raise NotImplementedError()


class PollingExecutableQueue(ExecutableQueueInterface):

	def __init__(self):

		self.__queue = []  # type: List[ExecutableElement]
		self.__insert_at_front_delayed_element_queue = DelayedElementQueue()
		self.__append_to_end_delayed_element_queue = DelayedElementQueue()
		self.__semaphore = threading.Semaphore()
		self.__delayed_polling_thread = None
		self.__processing_thread = None
		self.__empty_wait_semaphore = threading.Semaphore(0)
		self.__empty_done_semaphore = threading.Semaphore(0)
		self.__is_waiting_for_empty = False
		self.__is_threads_active = True

		self.__start_delayed_polling_thread()
		self.__start_processing_thread()

	def __start_delayed_polling_thread(self):

		def _thread_method():

			while self.__is_threads_active:
				time.sleep(1)
				_is_successful = True
				while _is_successful:
					_is_successful, _delayed_element = self.__insert_at_front_delayed_element_queue.try_get()
					if _is_successful:
						_executable_element = _delayed_element.get_element()  # type: ExecutableElement
						self.insert_at_front_immediately(
							executable_element=_executable_element
						)
				_is_successful = True
				while _is_successful:
					_is_successful, _delayed_element = self.__append_to_end_delayed_element_queue.try_get()  # type: Tuple[bool, ExecutableElement]
					if _is_successful:
						_executable_element = _delayed_element.get_element()  # type: ExecutableElement
						self.append_to_end_immediately(
							executable_element=_executable_element
						)

		self.__delayed_polling_thread = threading.Thread(
			target=_thread_method
		)
		self.__delayed_polling_thread.daemon = True
		self.__delayed_polling_thread.start()

	def __start_processing_thread(self):

		def _thread_method():

			while self.__is_threads_active:
				_executable_element = None  # type: ExecutableElement
				self.__semaphore.acquire()
				if len(self.__queue) != 0:
					_executable_element = self.__queue.pop()
				else:
					if self.__is_waiting_for_empty:
						self.__empty_wait_semaphore.release()
						self.__empty_done_semaphore.acquire()
				self.__semaphore.release()
				if _executable_element is None:
					time.sleep(1.0)
				else:
					_execution_parameters = self.get_execution_parameters()
					_execution_result = _executable_element.execute(**_execution_parameters)
					self.process_execution_result(
						execution_result=_execution_result
					)

		self.__processing_thread = threading.Thread(
			target=_thread_method
		)
		self.__processing_thread.daemon = True
		self.__processing_thread.start()

	def insert_at_front_immediately(self, *, executable_element: ExecutableElement):

		self.__semaphore.acquire()

		self.__queue.insert(0, executable_element)

		self.__semaphore.release()

	def append_to_end_immediately(self, *, executable_element: ExecutableElement):

		self.__semaphore.acquire()

		self.__queue.append(executable_element)

		self.__semaphore.release()

	def insert_at_front_after_datetime(self, *, executable_element: ExecutableElement, delay_datetime: datetime):

		self.__semaphore.acquire()

		self.__insert_at_front_delayed_element_queue.add(
			delayed_element=DelayedElement(
				element=executable_element,
				delay_datetime=delay_datetime
			)
		)

		self.__semaphore.release()

	def append_to_end_after_datetime(self, *, executable_element: ExecutableElement, delay_datetime: datetime):

		self.__semaphore.acquire()

		self.__append_to_end_delayed_element_queue.add(
			delayed_element=DelayedElement(
				element=executable_element,
				delay_datetime=delay_datetime
			)
		)

		self.__semaphore.release()

	def insert_at_front_after_elapsed_seconds(self, *, executable_element: ExecutableElement, seconds_total: int):

		self.__semaphore.acquire()

		_datetime = datetime.utcnow() + timedelta(0, seconds_total)
		self.__insert_at_front_delayed_element_queue.add(
			delayed_element=DelayedElement(
				element=executable_element,
				delay_datetime=_datetime
			)
		)

		self.__semaphore.release()

	def append_to_end_after_elapsed_seconds(self, *, executable_element: ExecutableElement, seconds_total: int):

		self.__semaphore.acquire()

		_datetime = datetime.utcnow() + timedelta(0, seconds_total)
		self.__append_to_end_delayed_element_queue.add(
			delayed_element=DelayedElement(
				element=executable_element,
				delay_datetime=_datetime
			)
		)

		self.__semaphore.release()

	def wait_until_empty(self):
		self.__is_waiting_for_empty = True
		self.__empty_wait_semaphore.acquire()
		self.__is_waiting_for_empty = False
		self.__empty_done_semaphore.release()

	def dispose(self):
		if self.__is_threads_active:
			self.__is_threads_active = False
			self.__delayed_polling_thread.join()
			self.__processing_thread.join()

	@abstractmethod
	def get_execution_parameters(self) -> Dict[str, object]:
		raise NotImplementedError()

	@abstractmethod
	def process_execution_result(self, *, execution_result: object):
		raise NotImplementedError()
