"""
Editor Sidebar Component
编辑器侧边栏组件（预留接口）
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal

class EditorSidebar(QWidget):
    """编辑器侧边栏（预留组件）"""
    
    # 预留信号
    action_triggered = pyqtSignal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 占位标签
        placeholder_label = QLabel("侧边栏\n(预留扩展)")
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                text-align: center;
                padding: 20px;
            }
        """)
        
        layout.addWidget(placeholder_label)
        layout.addStretch()
        
        # 设置最小宽度
        self.setMinimumWidth(200)