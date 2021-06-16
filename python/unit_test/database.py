import unittest
from unittest import mock
from unittest.mock import patch
from core.database import DatabaseCommandPollingExecutableQueue, DatabaseInterface, Callback, ExecutableElement, CommandResult, DefaultCommandResult
from core.callback import FunctionCallback, JsonConvertable
from core.queue import DefaultExecutableElement, DelegatedExecutableElement
from typing import List
import time


class TestDatabaseCommandPollingExecutableQueue(unittest.TestCase):

	@patch.multiple(DatabaseInterface, __abstractmethods__=set())
	@patch.multiple(Callback, __abstractmethods__=set())
	def test_initialization(self):

		_database_interface = DatabaseInterface()
		_execution_result_callback = Callback()

		_database_command_polling_executable_queue = DatabaseCommandPollingExecutableQueue(
			database_interface=_database_interface,
			execution_result_callback=_execution_result_callback
		)

	@patch.multiple(DatabaseInterface, __abstractmethods__=set())
	def test_insert_at_front_immediately_and_wait_for_callback(self):

		_json = '{ "test": true }'

		def _function_callback(data: object) -> JsonConvertable:
			self.assertEqual(_json, data)
			return None

		_database_interface = DatabaseInterface()

		_execution_result_callback = FunctionCallback(
			function=_function_callback
		)

		_database_command_polling_executable_queue = DatabaseCommandPollingExecutableQueue(
			database_interface=_database_interface,
			execution_result_callback=_execution_result_callback
		)

		def _delegate_function(*args, **kwargs) -> object:
			self.assertEqual(_database_interface, kwargs["database_interface"])
			return DefaultCommandResult(
				default_json=_json
			)

		_executable_element = DelegatedExecutableElement(
			delegate_function=_delegate_function
		)

		_database_command_polling_executable_queue.insert_at_front_immediately(
			executable_element=_executable_element
		)

		_database_command_polling_executable_queue.wait_until_empty()

		_database_command_polling_executable_queue.dispose()

	@patch.multiple(DatabaseInterface, __abstractmethods__=set())
	def test_insert_order_respected_sequential_and_fast(self):

		_inserts_total = 10

		def _get_json_per_index(index: int) -> str:
			return f'{{ "index": {index} }}'

		_order_of_callback = []  # type: List[int]

		def _function_callback(data: object) -> JsonConvertable:
			_order_of_callback.append(data)
			return None

		_database_interface = DatabaseInterface()

		_execution_result_callback = FunctionCallback(
			function=_function_callback
		)

		_database_command_polling_executable_queue = DatabaseCommandPollingExecutableQueue(
			database_interface=_database_interface,
			execution_result_callback=_execution_result_callback
		)

		for _index in range(_inserts_total):

			_executable_element = DefaultExecutableElement(
				default_output=DefaultCommandResult(
					default_json=_get_json_per_index(_index)
				)
			)

			_database_command_polling_executable_queue.insert_at_front_immediately(
				executable_element=_executable_element
			)

		_database_command_polling_executable_queue.wait_until_empty()

		_database_command_polling_executable_queue.dispose()

		self.assertEqual(len(_order_of_callback), _inserts_total)
		for _index in range(_inserts_total):
			self.assertEqual(_order_of_callback[_index], _get_json_per_index(_index))

	@patch.multiple(DatabaseInterface, __abstractmethods__=set())
	def test_insert_order_respected_sequential_and_slow(self):

		_inserts_total = 5

		def _get_json_per_index(index: int) -> str:
			return f'{{ "index": {index} }}'

		_order_of_callback = []  # type: List[int]

		def _function_callback(data: object) -> JsonConvertable:
			_order_of_callback.append(data)
			return None

		_database_interface = DatabaseInterface()

		_execution_result_callback = FunctionCallback(
			function=_function_callback
		)

		_database_command_polling_executable_queue = DatabaseCommandPollingExecutableQueue(
			database_interface=_database_interface,
			execution_result_callback=_execution_result_callback
		)

		for _index in range(_inserts_total):
			_executable_element = DefaultExecutableElement(
				default_output=DefaultCommandResult(
					default_json=_get_json_per_index(_index)
				)
			)

			_database_command_polling_executable_queue.insert_at_front_immediately(
				executable_element=_executable_element
			)

			time.sleep(0.75)

		_database_command_polling_executable_queue.wait_until_empty()

		_database_command_polling_executable_queue.dispose()

		self.assertEqual(len(_order_of_callback), _inserts_total)
		for _index in range(_inserts_total):
			self.assertEqual(_order_of_callback[_index], _get_json_per_index(_index))

	@patch.multiple(DatabaseInterface, __abstractmethods__=set())
	def test_insert_order_respected_sequential_and_slower(self):

		_inserts_total = 5

		def _get_json_per_index(index: int) -> str:
			return f'{{ "index": {index} }}'

		_order_of_callback = []  # type: List[int]

		def _function_callback(data: object) -> JsonConvertable:
			_order_of_callback.append(data)
			return None

		_database_interface = DatabaseInterface()

		_execution_result_callback = FunctionCallback(
			function=_function_callback
		)

		_database_command_polling_executable_queue = DatabaseCommandPollingExecutableQueue(
			database_interface=_database_interface,
			execution_result_callback=_execution_result_callback
		)

		for _index in range(_inserts_total):
			_executable_element = DefaultExecutableElement(
				default_output=DefaultCommandResult(
					default_json=_get_json_per_index(_index)
				)
			)

			_database_command_polling_executable_queue.insert_at_front_immediately(
				executable_element=_executable_element
			)

			time.sleep(1.25)

		_database_command_polling_executable_queue.wait_until_empty()

		_database_command_polling_executable_queue.dispose()

		self.assertEqual(len(_order_of_callback), _inserts_total)
		for _index in range(_inserts_total):
			self.assertEqual(_order_of_callback[_index], _get_json_per_index(_index))

	def test_set_of_commands_for_creating_inserting_and_pulling_data(self):
		pass


if __name__ == "__main__":
	unittest.main()
