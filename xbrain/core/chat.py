
import requests
import json

def run(messages, model="gpt-3.5-turbo"):
    """基本的聊天函数"""
    try:
        # 这里可以集成实际的AI API调用
        # 目前返回一个示例响应
        return "AI功能需要配置API密钥才能使用。请在设置中配置您的API密钥。"
    except Exception as e:
        return f"AI服务暂不可用: {str(e)}"
