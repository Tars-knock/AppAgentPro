from scripts.model import BaseModel


class MessageCenter:
    """
    消息中心类，准备把这个类设计成无状态的service，
    主要职责是管理session和message
    """

    def __init__(self):
        pass

    def get_message(self, user, session):
        # 通过数据库获取当前专家当前session的对话历史
        pass

    def do_conversation(self, messages, model: BaseModel) -> list:
        response = model.get_model_response(messages)
        messages.append(response)
        return messages
