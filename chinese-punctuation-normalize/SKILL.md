---
name: chinese-punctuation-normalize
description: Normalizes punctuation in documents to Chinese full-width punctuation. Use when normalizing punctuation, converting to Chinese punctuation, 规范化标点符号, 中文标点, standardizing punctuation in Chinese text, 修正标点, 标点转换, 全角标点, 中文文档标点处理, punctuation fix, punctuation correction, or when user mentions fixing punctuation in Chinese articles. Auto-triggers when user says "帮我改一下标点", "标点符号有问题", "转换成中文标点", "修正标点符号", "标点规范化", or similar punctuation-related requests in Chinese context.
---

# 中文标点符号规范化

将文档中的标点符号规范化为中文标点，并在中文与英文/数字之间补充必要空格；仅调整标点和中英混排间距，不改变文档结构和语义内容。

## 快速开始

使用自动化脚本进行标点转换：

```bash
# 先预览转换结果（输出到标准输出，不修改原文件）
python scripts/normalize_punctuation.py <文件路径>
```

确认预览结果无误后，再执行原地修改：

> ⚠️ `--in-place` 会直接覆盖原文件，不可逆。执行前请向用户确认，或确保文件已有备份。

```bash
python scripts/normalize_punctuation.py <文件路径> --in-place
```

脚本会自动：
- 保护代码块、行内代码、URL 等不需要修改的内容
- 转换中文文本中的标点符号
- 处理引号、并列词语等特殊情况
- 在中文与英文/数字之间补充空格

## 核心规则

中文语境下的标点符号统一使用中文全角标点；中文与英文/数字相邻时补充半角空格：

| 英文标点 | 中文标点 |
|----------|----------|
| 逗号 ,   | 逗号 ，  |
| 句号 .   | 句号 。  |
| 冒号 :   | 冒号 ：  |
| 问号 ?   | 问号 ？  |
| 感叹号 ! | 感叹号 ！|
| 分号 ;   | 分号 ；  |
| 引号 ""  | 引号 “”  |
| 括号 ()  | 括号 （）|

并列词语之间使用顿号 、 而非逗号。

中文与英文/数字直接相邻时补充空格，例如：

- `我是abcd小王子` -> `我是 abcd 小王子`
- `你是123` -> `你是 123`
- `AI助手` -> `AI 助手`

## 保持不变的情况

以下内容中的标点符号**不修改**：

1. **代码块**：\`\`\` 包裹的内容
2. **行内代码**：\` 包裹的内容
3. **公式和函数语法**：如 `f(x)`, `sum(a,b)` 等
4. **URL 链接**：如 `https://example.com/path?id=1`
5. **英文句子**：整句英文保持英文标点
6. **专有名词、品牌名称**：如 iPhone、macOS
7. **数字**：小数点、千分位保持英文（3.14、1,000）
8. **Markdown 格式标记**：表格的 \| 和 --- 等
9. **在 md 文件中表示链接的英文括号**：例如：[link](https://platform.openai.com/tokenizer) 中的括号保持英文括号不变。
10. **已经存在的合理空格**：不重复插入多个连续空格

## 特殊处理

1. **标题、小标题后的冒号**：使用中文冒号 ：
2. **列表项编号**：
   - 纯数字编号（1. 2. 3.）保持英文句点
   - 中文序号（第一、第二）后接中文顿号或冒号
3. **图片、截图占位符**：其中的中文使用中文标点
4. **中英混排间距**：仅在中文与英文/数字直接相邻时补空格，不主动重写句子结构或臆造逗号

## Gotchas

- **英文句子误转**：整句英文（如 "See the README for details."）不应转换，但混合句（"请参考 README, 了解详情"）需要转换逗号。判断依据是当前标点是否处于中文语境中。
- **Markdown 链接括号**：`[文字](url)` 中的 `(` `)` 是 Markdown 语法，**不得**转为全角括号，否则链接失效。
- **数字中的标点**：小数点（`3.14`）和千分位（`1,000`）保持英文，不要误转为句号和全角逗号。
- **冒号滥转**：时间格式（`10:30`）、代码中的键值对（`key: value`）、URL 中的冒号均不转换。
- **引号方向**：英文直引号 `"` 转为中文弯引号时，需判断左右方向（`"` vs `"`），脚本应按上下文自动配对，人工处理时容易搞错。
- **空格只补不猜**：`我是 abcd 小王子` 这类中英混排可以自动补空格，但 `小王子你是` 这类原文缺少逗号的地方，脚本不会猜测语义后擅自补标点。
- **`--in-place` 破坏性操作**：每次使用前必须先用无参数模式预览，确认无误再执行原地修改。

## 详细规则

对于复杂的标点转换场景（如混合中英文、引号嵌套、边界情况等），详见 [references/punctuation_rules.md](references/punctuation_rules.md)，包含：

- 完整的标点符号映射表和 Unicode 编码
- 各种特殊场景的详细处理规则
- 常见错误示例和正确写法
- 边界情况的完整说明

## 处理流程

1. 读取目标文档全文
2. 识别并跳过：代码块、行内代码、URL、英文句子
3. 对需修改区域按映射表逐项替换
4. 检查并列词语，将不当逗号改为顿号
5. 在中文与英文/数字之间补充必要空格
6. 验证文档结构和格式未被改变

## 示例

**修改前**：我是abcd小王子,你是123,他是kkk.这个"真开心'哈哈哈'"。
**修改后**：我是 abcd 小王子，你是 123，他是 kkk。这个“真开心‘哈哈哈’”。

更多示例和边界情况见 [references/punctuation_rules.md](references/punctuation_rules.md)。