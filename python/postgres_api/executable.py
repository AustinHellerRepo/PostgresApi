from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable


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