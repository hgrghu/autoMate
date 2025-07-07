"""
AI富文本编辑器打包配置
Build Configuration for AI Rich Text Editor
"""

import os
import sys
from pathlib import Path

# 项目信息
APP_NAME = "AI富文本编辑器"
APP_VERSION = "2.0.0"
APP_AUTHOR = "autoMate团队"
APP_DESCRIPTION = "基于AI的智能富文本编辑器"
APP_COPYRIGHT = "Copyright (c) 2024 autoMate Team"

# 文件路径
PROJECT_DIR = Path(__file__).parent
EDITOR_DIR = PROJECT_DIR / "editor"
IMGS_DIR = PROJECT_DIR / "imgs"
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"

# 图标文件
ICON_FILE = IMGS_DIR / "logo.png"
if sys.platform.startswith('win'):
    ICON_FILE = str(ICON_FILE).replace('.png', '.ico')

# PyInstaller配置
PYINSTALLER_CONFIG = {
    'name': 'AIRichTextEditor',
    'icon': str(ICON_FILE),
    'console': False,  # 不显示控制台窗口
    'onefile': True,   # 打包成单个exe文件
    'windowed': True,  # Windows应用程序模式
    'add_data': [
        (str(IMGS_DIR / "*.png"), "imgs"),
        (str(EDITOR_DIR / "templates"), "editor/templates"),
        ("AI富文本编辑器使用指南_增强版.md", "."),
    ],
    'hidden_imports': [
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.QtPrintSupport',
        'requests',
        'json',
        'sqlite3',
        'datetime',
        'pathlib',
        'markdown',
        'docx',
        'weasyprint',
        'PIL',
        'bs4',
        'lxml',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'test',
        'unittest',
        'pdb',
        'doctest',
    ],
    'collect_data': [
        'PyQt6',
    ]
}

# 依赖包列表
REQUIRED_PACKAGES = [
    'PyQt6>=6.4.0',
    'requests>=2.28.0',
    'python-docx>=0.8.11',
    'markdown>=3.4.0',
    'weasyprint>=56.0',
    'Pillow>=9.0.0',
    'beautifulsoup4>=4.11.0',
    'lxml>=4.9.0',
]

# 可选依赖（用于增强功能）
OPTIONAL_PACKAGES = [
    'openai>=0.27.0',  # OpenAI API
    'anthropic>=0.3.0',  # Claude API
    'transformers>=4.21.0',  # 本地模型支持
]

# 构建输出目录
OUTPUT_DIR = DIST_DIR / f"{APP_NAME}_v{APP_VERSION}"

def get_version_info():
    """获取版本信息字典"""
    return {
        'version': APP_VERSION,
        'description': APP_DESCRIPTION,
        'copyright': APP_COPYRIGHT,
        'company': APP_AUTHOR,
        'product': APP_NAME,
    }

def get_entry_points():
    """获取程序入口点"""
    return {
        'gui_scripts': [
            f'{APP_NAME.lower().replace(" ", "_")}=main:main'
        ]
    }

# 发布配置
RELEASE_CONFIG = {
    'create_installer': True,
    'installer_name': f'{APP_NAME}_Setup_v{APP_VERSION}',
    'include_docs': True,
    'include_examples': True,
    'compress': True,
}

# 安装程序配置（NSIS）
NSIS_CONFIG = {
    'name': APP_NAME,
    'version': APP_VERSION,
    'publisher': APP_AUTHOR,
    'url': 'https://github.com/automate-team/ai-rich-text-editor',
    'description': APP_DESCRIPTION,
    'license': str(PROJECT_DIR / "LICENSE"),
    'icon': str(ICON_FILE),
    'install_dir': f'$PROGRAMFILES\\{APP_AUTHOR}\\{APP_NAME}',
    'start_menu_dir': f'{APP_AUTHOR}\\{APP_NAME}',
}