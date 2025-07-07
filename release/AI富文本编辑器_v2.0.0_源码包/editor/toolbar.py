"""
Editor Toolbar Component
编辑器工具栏组件，提供格式化和编辑功能
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox,
    QSpinBox, QLabel, QColorDialog, QFontComboBox, QFrame,
    QButtonGroup, QToolButton, QMenu, QWidgetAction
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QAction

class ColorButton(QPushButton):
    """颜色选择按钮"""
    
    color_changed = pyqtSignal(QColor)
    
    def __init__(self, color=Qt.GlobalColor.black, parent=None):
        super().__init__(parent)
        self.current_color = QColor(color)
        self.setFixedSize(30, 25)
        self.clicked.connect(self.choose_color)
        self.update_button_color()
        
    def update_button_color(self):
        """更新按钮颜色显示"""
        # 创建颜色图标
        pixmap = QPixmap(20, 20)
        pixmap.fill(self.current_color)
        
        # 添加边框
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawRect(0, 0, 19, 19)
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        
    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.update_button_color()
            self.color_changed.emit(color)
            
    def set_color(self, color):
        """设置颜色"""
        self.current_color = QColor(color)
        self.update_button_color()

class EditorToolbar(QWidget):
    """编辑器工具栏"""
    
    format_applied = pyqtSignal(str, object)  # 格式类型, 格式值
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 第一行：字体和大小
        first_row = QHBoxLayout()
        
        # 字体选择
        first_row.addWidget(QLabel("字体:"))
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(120)
        first_row.addWidget(self.font_combo)
        
        # 字体大小
        first_row.addWidget(QLabel("大小:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(12)
        self.size_spin.setMaximumWidth(60)
        first_row.addWidget(self.size_spin)
        
        # 分隔符
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        first_row.addWidget(separator1)
        
        # 文字颜色
        first_row.addWidget(QLabel("颜色:"))
        self.text_color_btn = ColorButton(Qt.GlobalColor.black)
        first_row.addWidget(self.text_color_btn)
        
        first_row.addStretch()
        main_layout.addLayout(first_row)
        
        # 第二行：格式化按钮
        second_row = QHBoxLayout()
        
        # 加粗
        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.bold_btn.setFixedSize(30, 25)
        self.bold_btn.setToolTip("加粗 (Ctrl+B)")
        second_row.addWidget(self.bold_btn)
        
        # 斜体
        self.italic_btn = QPushButton("I")
        self.italic_btn.setCheckable(True)
        font = QFont("Arial", 10)
        font.setItalic(True)
        self.italic_btn.setFont(font)
        self.italic_btn.setFixedSize(30, 25)
        self.italic_btn.setToolTip("斜体 (Ctrl+I)")
        second_row.addWidget(self.italic_btn)
        
        # 下划线
        self.underline_btn = QPushButton("U")
        self.underline_btn.setCheckable(True)
        font = QFont("Arial", 10)
        font.setUnderline(True)
        self.underline_btn.setFont(font)
        self.underline_btn.setFixedSize(30, 25)
        self.underline_btn.setToolTip("下划线 (Ctrl+U)")
        second_row.addWidget(self.underline_btn)
        
        # 分隔符
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        second_row.addWidget(separator2)
        
        # 对齐方式
        self.align_left_btn = QPushButton("⟦")
        self.align_left_btn.setCheckable(True)
        self.align_left_btn.setFixedSize(30, 25)
        self.align_left_btn.setToolTip("左对齐")
        second_row.addWidget(self.align_left_btn)
        
        self.align_center_btn = QPushButton("⟧")
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.setFixedSize(30, 25)
        self.align_center_btn.setToolTip("居中对齐")
        second_row.addWidget(self.align_center_btn)
        
        self.align_right_btn = QPushButton("⟨")
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.setFixedSize(30, 25)
        self.align_right_btn.setToolTip("右对齐")
        second_row.addWidget(self.align_right_btn)
        
        # 对齐按钮组
        self.align_group = QButtonGroup()
        self.align_group.addButton(self.align_left_btn, 0)
        self.align_group.addButton(self.align_center_btn, 1)
        self.align_group.addButton(self.align_right_btn, 2)
        self.align_group.setExclusive(True)
        
        # 分隔符
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.VLine)
        second_row.addWidget(separator3)
        
        # 列表
        self.bullet_list_btn = QPushButton("•")
        self.bullet_list_btn.setCheckable(True)
        self.bullet_list_btn.setFixedSize(30, 25)
        self.bullet_list_btn.setToolTip("无序列表")
        second_row.addWidget(self.bullet_list_btn)
        
        self.number_list_btn = QPushButton("1.")
        self.number_list_btn.setCheckable(True)
        self.number_list_btn.setFixedSize(30, 25)
        self.number_list_btn.setToolTip("有序列表")
        second_row.addWidget(self.number_list_btn)
        
        # 分隔符
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.Shape.VLine)
        second_row.addWidget(separator4)
        
        # 插入功能
        self.insert_image_btn = QPushButton("图")
        self.insert_image_btn.setFixedSize(30, 25)
        self.insert_image_btn.setToolTip("插入图片")
        second_row.addWidget(self.insert_image_btn)
        
        self.insert_table_btn = QPushButton("表")
        self.insert_table_btn.setFixedSize(30, 25)
        self.insert_table_btn.setToolTip("插入表格")
        second_row.addWidget(self.insert_table_btn)
        
        # 分隔符
        separator5 = QFrame()
        separator5.setFrameShape(QFrame.Shape.VLine)
        second_row.addWidget(separator5)
        
        # 缩进
        self.indent_btn = QPushButton("→")
        self.indent_btn.setFixedSize(30, 25)
        self.indent_btn.setToolTip("增加缩进")
        second_row.addWidget(self.indent_btn)
        
        self.outdent_btn = QPushButton("←")
        self.outdent_btn.setFixedSize(30, 25)
        self.outdent_btn.setToolTip("减少缩进")
        second_row.addWidget(self.outdent_btn)
        
        second_row.addStretch()
        main_layout.addLayout(second_row)
        
        # 设置样式
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f8f8f8;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
            QPushButton:checked {
                background-color: #007acc;
                color: white;
            }
            QComboBox, QSpinBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px 5px;
                background-color: white;
            }
        """)
        
    def setup_connections(self):
        """设置信号连接"""
        # 字体相关
        self.font_combo.currentFontChanged.connect(
            lambda font: self.format_applied.emit("font_family", font.family())
        )
        self.size_spin.valueChanged.connect(
            lambda size: self.format_applied.emit("font_size", size)
        )
        self.text_color_btn.color_changed.connect(
            lambda color: self.format_applied.emit("text_color", color)
        )
        
        # 格式按钮
        self.bold_btn.clicked.connect(
            lambda: self.format_applied.emit("bold", None)
        )
        self.italic_btn.clicked.connect(
            lambda: self.format_applied.emit("italic", None)
        )
        self.underline_btn.clicked.connect(
            lambda: self.format_applied.emit("underline", None)
        )
        
        # 对齐按钮
        self.align_group.buttonClicked.connect(self.on_align_clicked)
        
        # 列表按钮
        self.bullet_list_btn.clicked.connect(
            lambda: self.format_applied.emit("list_bullet", None)
        )
        self.number_list_btn.clicked.connect(
            lambda: self.format_applied.emit("list_number", None)
        )
        
        # 插入按钮
        self.insert_image_btn.clicked.connect(
            lambda: self.format_applied.emit("insert_image", None)
        )
        self.insert_table_btn.clicked.connect(
            lambda: self.format_applied.emit("insert_table", None)
        )
        
        # 缩进按钮
        self.indent_btn.clicked.connect(
            lambda: self.format_applied.emit("indent", None)
        )
        self.outdent_btn.clicked.connect(
            lambda: self.format_applied.emit("outdent", None)
        )
        
    def on_align_clicked(self, button):
        """对齐按钮点击处理"""
        button_id = self.align_group.id(button)
        if button_id == 0:
            self.format_applied.emit("align_left", None)
        elif button_id == 1:
            self.format_applied.emit("align_center", None)
        elif button_id == 2:
            self.format_applied.emit("align_right", None)
            
    def update_format_state(self, cursor):
        """更新格式状态"""
        # 获取当前格式
        char_format = cursor.charFormat()
        block_format = cursor.blockFormat()
        
        # 更新字体
        font = char_format.font()
        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentFont(font)
        self.font_combo.blockSignals(False)
        
        # 更新字体大小
        self.size_spin.blockSignals(True)
        self.size_spin.setValue(int(font.pointSize()) if font.pointSize() > 0 else 12)
        self.size_spin.blockSignals(False)
        
        # 更新格式按钮状态
        self.bold_btn.setChecked(font.bold())
        self.italic_btn.setChecked(font.italic())
        self.underline_btn.setChecked(font.underline())
        
        # 更新文字颜色
        text_color = char_format.foreground().color()
        if text_color.isValid():
            self.text_color_btn.set_color(text_color)
        
        # 更新对齐状态
        alignment = block_format.alignment()
        self.align_group.blockSignals(True)
        if alignment == Qt.AlignmentFlag.AlignLeft:
            self.align_left_btn.setChecked(True)
        elif alignment == Qt.AlignmentFlag.AlignCenter:
            self.align_center_btn.setChecked(True)
        elif alignment == Qt.AlignmentFlag.AlignRight:
            self.align_right_btn.setChecked(True)
        else:
            self.align_left_btn.setChecked(True)  # 默认左对齐
        self.align_group.blockSignals(False)
        
        # 更新列表状态
        current_list = cursor.currentList()
        if current_list:
            list_format = current_list.format()
            if list_format.style() == 1:  # ListDisc
                self.bullet_list_btn.setChecked(True)
                self.number_list_btn.setChecked(False)
            elif list_format.style() == 4:  # ListDecimal
                self.bullet_list_btn.setChecked(False)
                self.number_list_btn.setChecked(True)
            else:
                self.bullet_list_btn.setChecked(False)
                self.number_list_btn.setChecked(False)
        else:
            self.bullet_list_btn.setChecked(False)
            self.number_list_btn.setChecked(False)