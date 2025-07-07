#!/usr/bin/env python3
"""
Integration Script for AI Enhanced Rich Text Editor
AI增强富文本编辑器集成脚本
"""

import sys
import os
from pathlib import Path

def integrate_editor_to_automate():
    """将编辑器集成到autoMate主程序中"""
    
    print("🔧 开始集成AI增强富文本编辑器到autoMate...")
    
    # 检查是否在autoMate项目根目录
    current_dir = Path.cwd()
    if not (current_dir / "main.py").exists():
        print("❌ 请在autoMate项目根目录下运行此脚本")
        return False
    
    try:
        # 1. 修改主窗口，添加编辑器入口
        modify_main_window()
        
        # 2. 创建编辑器菜单项
        add_editor_menu()
        
        # 3. 更新requirements.txt
        update_requirements()
        
        print("✅ 集成完成！")
        print("📝 新功能已添加到autoMate主界面:")
        print("   - 菜单栏 -> 工具 -> AI文本编辑器")
        print("   - 或使用快捷键 Ctrl+E")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成失败: {e}")
        return False

def modify_main_window():
    """修改主窗口，添加编辑器入口"""
    main_window_file = Path("ui/main_window.py")
    
    if not main_window_file.exists():
        print("⚠️ 未找到主窗口文件，跳过界面集成")
        return
    
    # 读取原文件
    with open(main_window_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经集成
    if "AI文本编辑器" in content:
        print("ℹ️ 编辑器已经集成到主窗口")
        return
    
    # 添加导入语句
    if "from editor.main_editor import AIRichTextEditor" not in content:
        import_section = "from PyQt6.QtWidgets import"
        if import_section in content:
            content = content.replace(
                import_section,
                f"# AI Editor Integration\ntry:\n    from editor.main_editor import AIRichTextEditor\n    EDITOR_AVAILABLE = True\nexcept ImportError:\n    EDITOR_AVAILABLE = False\n\n{import_section}"
            )
    
    # 在菜单创建部分添加编辑器菜单
    menu_section = 'help_menu = menubar.addMenu(\'帮助(&H)\')'
    if menu_section in content:
        editor_menu_code = '''
        # AI文本编辑器菜单
        if EDITOR_AVAILABLE:
            tools_menu = menubar.addMenu('工具(&T)')
            
            editor_action = tools_menu.addAction('AI文本编辑器')
            editor_action.setShortcut('Ctrl+E')
            editor_action.triggered.connect(self.open_ai_editor)
        '''
        
        content = content.replace(menu_section, f"{menu_section}{editor_menu_code}")
    
    # 添加编辑器打开方法
    if "def open_ai_editor(self):" not in content:
        editor_method = '''
    def open_ai_editor(self):
        """打开AI文本编辑器"""
        try:
            if not hasattr(self, 'ai_editor') or self.ai_editor is None:
                self.ai_editor = AIRichTextEditor()
            self.ai_editor.show()
            self.ai_editor.activateWindow()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开AI文本编辑器:\\n{str(e)}")
        '''
        
        # 在类的最后添加方法
        class_end = content.rfind("def closeEvent(self, event):")
        if class_end != -1:
            method_end = content.find("\n\n", class_end)
            if method_end != -1:
                content = content[:method_end] + editor_method + content[method_end:]
    
    # 写回文件
    with open(main_window_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 主窗口集成完成")

def add_editor_menu():
    """添加编辑器菜单项"""
    print("ℹ️ 编辑器菜单已通过主窗口集成")

def update_requirements():
    """更新requirements.txt"""
    requirements_file = Path("requirements.txt")
    editor_requirements_file = Path("editor_requirements.txt")
    
    if not requirements_file.exists():
        print("⚠️ 未找到requirements.txt文件")
        return
    
    if not editor_requirements_file.exists():
        print("⚠️ 未找到editor_requirements.txt文件")
        return
    
    # 读取原requirements
    with open(requirements_file, 'r', encoding='utf-8') as f:
        original_requirements = f.read()
    
    # 读取编辑器requirements
    with open(editor_requirements_file, 'r', encoding='utf-8') as f:
        editor_requirements = f.read()
    
    # 提取编辑器特有的依赖
    editor_specific = [
        "html2text>=2020.1.16",
        "markdown>=3.4.4", 
        "python-docx>=0.8.11",
        "weasyprint>=60.0",
        "matplotlib>=3.7.0"
    ]
    
    # 检查是否需要添加
    needs_update = False
    for req in editor_specific:
        if req.split('>=')[0].split('==')[0] not in original_requirements:
            needs_update = True
            break
    
    if needs_update:
        updated_requirements = original_requirements + "\n# AI文本编辑器依赖\n"
        for req in editor_specific:
            if req.split('>=')[0].split('==')[0] not in original_requirements:
                updated_requirements += f"{req}\n"
        
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(updated_requirements)
        
        print("✅ requirements.txt 已更新")
    else:
        print("ℹ️ requirements.txt 无需更新")

def create_launch_script():
    """创建启动脚本"""
    script_content = '''#!/usr/bin/env python3
"""
autoMate with AI Enhanced Editor Launcher
集成AI编辑器的autoMate启动脚本
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    print("🚀 启动 autoMate (集成AI编辑器版本)...")
    
    # 导入并启动主程序
    from ui.main import main as automate_main
    automate_main()

if __name__ == "__main__":
    main()
'''
    
    with open("run_automate_with_editor.py", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 创建了集成启动脚本: run_automate_with_editor.py")

def main():
    """主函数"""
    print("=" * 60)
    print("  AI Enhanced Rich Text Editor Integration")
    print("  AI增强富文本编辑器集成工具")
    print("=" * 60)
    
    if integrate_editor_to_automate():
        create_launch_script()
        
        print("\n" + "=" * 60)
        print("🎉 集成成功完成！")
        print("\n使用方法:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动程序: python main.py")
        print("3. 在主界面菜单栏选择: 工具 -> AI文本编辑器")
        print("4. 或使用快捷键: Ctrl+E")
        print("\n单独启动编辑器:")
        print("python run_editor.py")
        print("=" * 60)
    else:
        print("\n❌ 集成失败，请检查错误信息")

if __name__ == "__main__":
    main()