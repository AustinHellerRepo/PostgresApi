from __future__ import annotations
import jwt
from abc import ABC, abstractmethod
import json
import requests
from typing import Callable


class RemoteApiInterface(ABC):

	@abstractmethod
	def post(self, *, url: str, json_object: object) -> UrlResponse:
		raise NotImplementedError()


class JsonConvertable(ABC):

	@abstractmethod
	def get_json(self) -> str:
		raise NotImplementedError()


class RequestsRemoteApiInterface(RemoteApiInterface):

	def post(self, *, url: str, json_object: object) -> UrlResponse:
		_request = requests.post(self._url, json=json_object)
		_url_callback_response = UrlResponse(
			status_code=_request.status_code,
			json_object=_request.json()
		)
		return _url_callback_response


class Callback(ABC):

	@abstractmethod
	def execute(self, *, data: object) -> JsonConvertable:
		raise NotImplementedError()


class UrlResponse(JsonConvertable):

	def __init__(self, *, status_code: int, json_object):
		super().__init__()

		self.__status_code = status_code
		self.__json_object = json_object

	def get_status_code(self) -> int:
		return self.__status_code

	def get_json_object(self) -> object:
		return self.__json_object

	def get_json(self) -> str:
		return json.dumps({
			"status_code": self.__status_code,
			"json_object": self.__json_object
		})


class FunctionCallback(Callback):

	def __init__(self, *, function: Callable[[object], JsonConvertable]):

		self.__function = function

	def execute(self, *, data: object) -> JsonConvertable:
		return self.__function(data)


class UrlCallback(Callback):

	def __init__(self, *, url: str, remote_api: RemoteApiInterface):

		self._url = url
		self._remote_api = remote_api

	@abstractmethod
	def execute(self, *, data: object):
		raise NotImplementedError()

	def _call_url(self, *, json_object) -> UrlResponse:
		return self._remote_api.post(
			url=self._url,
			json_object=json_object
		)


class JsonWebTokenCallback(UrlCallback):

	def __init__(self, *, url: str, secret: str, remote_api: RemoteApiInterface):
		super().__init__(
			url=url,
			remote_api=remote_api
		)

		self.__secret = secret

	def execute(self, *, data: object) -> JsonConvertable:
		_json = None
		if isinstance(data, JsonConvertable):
			_json = json.loads(data.get_json())
		elif isinstance(data, str):
			_json = json.loads(data)
		else:
			_json = data
		_encoded_jwt = jwt.encode(_json, self.__secret, algorithm="HS256")
		_url_response = self._call_url(
			json_object=json.dumps({
				"token": _encoded_jwt
			})
		)
		return _url_response
