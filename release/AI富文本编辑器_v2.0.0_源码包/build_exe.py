#!/usr/bin/env python3
"""
AI富文本编辑器打包构建脚本
Build Script for AI Rich Text Editor
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import time

# 导入配置
from build_config import *

class BuildManager:
    """构建管理器"""
    
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.build_dir = BUILD_DIR
        self.dist_dir = DIST_DIR
        self.start_time = time.time()
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_environment(self):
        """检查构建环境"""
        self.log("检查构建环境...")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            self.log("Python版本必须是3.8或更高", "ERROR")
            return False
        
        # 检查必要的工具
        required_tools = ['pip', 'pyinstaller']
        for tool in required_tools:
            if shutil.which(tool) is None:
                self.log(f"缺少必要工具: {tool}", "ERROR")
                return False
        
        self.log("环境检查通过")
        return True
        
    def install_dependencies(self):
        """安装依赖"""
        self.log("安装构建依赖...")
        
        build_deps = [
            'pyinstaller>=5.0',
            'pillow>=9.0.0',
            'setuptools>=60.0',
        ]
        
        for dep in build_deps:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                             check=True, capture_output=True)
                self.log(f"安装依赖: {dep}")
            except subprocess.CalledProcessError as e:
                self.log(f"安装依赖失败: {dep} - {e}", "ERROR")
                return False
        
        # 安装项目依赖
        req_file = self.project_dir / "editor_requirements.txt"
        if req_file.exists():
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(req_file)], 
                             check=True, capture_output=True)
                self.log("安装项目依赖")
            except subprocess.CalledProcessError as e:
                self.log(f"安装项目依赖失败: {e}", "ERROR")
                return False
        
        return True
        
    def create_icon(self):
        """创建应用程序图标"""
        self.log("创建应用程序图标...")
        
        try:
            result = subprocess.run([sys.executable, 'create_icon.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("图标创建成功")
                return True
            else:
                self.log(f"图标创建失败: {result.stderr}", "WARNING")
                return True  # 继续构建，即使图标创建失败
        except Exception as e:
            self.log(f"图标创建异常: {e}", "WARNING")
            return True
            
    def clean_build(self):
        """清理构建目录"""
        self.log("清理构建目录...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.log(f"清理目录: {dir_path}")
        
        # 清理临时文件
        temp_files = [
            self.project_dir / "*.pyc",
            self.project_dir / "__pycache__",
            self.project_dir / "*.egg-info",
            self.project_dir / "version_info.txt",
        ]
        
        for pattern in temp_files:
            for file_path in self.project_dir.rglob(pattern.name):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.log(f"清理文件失败: {file_path} - {e}", "WARNING")
    
    def optimize_modules(self):
        """优化模块导入"""
        self.log("优化模块导入...")
        
        # 检查xbrain模块
        xbrain_dir = self.project_dir / "xbrain"
        if not xbrain_dir.exists():
            self.log("创建xbrain模块目录...")
            xbrain_dir.mkdir(exist_ok=True)
            
            # 创建基本的xbrain模块结构
            (xbrain_dir / "__init__.py").touch()
            
            utils_dir = xbrain_dir / "utils"
            utils_dir.mkdir(exist_ok=True)
            (utils_dir / "__init__.py").touch()
            
            core_dir = xbrain_dir / "core"
            core_dir.mkdir(exist_ok=True)
            (core_dir / "__init__.py").touch()
            
            # 创建基本的配置和聊天模块
            self.create_basic_modules(utils_dir, core_dir)
    
    def create_basic_modules(self, utils_dir, core_dir):
        """创建基本模块"""
        # 创建配置模块
        config_content = '''
class Config:
    def __init__(self):
        self.OPENAI_API_KEY = ""
        self.OPENAI_BASE_URL = "https://api.openai.com/v1"
        self.MODEL_NAME = "gpt-3.5-turbo"
'''
        (utils_dir / "config.py").write_text(config_content, encoding='utf-8')
        
        # 创建聊天模块
        chat_content = '''
import requests
import json

def run(messages, model="gpt-3.5-turbo"):
    """基本的聊天函数"""
    try:
        # 这里可以集成实际的AI API调用
        # 目前返回一个示例响应
        return "AI功能需要配置API密钥才能使用。请在设置中配置您的API密钥。"
    except Exception as e:
        return f"AI服务暂不可用: {str(e)}"
'''
        (core_dir / "chat.py").write_text(chat_content, encoding='utf-8')
    
    def build_executable(self):
        """构建可执行文件"""
        self.log("开始构建可执行文件...")
        
        # PyInstaller命令
        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            'ai_editor.spec'
        ]
        
        try:
            # 运行PyInstaller
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # 实时输出构建日志
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(f"PyInstaller: {output.strip()}")
            
            if process.returncode == 0:
                self.log("可执行文件构建成功")
                return True
            else:
                self.log("可执行文件构建失败", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"构建过程异常: {e}", "ERROR")
            return False
    
    def post_build_optimization(self):
        """构建后优化"""
        self.log("执行构建后优化...")
        
        exe_path = self.dist_dir / "AI富文本编辑器.exe"
        if not exe_path.exists():
            self.log("可执行文件不存在，跳过优化", "WARNING")
            return False
        
        # 检查文件大小
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        self.log(f"可执行文件大小: {file_size:.1f} MB")
        
        # 如果文件过大，给出建议
        if file_size > 200:
            self.log("文件大小较大，建议使用--onedir模式或优化依赖", "WARNING")
        
        return True
    
    def create_distribution(self):
        """创建发布包"""
        self.log("创建发布包...")
        
        # 创建发布目录
        release_dir = self.dist_dir / f"AI富文本编辑器_v{APP_VERSION}"
        release_dir.mkdir(exist_ok=True)
        
        # 复制可执行文件
        exe_path = self.dist_dir / "AI富文本编辑器.exe"
        if exe_path.exists():
            shutil.copy2(exe_path, release_dir)
            self.log("复制可执行文件")
        
        # 复制文档文件
        docs_to_copy = [
            "AI富文本编辑器使用指南_增强版.md",
            "README.md",
            "LICENSE",
        ]
        
        for doc in docs_to_copy:
            doc_path = self.project_dir / doc
            if doc_path.exists():
                shutil.copy2(doc_path, release_dir)
                self.log(f"复制文档: {doc}")
        
        # 创建启动说明
        readme_content = f"""
# AI富文本编辑器 v{APP_VERSION}

## 快速开始

1. 双击 "AI富文本编辑器.exe" 启动程序
2. 首次使用请在设置中配置AI API密钥
3. 查看 "AI富文本编辑器使用指南_增强版.md" 获取详细使用说明

## 系统要求

- Windows 10 或更高版本
- 4GB 内存（推荐8GB或更多）
- 500MB 可用磁盘空间
- 网络连接（AI功能需要）

## 技术支持

如有问题，请访问项目主页或联系技术支持。

---
© 2024 autoMate团队
"""
        
        (release_dir / "使用说明.txt").write_text(readme_content, encoding='utf-8')
        
        # 创建ZIP压缩包
        zip_path = self.dist_dir / f"AI富文本编辑器_v{APP_VERSION}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in release_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(release_dir)
                    zipf.write(file_path, arcname)
        
        self.log(f"创建发布包: {zip_path}")
        
        # 显示发布信息
        self.show_release_info(release_dir, zip_path)
        
        return True
    
    def show_release_info(self, release_dir, zip_path):
        """显示发布信息"""
        self.log("=" * 60)
        self.log("构建完成!")
        self.log("=" * 60)
        
        build_time = time.time() - self.start_time
        self.log(f"构建耗时: {build_time:.1f} 秒")
        
        if release_dir.exists():
            self.log(f"发布目录: {release_dir}")
        
        if zip_path.exists():
            zip_size = zip_path.stat().st_size / (1024 * 1024)
            self.log(f"发布包: {zip_path} ({zip_size:.1f} MB)")
        
        self.log("发布内容:")
        for item in release_dir.iterdir():
            if item.is_file():
                size = item.stat().st_size / (1024 * 1024)
                self.log(f"  - {item.name} ({size:.1f} MB)")
        
        self.log("=" * 60)
        self.log("接下来的步骤:")
        self.log("1. 测试可执行文件是否正常运行")
        self.log("2. 将发布包上传到GitHub Release")
        self.log("3. 更新项目文档和版本信息")
        self.log("=" * 60)
    
    def run_build(self):
        """运行完整构建流程"""
        self.log("开始构建AI富文本编辑器...")
        self.log(f"版本: {APP_VERSION}")
        self.log(f"项目目录: {self.project_dir}")
        
        try:
            # 1. 检查环境
            if not self.check_environment():
                return False
            
            # 2. 清理构建目录
            self.clean_build()
            
            # 3. 安装依赖
            if not self.install_dependencies():
                return False
            
            # 4. 优化模块
            self.optimize_modules()
            
            # 5. 创建图标
            self.create_icon()
            
            # 6. 构建可执行文件
            if not self.build_executable():
                return False
            
            # 7. 构建后优化
            self.post_build_optimization()
            
            # 8. 创建发布包
            if not self.create_distribution():
                return False
            
            self.log("构建流程完成!", "SUCCESS")
            return True
            
        except KeyboardInterrupt:
            self.log("构建被用户中断", "WARNING")
            return False
        except Exception as e:
            self.log(f"构建过程发生错误: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("AI富文本编辑器构建工具")
    print("=" * 50)
    
    builder = BuildManager()
    success = builder.run_build()
    
    if success:
        print("\n🎉 构建成功!")
        print("可执行文件已准备好发布。")
        sys.exit(0)
    else:
        print("\n❌ 构建失败!")
        print("请检查错误信息并重试。")
        sys.exit(1)

if __name__ == "__main__":
    main()