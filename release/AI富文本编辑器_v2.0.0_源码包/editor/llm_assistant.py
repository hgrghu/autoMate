"""
LLM Assistant Module
LLM助手模块，提供AI辅助文本编辑功能
"""

import asyncio
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QScrollArea, QFrame, QComboBox,
    QSpinBox, QCheckBox, QProgressBar, QGroupBox, QTabWidget,
    QSplitter, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QIcon

try:
    from xbrain.core.chat import run
    from xbrain.utils.config import Config
except ImportError:
    # 备用导入，用于打包版本
    def run(messages, model="gpt-3.5-turbo"):
        return "AI功能需要配置API密钥才能使用。请在设置中配置您的API密钥。"
    
    class Config:
        def __init__(self):
            self.OPENAI_API_KEY = ""
            self.OPENAI_BASE_URL = "https://api.openai.com/v1"
            self.MODEL_NAME = "gpt-3.5-turbo"

class LLMWorker(QThread):
    """LLM处理工作线程"""
    
    finished = pyqtSignal(str, str)  # 结果文本, 操作类型
    error = pyqtSignal(str)  # 错误信息
    progress = pyqtSignal(str)  # 进度信息
    
    def __init__(self, operation, text, params=None):
        super().__init__()
        self.operation = operation
        self.text = text
        self.params = params or {}
        
    def run(self):
        """执行LLM处理"""
        try:
            self.progress.emit("正在处理...")
            
            # 根据操作类型构建提示词
            prompt = self.build_prompt()
            
            # 调用LLM
            response = run([{"role": "user", "content": prompt}])
            
            self.finished.emit(response, self.operation)
            
        except Exception as e:
            self.error.emit(f"处理失败: {str(e)}")
            
    def build_prompt(self):
        """构建提示词"""
        if self.operation == "polish":
            return f"""请润色以下文本，改善表达、修正语法错误，保持原意不变：

原文：
{self.text}

请直接返回润色后的文本，不要添加其他说明。"""

        elif self.operation == "expand":
            target_length = self.params.get("target_length", "适当")
            return f"""请扩写以下文本，增加细节描述和深入分析，目标长度：{target_length}

原文：
{self.text}

请直接返回扩写后的文本，不要添加其他说明。"""

        elif self.operation == "contract":
            target_length = self.params.get("target_length", "适当")
            return f"""请缩写以下文本，保留核心要点，目标长度：{target_length}

原文：
{self.text}

请直接返回缩写后的文本，不要添加其他说明。"""

        elif self.operation == "translate":
            target_lang = self.params.get("target_language", "英文")
            return f"""请将以下文本翻译为{target_lang}：

原文：
{self.text}

请直接返回翻译结果，不要添加其他说明。"""

        elif self.operation == "summarize":
            return f"""请总结以下文本的主要内容和要点：

原文：
{self.text}

请提供简洁明了的总结。"""

        elif self.operation == "question":
            question = self.params.get("question", "请解释这段文字的含义")
            return f"""基于以下文本回答问题：

文本：
{self.text}

问题：{question}

请提供详细的回答。"""

        elif self.operation == "style_convert":
            target_style = self.params.get("target_style", "正式")
            return f"""请将以下文本转换为{target_style}风格：

原文：
{self.text}

请直接返回转换后的文本，不要添加其他说明。"""

        elif self.operation == "grammar_check":
            return f"""请检查以下文本的语法错误并修正：

原文：
{self.text}

请返回修正后的文本，如果没有错误请说明。"""

        elif self.operation == "content_audit":
            return f"""请审核以下文本，检查是否存在敏感词、不当内容或逻辑漏洞：

文本：
{self.text}

请提供审核结果和建议。"""

        elif self.operation == "generate_outline":
            return f"""基于以下主题或内容，生成详细的文章大纲：

主题/内容：
{self.text}

请生成结构清晰的大纲，包含主要章节和子章节。"""

        elif self.operation == "generate_content":
            return f"""根据以下大纲或主题，生成对应的内容：

大纲/主题：
{self.text}

请生成高质量的内容，结构清晰，逻辑合理。"""

        else:
            return f"请处理以下文本：\n{self.text}"

class QuickActionWidget(QFrame):
    """快捷操作小部件"""
    
    action_triggered = pyqtSignal(str, dict)  # 操作类型, 参数
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("快捷操作")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 文本处理按钮
        text_group = QGroupBox("文本处理")
        text_layout = QVBoxLayout(text_group)
        
        polish_btn = QPushButton("润色文本")
        polish_btn.clicked.connect(lambda: self.action_triggered.emit("polish", {}))
        text_layout.addWidget(polish_btn)
        
        expand_btn = QPushButton("扩写文本")
        expand_btn.clicked.connect(lambda: self.action_triggered.emit("expand", {}))
        text_layout.addWidget(expand_btn)
        
        contract_btn = QPushButton("缩写文本")
        contract_btn.clicked.connect(lambda: self.action_triggered.emit("contract", {}))
        text_layout.addWidget(contract_btn)
        
        layout.addWidget(text_group)
        
        # 翻译功能
        translate_group = QGroupBox("翻译")
        translate_layout = QVBoxLayout(translate_group)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("目标语言:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["英文", "中文", "日文", "韩文", "法文", "德文", "西班牙文"])
        lang_layout.addWidget(self.lang_combo)
        translate_layout.addLayout(lang_layout)
        
        translate_btn = QPushButton("翻译")
        translate_btn.clicked.connect(self.translate_text)
        translate_layout.addWidget(translate_btn)
        
        layout.addWidget(translate_group)
        
        # 风格转换
        style_group = QGroupBox("风格转换")
        style_layout = QVBoxLayout(style_group)
        
        style_layout_h = QHBoxLayout()
        style_layout_h.addWidget(QLabel("目标风格:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["正式", "非正式", "幽默", "学术", "商务", "诗意"])
        style_layout_h.addWidget(self.style_combo)
        style_layout.addLayout(style_layout_h)
        
        style_btn = QPushButton("转换风格")
        style_btn.clicked.connect(self.convert_style)
        style_layout.addWidget(style_btn)
        
        layout.addWidget(style_group)
        
        # 全文操作
        full_group = QGroupBox("全文操作")
        full_layout = QVBoxLayout(full_group)
        
        summary_btn = QPushButton("生成摘要")
        summary_btn.clicked.connect(lambda: self.action_triggered.emit("full_summary", {}))
        full_layout.addWidget(summary_btn)
        
        outline_btn = QPushButton("生成大纲")
        outline_btn.clicked.connect(lambda: self.action_triggered.emit("generate_outline", {}))
        full_layout.addWidget(outline_btn)
        
        audit_btn = QPushButton("内容审核")
        audit_btn.clicked.connect(lambda: self.action_triggered.emit("content_audit", {}))
        full_layout.addWidget(audit_btn)
        
        layout.addWidget(full_group)
        
        layout.addStretch()
        
    def translate_text(self):
        """翻译文本"""
        target_lang = self.lang_combo.currentText()
        self.action_triggered.emit("translate", {"target_language": target_lang})
        
    def convert_style(self):
        """转换风格"""
        target_style = self.style_combo.currentText()
        self.action_triggered.emit("style_convert", {"target_style": target_style})

class ChatWidget(QFrame):
    """聊天小部件"""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.chat_history = []
        
    def setup_ui(self):
        """设置界面"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("AI聊天助手")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 聊天历史显示
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(200)
        layout.addWidget(self.chat_display)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("输入消息或问题...")
        self.chat_input.returnPressed.connect(self.send_message)
        
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)
        
        # 清除按钮
        clear_btn = QPushButton("清除历史")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)
        
    def send_message(self):
        """发送消息"""
        message = self.chat_input.text().strip()
        if message:
            self.chat_input.clear()
            self.add_message("用户", message)
            self.message_sent.emit(message)
            
    def add_message(self, sender, message):
        """添加消息到历史"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_history.append({"sender": sender, "message": message, "time": timestamp})
        self.update_display()
        
    def update_display(self):
        """更新显示"""
        self.chat_display.clear()
        for msg in self.chat_history[-10:]:  # 只显示最近10条
            if msg["sender"] == "用户":
                self.chat_display.append(f'<span style="color: blue;">[{msg["time"]}] 用户: {msg["message"]}</span>')
            else:
                self.chat_display.append(f'<span style="color: green;">[{msg["time"]}] AI: {msg["message"]}</span>')
        
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
    def clear_history(self):
        """清除历史"""
        self.chat_history.clear()
        self.chat_display.clear()

class LLMAssistant(QWidget):
    """LLM助手主界面"""
    
    text_processed = pyqtSignal(str, str)  # 处理后文本, 操作类型
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_worker = None
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 快捷操作标签页
        self.quick_actions = QuickActionWidget()
        self.tab_widget.addTab(self.quick_actions, "快捷操作")
        
        # 聊天标签页
        self.chat_widget = ChatWidget()
        self.tab_widget.addTab(self.chat_widget, "AI聊天")
        
        layout.addWidget(self.tab_widget)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        # 连接信号
        self.quick_actions.action_triggered.connect(self.handle_quick_action)
        self.chat_widget.message_sent.connect(self.handle_chat_message)
        
    def handle_quick_action(self, action_type, params):
        """处理快捷操作"""
        # 获取选中文本
        if hasattr(self.parent(), 'text_editor'):
            text_editor = self.parent().text_editor
            cursor = text_editor.textCursor()
            selected_text = cursor.selectedText()
            
            if action_type == "full_summary":
                # 全文摘要
                text = text_editor.toPlainText()
                if text.strip():
                    self.process_text("summarize", text, params)
                else:
                    QMessageBox.information(self, "提示", "文档为空")
            elif selected_text:
                self.process_text(action_type, selected_text, params)
            else:
                QMessageBox.information(self, "提示", "请先选择要处理的文本")
                
    def handle_chat_message(self, message):
        """处理聊天消息"""
        self.process_text("chat", message, {})
        
    def process_text(self, operation, text, params=None):
        """处理文本"""
        if self.current_worker and self.current_worker.isRunning():
            QMessageBox.information(self, "提示", "正在处理中，请稍候...")
            return
            
        # 检查配置
        config = Config()
        if not config.OPENAI_API_KEY:
            QMessageBox.warning(self, "配置错误", "请先在设置中配置API Key")
            return
            
        # 创建工作线程
        self.current_worker = LLMWorker(operation, text, params)
        self.current_worker.finished.connect(self.on_processing_finished)
        self.current_worker.error.connect(self.on_processing_error)
        self.current_worker.progress.connect(self.on_processing_progress)
        
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("处理中...")
        
        # 启动处理
        self.current_worker.start()
        
    def on_processing_finished(self, result, operation):
        """处理完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("就绪")
        
        if operation == "chat":
            # 聊天回复
            self.chat_widget.add_message("AI", result)
        else:
            # 文本处理结果
            self.text_processed.emit(result, "replace")
            
    def on_processing_error(self, error_message):
        """处理错误"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("错误")
        QMessageBox.critical(self, "处理失败", error_message)
        
    def on_processing_progress(self, message):
        """处理进度更新"""
        self.status_label.setText(message)
        
    # 公共接口方法
    def polish_text(self, text):
        """润色文本"""
        self.process_text("polish", text)
        
    def expand_text(self, text):
        """扩写文本"""
        self.process_text("expand", text)
        
    def contract_text(self, text):
        """缩写文本"""
        self.process_text("contract", text)
        
    def summarize_text(self, text):
        """总结文本"""
        self.process_text("summarize", text)
        
    def translate_text(self, text, target_language="英文"):
        """翻译文本"""
        self.process_text("translate", text, {"target_language": target_language})
        
    def ask_question(self, text, question="请解释这段文字的含义"):
        """对文本提问"""
        self.process_text("question", text, {"question": question})
        
    def generate_summary(self, text):
        """生成全文摘要"""
        self.process_text("summarize", text)
        
    def check_style(self, text):
        """检查风格一致性"""
        self.process_text("content_audit", text)
        
    def generate_outline(self, topic):
        """生成大纲"""
        self.process_text("generate_outline", topic)
        
    def generate_content(self, outline):
        """生成内容"""
        self.process_text("generate_content", outline)