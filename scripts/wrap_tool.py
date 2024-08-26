import inspect
import re
import json


def wrap_to_tool(func):
    """
    装饰器，功能是将普通的函数装饰成可以提交给LLM进行调用的tool
    :param func: 被装饰的函数,需要拥有拥有完整规范的类注释
    :return: 包装好的tool，拥有invoke方法供LLM使用；to_tool_json方法给LLM大人生成tool介绍
    """
    return WrapTool(func)


class WrapTool:
    def __init__(self, func):
        self.return_doc = None
        self.origin_func = func
        self.type = "function"
        self.name = func.__name__
        self.doc = inspect.getdoc(func)
        self.description = ''
        self.param_doc = {}
        self.__split_doc()
        self.param_info = None
        self.required_params = None
        self.__param_info_process()

    def __call__(self, *args, **kwargs):
        return self.origin_func(*args, **kwargs)

    def invoke(self, json_str):
        """
        用gpt的参数调用被包装的func
        """
        try:
            params = json.loads(json_str)
            if not isinstance(params, dict):
                raise ValueError("function params must be a dict")
            return self.origin_func(**params)
        except json.JSONDecodeError:
            raise ValueError("function param not a valid json")
        except TypeError as e:
            raise ValueError(f"Error in function call {self.name} :{e}")

    def __split_doc(self):
        """
        解析方法的注释并提取方法说明、参数说明、返回值说明
        """
        if not self.doc:
            return None

        # 匹配描述部分，使用非贪婪模式匹配到第一个 :param 或 :return 之前
        description_match = re.match(r"^(.*?)(?=\n\s*:(param|return))", self.doc, re.DOTALL)
        if description_match:
            self.description = description_match.group(1).strip()
        else:
            self.description = self.doc.strip()

        # 匹配所有 :param 和 :return 片段
        param_pattern = r":param\s+(\w+):\s+(.+)"
        return_pattern = r":return:\s+(.+)"
        param_matches = re.findall(param_pattern, self.doc)
        return_match = re.search(return_pattern, self.doc)

        # 提取参数说明
        for param_name, param_desc in param_matches:
            self.param_doc[param_name] = param_desc.strip()

        # 提取返回值说明
        if return_match:
            self.return_doc = return_match.group(1).strip()

    def __param_info_process(self):
        """
        处理传入函数的参数信息
        :return:
        """
        # 获取函数签名
        sig = inspect.signature(self.origin_func)

        # 获取参数信息
        params = sig.parameters
        # 参数名字与类型，类型默认为string
        param_info = {}
        # 必传参数集合
        self.required_params = []

        for name, param in params.items():
            type_annotation = param.annotation if param.annotation is not inspect.Parameter.empty else "string"
            param_info[name] = type_annotation
            if param.default is inspect.Parameter.empty:
                self.required_params.append(name)
        self.param_info = param_info

    def to_tool_json(self) -> str:

        param_info = {
            name: {
                "type": param,
                "description": self.param_doc[name]
            }
            for name, param in self.param_info.items()
        }

        # param_info_json = json.dumps(param_info, indent=4)

        # 生成最终的JSON字符串
        tool_json = {
            "type": self.type,
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": param_info,
                    "required": self.required_params
                }
            }
        }

        return json.dumps(tool_json, ensure_ascii=False, indent=4)  # 美化JSON输出

# if __name__ == "__main__":
# wrap_tool = WrapTool(geo_function.get_location_info)
# print(wrap_tool.to_tool_json())
