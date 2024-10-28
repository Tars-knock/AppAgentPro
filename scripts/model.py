import re
from abc import abstractmethod
from typing import List, Iterable
from http import HTTPStatus

import requests
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import json

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
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # 对于自己定义的包装类，进行特殊处理
        self.origin_tools = tools
        self.tools = json.dumps([json.loads(tool.to_tool_json()) for tool in tools])

    def get_model_response(self, messages: Iterable[ChatCompletionMessageParam]):
        """
        根据输入获取GPT的结果
        :param messages: 需要输入的message列表
        :return: GPT返回的原始response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        return response

    def execute_function_call(self, message) -> (bool, str):
        """
        根据GPT的指示，从tools中选择工具并执行
        :param message: gpt返回的，需要进行function_call的消息
        :return: 函数是否执行成功， 函数执行结果
        """
        try:
            function_name = message.tool_calls[0].function.name
            tools_map = {tool.name: tool for tool in self.origin_tools}
            # 如果gpt调用的是函数库中提供的方法
            if function_name in tools_map:
                # 获取gpt调用的方法
                function = tools_map[function_name]
                # 获取GPT给出的方法参数列表
                gpt_params = json.loads(message.tool_calls[0].function.arguments)
                results = function(**gpt_params)
            else:
                results = False, f"Error: function {message.tool_calls[0].function.name} does not exist"
            return True, results
        except Exception as e:
            return False, f"Error: {e}"
