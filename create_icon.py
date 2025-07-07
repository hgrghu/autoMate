#!/usr/bin/env python3
"""
图标转换脚本
将PNG图标转换为ICO格式，用于Windows exe文件
"""

import sys
import os
from pathlib import Path

def create_icon():
    """创建ICO图标文件"""
    try:
        from PIL import Image
        
        # 路径设置
        project_dir = Path(__file__).parent
        png_path = project_dir / "imgs" / "logo.png"
        ico_path = project_dir / "imgs" / "logo.ico"
        
        if not png_path.exists():
            print(f"警告: PNG图标文件不存在: {png_path}")
            return False
        
        # 打开PNG图像
        img = Image.open(png_path)
        
        # 转换为RGBA模式（如果不是的话）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建多个尺寸的图标
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_images = []
        
        for size in icon_sizes:
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized_img)
        
        # 保存为ICO文件
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        
        print(f"成功创建ICO图标: {ico_path}")
        return True
        
    except ImportError:
        print("错误: 需要安装Pillow库来转换图标")
        print("请运行: pip install Pillow")
        return False
    except Exception as e:
        print(f"创建图标时出错: {e}")
        return False

def create_default_icon():
    """创建默认图标（如果原图标不存在）"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        project_dir = Path(__file__).parent
        ico_path = project_dir / "imgs" / "logo.ico"
        
        # 创建一个简单的默认图标
        img = Image.new('RGBA', (256, 256), (70, 130, 180, 255))  # 钢蓝色背景
        draw = ImageDraw.Draw(img)
        
        # 绘制一个简单的"AI"文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            # 如果系统字体不可用，使用默认字体
            font = ImageFont.load_default()
        
        # 绘制白色"AI"文字
        text = "AI"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (256 - text_width) // 2
        y = (256 - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # 创建多个尺寸
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_images = []
        
        for size in icon_sizes:
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized_img)
        
        # 保存为ICO文件
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        
        print(f"成功创建默认ICO图标: {ico_path}")
        return True
        
    except Exception as e:
        print(f"创建默认图标时出错: {e}")
        return False

if __name__ == "__main__":
    print("正在创建应用程序图标...")
    
    # 确保imgs目录存在
    imgs_dir = Path(__file__).parent / "imgs"
    imgs_dir.mkdir(exist_ok=True)
    
    # 尝试转换现有的PNG图标
    if create_icon():
        print("图标转换完成!")
    else:
        print("PNG图标不存在或转换失败，创建默认图标...")
        if create_default_icon():
            print("默认图标创建完成!")
        else:
            print("图标创建失败，将使用系统默认图标")
            sys.exit(1)