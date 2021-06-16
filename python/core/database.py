from __future__ import annotations
from core.queue import DelayedElementQueue, DelayedElement, PollingExecutableQueue, ExecutableElement
from core.callback import Callback
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_DEFAULT
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import threading
import time


class DatabaseCommandPollingExecutableQueue(PollingExecutableQueue):

	def __init__(self, *, database_interface: DatabaseInterface, execution_result_callback: Callback):
		super().__init__()

		self.__database_interface = database_interface
		self.__execution_result_callback = execution_result_callback

	def get_execution_parameters(self) -> Dict[str, object]:
		return {
			"database_interface": self.__database_interface
		}

	def process_execution_result(self, *, execution_result: CommandResult):
		self.__execution_result_callback.execute(
			data=execution_result.get_json()
		)


class CommandResult(ABC):

	@abstractmethod
	def get_json(self) -> str:
		raise NotImplementedError()


class DefaultCommandResult(CommandResult):

	def __init__(self, *, default_json: str):

		self.__default_json = default_json

	def get_json(self) -> str:
		return self.__default_json


class Command(ExecutableElement):

	@abstractmethod
	def execute(self, *, database_interface: DatabaseInterface) -> CommandResult:
		raise NotImplementedError()


class CreateDatabaseCommand(Command):

	def __init__(self, *, database_name: str):

		self.__database_name = database_name

	def execute(self, *, database_interface: DatabaseInterface):

		database_interface.create_database(
			database_name=self.__database_name
		)


class ExecuteQueryCommand(Command):

	def __init__(self, *, database_name: str, query: str, parameters: Dict[str, str]):

		self.__database_name = database_name
		self.__query = query
		self.__parameters = parameters

	def execute(self, *, database_interface: DatabaseInterface):

		database_interface.connect_to_database(
			database_name=self.__database_name
		)
		database_interface.execute_query(
			query=self.__query,
			parameters=self.__parameters
		)
		database_interface.disconnect_from_database()


class DatabaseInterface(ABC):

	def create_database(self, *, database_name: str):
		raise NotImplementedError()

	def connect_to_database(self, *, database_name: str):
		raise NotImplementedError()

	def execute_query(self, *, query: str, parameters: Dict[str, str]):
		raise NotImplementedError()

	def disconnect_from_database(self):
		raise NotImplementedError()


class PostgresDatabaseInterface(DatabaseInterface):

	def __init__(self, *, user_name: str, password: str, host_url: str, port: int):
		super().__init__()

		self.__user_name = user_name
		self.__password = password
		self.__host_url = host_url
		self.__port = port

		pass

	def create_database(self, *, database_name: str):

		_connection = psycopg2.connect(
			user=self.__user_name,
			password=self.__password,
			host=self.__host_url,
			port=self.__port,
			database="postgres"
		)

