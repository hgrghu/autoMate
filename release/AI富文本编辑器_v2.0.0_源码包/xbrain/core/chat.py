"""
AI聊天核心模块
"""

import requests
import json
from typing import List, Dict, Any

def run(messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", **kwargs) -> str:
    """
    运行AI聊天
    
    Args:
        messages: 消息列表
        model: 模型名称
        **kwargs: 其他参数
    
    Returns:
        AI回复内容
    """
    try:
        # 这里是示例实现，用户需要配置实际的API密钥
        # 实际使用时需要替换为真实的API调用
        
        response_text = "AI功能需要配置API密钥才能使用。请在设置中配置您的OpenAI API密钥。\n\n"
        response_text += "配置步骤：\n"
        response_text += "1. 获取OpenAI API密钥\n"
        response_text += "2. 在代码中替换xbrain/core/chat.py中的API调用\n"
        response_text += "3. 重新启动应用程序\n\n"
        response_text += "您也可以集成其他AI服务，如Claude、文心一言等。"
        
        return response_text
        
    except Exception as e:
        return f"AI服务暂不可用: {str(e)}"

def create_chat_completion(messages: List[Dict[str, str]], 
                          api_key: str = None,
                          base_url: str = "https://api.openai.com/v1",
                          model: str = "gpt-3.5-turbo") -> str:
    """
    创建聊天完成请求（示例实现）
    
    Args:
        messages: 消息列表
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
    
    Returns:
        AI回复
    """
    if not api_key:
        return "请配置API密钥"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"API请求失败: {response.status_code}"
            
    except Exception as e:
        return f"请求异常: {str(e)}"