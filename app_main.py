#!/usr/bin/env python3
"""
AI富文本编辑器主程序入口
Main Entry Point for AI Rich Text Editor

优化版本，专为打包设计
"""

import sys
import os
import traceback
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def setup_environment():
    """设置运行环境"""
    try:
        # 获取应用程序路径
        if getattr(sys, 'frozen', False):
            # 打包后的exe文件
            app_dir = Path(sys.executable).parent
            sys.path.insert(0, str(app_dir))
        else:
            # 开发环境
            app_dir = Path(__file__).parent
            sys.path.insert(0, str(app_dir))
        
        # 设置资源路径
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(app_dir / 'platforms')
        
        # 创建必要的目录
        directories = ['templates', 'exports', 'versions', 'logs']
        for directory in directories:
            (app_dir / directory).mkdir(exist_ok=True)
            
        return app_dir
        
    except Exception as e:
        logging.error(f"环境设置失败: {e}")
        return None

def check_dependencies():
    """检查关键依赖"""
    required_modules = [
        'PyQt6.QtWidgets',
        'PyQt6.QtCore', 
        'PyQt6.QtGui',
        'requests'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError as e:
            missing_modules.append(module)
            logging.error(f"缺少依赖: {module}")
    
    if missing_modules:
        return False, missing_modules
    
    return True, []

def show_error_dialog(title, message):
    """显示错误对话框"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    except Exception as e:
        # 如果PyQt6不可用，使用系统对话框
        print(f"错误: {title}\n{message}")

def main():
    """主函数"""
    try:
        # 设置运行环境
        app_dir = setup_environment()
        if app_dir is None:
            show_error_dialog("启动失败", "无法设置应用程序环境")
            return 1
        
        # 检查依赖
        deps_ok, missing = check_dependencies()
        if not deps_ok:
            error_msg = f"缺少必要的依赖模块:\n" + "\n".join(missing)
            error_msg += "\n\n请重新安装应用程序或联系技术支持。"
            show_error_dialog("依赖检查失败", error_msg)
            return 1
        
        # 导入并启动编辑器
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt, QStandardPaths
        from PyQt6.QtGui import QIcon, QPixmap
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("AI富文本编辑器")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("autoMate团队")
        app.setQuitOnLastWindowClosed(True)
        
        # 设置应用程序样式
        app.setStyle('Fusion')
        
        # 设置应用程序图标
        try:
            icon_path = app_dir / "imgs" / "logo.png"
            if not icon_path.exists() and getattr(sys, 'frozen', False):
                # 打包后的路径
                icon_path = app_dir / "logo.png"
            
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logging.warning(f"无法设置应用程序图标: {e}")
        
        # 设置高DPI支持
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # 导入主编辑器
        try:
            from editor.main_editor import AIRichTextEditor
        except ImportError:
            # 尝试备用导入路径
            sys.path.insert(0, str(app_dir / "editor"))
            from main_editor import AIRichTextEditor
        
        # 创建主窗口
        main_window = AIRichTextEditor()
        
        # 设置窗口属性
        main_window.setWindowTitle("AI富文本编辑器 v2.0.0")
        main_window.show()
        
        # 居中显示窗口
        try:
            screen = app.screens()[0]
            window_rect = main_window.frameGeometry()
            center_point = screen.availableGeometry().center()
            window_rect.moveCenter(center_point)
            main_window.move(window_rect.topLeft())
        except Exception as e:
            logging.warning(f"无法居中窗口: {e}")
        
        logging.info("AI富文本编辑器启动成功")
        
        # 启动应用程序事件循环
        exit_code = app.exec()
        
        logging.info(f"应用程序退出，退出代码: {exit_code}")
        return exit_code
        
    except ImportError as e:
        error_msg = f"无法导入必要的模块: {e}\n\n请确保应用程序安装完整。"
        show_error_dialog("导入错误", error_msg)
        logging.error(f"导入错误: {e}")
        return 1
        
    except Exception as e:
        error_msg = f"应用程序启动时发生未知错误:\n\n{str(e)}\n\n请联系技术支持。"
        show_error_dialog("启动错误", error_msg)
        logging.error(f"启动错误: {e}")
        logging.error(traceback.format_exc())
        return 1

def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理"""
    if issubclass(exc_type, KeyboardInterrupt):
        # 允许Ctrl+C正常退出
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.critical(f"未捕获的异常: {error_msg}")
    
    # 显示用户友好的错误消息
    user_msg = f"程序遇到了一个意外错误并需要关闭。\n\n错误类型: {exc_type.__name__}\n错误信息: {exc_value}"
    show_error_dialog("程序错误", user_msg)

if __name__ == "__main__":
    # 设置全局异常处理
    sys.excepthook = handle_exception
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except SystemExit:
        pass
    except Exception as e:
        logging.critical(f"主程序异常退出: {e}")
        sys.exit(1)