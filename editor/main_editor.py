"""
AI Enhanced Rich Text Editor - Main Editor Window
主编辑器窗口，集成文本编辑、LLM辅助、图片处理等功能
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QToolBar, QMenuBar, QStatusBar, QDockWidget,
    QApplication, QMessageBox, QFileDialog, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextDocument, QIcon, QPixmap

from .text_editor import AITextEditor
from .llm_assistant import LLMAssistant
from .sidebar import EditorSidebar
from .toolbar import EditorToolbar
from .export_manager import ExportManager
from .outline_view import OutlineView
from .version_manager import VersionManager
from .document_generator import DocumentGeneratorDialog
from .smart_layout import SmartLayoutDialog
from .template_manager import TemplateDialog

class AIRichTextEditor(QMainWindow):
    """AI增强富文本编辑器主窗口"""
    
    # 信号定义
    document_changed = pyqtSignal()
    selection_changed = pyqtSignal(str)  # 选中文本内容
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.setup_autosave()
        
        # 组件实例
        self.current_file = None
        self.is_modified = False
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("AI增强富文本编辑器 - autoMate")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置窗口图标
        try:
            icon_path = Path(__file__).parent.parent / "imgs" / "logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 水平分割器
        main_layout = QHBoxLayout(central_widget)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：大纲视图 (可停靠)
        self.outline_dock = QDockWidget("文档大纲", self)
        self.outline_view = OutlineView()
        self.outline_dock.setWidget(self.outline_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.outline_dock)
        
        # 中央：编辑区域
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # 工具栏
        self.toolbar = EditorToolbar(self)
        editor_layout.addWidget(self.toolbar)
        
        # 文本编辑器
        self.text_editor = AITextEditor(self)
        editor_layout.addWidget(self.text_editor)
        
        # 右侧：LLM助手侧边栏 (可停靠)
        self.llm_dock = QDockWidget("AI助手", self)
        self.llm_assistant = LLMAssistant(self)
        self.llm_dock.setWidget(self.llm_assistant)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.llm_dock)
        
        # 设置分割器
        main_splitter.addWidget(editor_widget)
        main_layout.addWidget(main_splitter)
        
        # 设置停靠窗口的初始大小
        self.resizeDocks([self.outline_dock, self.llm_dock], [250, 350], Qt.Orientation.Horizontal)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 导出管理器
        self.export_manager = ExportManager(self)
        
        # 版本管理器
        self.version_manager = VersionManager(self)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建
        new_action = file_menu.addAction('新建')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_document)
        
        # 打开
        open_action = file_menu.addAction('打开')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_document)
        
        # 保存
        save_action = file_menu.addAction('保存')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_document)
        
        # 另存为
        save_as_action = file_menu.addAction('另存为')
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as_document)
        
        file_menu.addSeparator()
        
        # 导出子菜单
        export_menu = file_menu.addMenu('导出')
        
        export_word_action = export_menu.addAction('导出为Word (.docx)')
        export_word_action.triggered.connect(lambda: self.export_document('docx'))
        
        export_pdf_action = export_menu.addAction('导出为PDF (.pdf)')
        export_pdf_action.triggered.connect(lambda: self.export_document('pdf'))
        
        export_md_action = export_menu.addAction('导出为Markdown (.md)')
        export_md_action.triggered.connect(lambda: self.export_document('md'))
        
        export_html_action = export_menu.addAction('导出为HTML (.html)')
        export_html_action.triggered.connect(lambda: self.export_document('html'))
        
        export_txt_action = export_menu.addAction('导出为纯文本 (.txt)')
        export_txt_action.triggered.connect(lambda: self.export_document('txt'))
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = file_menu.addAction('退出')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        
        undo_action = edit_menu.addAction('撤销')
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.text_editor.undo)
        
        redo_action = edit_menu.addAction('重做')
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.text_editor.redo)
        
        edit_menu.addSeparator()
        
        cut_action = edit_menu.addAction('剪切')
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.text_editor.cut)
        
        copy_action = edit_menu.addAction('复制')
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.text_editor.copy)
        
        paste_action = edit_menu.addAction('粘贴')
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.text_editor.paste)
        
        # AI菜单
        ai_menu = menubar.addMenu('AI助手(&A)')
        
        polish_action = ai_menu.addAction('润色选中文本')
        polish_action.triggered.connect(self.polish_selected_text)
        
        expand_action = ai_menu.addAction('扩写选中文本')
        expand_action.triggered.connect(self.expand_selected_text)
        
        summarize_action = ai_menu.addAction('总结选中文本')
        summarize_action.triggered.connect(self.summarize_selected_text)
        
        translate_action = ai_menu.addAction('翻译选中文本')
        translate_action.triggered.connect(self.translate_selected_text)
        
        ai_menu.addSeparator()
        
        full_summary_action = ai_menu.addAction('生成全文摘要')
        full_summary_action.triggered.connect(self.generate_full_summary)
        
        style_check_action = ai_menu.addAction('风格统一检查')
        style_check_action.triggered.connect(self.check_style_consistency)
        
        ai_menu.addSeparator()
        
        # 智能文档生成
        doc_gen_action = ai_menu.addAction('智能文档生成器')
        doc_gen_action.triggered.connect(self.open_document_generator)
        
        # 智能排版设计
        smart_layout_action = ai_menu.addAction('智能排版设计')
        smart_layout_action.triggered.connect(self.open_smart_layout)
        
        # 文档模板库
        template_action = ai_menu.addAction('文档模板库')
        template_action.triggered.connect(self.open_template_library)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        toggle_outline_action = view_menu.addAction('显示/隐藏大纲')
        toggle_outline_action.triggered.connect(self.toggle_outline_view)
        
        toggle_ai_action = view_menu.addAction('显示/隐藏AI助手')
        toggle_ai_action.triggered.connect(self.toggle_ai_assistant)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = help_menu.addAction('关于')
        about_action.triggered.connect(self.show_about)
        
    def setup_connections(self):
        """设置信号连接"""
        # 文本编辑器信号
        self.text_editor.textChanged.connect(self.on_document_changed)
        self.text_editor.selectionChanged.connect(self.on_selection_changed)
        
        # LLM助手信号
        self.llm_assistant.text_processed.connect(self.on_llm_text_processed)
        
        # 大纲视图信号
        self.outline_view.section_clicked.connect(self.text_editor.goto_section)
        
        # 工具栏信号
        self.toolbar.format_applied.connect(self.text_editor.apply_format)
        
    def setup_autosave(self):
        """设置自动保存"""
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30000)  # 每30秒自动保存
        
    def on_document_changed(self):
        """文档内容改变时的处理"""
        self.is_modified = True
        self.update_window_title()
        self.document_changed.emit()
        
        # 更新大纲视图
        self.outline_view.update_outline(self.text_editor.document())
        
        # 保存版本历史
        self.version_manager.save_version(self.text_editor.toHtml())
        
    def on_selection_changed(self):
        """选中文本改变时的处理"""
        cursor = self.text_editor.textCursor()
        selected_text = cursor.selectedText()
        self.selection_changed.emit(selected_text)
        
        # 更新工具栏状态
        self.toolbar.update_format_state(cursor)
        
    def on_llm_text_processed(self, processed_text, operation_type):
        """LLM处理文本完成后的回调"""
        if operation_type == "replace":
            cursor = self.text_editor.textCursor()
            cursor.insertText(processed_text)
        elif operation_type == "insert":
            self.text_editor.append(processed_text)
        
        self.status_bar.showMessage(f"AI操作完成: {operation_type}")
        
    def new_document(self):
        """新建文档"""
        if self.check_save_changes():
            self.text_editor.clear()
            self.current_file = None
            self.is_modified = False
            self.update_window_title()
            self.version_manager.clear_history()
            
    def open_document(self):
        """打开文档"""
        if not self.check_save_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文档", "",
            "富文本文档 (*.html);;Word文档 (*.docx);;Markdown (*.md);;所有文件 (*)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.docx'):
                    content = self.export_manager.import_docx(file_path)
                elif file_path.endswith('.md'):
                    content = self.export_manager.import_markdown(file_path)
                else:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                
                self.text_editor.setHtml(content)
                self.current_file = file_path
                self.is_modified = False
                self.update_window_title()
                self.version_manager.clear_history()
                self.status_bar.showMessage(f"已打开: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件:\n{str(e)}")
                
    def save_document(self):
        """保存文档"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_document()
            
    def save_as_document(self):
        """另存为文档"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文档", "",
            "富文本文档 (*.html);;所有文件 (*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.update_window_title()
            
    def save_to_file(self, file_path):
        """保存到指定文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_editor.toHtml())
            
            self.is_modified = False
            self.update_window_title()
            self.status_bar.showMessage(f"已保存: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存文件:\n{str(e)}")
            
    def autosave(self):
        """自动保存"""
        if self.is_modified and self.current_file:
            self.save_to_file(self.current_file)
            
    def export_document(self, format_type):
        """导出文档"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"导出为{format_type.upper()}", "",
            f"{format_type.upper()}文件 (*.{format_type})"
        )
        
        if file_path:
            try:
                success = self.export_manager.export_document(
                    self.text_editor.document(), file_path, format_type
                )
                if success:
                    self.status_bar.showMessage(f"已导出: {file_path}")
                    QMessageBox.information(self, "成功", f"文档已成功导出为 {format_type.upper()} 格式")
                else:
                    QMessageBox.warning(self, "警告", "导出过程中遇到问题，请检查文件")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")
                
    def check_save_changes(self):
        """检查是否需要保存更改"""
        if not self.is_modified:
            return True
            
        reply = QMessageBox.question(
            self, "保存更改",
            "文档已修改，是否保存更改？",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            self.save_document()
            return not self.is_modified
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
            
    def update_window_title(self):
        """更新窗口标题"""
        title = "AI增强富文本编辑器"
        if self.current_file:
            title += f" - {Path(self.current_file).name}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
        
    # AI辅助功能
    def polish_selected_text(self):
        """润色选中文本"""
        selected_text = self.text_editor.textCursor().selectedText()
        if selected_text:
            self.llm_assistant.polish_text(selected_text)
        else:
            QMessageBox.information(self, "提示", "请先选择要润色的文本")
            
    def expand_selected_text(self):
        """扩写选中文本"""
        selected_text = self.text_editor.textCursor().selectedText()
        if selected_text:
            self.llm_assistant.expand_text(selected_text)
        else:
            QMessageBox.information(self, "提示", "请先选择要扩写的文本")
            
    def summarize_selected_text(self):
        """总结选中文本"""
        selected_text = self.text_editor.textCursor().selectedText()
        if selected_text:
            self.llm_assistant.summarize_text(selected_text)
        else:
            QMessageBox.information(self, "提示", "请先选择要总结的文本")
            
    def translate_selected_text(self):
        """翻译选中文本"""
        selected_text = self.text_editor.textCursor().selectedText()
        if selected_text:
            self.llm_assistant.translate_text(selected_text)
        else:
            QMessageBox.information(self, "提示", "请先选择要翻译的文本")
            
    def generate_full_summary(self):
        """生成全文摘要"""
        full_text = self.text_editor.toPlainText()
        if full_text.strip():
            self.llm_assistant.generate_summary(full_text)
        else:
            QMessageBox.information(self, "提示", "文档为空，无法生成摘要")
            
    def check_style_consistency(self):
        """检查风格一致性"""
        full_text = self.text_editor.toPlainText()
        if full_text.strip():
            self.llm_assistant.check_style(full_text)
        else:
            QMessageBox.information(self, "提示", "文档为空，无法检查风格")
            
    def open_document_generator(self):
        """打开AI文档生成器"""
        dialog = DocumentGeneratorDialog(self)
        dialog.document_generated.connect(self.on_document_generated)
        dialog.exec()
        
    def on_document_generated(self, document_content):
        """文档生成完成后的处理"""
        # 检查是否需要保存当前文档
        if self.check_save_changes():
            self.text_editor.setPlainText(document_content)
            self.current_file = None
            self.is_modified = True
            self.update_window_title()
            self.status_bar.showMessage("AI文档生成完成")
            
    def open_smart_layout(self):
        """打开智能排版设计器"""
        current_text = self.text_editor.toPlainText()
        if not current_text.strip():
            QMessageBox.information(self, "提示", "请先输入一些文本内容再使用智能排版功能")
            return
            
        dialog = SmartLayoutDialog(current_text, self)
        dialog.layout_applied.connect(self.on_layout_applied)
        dialog.exec()
        
    def on_layout_applied(self, formatted_text, style_info):
        """智能排版应用完成后的处理"""
        # 应用格式化文本
        self.text_editor.setPlainText(formatted_text)
        
        # 应用样式设置
        layout_options = style_info.get('layout_options', {})
        
        # 设置字体
        if 'font_family' in layout_options and 'font_size' in layout_options:
            font = QFont(layout_options['font_family'], layout_options['font_size'])
            self.text_editor.setFont(font)
            
                 self.is_modified = True
         self.update_window_title()
         self.status_bar.showMessage("智能排版已应用")
         
    def open_template_library(self):
        """打开文档模板库"""
        dialog = TemplateDialog(self)
        dialog.template_selected.connect(self.on_template_selected)
        dialog.exec()
        
    def on_template_selected(self, template_content):
        """模板选择完成后的处理"""
        # 检查是否需要保存当前文档
        if self.check_save_changes():
            self.text_editor.setPlainText(template_content)
            self.current_file = None
            self.is_modified = True
            self.update_window_title()
            self.status_bar.showMessage("模板已应用")
            
    # 视图控制
    def toggle_outline_view(self):
        """切换大纲视图显示"""
        if self.outline_dock.isVisible():
            self.outline_dock.hide()
        else:
            self.outline_dock.show()
            
    def toggle_ai_assistant(self):
        """切换AI助手显示"""
        if self.llm_dock.isVisible():
            self.llm_dock.hide()
        else:
            self.llm_dock.show()
            
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "AI增强富文本编辑器\n\n"
            "基于autoMate项目构建的智能文本编辑器\n"
            "集成LLM辅助编辑功能\n\n"
            "版本: 1.0.0"
        )
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()


def main():
    """主函数 - 用于测试"""
    app = QApplication(sys.argv)
    editor = AIRichTextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()