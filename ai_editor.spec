# -*- mode: python ; coding: utf-8 -*-
"""
AI富文本编辑器 PyInstaller 配置文件
用于打包生成exe文件
"""

import sys
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(os.getcwd())
EDITOR_DIR = ROOT_DIR / 'editor'
IMGS_DIR = ROOT_DIR / 'imgs'

# 数据文件列表
datas = [
    # 图片资源
    (str(IMGS_DIR), 'imgs'),
    # 文档文件
    ('AI富文本编辑器使用指南_增强版.md', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
]

# 隐藏导入模块
hiddenimports = [
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
    'PIL.Image',
    'PIL.ImageQt',
    'bs4',
    'lxml',
    'lxml.etree',
    'lxml.html',
    # 编辑器模块
    'editor',
    'editor.main_editor',
    'editor.text_editor', 
    'editor.llm_assistant',
    'editor.toolbar',
    'editor.export_manager',
    'editor.outline_view',
    'editor.version_manager',
    'editor.document_generator',
    'editor.smart_layout',
    'editor.template_manager',
    'editor.sidebar',
]

# 排除的模块
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'tensorflow',
    'torch',
    'jupyter',
    'ipython',
    'test',
    'unittest',
    'pdb',
    'doctest',
    'distutils',
    'setuptools',
    'wheel',
    'pip',
]

# 二进制文件
binaries = []

# PyInstaller分析
a = Analysis(
    ['app_main.py'],
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 优化：移除不需要的文件
def remove_unwanted_files(a):
    """移除不需要的文件以减小体积"""
    unwanted_patterns = [
        'api-ms-win-*',
        'ucrtbase.dll',
        'msvcp*.dll',
        'vcruntime*.dll',
        'concrt*.dll',
        'vcomp*.dll',
    ]
    
    a.binaries = [x for x in a.binaries if not any(pattern in x[0] for pattern in unwanted_patterns)]
    return a

a = remove_unwanted_files(a)

# 生成PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 生成EXE文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI富文本编辑器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(IMGS_DIR / 'logo.png') if (IMGS_DIR / 'logo.png').exists() else None,
    version_file=None,
)

# Windows版本信息
if sys.platform.startswith('win'):
    import time
    
    version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'autoMate团队'),
            StringStruct(u'FileDescription', u'AI富文本编辑器'),
            StringStruct(u'FileVersion', u'2.0.0'),
            StringStruct(u'InternalName', u'AI富文本编辑器'),
            StringStruct(u'LegalCopyright', u'Copyright © 2024 autoMate Team'),
            StringStruct(u'OriginalFilename', u'AI富文本编辑器.exe'),
            StringStruct(u'ProductName', u'AI富文本编辑器'),
            StringStruct(u'ProductVersion', u'2.0.0'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    # 创建版本文件
    version_file_path = ROOT_DIR / 'version_info.txt'
    with open(version_file_path, 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    # 更新EXE配置
    exe.version = version_file_path