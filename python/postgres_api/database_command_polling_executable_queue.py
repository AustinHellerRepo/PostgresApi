from __future__ import annotations
from postgres_api.database_interface import DatabaseInterface, DatabaseCommandResult
from postgres_api.queue import SingleThreadedExecutableQueue
from postgres_api.callback import Callback
from typing import Dict


class DatabaseCommandSingleThreadedExecutableQueue(SingleThreadedExecutableQueue):

	def __init__(self, *, database_interface: DatabaseInterface, execution_result_callback: Callback):
		super().__init__()

		self.__database_interface = database_interface
		self.__execution_result_callback = execution_result_callback

	def get_execution_parameters(self) -> Dict[str, object]:
		return {
			"database_interface": self.__database_interface
		}

	def process_execution_result(self, *, execution_result: DatabaseCommandResult):
		self.__execution_result_callback.execute(
			data=execution_result.get_json_string()
		)
