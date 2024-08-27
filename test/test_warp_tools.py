from unittest import TestCase

from scripts.wrap_tool import wrap_to_tool


@wrap_to_tool
def case_func(a, b):
    """
    测试用例，这个函数的功能是将传入的两个参数相加并返回
    :param a: 第一个参数
    :param b: 第二个参数
    :return: 两个参数相加得到的和
    """
    return a + b


case_func_json = '''{
    "type": "function",
    "function": {
        "name": "case_func",
        "description": "测试用例，这个函数的功能是将传入的两个参数相加并返回",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "string",
                    "description": "第一个参数"
                },
                "b": {
                    "type": "string",
                    "description": "第二个参数"
                }
            },
            "required": [
                "a",
                "b"
            ]
        }
    }
}'''


class TestWarpTools(TestCase):
    """
    对warpTool工具进行单测
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_wrap_to_tool(self):
        res = case_func(1, 2)
        self.assertEqual(res, 3)

    def test_warp_tool_invoke(self):
        tool_json = case_func.to_tool_json()
        self.assertEqual(tool_json, case_func_json)
