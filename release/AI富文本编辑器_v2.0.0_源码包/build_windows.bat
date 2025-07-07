@echo off
chcp 65001 > nul
cls
echo ================================================================
echo          AI富文本编辑器 v2.0.0 - Windows构建脚本
echo ================================================================
echo.

echo [1/7] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请确保Python 3.8+已安装并添加到PATH
    echo 下载地址: https://python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

echo.
echo [2/7] 检查pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip不可用
    pause
    exit /b 1
)
echo ✅ pip可用

echo.
echo [3/7] 安装构建依赖...
echo 正在安装PyInstaller...
pip install pyinstaller>=6.0 --quiet
if %errorlevel% neq 0 (
    echo ❌ PyInstaller安装失败
    pause
    exit /b 1
)

echo 正在安装Pillow...
pip install Pillow>=9.0.0 --quiet
if %errorlevel% neq 0 (
    echo ❌ Pillow安装失败
    pause
    exit /b 1
)
echo ✅ 构建依赖安装完成

echo.
echo [4/7] 安装项目依赖...
if exist editor_requirements.txt (
    pip install -r editor_requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo ⚠️ 部分依赖安装失败，但继续构建...
    ) else (
        echo ✅ 项目依赖安装完成
    )
) else (
    echo ⚠️ 依赖文件不存在，跳过...
)

echo.
echo [5/7] 创建应用程序图标...
python create_icon.py
if %errorlevel% neq 0 (
    echo ⚠️ 图标创建失败，使用默认图标
) else (
    echo ✅ 图标创建成功
)

echo.
echo [6/7] 开始打包应用程序...
echo 这可能需要几分钟时间，请耐心等待...
pyinstaller --clean --noconfirm ai_editor.spec
if %errorlevel% neq 0 (
    echo ❌ 打包失败
    echo.
    echo 可能的解决方案:
    echo 1. 检查所有依赖是否正确安装
    echo 2. 确保没有杀毒软件阻止文件操作
    echo 3. 尝试以管理员身份运行
    echo 4. 查看详细错误信息
    pause
    exit /b 1
)

echo.
echo [7/7] 验证构建结果...
if exist "dist\AI富文本编辑器.exe" (
    for %%A in ("dist\AI富文本编辑器.exe") do set FILE_SIZE=%%~zA
    set /a FILE_SIZE_MB=!FILE_SIZE!/1048576
    echo ✅ 构建成功！
    echo.
    echo ================================================================
    echo                        🎉 构建完成！
    echo ================================================================
    echo.
    echo 📁 可执行文件位置: dist\AI富文本编辑器.exe
    echo 📊 文件大小: %FILE_SIZE% 字节 (约 !FILE_SIZE_MB! MB)
    echo.
    echo 📋 接下来可以：
    echo 1. 双击运行 dist\AI富文本编辑器.exe 测试程序
    echo 2. 将exe文件分享给其他用户
    echo 3. 创建安装包或压缩包发布
    echo.
    echo 💡 提示：
    echo - 首次运行可能需要几秒钟启动时间
    echo - 如需使用AI功能，请配置API密钥
    echo - 查看使用指南了解更多功能
    echo.
) else (
    echo ❌ 构建失败，未找到可执行文件
    echo.
    echo 故障排除：
    echo 1. 检查是否有足够的磁盘空间
    echo 2. 确认所有依赖正确安装
    echo 3. 查看构建日志中的错误信息
    pause
    exit /b 1
)

echo ================================================================
pause