"""
AI Enhanced Rich Text Editor Module
基于autoMate项目的AI增强富文本编辑器扩展
"""

__version__ = "1.0.0"
__author__ = "autoMate Team"

from .main_editor import AIRichTextEditor
from .llm_assistant import LLMAssistant
from .export_manager import ExportManager

__all__ = ['AIRichTextEditor', 'LLMAssistant', 'ExportManager']