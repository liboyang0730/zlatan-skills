---
name: clean-markdown-redundant
description: Removes OCR image comment blocks and font color tags from Markdown articles while preserving original content and basic Markdown structure. Use when cleaning Markdown, removing OCR annotations, stripping font tags, deleting redundant content, or when user mentions 清理Markdown、清理冗余内容、格式优化、删除OCR注释、移除字体标签、清理格式、删除注释块、清理font标签、Markdown清理、格式清洗. Auto-triggers when user says "清理一下这篇文章", "删除OCR内容", "去掉font标签", "清理冗余格式", "这篇文章格式太乱了", "删除图片注释", "清理注释块", or similar cleaning requests for Markdown documents.
---

# 清理 Markdown 格式冗余内容

仅删除指定冗余内容，不修改任何其他文本、格式、标点或结构。

## 快速开始

使用自动化脚本清理冗余内容：

```bash
# 清理并输出到标准输出
python scripts/clean_redundant.py <文件路径>

# 原地修改文件
python scripts/clean_redundant.py <文件路径> --in-place
```

脚本会自动：
- 删除 OCR 图片注释块
- 删除字体颜色标签（保留标签内的文字）
- 清理多余的空行

## 需要删除的内容

### 1. OCR 图片注释块

删除所有以 `<!--` 开头、`-->` 结尾，且包含「这是一张图片，ocr内容为：」的完整注释块。匹配时忽略大小写和空格变体（如「OCR内容为：」「ocr 内容为：」。

**示例：**
- `<!-- 这是一张图片，ocr 内容为：测试文字 -->` → 整行/整段删除
- `<!--这是一张图片，ocr内容为：123-->` → 删除

**正则参考：** `<!--\s*这是一张图片[,，]?\s*ocr\s*内容为\s*[:：].*?-->`

### 2. 字体颜色标签

- **开头标签：** `<font style="color:rgb(...)">` 或 `<font style="color:rgba(...)">` 及含空格的变体
- **结尾标签：** `</font>`

**规则：** 仅移除标签本身，**保留标签内的文字内容**。

**正则参考：**
- 开头：`<font\s+style\s*=\s*["']color\s*:\s*rgba?\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)\s*;?\s*["']\s*>`
- 结尾：`</font>`

## 保持不变的内容

- Markdown 格式（标题、列表、代码块、链接、表格、行内代码等）
- 其他 HTML 标签（如 `<br>`、`<div>`）
- 正常的 HTML 注释（非 OCR 图片注释）
- 文本内容、标点符号、空格、换行

## 详细清理规则

对于复杂的清理场景（如嵌套标签、跨行标签、边界情况等），详见 [references/cleaning_patterns.md](references/cleaning_patterns.md)，包含：

- OCR 注释块的所有变体形式和匹配规则
- 字体颜色标签的所有变体形式
- 嵌套、跨行等边界情况的处理
- 详细的正则表达式说明
- 完整的清理效果示例

## 处理要求

1. 删除后确保无多余空行、无残留空格，前后文字自然衔接
2. 无残留标签片段（如半个 `<font>`）
3. 支持多行、嵌套的目标内容，彻底删除

## 示例

**输入：**
```markdown
# 标题

这是一段<font style="color:rgba(255,0,0,1);">红色文字</font>内容。

<!-- 这是一张图片，ocr内容为：图片中的文字说明 -->
```

**输出：**
```markdown
# 标题

这是一段红色文字内容。
```