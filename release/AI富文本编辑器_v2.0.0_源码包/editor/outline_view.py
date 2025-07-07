"""
Outline View Component
大纲视图组件，显示和管理文档结构
"""

import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QHeaderView, QMenu, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class OutlineView(QWidget):
    """文档大纲视图"""
    
    section_clicked = pyqtSignal(str)  # 章节被点击
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_document = None
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建树形控件
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("文档大纲")
        self.tree_widget.setRootIsDecorated(True)
        self.tree_widget.setAlternatingRowColors(True)
        
        # 设置列宽自适应
        header = self.tree_widget.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # 连接信号
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.tree_widget)
        
        # 设置样式
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #3399ff;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:hover {
                background-color: #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #3399ff;
                color: white;
            }
        """)
        
    def update_outline(self, document):
        """更新大纲"""
        self.current_document = document
        self.tree_widget.clear()
        
        if not document:
            return
            
        # 提取文档中的标题
        plain_text = document.toPlainText()
        headings = self.extract_headings(plain_text)
        
        if not headings:
            # 如果没有标题，按段落显示
            self.create_paragraph_outline(plain_text)
        else:
            # 创建层级结构
            self.create_heading_outline(headings)
            
    def extract_headings(self, text):
        """提取标题"""
        headings = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 检测Markdown样式标题
            md_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if md_match:
                level = len(md_match.group(1))
                title = md_match.group(2)
                headings.append({
                    'level': level,
                    'title': title,
                    'line': i + 1,
                    'text': line
                })
                continue
                
            # 检测数字编号标题
            num_match = re.match(r'^(\d+\.)+\s*(.+)', line)
            if num_match:
                dots = num_match.group(1).count('.')
                title = num_match.group(2)
                headings.append({
                    'level': dots,
                    'title': title,
                    'line': i + 1,
                    'text': line
                })
                continue
                
            # 检测较短且可能是标题的行
            if len(line) < 50 and not line.endswith(('。', '.', '!', '?', '；', ';')):
                # 检查是否包含常见标题关键词
                title_keywords = ['第', '章', '节', '部分', '概述', '介绍', '总结', '结论']
                if any(keyword in line for keyword in title_keywords):
                    headings.append({
                        'level': 1,
                        'title': line,
                        'line': i + 1,
                        'text': line
                    })
                    
        return headings
        
    def create_heading_outline(self, headings):
        """创建标题大纲"""
        stack = []  # 用于维护层级关系
        
        for heading in headings:
            level = heading['level']
            title = heading['title']
            
            # 创建树项
            item = QTreeWidgetItem()
            item.setText(0, title)
            item.setData(0, Qt.ItemDataRole.UserRole, heading)
            
            # 设置图标和字体
            if level == 1:
                item.setIcon(0, self.get_icon("📚"))
                font = QFont()
                font.setBold(True)
                item.setFont(0, font)
            elif level == 2:
                item.setIcon(0, self.get_icon("📖"))
            elif level == 3:
                item.setIcon(0, self.get_icon("📝"))
            else:
                item.setIcon(0, self.get_icon("•"))
                
            # 找到合适的父项
            while stack and stack[-1]['level'] >= level:
                stack.pop()
                
            if stack:
                parent_item = stack[-1]['item']
                parent_item.addChild(item)
            else:
                self.tree_widget.addTopLevelItem(item)
                
            # 添加到栈中
            stack.append({
                'level': level,
                'item': item,
                'heading': heading
            })
            
        # 展开所有项
        self.tree_widget.expandAll()
        
    def create_paragraph_outline(self, text):
        """创建段落大纲"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs):
            # 限制显示长度
            display_text = paragraph[:50] + "..." if len(paragraph) > 50 else paragraph
            
            item = QTreeWidgetItem()
            item.setText(0, f"段落 {i+1}: {display_text}")
            item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'paragraph',
                'text': paragraph,
                'index': i
            })
            item.setIcon(0, self.get_icon("¶"))
            
            self.tree_widget.addTopLevelItem(item)
            
    def get_icon(self, emoji):
        """获取图标"""
        # 简单的文本图标，实际项目中可以使用真实图标
        return QIcon()
        
    def on_item_clicked(self, item):
        """处理项点击"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            if 'text' in data:
                # 发送信号跳转到对应位置
                self.section_clicked.emit(data['text'])
                
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tree_widget.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # 跳转到章节
        goto_action = menu.addAction("跳转到此处")
        goto_action.triggered.connect(lambda: self.on_item_clicked(item))
        
        menu.addSeparator()
        
        # 编辑标题
        edit_action = menu.addAction("编辑标题")
        edit_action.triggered.connect(lambda: self.edit_heading(item))
        
        # 删除章节
        delete_action = menu.addAction("删除章节")
        delete_action.triggered.connect(lambda: self.delete_heading(item))
        
        menu.addSeparator()
        
        # 添加子章节
        add_child_action = menu.addAction("添加子章节")
        add_child_action.triggered.connect(lambda: self.add_child_heading(item))
        
        # 在此位置显示菜单
        menu.exec(self.tree_widget.mapToGlobal(position))
        
    def edit_heading(self, item):
        """编辑标题"""
        current_text = item.text(0)
        new_text, ok = QInputDialog.getText(
            self, "编辑标题", "标题:", text=current_text
        )
        
        if ok and new_text.strip():
            item.setText(0, new_text.strip())
            # 这里应该更新原文档，暂时只更新显示
            
    def delete_heading(self, item):
        """删除章节"""
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除章节 '{item.text(0)}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 获取父项
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.tree_widget.indexOfTopLevelItem(item)
                self.tree_widget.takeTopLevelItem(index)
                
    def add_child_heading(self, parent_item):
        """添加子章节"""
        heading_text, ok = QInputDialog.getText(
            self, "添加子章节", "子章节标题:"
        )
        
        if ok and heading_text.strip():
            child_item = QTreeWidgetItem()
            child_item.setText(0, heading_text.strip())
            child_item.setIcon(0, self.get_icon("📝"))
            parent_item.addChild(child_item)
            parent_item.setExpanded(True)
            
    def get_current_structure(self):
        """获取当前大纲结构"""
        structure = []
        
        def traverse_item(item, level=0):
            data = {
                'title': item.text(0),
                'level': level,
                'children': []
            }
            
            for i in range(item.childCount()):
                child = item.child(i)
                data['children'].append(traverse_item(child, level + 1))
                
            return data
            
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            structure.append(traverse_item(item))
            
        return structure