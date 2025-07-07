#!/usr/bin/env python3
"""
AI富文本编辑器增强版启动脚本
Enhanced AI Rich Text Editor Launcher

包含新功能：
- AI文档生成器
- 智能排版设计
- 文档模板库
- 完整的AI辅助功能

作者: autoMate团队
版本: 2.0.0 (增强版)
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """检查并安装必要的依赖"""
    print("🔍 检查系统依赖...")
    
    required_packages = [
        'PyQt6',
        'python-docx',
        'markdown',
        'weasyprint',
        'requests',
        'Pillow',
        'beautifulsoup4',
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
            print(f"✅ {package}: 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: 未安装")
    
    if missing_packages:
        print(f"\n📦 发现 {len(missing_packages)} 个缺失的依赖包")
        print("正在安装缺失的依赖...")
        
        for package in missing_packages:
            try:
                print(f"安装 {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 安装失败，请手动安装")
                return False
    
    print("✅ 所有依赖检查完成\n")
    return True

def check_ai_config():
    """检查AI配置"""
    print("🤖 检查AI配置...")
    
    # 这里可以添加API密钥检查逻辑
    config_file = Path(__file__).parent / "xbrain" / "utils" / "config.py"
    
    if not config_file.exists():
        print("⚠️  AI配置文件不存在，将使用默认配置")
        print("   首次使用时请在设置中配置API密钥")
    else:
        print("✅ AI配置文件存在")
    
    print("✅ AI配置检查完成\n")

def create_directories():
    """创建必要的目录结构"""
    print("📁 创建必要的目录...")
    
    directories = [
        'editor/templates',
        'editor/exports',
        'editor/versions',
        'editor/assets'
    ]
    
    base_path = Path(__file__).parent
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录创建: {directory}")
    
    print("✅ 目录结构创建完成\n")

def show_welcome():
    """显示欢迎信息"""
    print("=" * 60)
    print("🎉 AI富文本编辑器 - 增强版 v2.0.0")
    print("   基于autoMate项目构建的智能文档处理工具")
    print("=" * 60)
    print()
    print("🆕 新增功能:")
    print("   • AI文档生成器 - 自动生成各类专业文档")
    print("   • 智能排版设计 - AI分析并优化文档排版")
    print("   • 文档模板库 - 丰富的专业模板集合")
    print("   • 增强AI功能 - 更强大的文本处理能力")
    print()
    print("💡 核心特性:")
    print("   • 富文本编辑和格式化")
    print("   • AI辅助写作和优化")
    print("   • 多格式导入导出")
    print("   • 版本管理和大纲视图")
    print("   • 图片和表格处理")
    print()
    print("🚀 正在启动编辑器...")
    print("=" * 60)
    print()

def launch_editor():
    """启动编辑器"""
    try:
        # 确保当前目录在Python路径中
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # 导入并启动编辑器
        from editor.main_editor import AIRichTextEditor
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("AI富文本编辑器增强版")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("autoMate团队")
        
        # 设置应用程序样式
        app.setStyle('Fusion')  # 使用现代化样式
        
        # 设置应用程序图标
        try:
            icon_path = current_dir / "imgs" / "logo.png"
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass  # 图标设置失败时忽略
        
        # 创建并显示主窗口
        editor = AIRichTextEditor()
        editor.show()
        
        # 显示启动成功信息
        print("✅ 编辑器启动成功!")
        print("📚 使用说明:")
        print("   • 查看 'AI富文本编辑器使用指南_增强版.md' 获取详细使用说明")
        print("   • 首次使用请在设置中配置AI API密钥")
        print("   • 试试新的AI文档生成器和智能排版功能!")
        print()
        
        # 运行应用程序
        return app.exec()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已正确安装")
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查系统环境和依赖配置")
        return 1

def show_system_info():
    """显示系统信息"""
    print("💻 系统信息:")
    print(f"   Python版本: {sys.version.split()[0]}")
    print(f"   操作系统: {os.name}")
    print(f"   工作目录: {Path.cwd()}")
    print()

def main():
    """主函数"""
    # 清屏（仅在支持的终端中）
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 显示欢迎信息
    show_welcome()
    
    # 显示系统信息
    show_system_info()
    
    # 创建必要目录
    create_directories()
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请手动安装缺失的包后重试")
        return 1
    
    # 检查AI配置
    check_ai_config()
    
    # 启动编辑器
    try:
        return launch_editor()
    except KeyboardInterrupt:
        print("\n👋 用户取消启动")
        return 0
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print("\n👋 感谢使用AI富文本编辑器增强版!")
    else:
        print(f"\n❌ 程序异常退出 (错误代码: {exit_code})")
        print("如果问题持续出现，请检查:")
        print("  1. Python版本是否为3.8+")
        print("  2. 所有依赖是否正确安装")
        print("  3. 系统权限是否充足")
        print("  4. 网络连接是否正常（AI功能需要）")
    
    sys.exit(exit_code)