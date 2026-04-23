#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理 Markdown 冗余内容脚本
删除 OCR 图片注释块和字体颜色标签
"""

import re
import sys
from pathlib import Path


def remove_ocr_comments(text):
    """删除 OCR 图片注释块"""

    # 匹配 OCR 注释块的正则表达式
    # 支持多种变体:
    # - <!-- 这是一张图片,ocr内容为:xxx -->
    # - <!-- 这是一张图片，ocr 内容为：xxx -->
    # - <!--这是一张图片,OCR内容为:xxx-->
    # - 以及其他空格和标点的变体

    pattern = r'<!--\s*这是一张图片[,，]?\s*ocr\s*内容为\s*[:：].*?-->'

    # 使用 DOTALL 标志支持多行匹配
    text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    return text


def remove_font_color_tags(text):
    """删除字体颜色标签,保留标签内的文字"""

    # 匹配开头标签的正则表达式
    # 支持多种变体:
    # - <font style="color:rgba(255,0,0,1);">
    # - <font style="color: rgba(255, 0, 0, 1);">
    # - <font style="color:rgba(255,0,0,1)">
    # - <font style="color:rgb(61,71,92);">
    # - <font style="color: rgb(61, 71, 92);">

    opening_pattern = r'<font\s+style\s*=\s*["\']color\s*:\s*rgba?\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)\s*;?\s*["\']\s*>'

    # 匹配结尾标签
    closing_pattern = r'</font>'

    # 先删除开头标签
    text = re.sub(opening_pattern, '', text, flags=re.IGNORECASE)

    # 再删除结尾标签
    text = re.sub(closing_pattern, '', text, flags=re.IGNORECASE)

    return text


def clean_empty_lines(text):
    """清理多余的空行"""

    # 将连续的多个空行替换为最多两个空行
    # 这样可以保持段落间的合理间距
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 删除文件末尾的多余空行
    text = text.rstrip() + '\n'

    return text


def clean_redundant_content(text):
    """主函数:清理冗余内容"""

    # 1. 删除 OCR 图片注释块
    text = remove_ocr_comments(text)

    # 2. 删除字体颜色标签
    text = remove_font_color_tags(text)

    # 3. 清理多余的空行
    text = clean_empty_lines(text)

    return text


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python clean_redundant.py <文件路径>")
        print("      python clean_redundant.py <文件路径> --in-place")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    in_place = '--in-place' in sys.argv

    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 清理冗余内容
    result = clean_redundant_content(content)

    if in_place:
        # 原地修改
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✓ 已更新文件: {file_path}")
    else:
        # 输出到标准输出
        print(result)


if __name__ == '__main__':
    main()