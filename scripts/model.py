import re
from abc import abstractmethod
from typing import List, Iterable
from http import HTTPStatus

import requests
from openai.types.chat import ChatCompletionMessageParam

from scripts.wrap_tool import WrapTool
from utils import print_with_color, encode_image


class BaseModel:
    def __init__(self):
        pass

    @abstractmethod
    def get_model_response(self, messages) -> (bool, str):
        pass


class OpenAIModel(BaseModel):
    def __init__(self, base_url: str, api_key: str, model: str, temperature: float, max_tokens: int,
                 tools: List[WrapTool]):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools

    def get_model_response(self, messages: Iterable[ChatCompletionMessageParam]) -> (bool, str):
        pass
    # todo 待补充
