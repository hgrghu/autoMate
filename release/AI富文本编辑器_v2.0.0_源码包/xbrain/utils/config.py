"""
配置管理模块
"""

class Config:
    """配置类"""
    def __init__(self):
        self.OPENAI_API_KEY = ""
        self.OPENAI_BASE_URL = "https://api.openai.com/v1"
        self.MODEL_NAME = "gpt-3.5-turbo"
        self.MAX_TOKENS = 4000
        self.TEMPERATURE = 0.7