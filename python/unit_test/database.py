import unittest
from unittest import mock
from unittest.mock import patch
from core.database import DatabaseCommandPollingExecutableQueue, DatabaseInterface, Callback, ExecutableElement, CommandResult, DefaultCommandResult
from core.callback import FunctionCallback, JsonConvertable
from core.queue import DefaultExecutableElement, DelegatedExecutableElement


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


if __name__ == "__main__":
	unittest.main()
