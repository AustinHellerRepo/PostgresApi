from __future__ import annotations
from postgres_api.database_interface import DatabaseCommand, CompositeDatabaseCommand, DatabaseCommandResult, CompositeDatabaseCommandResult, DatabaseInterface, DatabaseCommandResultFactoryInterface, DatabaseCommandFactoryInterface
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_DEFAULT
from typing import Dict, List, Tuple
import json


class SuccessCreatingDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, database_name: str):

		self.__database_name = database_name

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": True,
			"database_name": self.__database_name
		})


class FailureCreatingDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, database_name: str, error_message: str):

		self.__database_name = database_name
		self.__error_message = error_message

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": False,
			"database_name": self.__database_name
		})


class SuccessConnectingToDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, database_name: str):

		self.__database_name = database_name

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": True,
			"database_name": self.__database_name
		})


class FailureConnectingToDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, database_name: str, error_message: str):

		self.__database_name = database_name
		self.__error_message = error_message

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": False,
			"database_name": self.__database_name,
			"error_message": self.__error_message
		})


class SuccessQueryingDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, query: str, parameters: Dict[str, object], output: object):

		self.__query = query
		self.__parameters = parameters
		self.__output = output

	def get_output(self) -> object:
		return self.__output

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": True,
			"query": self.__query,
			"parameters": self.__parameters,
			"output": self.__output
		})


class FailureQueryingDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, query: str, parameters: Dict[str, object], output: object, error_message: str):

		self.__query = query
		self.__parameters = parameters
		self.__output = output
		self.__error_message = error_message

	def get_output(self) -> object:
		return self.__output

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": False,
			"query": self.__query,
			"parameters": self.__parameters,
			"output": self.__output,
			"error_message": self.__error_message
		})


class SuccessDisconnectingFromDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, database_name: str):

		self.__database_name = database_name

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": True,
			"database_name": self.__database_name
		})


class FailureDisconnectingFromDatabaseDatabaseCommandResult(DatabaseCommandResult):

	def __init__(self, *, database_name: str, error_message: str):

		self.__database_name = database_name
		self.__error_message = error_message

	def get_json_string(self) -> str:
		return json.dumps({
			"version": 1,
			"is_successful": False,
			"database_name": self.__database_name,
			"error_message": self.__error_message
		})


class ExecuteQueryDatabaseCommandResult(CompositeDatabaseCommandResult):

	def __init__(self, *, child_database_command_results: List[DatabaseCommandResult], is_successful: bool):
		super().__init__(
			child_database_command_results=child_database_command_results
		)

		self.__is_successful = is_successful

	def try_get_output(self) -> Tuple[bool, object]:

		if not self.__is_successful:
			return False, None
		else:
			_database_command_result = self.get_child_command_results()[1]  # type: SuccessQueryingDatabaseDatabaseCommandResult
			return True, _database_command_result.get_output()


class CreateDatabaseDatabaseCommand(DatabaseCommand):

	def __init__(self, *, database_name: str):

		self.__database_name = database_name

	def execute(self, *, database_interface: DatabaseInterface, database_command_result_factory: DatabaseCommandResultFactoryInterface) -> DatabaseCommandResult:

		_result = None
		try:
			database_interface.create_database(
				database_name=self.__database_name
			)
			_result = database_command_result_factory.get_success_creating_database_result(
				database_name=self.__database_name
			)
		except Exception as ex:
			_result = database_command_result_factory.get_failure_creating_database_result(
				database_name=self.__database_name,
				error_message=str(ex)
			)
		return _result


class ExecuteQueryDatabaseCommand(DatabaseCommand):

	def __init__(self, *, database_name: str, query: str, parameters: Dict[str, str]):

		self.__database_name = database_name
		self.__query = query
		self.__parameters = parameters

	def execute(self, *, database_interface: DatabaseInterface, database_command_result_factory: DatabaseCommandResultFactoryInterface) -> DatabaseCommandResult:

		_results = []  # type: List[DatabaseCommandResult]

		_is_successful = True

		if _is_successful:
			try:
				database_interface.connect_to_database(
					database_name=self.__database_name
				)
				_connecting_to_database_result = database_command_result_factory.get_success_connecting_to_database_result(
					database_name=self.__database_name
				)
			except Exception as ex:
				_is_successful = False
				_connecting_to_database_result = database_command_result_factory.get_failure_connecting_to_database_result(
					database_name=self.__database_name,
					error_message=str(ex)
				)
			_results.append(_connecting_to_database_result)

		if _is_successful:
			_output = None
			try:
				_output = database_interface.execute_query(
					query=self.__query,
					parameters=self.__parameters
				)
				_querying_database_result = database_command_result_factory.get_success_querying_database_result(
					query=self.__query,
					parameters=self.__parameters,
					output=_output
				)
			except Exception as ex:
				_is_successful = False
				_querying_database_result = database_command_result_factory.get_failure_querying_database_result(
					query=self.__query,
					parameters=self.__parameters,
					output=_output,
					error_message=str(ex)
				)
			_results.append(_querying_database_result)

		if _is_successful:
			try:
				database_interface.disconnect_from_database()
				_disconnecting_from_database_result = database_command_result_factory.get_success_disconnecting_from_database_result(
					database_name=self.__database_name
				)
			except Exception as ex:
				_disconnecting_from_database_result = database_command_result_factory.get_failure_disconnecting_from_database_result(
					database_name=self.__database_name,
					error_message=str(ex)
				)
			_results.append(_disconnecting_from_database_result)

		_result = CompositeDatabaseCommandResult(
			child_database_command_results=_results
		)

		return _result


class PostgresDatabase(DatabaseInterface):

	def __init__(self, *, user_name: str, password: str, host_url: str, port: int):
		super().__init__()

		self.__user_name = user_name
		self.__password = password
		self.__host_url = host_url
		self.__port = port

		self.__connected_to_database = None  # type: str

		pass

	def create_database(self, *, database_name: str):

		_connection = psycopg2.connect(
			user=self.__user_name,
			password=self.__password,
			host=self.__host_url,
			port=self.__port,
			database="postgres"
		)

		raise NotImplementedError()

	def connect_to_database(self, *, database_name: str):

		if self.__connected_to_database is not None:
			raise Exception(f"Cannot connect to database \"{database_name}\" because already connected to database \"{self.__connected_to_database}\".")
		self.__connected_to_database = database_name

	def disconnect_from_database(self):

		if self.__connected_to_database is None:
			raise Exception(f"Unexpected attempt to disconnect from database while not connected to a database.")
		self.__connected_to_database = None

	def execute_query(self, *, query: str, parameters: Dict[str, object]) -> object:

		raise NotImplementedError()


class PostgresDatabaseCommandFactory(DatabaseCommandFactoryInterface):

	def get_execute_query_database_command(self, *, query: str, parameters: Dict[str, object]):

		raise NotImplementedError()


class PostgresApiDatabaseCommandResultFactory(DatabaseCommandResultFactoryInterface):

	def get_success_creating_database_result(self, *, database_name: str) -> DatabaseCommandResult:
		return SuccessCreatingDatabaseDatabaseCommandResult(
			database_name=database_name
		)

	def get_failure_creating_database_result(self, *, database_name: str, error_message: str) -> DatabaseCommandResult:
		return FailureCreatingDatabaseDatabaseCommandResult(
			database_name=database_name,
			error_message=error_message
		)

	def get_success_connecting_to_database_result(self, *, database_name: str) -> DatabaseCommandResult:
		return SuccessConnectingToDatabaseDatabaseCommandResult(
			database_name=database_name
		)

	def get_failure_connecting_to_database_result(self, *, database_name: str, error_message: str) -> DatabaseCommandResult:
		return FailureConnectingToDatabaseDatabaseCommandResult(
			database_name=database_name,
			error_message=error_message
		)

	def get_success_querying_database_result(self, *, query: str, parameters: Dict[str, object], output: object) -> DatabaseCommandResult:
		return SuccessQueryingDatabaseDatabaseCommandResult(
			query=query,
			parameters=parameters,
			output=output
		)

	def get_failure_querying_database_result(self, *, query: str, parameters: Dict[str, object], output: object, error_message: str) -> DatabaseCommandResult:
		return FailureQueryingDatabaseDatabaseCommandResult(
			query=query,
			parameters=parameters,
			output=output,
			error_message=error_message
		)

	def get_success_disconnecting_from_database_result(self, *, database_name: str) -> DatabaseCommandResult:
		return SuccessDisconnectingFromDatabaseDatabaseCommandResult(
			database_name=database_name
		)

	def get_failure_disconnecting_from_database_result(self, *, database_name: str, error_message: str) -> DatabaseCommandResult:
		return FailureDisconnectingFromDatabaseDatabaseCommandResult(
			database_name=database_name,
			error_message=error_message
		)