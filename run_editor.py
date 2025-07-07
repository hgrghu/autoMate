#!/usr/bin/env python3
"""
AI Enhanced Rich Text Editor Launcher
AI增强富文本编辑器启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖包"""
    missing_packages = []
    
    try:
        import PyQt6
    except ImportError:
        missing_packages.append("PyQt6")
    
    try:
        import html2text
    except ImportError:
        missing_packages.append("html2text")
    
    try:
        import markdown
    except ImportError:
        missing_packages.append("markdown")
    
    if missing_packages:
        print("❌ 缺少必要的依赖包:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r editor_requirements.txt")
        return False
        
    return True

def setup_environment():
    """设置环境"""
    # 设置QT相关环境变量
    os.environ.setdefault('QT_AUTO_SCREEN_SCALE_FACTOR', '1')
    
    # 确保使用正确的DPI设置
    if hasattr(sys, 'platform') and sys.platform == 'win32':
        try:
            from PyQt6.QtCore import Qt
            from PyQt6.QtWidgets import QApplication
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except ImportError:
            pass

def main():
    """主函数"""
    print("🚀 启动 AI增强富文本编辑器...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置环境
    setup_environment()
    
    try:
        # 导入并启动编辑器
        from editor.main_editor import AIRichTextEditor
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName("AI增强富文本编辑器")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("autoMate")
        
        # 设置应用图标
        try:
            icon_path = project_root / "imgs" / "logo.png"
            if icon_path.exists():
                from PyQt6.QtGui import QIcon
                app.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            print(f"⚠️ 无法加载应用图标: {e}")
        
        # 创建主窗口
        editor = AIRichTextEditor()
        editor.show()
        
        print("✅ 编辑器启动成功!")
        print("💡 提示: 请在设置中配置API Key以使用AI功能")
        
        # 运行应用
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已正确安装所有依赖包")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()