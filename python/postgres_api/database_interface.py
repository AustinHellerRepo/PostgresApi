from __future__ import annotations
from abc import ABC, abstractmethod
from postgres_api.command import CommandResult, Command, CommandResultFactoryInterface, CommandFactoryInterface, CompositeCommand, CompositeCommandResult
from typing import Dict, List


class DatabaseCommandResultFactoryInterface(CommandResultFactoryInterface):

	@abstractmethod
	def get_success_creating_database_result(self, *, database_name: str) -> DatabaseCommandResult:
		raise NotImplementedError()

	@abstractmethod
	def get_failure_creating_database_result(self, *, database_name: str, error_message: str) -> DatabaseCommandResult:
		raise NotImplementedError()

	@abstractmethod
	def get_success_connecting_to_database_result(self, *, database_name: str) -> DatabaseCommandResult:
		raise NotImplementedError()

	@abstractmethod
	def get_failure_connecting_to_database_result(self, *, database_name: str, error_message: str) -> DatabaseCommandResult:
		raise NotImplementedError()

	@abstractmethod
	def get_success_querying_database_result(self, *, query: str, parameters: Dict[str, object], output: object) -> DatabaseCommandResult:
		raise NotImplementedError()

	@abstractmethod
	def get_failure_querying_database_result(self, *, query: str, parameters: Dict[str, object], output: object, error_message: str) -> DatabaseCommandResult:
		raise NotImplementedError()

	@abstractmethod
	def get_success_disconnecting_from_database_result(self, *, database_name: str) -> DatabaseCommandResult:
		raise NotImplementedError()

	@abstractmethod
	def get_failure_disconnecting_from_database_result(self, *, database_name: str, error_message: str) -> DatabaseCommandResult:
		raise NotImplementedError()


class DatabaseCommandResult(CommandResult):

	@abstractmethod
	def get_json_string(self) -> str:
		raise NotImplementedError()


class CompositeDatabaseCommandResult(CompositeCommandResult):

	def __init__(self, *, child_database_command_results: List[DatabaseCommandResult]):
		super().__init__(
			child_command_results=child_database_command_results
		)

		pass

	@abstractmethod
	def get_json_string(self) -> str:
		raise NotImplementedError()


class DatabaseCommand(Command):

	@abstractmethod
	def execute(self, *, database_interface: DatabaseInterface, database_command_result_factory: DatabaseCommandResultFactoryInterface) -> DatabaseCommandResult:
		raise NotImplementedError()


class CompositeDatabaseCommand(CompositeCommand):

	def __init__(self, *, child_database_commands: List[DatabaseCommand]):
		super().__init__(
			child_commands=child_database_commands
		)

		pass

	@abstractmethod
	def execute(self, *, database_interface: DatabaseInterface, database_command_result_factory: DatabaseCommandResultFactoryInterface) -> DatabaseCommandResult:
		raise NotImplementedError()


class DatabaseCommandFactoryInterface(CommandFactoryInterface):

	pass


class DatabaseInterface(ABC):

	@abstractmethod
	def create_database(self, *, database_name: str):
		raise NotImplementedError()

	@abstractmethod
	def connect_to_database(self, *, database_name: str):
		raise NotImplementedError()

	@abstractmethod
	def execute_query(self, *, query: str, parameters: Dict[str, object]) -> object:
		raise NotImplementedError()

	@abstractmethod
	def disconnect_from_database(self):
		raise NotImplementedError()
