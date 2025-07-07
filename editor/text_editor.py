"""
AI Enhanced Text Editor Component
增强的文本编辑器组件，支持富文本编辑、图片插入、表格操作等
"""

import re
from PyQt6.QtWidgets import (
    QTextEdit, QMenu, QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSpinBox, QColorDialog, QFontDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog, QComboBox, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QUrl
from PyQt6.QtGui import (
    QTextCursor, QTextCharFormat, QTextBlockFormat, QTextListFormat,
    QFont, QColor, QPixmap, QTextImageFormat, QTextTableFormat,
    QTextFrameFormat, QAction, QContextMenuEvent, QDragEnterEvent,
    QDropEvent
)

class TableEditDialog(QDialog):
    """表格编辑对话框"""
    
    def __init__(self, rows=3, cols=3, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插入/编辑表格")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 表格尺寸设置
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("行数:"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 20)
        self.rows_spin.setValue(rows)
        size_layout.addWidget(self.rows_spin)
        
        size_layout.addWidget(QLabel("列数:"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 20)
        self.cols_spin.setValue(cols)
        size_layout.addWidget(self.cols_spin)
        
        layout.addLayout(size_layout)
        
        # 表格预览
        self.table_widget = QTableWidget()
        self.update_table_preview()
        layout.addWidget(self.table_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # 连接信号
        self.rows_spin.valueChanged.connect(self.update_table_preview)
        self.cols_spin.valueChanged.connect(self.update_table_preview)
        
    def update_table_preview(self):
        """更新表格预览"""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        
        self.table_widget.setRowCount(rows)
        self.table_widget.setColumnCount(cols)
        
        for i in range(rows):
            for j in range(cols):
                self.table_widget.setItem(i, j, QTableWidgetItem(f"单元格{i+1}-{j+1}"))
                
    def get_table_data(self):
        """获取表格数据"""
        rows = self.table_widget.rowCount()
        cols = self.table_widget.columnCount()
        data = []
        
        for i in range(rows):
            row_data = []
            for j in range(cols):
                item = self.table_widget.item(i, j)
                row_data.append(item.text() if item else "")
            data.append(row_data)
            
        return data

class ImageResizeDialog(QDialog):
    """图片尺寸调整对话框"""
    
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("调整图片尺寸")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 尺寸设置
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("宽度:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 2000)
        self.width_spin.setValue(width)
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("高度:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 2000)
        self.height_spin.setValue(height)
        size_layout.addWidget(self.height_spin)
        
        layout.addLayout(size_layout)
        
        # 保持比例
        self.keep_ratio = QCheckBox("保持宽高比")
        self.keep_ratio.setChecked(True)
        layout.addWidget(self.keep_ratio)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.original_ratio = width / height if height > 0 else 1
        
        # 连接信号
        self.width_spin.valueChanged.connect(self.on_width_changed)
        self.height_spin.valueChanged.connect(self.on_height_changed)
        
    def on_width_changed(self):
        """宽度改变时自动调整高度"""
        if self.keep_ratio.isChecked():
            new_height = int(self.width_spin.value() / self.original_ratio)
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(new_height)
            self.height_spin.blockSignals(False)
            
    def on_height_changed(self):
        """高度改变时自动调整宽度"""
        if self.keep_ratio.isChecked():
            new_width = int(self.height_spin.value() * self.original_ratio)
            self.width_spin.blockSignals(True)
            self.width_spin.setValue(new_width)
            self.width_spin.blockSignals(False)
            
    def get_size(self):
        """获取新尺寸"""
        return self.width_spin.value(), self.height_spin.value()

class AITextEditor(QTextEdit):
    """AI增强文本编辑器"""
    
    # 信号定义
    format_applied = pyqtSignal(str, object)  # 格式类型, 格式值
    image_inserted = pyqtSignal(str)  # 图片路径
    table_inserted = pyqtSignal(int, int)  # 行数, 列数
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_editor()
        self.setup_drag_drop()
        
    def setup_editor(self):
        """设置编辑器基本属性"""
        # 设置字体
        font = QFont("Microsoft YaHei", 12)
        self.setFont(font)
        
        # 设置基本样式
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                selection-background-color: #3399ff;
            }
        """)
        
        # 允许富文本
        self.setAcceptRichText(True)
        
        # 启用拼写检查（如果需要）
        self.setAcceptDrops(True)
        
    def setup_drag_drop(self):
        """设置拖拽功能"""
        self.setAcceptDrops(True)
        
    def contextMenuEvent(self, event: QContextMenuEvent):
        """右键菜单事件"""
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        
        # 获取选中文本
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            # AI辅助功能菜单
            ai_menu = menu.addMenu("AI辅助")
            
            polish_action = ai_menu.addAction("润色文本")
            polish_action.triggered.connect(lambda: self.request_ai_processing("polish", selected_text))
            
            expand_action = ai_menu.addAction("扩写文本")
            expand_action.triggered.connect(lambda: self.request_ai_processing("expand", selected_text))
            
            summarize_action = ai_menu.addAction("总结文本")
            summarize_action.triggered.connect(lambda: self.request_ai_processing("summarize", selected_text))
            
            translate_action = ai_menu.addAction("翻译文本")
            translate_action.triggered.connect(lambda: self.request_ai_processing("translate", selected_text))
            
            question_action = ai_menu.addAction("提问")
            question_action.triggered.connect(lambda: self.request_ai_processing("question", selected_text))
            
            menu.addSeparator()
            
        # 格式化菜单
        format_menu = menu.addMenu("格式")
        
        bold_action = format_menu.addAction("加粗")
        bold_action.triggered.connect(self.toggle_bold)
        
        italic_action = format_menu.addAction("斜体")
        italic_action.triggered.connect(self.toggle_italic)
        
        underline_action = format_menu.addAction("下划线")
        underline_action.triggered.connect(self.toggle_underline)
        
        format_menu.addSeparator()
        
        font_action = format_menu.addAction("字体...")
        font_action.triggered.connect(self.change_font)
        
        color_action = format_menu.addAction("文字颜色...")
        color_action.triggered.connect(self.change_text_color)
        
        # 插入菜单
        insert_menu = menu.addMenu("插入")
        
        image_action = insert_menu.addAction("插入图片...")
        image_action.triggered.connect(self.insert_image)
        
        table_action = insert_menu.addAction("插入表格...")
        table_action.triggered.connect(self.insert_table)
        
        # 检查光标位置的元素
        current_format = cursor.charFormat()
        if current_format.isImageFormat():
            menu.addSeparator()
            resize_image_action = menu.addAction("调整图片尺寸...")
            resize_image_action.triggered.connect(self.resize_current_image)
        
        menu.exec(event.globalPos())
        
    def request_ai_processing(self, operation, text):
        """请求AI处理文本"""
        # 这里会触发信号，由主窗口的LLM助手处理
        if hasattr(self.parent(), 'llm_assistant'):
            llm_assistant = self.parent().llm_assistant
            if operation == "polish":
                llm_assistant.polish_text(text)
            elif operation == "expand":
                llm_assistant.expand_text(text)
            elif operation == "summarize":
                llm_assistant.summarize_text(text)
            elif operation == "translate":
                llm_assistant.translate_text(text)
            elif operation == "question":
                llm_assistant.ask_question(text)
                
    def apply_format(self, format_type, value):
        """应用格式"""
        cursor = self.textCursor()
        
        if format_type == "bold":
            self.toggle_bold()
        elif format_type == "italic":
            self.toggle_italic()
        elif format_type == "underline":
            self.toggle_underline()
        elif format_type == "font_family":
            self.set_font_family(value)
        elif format_type == "font_size":
            self.set_font_size(value)
        elif format_type == "text_color":
            self.set_text_color(value)
        elif format_type == "align_left":
            self.set_alignment(Qt.AlignmentFlag.AlignLeft)
        elif format_type == "align_center":
            self.set_alignment(Qt.AlignmentFlag.AlignCenter)
        elif format_type == "align_right":
            self.set_alignment(Qt.AlignmentFlag.AlignRight)
        elif format_type == "list_bullet":
            self.toggle_list(QTextListFormat.Style.ListDisc)
        elif format_type == "list_number":
            self.toggle_list(QTextListFormat.Style.ListDecimal)
            
    def toggle_bold(self):
        """切换加粗"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setBold(not font.bold())
        format.setFont(font)
        cursor.setCharFormat(format)
        self.setTextCursor(cursor)
        
    def toggle_italic(self):
        """切换斜体"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setItalic(not font.italic())
        format.setFont(font)
        cursor.setCharFormat(format)
        self.setTextCursor(cursor)
        
    def toggle_underline(self):
        """切换下划线"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setUnderline(not font.underline())
        format.setFont(font)
        cursor.setCharFormat(format)
        self.setTextCursor(cursor)
        
    def set_font_family(self, family):
        """设置字体族"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setFamily(family)
        format.setFont(font)
        cursor.setCharFormat(format)
        self.setTextCursor(cursor)
        
    def set_font_size(self, size):
        """设置字体大小"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        font = format.font()
        font.setPointSize(size)
        format.setFont(font)
        cursor.setCharFormat(format)
        self.setTextCursor(cursor)
        
    def set_text_color(self, color):
        """设置文字颜色"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        format.setForeground(color)
        cursor.setCharFormat(format)
        self.setTextCursor(cursor)
        
    def set_alignment(self, alignment):
        """设置对齐方式"""
        cursor = self.textCursor()
        block_format = cursor.blockFormat()
        block_format.setAlignment(alignment)
        cursor.setBlockFormat(block_format)
        self.setTextCursor(cursor)
        
    def toggle_list(self, list_style):
        """切换列表"""
        cursor = self.textCursor()
        
        # 检查当前是否在列表中
        current_list = cursor.currentList()
        if current_list:
            # 如果已经在列表中，移除列表格式
            list_format = current_list.format()
            if list_format.style() == list_style:
                # 相同样式，移除列表
                block_format = cursor.blockFormat()
                block_format.setIndent(0)
                cursor.setBlockFormat(block_format)
                return
        
        # 创建新列表格式
        list_format = QTextListFormat()
        list_format.setStyle(list_style)
        list_format.setIndent(1)
        cursor.createList(list_format)
        
    def change_font(self):
        """改变字体"""
        cursor = self.textCursor()
        current_format = cursor.charFormat()
        current_font = current_format.font()
        
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            format = QTextCharFormat()
            format.setFont(font)
            cursor.setCharFormat(format)
            self.setTextCursor(cursor)
            
    def change_text_color(self):
        """改变文字颜色"""
        color = QColorDialog.getColor(Qt.GlobalColor.black, self)
        if color.isValid():
            self.set_text_color(color)
            
    def insert_image(self):
        """插入图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp);;所有文件 (*)"
        )
        
        if file_path:
            # 加载图片
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 限制图片大小
                max_width = 600
                if pixmap.width() > max_width:
                    pixmap = pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
                
                # 创建图片格式
                image_format = QTextImageFormat()
                image_format.setName(file_path)
                image_format.setWidth(pixmap.width())
                image_format.setHeight(pixmap.height())
                
                # 插入图片
                cursor = self.textCursor()
                cursor.insertImage(image_format)
                
                self.image_inserted.emit(file_path)
            else:
                QMessageBox.warning(self, "错误", "无法加载图片文件")
                
    def resize_current_image(self):
        """调整当前图片尺寸"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        
        if format.isImageFormat():
            image_format = format.toImageFormat()
            current_width = int(image_format.width())
            current_height = int(image_format.height())
            
            dialog = ImageResizeDialog(current_width, current_height, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_width, new_height = dialog.get_size()
                image_format.setWidth(new_width)
                image_format.setHeight(new_height)
                cursor.setCharFormat(image_format)
                self.setTextCursor(cursor)
                
    def insert_table(self):
        """插入表格"""
        dialog = TableEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            table_data = dialog.get_table_data()
            rows = len(table_data)
            cols = len(table_data[0]) if table_data else 0
            
            if rows > 0 and cols > 0:
                cursor = self.textCursor()
                
                # 创建表格格式
                table_format = QTextTableFormat()
                table_format.setBorder(1)
                table_format.setBorderBrush(QColor(Qt.GlobalColor.black))
                table_format.setCellPadding(4)
                table_format.setCellSpacing(0)
                
                # 插入表格
                table = cursor.insertTable(rows, cols, table_format)
                
                # 填充表格数据
                for i in range(rows):
                    for j in range(cols):
                        cell = table.cellAt(i, j)
                        cell_cursor = cell.firstCursorPosition()
                        cell_cursor.insertText(table_data[i][j])
                        
                self.table_inserted.emit(rows, cols)
                
    def goto_section(self, section_name):
        """跳转到指定章节"""
        # 搜索章节标题
        document = self.document()
        cursor = document.find(section_name)
        if not cursor.isNull():
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
            
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
            
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    # 插入图片
                    pixmap = QPixmap(file_path)
                    if not pixmap.isNull():
                        # 限制图片大小
                        max_width = 600
                        if pixmap.width() > max_width:
                            pixmap = pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
                        
                        # 创建图片格式
                        image_format = QTextImageFormat()
                        image_format.setName(file_path)
                        image_format.setWidth(pixmap.width())
                        image_format.setHeight(pixmap.height())
                        
                        # 在拖拽位置插入图片
                        cursor = self.cursorForPosition(event.position().toPoint())
                        self.setTextCursor(cursor)
                        cursor.insertImage(image_format)
                        
                        self.image_inserted.emit(file_path)
                        event.acceptProposedAction()
                        return
        
        super().dropEvent(event)
        
    def get_current_format_state(self):
        """获取当前格式状态"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        block_format = cursor.blockFormat()
        
        return {
            'bold': format.font().bold(),
            'italic': format.font().italic(),
            'underline': format.font().underline(),
            'font_family': format.font().family(),
            'font_size': format.font().pointSize(),
            'text_color': format.foreground().color(),
            'alignment': block_format.alignment(),
            'in_list': cursor.currentList() is not None
        }