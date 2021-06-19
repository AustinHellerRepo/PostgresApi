from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
import json
from typing import List


class EntryPointTypeEnum(ABC, Enum):
	pass


class PostgresApiEntryPointTypeEnum(EntryPointTypeEnum):

	CreateDatabase = auto(),
	InsertRecord = auto(),
	GetRecord = auto(),
	GetRecords = auto(),
	UpdateRecord = auto(),
	DeleteRecord = auto(),
	DeleteRecords = auto()


class EntryPointInterfaceFactoryInterface(ABC):

	@abstractmethod
	def get_entry_point_interface(self, version: int, entry_point_type: EntryPointTypeEnum):
		raise NotImplementedError()


class EntryPointInterface(ABC):
	"""
	This class implements all necessary actions to fulfill the responsibilities of an API entry point
	"""

	def __init__(self, *, version: int, entry_point_type: EntryPointTypeEnum):

		self.__version = version
		self.__entry_point_type = entry_point_type

	@abstractmethod
	def process_json_input(self, *, json_parser: JsonParserInterface):
		raise NotImplementedError()


class JsonPropertyDoesNotExistException(Exception):

	def __init__(self, *, json_string: str, property_name: str):

		self.__json_string = json_string
		self.__property_name = property_name

	def get_json_string(self) -> str:
		return self.__json_string

	def get_property_name(self) -> str:
		return self.__property_name


class JsonParserInterface(ABC):
	"""
	This class provides json parsing functionality specific to an entry point
	"""

	def __init__(self, *, json_string: str):

		self._json_string = json_string

	@staticmethod
	def get_property_value_from_json_string(*, json_string: str, property_names: List[str]):
		_json = json.loads(json_string)
		for _property_name in property_names:
			if _property_name not in _json:
				raise JsonPropertyDoesNotExistException(
					json_string=json.dumps(_json),
					property_name=_property_name
				)
			_json = _json[_property_name]
		return _json

	def get_property_value(self, *, property_names: List[str]):
		return JsonParserInterface.get_property_value_from_json_string(
			json_string=self._json_string,
			property_names=property_names
		)
