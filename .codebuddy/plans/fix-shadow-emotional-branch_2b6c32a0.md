---
name: fix-shadow-emotional-branch
overview: 修复影子对话 emotional 分支中，追问轮次判断逻辑过于粗糙的问题——当用户回答敷衍（如"不知道呢"）时不应触发深度分析，而应继续追问。
todos:
  - id: add-evasive-detection
    content: 在 nodes.py 中新增敷衍回答检测函数并修改 prepare_node 轮次递增逻辑
    status: completed
---

## 问题描述

影子页面中，用户回答"不知道呢"后，AI 跳过了追问阶段，直接输出了【核心溯源】的深度分析。正确流程应该是继续追问或温和结束。

## 根因分析

- `prepare_node` 在收到任何 `supplements` 时无条件递增 `round_num`
- 当 `round_num >= MAX_ROUNDS(1)` 时直接触发深度分析
- 逻辑没有评估回答质量，即使"不知道呢"这样的敷衍回答也会触发分析

## 修复目标

增加敷衍/模糊回答检测，只有有效回答才触发深度分析：

- 敷衍回答（如"不知道"、"没"、"还行"等）→ 继续追问
- 有效回答（长度 ≥ 8 字且非敷衍词）→ 递增轮次 → 触发深度分析

## 技术方案

在 `shadow_server/app/nodes.py` 的 `prepare_node` 函数中：

1. 新增 `_is_evasive_answer(text: str) -> bool` 函数：

- 检测敷衍关键词：不知道、没、还行、还好、不知道呢、没什么、没什么事、都行、随便、都可以、没想好、再说吧等
- 检测极短回答：长度 < 8 字符
- 同时满足上述任一条件则判定为敷衍

2. 修改 `prepare_node` 中的轮次递增逻辑：

- 仅当 `has_supplements` 且 **非敷衍回答** 时才追加到 answers 并递增 round_num
- 敷衍回答追加到 `clarification_answers` 但**不递增 round_num**，保持追问状态

## 关键代码改动

```python
def _is_evasive_answer(text: str) -> bool:
    """检测敷衍/模糊回答"""
    text = (text or "").strip()
    if len(text) < 8:
        return True
    evasive_patterns = ["不知道", "没什", "还行", "还好", "没什么", "都行", "随便", "没想好", "再说"]
    return any(p in text for p in evasive_patterns)

# 在 prepare_node 中：
if has_supplements:
    answer = req.supplements.strip()
    if _is_evasive_answer(answer):
        # 敷衍回答：追加但不递增轮次，继续追问
        answers.append(answer)
        round_num = 0  # 保持追问状态
        logger.info("[prepare_node] 敷衍回答，继续追问")
    else:
        # 有效回答：追加并递增轮次
        answers.append(answer)
        round_num += 1
```