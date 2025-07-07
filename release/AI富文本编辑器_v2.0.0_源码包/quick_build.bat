@echo off
chcp 65001 > nul
echo ================================================================
echo                AI富文本编辑器 - 快速构建脚本
echo                      版本: 2.0.0
echo ================================================================
echo.

echo [1/5] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo [2/5] 安装构建依赖...
pip install pyinstaller pillow --quiet
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo [3/5] 安装项目依赖...
if exist editor_requirements.txt (
    pip install -r editor_requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo 警告: 部分项目依赖安装失败，但继续构建...
    )
)

echo [4/5] 创建图标文件...
python create_icon.py
if %errorlevel% neq 0 (
    echo 警告: 图标创建失败，使用默认图标
)

echo [5/5] 开始打包...
pyinstaller --clean --noconfirm ai_editor.spec
if %errorlevel% neq 0 (
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo.
echo ================================================================
echo                         构建完成!
echo ================================================================
echo.
echo 可执行文件位置: dist\AI富文本编辑器.exe
echo.
echo 接下来可以:
echo 1. 测试运行可执行文件
echo 2. 运行完整构建脚本: python build_exe.py
echo 3. 创建发布包
echo.
pause