"""
Version Manager Module
版本管理器模块，管理文档的版本历史和恢复功能
"""

import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QTextEdit, QDialog, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class VersionViewDialog(QDialog):
    """版本查看对话框"""
    
    def __init__(self, version_data, parent=None):
        super().__init__(parent)
        self.version_data = version_data
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("版本详情")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 版本信息
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"版本: {self.version_data['id']}"))
        info_layout.addWidget(QLabel(f"时间: {self.version_data['timestamp']}"))
        info_layout.addWidget(QLabel(f"大小: {len(self.version_data['content'])} 字符"))
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # 内容预览
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        self.content_view.setHtml(self.version_data['content'])
        layout.addWidget(self.content_view)
        
        # 按钮
        button_layout = QHBoxLayout()
        restore_btn = QPushButton("恢复到此版本")
        restore_btn.clicked.connect(self.accept)
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(restore_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

class VersionManager:
    """版本管理器"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.db_path = Path.home() / ".automate_editor" / "versions.db"
        self.max_versions = 50  # 最大保存版本数
        self.setup_database()
        
    def setup_database(self):
        """设置数据库"""
        # 确保目录存在
        self.db_path.parent.mkdir(exist_ok=True)
        
        # 创建数据库表
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_hash TEXT,
                content TEXT,
                content_hash TEXT,
                timestamp TEXT,
                file_path TEXT,
                comment TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_version(self, content, file_path=None, comment=None):
        """保存版本"""
        if not content or not content.strip():
            return None
            
        # 计算内容哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # 检查是否与最新版本相同
        if self.is_duplicate_version(content_hash):
            return None
            
        # 文档哈希（基于文件路径或内容）
        doc_hash = hashlib.md5((file_path or content[:100]).encode()).hexdigest()
        
        # 保存到数据库
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO versions (document_hash, content, content_hash, timestamp, file_path, comment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            doc_hash,
            content,
            content_hash,
            datetime.now().isoformat(),
            file_path or "",
            comment or ""
        ))
        
        version_id = cursor.lastrowid
        conn.commit()
        
        # 清理旧版本
        self.cleanup_old_versions(doc_hash)
        
        conn.close()
        return version_id
        
    def is_duplicate_version(self, content_hash):
        """检查是否为重复版本"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM versions 
            WHERE content_hash = ?
            ORDER BY id DESC LIMIT 1
        ''', (content_hash,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
        
    def cleanup_old_versions(self, document_hash):
        """清理旧版本"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 获取版本数量
        cursor.execute('''
            SELECT COUNT(*) FROM versions WHERE document_hash = ?
        ''', (document_hash,))
        
        count = cursor.fetchone()[0]
        
        if count > self.max_versions:
            # 删除最旧的版本
            cursor.execute('''
                DELETE FROM versions WHERE document_hash = ? AND id NOT IN (
                    SELECT id FROM versions WHERE document_hash = ?
                    ORDER BY id DESC LIMIT ?
                )
            ''', (document_hash, document_hash, self.max_versions))
            
        conn.commit()
        conn.close()
        
    def get_versions(self, file_path=None):
        """获取版本列表"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if file_path:
            doc_hash = hashlib.md5(file_path.encode()).hexdigest()
            cursor.execute('''
                SELECT id, timestamp, content, comment FROM versions 
                WHERE document_hash = ?
                ORDER BY id DESC
            ''', (doc_hash,))
        else:
            cursor.execute('''
                SELECT id, timestamp, content, comment FROM versions 
                ORDER BY id DESC LIMIT 20
            ''')
            
        versions = []
        for row in cursor.fetchall():
            versions.append({
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'comment': row[3] or ""
            })
            
        conn.close()
        return versions
        
    def get_version(self, version_id):
        """获取特定版本"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, content, comment FROM versions 
            WHERE id = ?
        ''', (version_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'comment': row[3] or ""
            }
        return None
        
    def delete_version(self, version_id):
        """删除版本"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM versions WHERE id = ?', (version_id,))
        
        conn.commit()
        conn.close()
        
    def clear_history(self):
        """清除所有历史版本"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM versions')
        
        conn.commit()
        conn.close()
        
    def show_version_dialog(self, file_path=None):
        """显示版本管理对话框"""
        dialog = VersionHistoryDialog(self, file_path, self.parent)
        return dialog.exec()

class VersionHistoryDialog(QDialog):
    """版本历史对话框"""
    
    version_restored = pyqtSignal(str)  # 版本内容
    
    def __init__(self, version_manager, file_path=None, parent=None):
        super().__init__(parent)
        self.version_manager = version_manager
        self.file_path = file_path
        self.setup_ui()
        self.load_versions()
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("版本历史")
        self.setModal(True)
        self.resize(900, 600)
        
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：版本列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("版本历史"))
        
        self.version_list = QListWidget()
        self.version_list.itemClicked.connect(self.on_version_selected)
        left_layout.addWidget(self.version_list)
        
        # 版本操作按钮
        version_btn_layout = QHBoxLayout()
        
        self.restore_btn = QPushButton("恢复")
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self.restore_version)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_version)
        
        self.view_btn = QPushButton("查看")
        self.view_btn.setEnabled(False)
        self.view_btn.clicked.connect(self.view_version)
        
        version_btn_layout.addWidget(self.restore_btn)
        version_btn_layout.addWidget(self.delete_btn)
        version_btn_layout.addWidget(self.view_btn)
        version_btn_layout.addStretch()
        
        left_layout.addLayout(version_btn_layout)
        
        # 右侧：版本预览
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("版本预览"))
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        right_layout.addWidget(self.preview_text)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 600])
        
        layout.addWidget(splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("清除所有历史")
        clear_btn.clicked.connect(self.clear_all_history)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def load_versions(self):
        """加载版本列表"""
        versions = self.version_manager.get_versions(self.file_path)
        
        self.version_list.clear()
        for version in versions:
            timestamp = datetime.fromisoformat(version['timestamp'])
            display_text = f"版本 {version['id']} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            if version['comment']:
                display_text += f" ({version['comment']})"
                
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, version)
            self.version_list.addItem(item)
            
    def on_version_selected(self, item):
        """版本选择处理"""
        version_data = item.data(Qt.ItemDataRole.UserRole)
        if version_data:
            # 显示预览
            self.preview_text.setHtml(version_data['content'])
            
            # 启用按钮
            self.restore_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.view_btn.setEnabled(True)
            
    def restore_version(self):
        """恢复版本"""
        current_item = self.version_list.currentItem()
        if not current_item:
            return
            
        version_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "确认恢复",
            f"确定要恢复到版本 {version_data['id']} 吗？\n当前内容将被替换。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.version_restored.emit(version_data['content'])
            self.accept()
            
    def delete_version(self):
        """删除版本"""
        current_item = self.version_list.currentItem()
        if not current_item:
            return
            
        version_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除版本 {version_data['id']} 吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.version_manager.delete_version(version_data['id'])
            self.load_versions()  # 重新加载列表
            self.preview_text.clear()
            
            # 禁用按钮
            self.restore_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.view_btn.setEnabled(False)
            
    def view_version(self):
        """查看版本详情"""
        current_item = self.version_list.currentItem()
        if not current_item:
            return
            
        version_data = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = VersionViewDialog(version_data, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 用户选择恢复
            self.version_restored.emit(version_data['content'])
            self.accept()
            
    def clear_all_history(self):
        """清除所有历史"""
        reply = QMessageBox.question(
            self, "确认清除",
            "确定要清除所有版本历史吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.version_manager.clear_history()
            self.load_versions()
            self.preview_text.clear()
            
            # 禁用按钮
            self.restore_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.view_btn.setEnabled(False)