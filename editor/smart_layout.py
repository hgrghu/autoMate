"""
Smart Layout Engine Module
智能排版引擎模块，支持自动排版和样式设计
"""

import re
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QComboBox, QLabel, QSpinBox, QCheckBox, QProgressBar,
    QGroupBox, QTabWidget, QWidget, QSlider, QColorDialog,
    QMessageBox, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextBlockFormat, QTextDocument

from xbrain.core.chat import run
from xbrain.utils.config import Config

@dataclass
class LayoutStyle:
    """排版样式配置"""
    name: str
    font_family: str
    base_font_size: int
    line_spacing: float
    paragraph_spacing: float
    heading_sizes: Dict[int, int]  # {level: size}
    colors: Dict[str, str]  # {element: color}
    margins: Dict[str, int]  # {direction: pixels}
    alignment: str
    
class DocumentAnalyzer:
    """文档分析器"""
    
    def __init__(self):
        self.patterns = {
            'heading': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'bullet_list': re.compile(r'^\s*[-*+]\s+(.+)$', re.MULTILINE),
            'numbered_list': re.compile(r'^\s*\d+\.\s+(.+)$', re.MULTILINE),
            'quote': re.compile(r'^>\s+(.+)$', re.MULTILINE),
            'code_block': re.compile(r'```[\s\S]*?```', re.MULTILINE),
            'table': re.compile(r'\|.*\|', re.MULTILINE),
            'emphasis': re.compile(r'\*\*(.+?)\*\*|\*(.+?)\*'),
            'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
        }
        
    def analyze_document(self, text: str) -> Dict:
        """分析文档结构和内容"""
        analysis = {
            'word_count': len(text.split()),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
            'structure': self.analyze_structure(text),
            'content_type': self.detect_content_type(text),
            'complexity': self.assess_complexity(text),
            'formatting_elements': self.detect_formatting_elements(text)
        }
        
        return analysis
        
    def analyze_structure(self, text: str) -> Dict:
        """分析文档结构"""
        structure = {
            'headings': [],
            'sections': 0,
            'max_heading_level': 0,
            'has_toc': False,
            'has_abstract': False,
            'has_conclusion': False
        }
        
        # 检测标题
        headings = self.patterns['heading'].findall(text)
        for level_str, title in headings:
            level = len(level_str)
            structure['headings'].append({'level': level, 'title': title})
            structure['max_heading_level'] = max(structure['max_heading_level'], level)
            
        structure['sections'] = len([h for h in structure['headings'] if h['level'] <= 2])
        
        # 检测特殊部分
        text_lower = text.lower()
        structure['has_toc'] = any(keyword in text_lower for keyword in ['目录', 'contents', 'toc'])
        structure['has_abstract'] = any(keyword in text_lower for keyword in ['摘要', 'abstract', '概述'])
        structure['has_conclusion'] = any(keyword in text_lower for keyword in ['结论', 'conclusion', '总结'])
        
        return structure
        
    def detect_content_type(self, text: str) -> str:
        """检测文档类型"""
        text_lower = text.lower()
        
        # 学术类关键词
        academic_keywords = ['摘要', 'abstract', '关键词', 'keywords', '参考文献', 'references', '方法', 'methodology']
        # 商业类关键词
        business_keywords = ['营销', 'marketing', '财务', 'financial', '战略', 'strategy', '投资', 'investment']
        # 技术类关键词
        technical_keywords = ['api', '接口', '算法', 'algorithm', '架构', 'architecture', '代码', 'code']
        
        academic_score = sum(1 for keyword in academic_keywords if keyword in text_lower)
        business_score = sum(1 for keyword in business_keywords if keyword in text_lower)
        technical_score = sum(1 for keyword in technical_keywords if keyword in text_lower)
        
        if academic_score >= max(business_score, technical_score):
            return 'academic'
        elif business_score >= technical_score:
            return 'business'
        elif technical_score > 0:
            return 'technical'
        else:
            return 'general'
            
    def assess_complexity(self, text: str) -> str:
        """评估文档复杂度"""
        word_count = len(text.split())
        avg_sentence_length = word_count / max(text.count('.'), 1)
        
        if word_count < 500:
            return 'simple'
        elif word_count < 2000 and avg_sentence_length < 20:
            return 'medium'
        else:
            return 'complex'
            
    def detect_formatting_elements(self, text: str) -> Dict:
        """检测格式化元素"""
        elements = {}
        
        for element_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            elements[element_type] = len(matches)
            
        return elements

class SmartLayoutEngine:
    """智能排版引擎"""
    
    def __init__(self):
        self.analyzer = DocumentAnalyzer()
        self.predefined_styles = self.load_predefined_styles()
        
    def load_predefined_styles(self) -> Dict[str, LayoutStyle]:
        """加载预定义样式"""
        styles = {}
        
        # 学术论文样式
        styles['academic'] = LayoutStyle(
            name="学术论文",
            font_family="Times New Roman",
            base_font_size=12,
            line_spacing=1.5,
            paragraph_spacing=12,
            heading_sizes={1: 18, 2: 16, 3: 14, 4: 12, 5: 12, 6: 12},
            colors={'text': '#000000', 'heading': '#000080', 'emphasis': '#800000'},
            margins={'top': 25, 'bottom': 25, 'left': 30, 'right': 25},
            alignment='justify'
        )
        
        # 商业文档样式
        styles['business'] = LayoutStyle(
            name="商业文档",
            font_family="Calibri",
            base_font_size=11,
            line_spacing=1.2,
            paragraph_spacing=10,
            heading_sizes={1: 22, 2: 18, 3: 14, 4: 12, 5: 11, 6: 11},
            colors={'text': '#333333', 'heading': '#0066CC', 'emphasis': '#CC6600'},
            margins={'top': 20, 'bottom': 20, 'left': 25, 'right': 25},
            alignment='left'
        )
        
        # 技术文档样式
        styles['technical'] = LayoutStyle(
            name="技术文档",
            font_family="Consolas",
            base_font_size=10,
            line_spacing=1.3,
            paragraph_spacing=8,
            heading_sizes={1: 16, 2: 14, 3: 12, 4: 11, 5: 10, 6: 10},
            colors={'text': '#2F2F2F', 'heading': '#006600', 'emphasis': '#660066'},
            margins={'top': 15, 'bottom': 15, 'left': 20, 'right': 20},
            alignment='left'
        )
        
        # 现代简约样式
        styles['modern'] = LayoutStyle(
            name="现代简约",
            font_family="Microsoft YaHei",
            base_font_size=12,
            line_spacing=1.6,
            paragraph_spacing=15,
            heading_sizes={1: 24, 2: 20, 3: 16, 4: 14, 5: 12, 6: 12},
            colors={'text': '#444444', 'heading': '#1A73E8', 'emphasis': '#E8710A'},
            margins={'top': 30, 'bottom': 30, 'left': 40, 'right': 40},
            alignment='left'
        )
        
        return styles
        
    def suggest_layout(self, text: str) -> Tuple[str, LayoutStyle]:
        """建议最佳排版方案"""
        analysis = self.analyzer.analyze_document(text)
        
        # 根据内容类型选择基础样式
        content_type = analysis['content_type']
        if content_type in self.predefined_styles:
            suggested_style = self.predefined_styles[content_type]
        else:
            suggested_style = self.predefined_styles['modern']
            
        # 根据复杂度调整
        if analysis['complexity'] == 'simple':
            suggested_style.line_spacing *= 0.9
            suggested_style.paragraph_spacing = int(suggested_style.paragraph_spacing * 0.8)
        elif analysis['complexity'] == 'complex':
            suggested_style.line_spacing *= 1.1
            suggested_style.paragraph_spacing = int(suggested_style.paragraph_spacing * 1.2)
            
        return content_type, suggested_style
        
    def apply_ai_layout_suggestions(self, text: str) -> str:
        """应用AI排版建议"""
        try:
            prompt = f"""
请分析以下文档并提供排版建议：

文档内容：
{text[:1000]}...

请分析：
1. 文档类型和风格
2. 内容结构和层次
3. 最适合的排版方案
4. 具体的格式化建议

请以JSON格式返回建议：
{{
    "document_type": "文档类型",
    "layout_style": "推荐样式",
    "formatting_suggestions": [
        "具体建议1",
        "具体建议2"
    ],
    "color_scheme": "色彩方案",
    "typography": "字体建议"
}}
"""
            
            response = run([{"role": "user", "content": prompt}])
            
            try:
                suggestions = json.loads(response)
                return self.apply_suggestions_to_text(text, suggestions)
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回原文本
                return text
                
        except Exception:
            return text
            
    def apply_suggestions_to_text(self, text: str, suggestions: Dict) -> str:
        """将AI建议应用到文本"""
        # 这里可以根据AI建议调整文本格式
        # 由于是演示，我们主要返回格式化后的文本
        formatted_text = text
        
        # 如果有具体的格式化建议，可以在这里实现
        if 'formatting_suggestions' in suggestions:
            for suggestion in suggestions['formatting_suggestions']:
                # 实现具体的格式化逻辑
                pass
                
        return formatted_text

class LayoutWorker(QThread):
    """排版处理工作线程"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(str, dict)  # 格式化文本, 样式信息
    error = pyqtSignal(str)
    
    def __init__(self, text, layout_options):
        super().__init__()
        self.text = text
        self.layout_options = layout_options
        self.engine = SmartLayoutEngine()
        
    def run(self):
        """执行排版处理"""
        try:
            self.progress.emit("分析文档结构...")
            
            # 分析文档并获取建议
            content_type, suggested_style = self.engine.suggest_layout(self.text)
            
            self.progress.emit("生成排版建议...")
            
            # 如果启用了AI建议
            if self.layout_options.get('use_ai_suggestions', False):
                formatted_text = self.engine.apply_ai_layout_suggestions(self.text)
            else:
                formatted_text = self.text
                
            self.progress.emit("应用样式设置...")
            
            # 准备样式信息
            style_info = {
                'content_type': content_type,
                'suggested_style': suggested_style,
                'layout_options': self.layout_options
            }
            
            self.finished.emit(formatted_text, style_info)
            
        except Exception as e:
            self.error.emit(f"排版处理失败: {str(e)}")

class SmartLayoutDialog(QDialog):
    """智能排版对话框"""
    
    layout_applied = pyqtSignal(str, dict)  # 格式化文本, 样式信息
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.original_text = text
        self.engine = SmartLayoutEngine()
        self.setup_ui()
        self.analyze_document()
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("智能排版设计器")
        self.setModal(True)
        self.resize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 文档分析标签页
        self.setup_analysis_tab()
        
        # 样式选择标签页
        self.setup_style_tab()
        
        # 高级设置标签页
        self.setup_advanced_tab()
        
        # AI建议标签页
        self.setup_ai_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 预览区域
        preview_group = QGroupBox("实时预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_area = QTextEdit()
        self.preview_area.setMaximumHeight(200)
        self.preview_area.setReadOnly(True)
        preview_layout.addWidget(self.preview_area)
        
        layout.addWidget(preview_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("重新分析")
        self.analyze_btn.clicked.connect(self.analyze_document)
        
        self.preview_btn = QPushButton("预览效果")
        self.preview_btn.clicked.connect(self.preview_layout)
        
        self.apply_btn = QPushButton("应用排版")
        self.apply_btn.clicked.connect(self.apply_layout)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def setup_analysis_tab(self):
        """设置文档分析标签页"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # 文档信息
        info_group = QGroupBox("文档信息")
        info_layout = QVBoxLayout(info_group)
        
        self.info_labels = {}
        info_items = [
            ('word_count', '字数统计'),
            ('paragraph_count', '段落数量'),
            ('content_type', '内容类型'),
            ('complexity', '复杂程度'),
            ('sections', '章节数量')
        ]
        
        for key, label in info_items:
            self.info_labels[key] = QLabel(f"{label}: 分析中...")
            info_layout.addWidget(self.info_labels[key])
            
        layout.addWidget(info_group)
        
        # 结构分析
        structure_group = QGroupBox("文档结构")
        structure_layout = QVBoxLayout(structure_group)
        
        self.structure_list = QListWidget()
        structure_layout.addWidget(self.structure_list)
        
        layout.addWidget(structure_group)
        
        # 建议
        suggestion_group = QGroupBox("排版建议")
        suggestion_layout = QVBoxLayout(suggestion_group)
        
        self.suggestion_text = QTextEdit()
        self.suggestion_text.setMaximumHeight(100)
        self.suggestion_text.setReadOnly(True)
        suggestion_layout.addWidget(self.suggestion_text)
        
        layout.addWidget(suggestion_group)
        
        self.tab_widget.addTab(analysis_widget, "文档分析")
        
    def setup_style_tab(self):
        """设置样式选择标签页"""
        style_widget = QWidget()
        layout = QVBoxLayout(style_widget)
        
        # 预设样式
        preset_group = QGroupBox("预设样式")
        preset_layout = QVBoxLayout(preset_group)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["学术论文", "商业文档", "技术文档", "现代简约", "自定义"])
        self.style_combo.currentTextChanged.connect(self.on_style_changed)
        preset_layout.addWidget(self.style_combo)
        
        layout.addWidget(preset_group)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QVBoxLayout(font_group)
        
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("字体:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Microsoft YaHei", "Times New Roman", "Calibri", "Consolas", "宋体", "黑体"])
        font_family_layout.addWidget(self.font_family_combo)
        font_layout.addLayout(font_family_layout)
        
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("基础字号:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_size_layout.addWidget(self.font_size_spin)
        font_layout.addLayout(font_size_layout)
        
        layout.addWidget(font_group)
        
        # 间距设置
        spacing_group = QGroupBox("间距设置")
        spacing_layout = QVBoxLayout(spacing_group)
        
        line_spacing_layout = QHBoxLayout()
        line_spacing_layout.addWidget(QLabel("行间距:"))
        self.line_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_spacing_slider.setRange(100, 300)
        self.line_spacing_slider.setValue(150)
        self.line_spacing_value = QLabel("1.5")
        line_spacing_layout.addWidget(self.line_spacing_slider)
        line_spacing_layout.addWidget(self.line_spacing_value)
        spacing_layout.addLayout(line_spacing_layout)
        
        para_spacing_layout = QHBoxLayout()
        para_spacing_layout.addWidget(QLabel("段落间距:"))
        self.para_spacing_spin = QSpinBox()
        self.para_spacing_spin.setRange(0, 30)
        self.para_spacing_spin.setValue(12)
        para_spacing_layout.addWidget(self.para_spacing_spin)
        spacing_layout.addLayout(para_spacing_layout)
        
        layout.addWidget(spacing_group)
        
        # 连接信号
        self.line_spacing_slider.valueChanged.connect(
            lambda v: self.line_spacing_value.setText(f"{v/100:.1f}")
        )
        
        self.tab_widget.addTab(style_widget, "样式设置")
        
    def setup_advanced_tab(self):
        """设置高级标签页"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # 页面设置
        page_group = QGroupBox("页面设置")
        page_layout = QVBoxLayout(page_group)
        
        margin_layout = QHBoxLayout()
        margin_layout.addWidget(QLabel("页边距:"))
        
        self.margin_top_spin = QSpinBox()
        self.margin_top_spin.setRange(0, 100)
        self.margin_top_spin.setValue(25)
        margin_layout.addWidget(QLabel("上:"))
        margin_layout.addWidget(self.margin_top_spin)
        
        self.margin_bottom_spin = QSpinBox()
        self.margin_bottom_spin.setRange(0, 100)
        self.margin_bottom_spin.setValue(25)
        margin_layout.addWidget(QLabel("下:"))
        margin_layout.addWidget(self.margin_bottom_spin)
        
        self.margin_left_spin = QSpinBox()
        self.margin_left_spin.setRange(0, 100)
        self.margin_left_spin.setValue(30)
        margin_layout.addWidget(QLabel("左:"))
        margin_layout.addWidget(self.margin_left_spin)
        
        self.margin_right_spin = QSpinBox()
        self.margin_right_spin.setRange(0, 100)
        self.margin_right_spin.setValue(25)
        margin_layout.addWidget(QLabel("右:"))
        margin_layout.addWidget(self.margin_right_spin)
        
        page_layout.addLayout(margin_layout)
        layout.addWidget(page_group)
        
        # 标题设置
        heading_group = QGroupBox("标题设置")
        heading_layout = QVBoxLayout(heading_group)
        
        for i in range(1, 4):
            heading_size_layout = QHBoxLayout()
            heading_size_layout.addWidget(QLabel(f"H{i}标题大小:"))
            
            size_spin = QSpinBox()
            size_spin.setRange(8, 36)
            size_spin.setValue(18 - i * 2)
            setattr(self, f'heading_{i}_size', size_spin)
            
            heading_size_layout.addWidget(size_spin)
            heading_layout.addLayout(heading_size_layout)
            
        layout.addWidget(heading_group)
        
        # 颜色设置
        color_group = QGroupBox("颜色设置")
        color_layout = QVBoxLayout(color_group)
        
        text_color_layout = QHBoxLayout()
        text_color_layout.addWidget(QLabel("正文颜色:"))
        self.text_color_btn = QPushButton("选择颜色")
        self.text_color_btn.clicked.connect(lambda: self.choose_color('text'))
        text_color_layout.addWidget(self.text_color_btn)
        color_layout.addLayout(text_color_layout)
        
        heading_color_layout = QHBoxLayout()
        heading_color_layout.addWidget(QLabel("标题颜色:"))
        self.heading_color_btn = QPushButton("选择颜色")
        self.heading_color_btn.clicked.connect(lambda: self.choose_color('heading'))
        heading_color_layout.addWidget(self.heading_color_btn)
        color_layout.addLayout(heading_color_layout)
        
        layout.addWidget(color_group)
        layout.addStretch()
        
        self.tab_widget.addTab(advanced_widget, "高级设置")
        
    def setup_ai_tab(self):
        """设置AI建议标签页"""
        ai_widget = QWidget()
        layout = QVBoxLayout(ai_widget)
        
        # AI分析选项
        options_group = QGroupBox("AI分析选项")
        options_layout = QVBoxLayout(options_group)
        
        self.use_ai_suggestions = QCheckBox("启用AI智能排版建议")
        self.use_ai_suggestions.setChecked(True)
        options_layout.addWidget(self.use_ai_suggestions)
        
        self.analyze_content_type = QCheckBox("自动识别文档类型")
        self.analyze_content_type.setChecked(True)
        options_layout.addWidget(self.analyze_content_type)
        
        self.suggest_improvements = QCheckBox("提供改进建议")
        self.suggest_improvements.setChecked(True)
        options_layout.addWidget(self.suggest_improvements)
        
        layout.addWidget(options_group)
        
        # AI建议显示
        suggestions_group = QGroupBox("AI排版建议")
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        self.ai_suggestions_text = QTextEdit()
        self.ai_suggestions_text.setReadOnly(True)
        self.ai_suggestions_text.setPlaceholderText("AI分析建议将在这里显示...")
        suggestions_layout.addWidget(self.ai_suggestions_text)
        
        get_suggestions_btn = QPushButton("获取AI建议")
        get_suggestions_btn.clicked.connect(self.get_ai_suggestions)
        suggestions_layout.addWidget(get_suggestions_btn)
        
        layout.addWidget(suggestions_group)
        
        self.tab_widget.addTab(ai_widget, "AI建议")
        
    def analyze_document(self):
        """分析文档"""
        analysis = self.engine.analyzer.analyze_document(self.original_text)
        
        # 更新信息标签
        self.info_labels['word_count'].setText(f"字数统计: {analysis['word_count']}")
        self.info_labels['paragraph_count'].setText(f"段落数量: {analysis['paragraph_count']}")
        self.info_labels['content_type'].setText(f"内容类型: {analysis['content_type']}")
        self.info_labels['complexity'].setText(f"复杂程度: {analysis['complexity']}")
        self.info_labels['sections'].setText(f"章节数量: {analysis['structure']['sections']}")
        
        # 更新结构列表
        self.structure_list.clear()
        for heading in analysis['structure']['headings']:
            indent = "  " * (heading['level'] - 1)
            item_text = f"{indent}H{heading['level']}: {heading['title']}"
            self.structure_list.addItem(item_text)
            
        # 生成建议
        content_type, suggested_style = self.engine.suggest_layout(self.original_text)
        suggestion_text = f"建议使用 '{suggested_style.name}' 样式\n"
        suggestion_text += f"检测到的文档类型: {content_type}\n"
        suggestion_text += f"推荐字体: {suggested_style.font_family}\n"
        suggestion_text += f"推荐字号: {suggested_style.base_font_size}pt"
        
        self.suggestion_text.setPlainText(suggestion_text)
        
        # 应用建议样式到控件
        self.apply_suggested_style(suggested_style)
        
    def apply_suggested_style(self, style: LayoutStyle):
        """应用建议样式到控件"""
        # 设置字体
        font_index = self.font_family_combo.findText(style.font_family)
        if font_index >= 0:
            self.font_family_combo.setCurrentIndex(font_index)
            
        # 设置字号
        self.font_size_spin.setValue(style.base_font_size)
        
        # 设置行间距
        self.line_spacing_slider.setValue(int(style.line_spacing * 100))
        
        # 设置段落间距
        self.para_spacing_spin.setValue(int(style.paragraph_spacing))
        
        # 设置页边距
        self.margin_top_spin.setValue(style.margins['top'])
        self.margin_bottom_spin.setValue(style.margins['bottom'])
        self.margin_left_spin.setValue(style.margins['left'])
        self.margin_right_spin.setValue(style.margins['right'])
        
    def on_style_changed(self, style_name):
        """样式选择改变"""
        style_map = {
            "学术论文": "academic",
            "商业文档": "business", 
            "技术文档": "technical",
            "现代简约": "modern"
        }
        
        if style_name in style_map:
            style_key = style_map[style_name]
            if style_key in self.engine.predefined_styles:
                self.apply_suggested_style(self.engine.predefined_styles[style_key])
                
    def choose_color(self, color_type):
        """选择颜色"""
        color = QColorDialog.getColor(Qt.GlobalColor.black, self)
        if color.isValid():
            btn = getattr(self, f'{color_type}_color_btn')
            btn.setStyleSheet(f"background-color: {color.name()}")
            btn.setProperty('color', color.name())
            
    def get_ai_suggestions(self):
        """获取AI建议"""
        if not self.use_ai_suggestions.isChecked():
            self.ai_suggestions_text.setPlainText("AI建议已禁用")
            return
            
        try:
            prompt = f"""
请分析以下文档并提供专业的排版建议：

文档内容（前500字）：
{self.original_text[:500]}

请提供：
1. 文档类型分析
2. 最适合的排版风格
3. 字体和颜色建议
4. 布局和间距建议
5. 提升可读性的具体建议

请用中文回复。
"""
            
            suggestions = run([{"role": "user", "content": prompt}])
            self.ai_suggestions_text.setPlainText(suggestions)
            
        except Exception as e:
            self.ai_suggestions_text.setPlainText(f"获取AI建议失败: {str(e)}")
            
    def preview_layout(self):
        """预览排版效果"""
        # 获取当前设置
        layout_options = self.get_layout_options()
        
        # 应用设置到预览区域
        sample_text = self.original_text[:500] + "..."
        self.preview_area.setPlainText(sample_text)
        
        # 应用字体设置
        font = QFont(layout_options['font_family'], layout_options['font_size'])
        self.preview_area.setFont(font)
        
    def get_layout_options(self):
        """获取当前排版选项"""
        return {
            'font_family': self.font_family_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'line_spacing': self.line_spacing_slider.value() / 100,
            'paragraph_spacing': self.para_spacing_spin.value(),
            'margins': {
                'top': self.margin_top_spin.value(),
                'bottom': self.margin_bottom_spin.value(),
                'left': self.margin_left_spin.value(),
                'right': self.margin_right_spin.value()
            },
            'heading_sizes': {
                1: getattr(self, 'heading_1_size').value(),
                2: getattr(self, 'heading_2_size').value(),
                3: getattr(self, 'heading_3_size').value()
            },
            'use_ai_suggestions': self.use_ai_suggestions.isChecked()
        }
        
    def apply_layout(self):
        """应用排版设置"""
        layout_options = self.get_layout_options()
        
        # 创建工作线程
        self.worker = LayoutWorker(self.original_text, layout_options)
        self.worker.finished.connect(self.on_layout_finished)
        self.worker.error.connect(self.on_layout_error)
        
        # 禁用按钮
        self.apply_btn.setEnabled(False)
        self.apply_btn.setText("正在处理...")
        
        # 启动处理
        self.worker.start()
        
    def on_layout_finished(self, formatted_text, style_info):
        """排版处理完成"""
        self.apply_btn.setEnabled(True)
        self.apply_btn.setText("应用排版")
        
        # 发送结果
        self.layout_applied.emit(formatted_text, style_info)
        
        QMessageBox.information(self, "完成", "排版设置已应用到编辑器！")
        self.accept()
        
    def on_layout_error(self, error_message):
        """排版处理错误"""
        self.apply_btn.setEnabled(True) 
        self.apply_btn.setText("应用排版")
        
        QMessageBox.critical(self, "错误", error_message)