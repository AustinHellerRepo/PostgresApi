from __future__ import annotations
from abc import ABC, abstractmethod
from postgres_api.executable import ExecutableElement
from postgres_api.json_convertable import JsonConvertable
from typing import List


class CommandResultFactoryInterface(ABC):

	@staticmethod
	def get_default_command_result(*, json_string: str) -> DefaultCommandResult:
		return DefaultCommandResult(
			default_json_string=json_string
		)


class CommandResult(JsonConvertable, ABC):

	@abstractmethod
	def get_json_string(self) -> str:
		raise NotImplementedError()


class CompositeCommandResult(CommandResult, ABC):

	def __init__(self, *, child_command_results: List[CommandResult]):

		self.__child_command_results = child_command_results

	def get_child_command_results(self) -> List[CommandResult]:
		return self.__child_command_results.copy()

	@abstractmethod
	def get_json_string(self) -> str:
		raise NotImplementedError


class DefaultCommandResult(CommandResult):

	def __init__(self, *, default_json_string: str):

		self.__default_json_string = default_json_string

	def get_json_string(self) -> str:
		return self.__default_json_string


class Command(ExecutableElement):

	@abstractmethod
	def execute(self, *args, **kwargs) -> CommandResult:
		raise NotImplementedError()


class CompositeCommand(Command, ABC):

	def __init__(self, *, child_commands: List[Command]):

		self._child_commands = child_commands

		raise NotImplementedError()

	@abstractmethod
	def execute(self, *args, **kwargs) -> CommandResult:
		raise NotImplementedError()


class CommandFactoryInterface(ABC):

	pass
