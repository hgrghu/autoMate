"""
AI Document Generator Module
AI文档生成器模块，支持通过自然语言描述生成各种类型的文档
"""

import json
import re
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QComboBox, QLabel, QSpinBox, QCheckBox, QProgressBar,
    QGroupBox, QTabWidget, QWidget, QScrollArea, QFrame,
    QMessageBox, QLineEdit, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

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

class DocumentGeneratorWorker(QThread):
    """文档生成工作线程"""
    
    progress = pyqtSignal(str)  # 进度信息
    section_generated = pyqtSignal(str, str)  # 章节标题, 内容
    finished = pyqtSignal(str)  # 完整文档
    error = pyqtSignal(str)  # 错误信息
    
    def __init__(self, requirements, doc_type, settings):
        super().__init__()
        self.requirements = requirements
        self.doc_type = doc_type
        self.settings = settings
        
    def run(self):
        """执行文档生成"""
        try:
            self.progress.emit("正在分析需求...")
            
            # 1. 生成文档大纲
            outline = self.generate_outline()
            self.progress.emit("大纲生成完成，开始生成内容...")
            
            # 2. 逐章节生成内容
            full_document = ""
            sections = self.parse_outline(outline)
            
            for i, (title, description) in enumerate(sections):
                self.progress.emit(f"正在生成: {title}")
                content = self.generate_section_content(title, description, outline)
                
                formatted_content = self.format_section(title, content, i + 1)
                full_document += formatted_content + "\n\n"
                
                self.section_generated.emit(title, formatted_content)
                
            # 3. 应用文档样式
            self.progress.emit("应用文档样式...")
            styled_document = self.apply_document_style(full_document)
            
            self.finished.emit(styled_document)
            
        except Exception as e:
            self.error.emit(f"文档生成失败: {str(e)}")
            
    def generate_outline(self):
        """生成文档大纲"""
        prompt = f"""
请根据以下需求生成详细的{self.doc_type}大纲：

需求描述：
{self.requirements}

文档类型：{self.doc_type}
字数要求：{self.settings.get('word_count', '不限')}
详细程度：{self.settings.get('detail_level', '中等')}
目标受众：{self.settings.get('target_audience', '通用')}

请生成结构化的大纲，包含：
1. 主要章节标题
2. 每个章节的简要描述
3. 预计字数分配

大纲格式：
## 章节标题
- 章节描述
- 预计字数：xxx字

请确保大纲逻辑清晰，结构合理。
"""
        
        return run([{"role": "user", "content": prompt}])
        
    def parse_outline(self, outline):
        """解析大纲"""
        sections = []
        lines = outline.split('\n')
        
        current_title = ""
        current_desc = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                if current_title:
                    sections.append((current_title, current_desc))
                current_title = line[3:].strip()
                current_desc = ""
            elif line.startswith('- ') and not line.startswith('- 预计字数'):
                current_desc += line[2:] + " "
                
        if current_title:
            sections.append((current_title, current_desc))
            
        return sections
        
    def generate_section_content(self, title, description, full_outline):
        """生成章节内容"""
        prompt = f"""
请为以下章节生成详细内容：

章节标题：{title}
章节描述：{description}

整体文档大纲：
{full_outline}

文档类型：{self.doc_type}
写作风格：{self.settings.get('writing_style', '专业')}
详细程度：{self.settings.get('detail_level', '中等')}

请生成该章节的完整内容，要求：
1. 内容丰富、逻辑清晰
2. 符合{self.doc_type}的写作规范
3. 与整体大纲保持一致
4. 包含必要的细节和例子

请直接返回章节内容，不要包含章节标题。
"""
        
        return run([{"role": "user", "content": prompt}])
        
    def format_section(self, title, content, section_num):
        """格式化章节"""
        if self.doc_type in ['学术论文', '研究报告']:
            return f"## {section_num}. {title}\n\n{content}"
        elif self.doc_type in ['商业计划书', '项目方案']:
            return f"### {title}\n\n{content}"
        elif self.doc_type == '简历':
            return f"**{title}**\n\n{content}"
        else:
            return f"## {title}\n\n{content}"
            
    def apply_document_style(self, document):
        """应用文档样式"""
        # 根据文档类型应用特定样式
        if self.doc_type == '学术论文':
            return self.apply_academic_style(document)
        elif self.doc_type == '商业计划书':
            return self.apply_business_style(document)
        elif self.doc_type == '技术文档':
            return self.apply_technical_style(document)
        else:
            return document
            
    def apply_academic_style(self, document):
        """应用学术论文样式"""
        # 添加摘要部分
        styled_doc = "# 摘要\n\n[待完善]\n\n"
        styled_doc += "# 关键词\n\n[待完善]\n\n"
        styled_doc += document
        styled_doc += "\n\n# 参考文献\n\n[1] [待添加参考文献]\n"
        return styled_doc
        
    def apply_business_style(self, document):
        """应用商业计划书样式"""
        header = f"""
# 商业计划书

**文档生成时间**: {datetime.now().strftime('%Y年%m月%d日')}

---

## 执行摘要

[核心内容概述]

---

"""
        return header + document
        
    def apply_technical_style(self, document):
        """应用技术文档样式"""
        header = f"""
# 技术文档

**版本**: 1.0  
**日期**: {datetime.now().strftime('%Y-%m-%d')}  
**状态**: 草稿

---

"""
        return header + document

class DocumentGeneratorDialog(QDialog):
    """文档生成对话框"""
    
    document_generated = pyqtSignal(str)  # 生成的文档内容
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_worker = None
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("AI智能文档生成器")
        self.setModal(True)
        self.resize(800, 700)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 基础设置标签页
        self.setup_basic_tab()
        
        # 高级设置标签页
        self.setup_advanced_tab()
        
        # 模板选择标签页
        self.setup_template_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 进度显示
        progress_group = QGroupBox("生成进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("准备就绪")
        progress_layout.addWidget(self.progress_label)
        
        # 实时预览
        self.preview_area = QTextEdit()
        self.preview_area.setMaximumHeight(150)
        self.preview_area.setPlaceholderText("生成的内容将在这里实时显示...")
        progress_layout.addWidget(QLabel("实时预览:"))
        progress_layout.addWidget(self.preview_area)
        
        layout.addWidget(progress_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("开始生成")
        self.generate_btn.clicked.connect(self.start_generation)
        
        self.stop_btn = QPushButton("停止生成")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_generation)
        
        self.preview_btn = QPushButton("预览大纲")
        self.preview_btn.clicked.connect(self.preview_outline)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.preview_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def setup_basic_tab(self):
        """设置基础标签页"""
        basic_widget = QWidget()
        layout = QVBoxLayout(basic_widget)
        
        # 文档类型选择
        type_group = QGroupBox("文档类型")
        type_layout = QVBoxLayout(type_group)
        
        self.doc_type_combo = QComboBox()
        self.doc_type_combo.addItems([
            "学术论文", "研究报告", "商业计划书", "项目方案",
            "技术文档", "用户手册", "产品说明", "市场分析",
            "简历", "求职信", "演讲稿", "新闻稿",
            "博客文章", "社交媒体文案", "广告文案", "其他"
        ])
        type_layout.addWidget(QLabel("选择文档类型:"))
        type_layout.addWidget(self.doc_type_combo)
        
        layout.addWidget(type_group)
        
        # 需求描述
        req_group = QGroupBox("需求描述")
        req_layout = QVBoxLayout(req_group)
        
        req_layout.addWidget(QLabel("详细描述您要生成的文档内容:"))
        self.requirements_text = QTextEdit()
        self.requirements_text.setPlaceholderText(
            "请详细描述您的文档需求，例如：\n"
            "- 文档主题和目标\n"
            "- 包含的主要内容\n"
            "- 特殊要求或格式\n"
            "- 目标读者群体\n\n"
            "示例：写一份关于人工智能在教育领域应用的研究报告，"
            "需要包含现状分析、技术原理、应用案例、发展趋势等内容，"
            "面向教育工作者和技术人员，要求专业严谨但通俗易懂。"
        )
        self.requirements_text.setMaximumHeight(200)
        req_layout.addWidget(self.requirements_text)
        
        layout.addWidget(req_group)
        
        # 快速设置
        quick_group = QGroupBox("快速设置")
        quick_layout = QHBoxLayout(quick_group)
        
        # 字数设置
        quick_layout.addWidget(QLabel("目标字数:"))
        self.word_count_combo = QComboBox()
        self.word_count_combo.addItems(["不限", "1000字以内", "2000-3000字", "5000字以上", "自定义"])
        quick_layout.addWidget(self.word_count_combo)
        
        # 详细程度
        quick_layout.addWidget(QLabel("详细程度:"))
        self.detail_combo = QComboBox()
        self.detail_combo.addItems(["简要", "中等", "详细", "非常详细"])
        self.detail_combo.setCurrentText("中等")
        quick_layout.addWidget(self.detail_combo)
        
        layout.addWidget(quick_group)
        
        self.tab_widget.addTab(basic_widget, "基础设置")
        
    def setup_advanced_tab(self):
        """设置高级标签页"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # 写作风格
        style_group = QGroupBox("写作风格")
        style_layout = QVBoxLayout(style_group)
        
        style_layout.addWidget(QLabel("写作风格:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "专业", "学术", "商务", "通俗", "幽默", 
            "正式", "非正式", "技术性", "创意性"
        ])
        style_layout.addWidget(self.style_combo)
        
        style_layout.addWidget(QLabel("目标受众:"))
        self.audience_combo = QComboBox()
        self.audience_combo.addItems([
            "通用", "专业人士", "学生", "管理层", 
            "技术人员", "普通用户", "投资者", "客户"
        ])
        style_layout.addWidget(self.audience_combo)
        
        layout.addWidget(style_group)
        
        # 格式要求
        format_group = QGroupBox("格式要求")
        format_layout = QVBoxLayout(format_group)
        
        self.include_toc = QCheckBox("包含目录")
        self.include_toc.setChecked(True)
        format_layout.addWidget(self.include_toc)
        
        self.include_abstract = QCheckBox("包含摘要/概述")
        format_layout.addWidget(self.include_abstract)
        
        self.include_conclusion = QCheckBox("包含结论/总结")
        self.include_conclusion.setChecked(True)
        format_layout.addWidget(self.include_conclusion)
        
        self.include_references = QCheckBox("包含参考文献")
        format_layout.addWidget(self.include_references)
        
        layout.addWidget(format_group)
        
        # 自定义要求
        custom_group = QGroupBox("自定义要求")
        custom_layout = QVBoxLayout(custom_group)
        
        custom_layout.addWidget(QLabel("特殊要求或补充说明:"))
        self.custom_requirements = QTextEdit()
        self.custom_requirements.setMaximumHeight(100)
        self.custom_requirements.setPlaceholderText(
            "例如：使用特定的引用格式、包含特定的章节、避免某些内容等"
        )
        custom_layout.addWidget(self.custom_requirements)
        
        layout.addWidget(custom_group)
        layout.addStretch()
        
        self.tab_widget.addTab(advanced_widget, "高级设置")
        
    def setup_template_tab(self):
        """设置模板标签页"""
        template_widget = QWidget()
        layout = QVBoxLayout(template_widget)
        
        layout.addWidget(QLabel("选择文档模板:"))
        
        self.template_list = QListWidget()
        
        # 添加预设模板
        templates = [
            ("学术论文模板", "包含摘要、引言、方法、结果、讨论、结论等标准学术结构"),
            ("商业计划书模板", "包含执行摘要、市场分析、产品介绍、营销策略等商业要素"),
            ("技术文档模板", "包含概述、技术规格、实现细节、使用说明等技术内容"),
            ("项目报告模板", "包含项目背景、目标、进展、结果、风险等项目管理要素"),
            ("产品说明书模板", "包含产品概述、功能特性、使用方法、注意事项等"),
            ("市场分析报告模板", "包含市场概况、竞争分析、趋势预测、建议等"),
            ("自定义模板", "根据您的具体需求完全自定义生成")
        ]
        
        for name, desc in templates:
            item = QListWidgetItem(f"{name}\n{desc}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.template_list.addItem(item)
            
        self.template_list.setCurrentRow(0)
        layout.addWidget(self.template_list)
        
        # 模板预览
        preview_group = QGroupBox("模板预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(150)
        preview_layout.addWidget(self.template_preview)
        
        layout.addWidget(preview_group)
        
        # 连接信号
        self.template_list.currentItemChanged.connect(self.on_template_changed)
        self.on_template_changed()  # 初始化预览
        
        self.tab_widget.addTab(template_widget, "模板选择")
        
    def on_template_changed(self):
        """模板选择变化"""
        current_item = self.template_list.currentItem()
        if current_item:
            template_name = current_item.data(Qt.ItemDataRole.UserRole)
            preview_text = self.get_template_preview(template_name)
            self.template_preview.setPlainText(preview_text)
            
    def get_template_preview(self, template_name):
        """获取模板预览"""
        previews = {
            "学术论文模板": """
1. 摘要
2. 关键词
3. 引言
4. 文献综述
5. 研究方法
6. 研究结果
7. 讨论与分析
8. 结论
9. 参考文献
            """,
            "商业计划书模板": """
1. 执行摘要
2. 公司概述
3. 市场分析
4. 产品与服务
5. 营销策略
6. 运营计划
7. 财务预测
8. 风险评估
            """,
            "技术文档模板": """
1. 概述
2. 系统架构
3. 技术规格
4. 实现细节
5. API 文档
6. 部署指南
7. 故障排除
8. 版本历史
            """,
            "自定义模板": "将根据您的具体需求生成定制化的文档结构。"
        }
        
        return previews.get(template_name, "模板预览不可用")
        
    def preview_outline(self):
        """预览大纲"""
        requirements = self.requirements_text.toPlainText().strip()
        if not requirements:
            QMessageBox.warning(self, "提示", "请先填写需求描述")
            return
            
        # 生成大纲预览
        settings = self.get_generation_settings()
        
        try:
            prompt = f"""
请为以下需求生成文档大纲：

需求：{requirements}
文档类型：{self.doc_type_combo.currentText()}
详细程度：{settings['detail_level']}

请生成简洁的大纲结构，只包含主要章节标题和简要说明。
"""
            
            outline = run([{"role": "user", "content": prompt}])
            
            # 显示预览对话框
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("大纲预览")
            preview_dialog.resize(600, 400)
            
            layout = QVBoxLayout(preview_dialog)
            layout.addWidget(QLabel("生成的文档大纲:"))
            
            preview_text = QTextEdit()
            preview_text.setPlainText(outline)
            preview_text.setReadOnly(True)
            layout.addWidget(preview_text)
            
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(preview_dialog.accept)
            layout.addWidget(close_btn)
            
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"预览生成失败: {str(e)}")
            
    def get_generation_settings(self):
        """获取生成设置"""
        return {
            'word_count': self.word_count_combo.currentText(),
            'detail_level': self.detail_combo.currentText(),
            'writing_style': self.style_combo.currentText(),
            'target_audience': self.audience_combo.currentText(),
            'include_toc': self.include_toc.isChecked(),
            'include_abstract': self.include_abstract.isChecked(),
            'include_conclusion': self.include_conclusion.isChecked(),
            'include_references': self.include_references.isChecked(),
            'custom_requirements': self.custom_requirements.toPlainText().strip()
        }
        
    def start_generation(self):
        """开始生成文档"""
        requirements = self.requirements_text.toPlainText().strip()
        if not requirements:
            QMessageBox.warning(self, "提示", "请先填写需求描述")
            return
            
        # 检查API配置
        config = Config()
        if not config.OPENAI_API_KEY:
            QMessageBox.warning(self, "配置错误", "请先在设置中配置API Key")
            return
            
        # 获取设置
        doc_type = self.doc_type_combo.currentText()
        settings = self.get_generation_settings()
        
        # 创建工作线程
        self.current_worker = DocumentGeneratorWorker(requirements, doc_type, settings)
        self.current_worker.progress.connect(self.on_progress_update)
        self.current_worker.section_generated.connect(self.on_section_generated)
        self.current_worker.finished.connect(self.on_generation_finished)
        self.current_worker.error.connect(self.on_generation_error)
        
        # 更新界面状态
        self.generate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.preview_area.clear()
        
        # 启动生成
        self.current_worker.start()
        
    def stop_generation(self):
        """停止生成"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()
            
        self.reset_ui_state()
        self.progress_label.setText("生成已停止")
        
    def on_progress_update(self, message):
        """进度更新"""
        self.progress_label.setText(message)
        
    def on_section_generated(self, title, content):
        """章节生成完成"""
        self.preview_area.append(f"### {title}\n")
        self.preview_area.append(content[:200] + "...\n\n")
        
        # 滚动到底部
        self.preview_area.verticalScrollBar().setValue(
            self.preview_area.verticalScrollBar().maximum()
        )
        
    def on_generation_finished(self, document):
        """生成完成"""
        self.reset_ui_state()
        self.progress_label.setText("生成完成！")
        
        # 发送生成的文档
        self.document_generated.emit(document)
        
        # 显示完成消息
        QMessageBox.information(
            self, "生成完成",
            "文档生成完成！内容已插入到编辑器中。\n\n"
            "您可以继续编辑和优化文档内容。"
        )
        
        self.accept()
        
    def on_generation_error(self, error_message):
        """生成错误"""
        self.reset_ui_state()
        self.progress_label.setText("生成失败")
        QMessageBox.critical(self, "生成失败", error_message)
        
    def reset_ui_state(self):
        """重置界面状态"""
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)