from abc import ABC, abstractmethod


class JsonConvertable(ABC):

	@abstractmethod
	def get_json_string(self) -> str:
		raise NotImplementedError()
