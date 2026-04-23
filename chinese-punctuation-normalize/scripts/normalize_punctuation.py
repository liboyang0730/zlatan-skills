#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文标点与中英混排规范化脚本。

功能：
1. 将中文语境中的英文半角标点转换为中文标点。
2. 在中文与英文/数字之间补充空格。
3. 保护代码块、行内代码、URL、Markdown 链接等不应被改动的片段。
"""

import re
import sys
from pathlib import Path


PROTECTED_PATTERN = re.compile(
    r"```[\s\S]*?```"
    r"|`[^`\n]+`"
    r"|\[[^\]]+\]\(https?://[^\s)]+\)"
    r"|https?://[^\s)\]}]+"
    r"|[A-Za-z_][A-Za-z0-9_]*\([^()\n]*[)）]"
)

HAN_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z0-9]")
ENUMERATION_TOKEN_RE = r"[\u4e00-\u9fffA-Za-z0-9+#._-]+"
ZH_CONTEXT_PUNCT = set("，。！？；：（）《》〈〉【】“”‘’、")


def is_han_char(char):
    return bool(char) and bool(HAN_CHAR_RE.fullmatch(char))


def is_ascii_word_char(char):
    return bool(char) and bool(ASCII_WORD_RE.fullmatch(char))


def is_zh_context_char(char):
    return is_han_char(char) or char in ZH_CONTEXT_PUNCT


def previous_visible_char(text, index):
    """返回 index 左侧最近的非空白字符。"""
    for pos in range(index - 1, -1, -1):
        if not text[pos].isspace():
            return text[pos]
    return ""


def next_visible_char(text, index):
    """返回 index 右侧最近的非空白字符。"""
    for pos in range(index + 1, len(text)):
        if not text[pos].isspace():
            return text[pos]
    return ""


def line_start_index(text, index):
    """返回当前字符所在行的起始位置。"""
    pos = text.rfind("\n", 0, index)
    return 0 if pos == -1 else pos + 1


def is_markdown_ordered_list_marker(text, index):
    """判断当前句点是否属于 Markdown 有序列表标记（支持行首有空格的缩进列表）。"""
    if text[index] != ".":
        return False

    start = line_start_index(text, index)
    prefix = text[start:index]
    # 去掉行首空格后，剩余部分必须全为数字
    stripped = prefix.lstrip(" \t")
    return bool(stripped) and stripped.isdigit()


def should_convert_punctuation(text, index):
    """只在中文语境中转换半角标点。"""
    char = text[index]
    prev_char = previous_visible_char(text, index)
    next_char = next_visible_char(text, index)

    if char in {".", ","} and prev_char.isdigit() and next_char.isdigit():
        return False

    if char == "." and is_markdown_ordered_list_marker(text, index):
        return False

    # 保护文件名/扩展名：.data、.md、.obd 等（. 后面紧跟 ASCII 字母）
    # 注意：只保护 ASCII 字母，中文字符后的 . 仍应转换
    if char == "." and next_char.isascii() and next_char.isalpha():
        return False

    if char == ":" and prev_char.isdigit() and next_char.isdigit():
        return False

    if char in {"(", ")"}:
        return is_han_char(prev_char) or is_han_char(next_char)

    return is_han_char(prev_char) or is_han_char(next_char)


def convert_basic_punctuation(text):
    """按上下文转换半角标点，括号使用栈保持配对一致。"""
    punctuation_map = {
        ",": "，",
        ".": "。",
        ":": "：",
        "?": "？",
        "!": "！",
        ";": "；",
    }

    result = []
    # 括号栈：记录每个左括号的类型（'zh' 或 'en'）
    bracket_stack = []

    for index, char in enumerate(text):
        if char in ("(", "（"):
            # 统一判断：中文语境用中文括号，否则用英文括号
            if char == "（" or should_convert_punctuation(text, index):
                result.append("（")
                bracket_stack.append("zh")
            else:
                result.append("(")
                bracket_stack.append("en")
        elif char in (")", "）"):
            # 根据对应左括号类型决定右括号形式，修正不匹配的情况
            bracket_type = bracket_stack.pop() if bracket_stack else ("zh" if char == "）" else "en")
            result.append("）" if bracket_type == "zh" else ")")
        elif char in punctuation_map and should_convert_punctuation(text, index):
            result.append(punctuation_map[char])
        else:
            result.append(char)
    return "".join(result)


def convert_quotes(text):
    """将中文语境中的英文直引号转换为中文引号。"""
    result = []
    double_open = True
    single_open = True

    for index, char in enumerate(text):
        prev_char = previous_visible_char(text, index)
        next_char = next_visible_char(text, index)
        chinese_context = is_zh_context_char(prev_char) or is_zh_context_char(next_char)

        if char == '"' and chinese_context:
            result.append("“" if double_open else "”")
            double_open = not double_open
            continue

        if char == "'" and chinese_context:
            result.append("‘" if single_open else "’")
            single_open = not single_open
            continue

        result.append(char)

    return "".join(result)


def fix_enumeration_comma(text):
    """将并列词语间的逗号改为顿号。"""
    pattern = re.compile(
        rf"(({ENUMERATION_TOKEN_RE}，){2,}{ENUMERATION_TOKEN_RE})"
    )

    def replace_match(match):
        items = [item.strip() for item in match.group(1).split("，")]
        if len(items) < 3:
            return match.group(1)
        return "、".join(items)

    return pattern.sub(replace_match, text)


def add_spacing_between_chinese_and_ascii(text):
    """在中文与英文/数字之间补充空格。"""
    text = re.sub(r"([\u4e00-\u9fff])([A-Za-z0-9]+)", r"\1 \2", text)
    text = re.sub(r"([A-Za-z0-9]+)([\u4e00-\u9fff])", r"\1 \2", text)
    text = re.sub(r" {2,}", " ", text)
    return text


def normalize_plain_text(text):
    """对普通文本片段做规范化。"""
    text = convert_basic_punctuation(text)
    text = convert_quotes(text)
    text = fix_enumeration_comma(text)
    text = add_spacing_between_chinese_and_ascii(text)
    return text


def normalize_punctuation(text):
    """主函数：规范化文本。"""
    parts = []
    last_end = 0

    for match in PROTECTED_PATTERN.finditer(text):
        parts.append(normalize_plain_text(text[last_end:match.start()]))
        parts.append(match.group(0))
        last_end = match.end()

    parts.append(normalize_plain_text(text[last_end:]))
    return "".join(parts)


def main():
    """命令行入口。"""
    if len(sys.argv) < 2:
        print("用法: python normalize_punctuation.py <文件路径>")
        print("      python normalize_punctuation.py <文件路径> --in-place")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    in_place = "--in-place" in sys.argv

    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    result = normalize_punctuation(content)

    if in_place:
        file_path.write_text(result, encoding="utf-8")
        print(f"已更新文件: {file_path}")
    else:
        print(result)


if __name__ == "__main__":
    main()