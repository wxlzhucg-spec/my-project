# -*- coding: utf-8 -*-
"""
影子 AI — 分类路由器交互测试

用法:
  cd shadow_server
  python3 -m app.scripts.test_router_interactive

支持两种模式:
  1. 批量测试: 自动跑预设用例，算准确率
  2. 交互测试: 手动输入问题，实时看分类结果
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.common.models import UserRequest
from app.core.router import router_node


# ── 预设用例 ──────────────────────────────────────────────
TEST_CASES = [
    # (question, emotion_keyword, expected_category)
    # GENERAL
    ("今天天气真好啊", "平静", "GENERAL"),
    ("你好，给我讲个笑话", "开心", "GENERAL"),
    ("推荐一部好看的电影", "无聊", "GENERAL"),
    ("你觉得人生的意义是什么", "平静", "GENERAL"),
    ("帮我取个网名", "无聊", "GENERAL"),
    ("你最最喜欢的食物是什么", "好奇", "GENERAL"),

    # WEB
    ("最近有什么新闻", "好奇", "WEB"),
    ("2024年奥运会赛程安排", "好奇", "WEB"),
    ("今天A股大盘多少点", "焦虑", "WEB"),
    ("最近有什么新政策出台", "好奇", "WEB"),
    ("iPhone 16价格是多少", "好奇", "WEB"),
    ("最近流行什么歌", "无聊", "WEB"),

    # EMOTION_DEEP
    ("工作压力太大了，每天加班到很晚，感觉自己快撑不住了", "焦虑", "EMOTION_DEEP"),
    ("最近和男朋友吵架了，不知道这段感情还能不能继续", "失落", "EMOTION_DEEP"),
    ("觉得自己什么都做不好，什么都比不上别人", "自卑", "EMOTION_DEEP"),
    ("妈妈生病了，但我又不能回去陪她，好无助", "无助", "EMOTION_DEEP"),
    ("被领导当众批评，觉得自己特别丢脸", "愤怒", "EMOTION_DEEP"),
    ("一直在纠结要不要辞职，但又怕找不到更好的", "迷茫", "EMOTION_DEEP"),
    ("感觉自己活得好累，好像没什么值得期待的事", "疲惫", "EMOTION_DEEP"),

    # 边界模糊
    ("我最近心情不太好", "低落", "EMOTION_DEEP"),
    ("帮我看看最近的新闻，感觉世界好乱", "焦虑", "WEB"),
    ("我总是拖延，怎么办", "焦虑", "EMOTION_DEEP"),
    ("最近房价跌了吗", "好奇", "WEB"),
]

CATEGORY_CN = {
    "GENERAL": "普通聊天",
    "WEB": "联网问答",
    "EMOTION_DEEP": "情绪深度",
}


def _color(text, code):
    return f"\033[{code}m{text}\033[0m"


def green(t):  return _color(t, "32")
def red(t):    return _color(t, "31")
def yellow(t): return _color(t, "33")
def cyan(t):   return _color(t, "36")
def bold(t):   return _color(t, "1")
def dim(t):    return _color(t, "2")


async def classify(question: str, emotion_keyword: str, mbti: str = "INFP") -> dict:
    """调用 router_node 分类，返回结果和耗时。"""
    req = UserRequest(question=question, emotion_keyword=emotion_keyword, mbti=mbti)
    state = {"request": req}
    t0 = time.time()
    updates = await router_node(state)
    elapsed = time.time() - t0
    return {
        "category": updates.get("category", "UNKNOWN"),
        "web_search": updates.get("web_search", False),
        "elapsed": elapsed,
        "updates": updates,
    }


# ══════════════════════════════════════════════════════════
#  批量测试
# ══════════════════════════════════════════════════════════

async def batch_test():
    print()
    print(bold("═" * 68))
    print(bold("  影子 AI — 分类路由器批量测试"))
    print(bold("═" * 68))
    print(f"  {'#':<3} {'期望':<14} {'实际':<14} {'结果':<4} {'耗时':<7} {'问题'}")
    print("  " + "─" * 62)

    results = []
    for i, (question, emotion, expected) in enumerate(TEST_CASES, 1):
        result = await classify(question, emotion)
        actual = result["category"]
        ok = actual == expected
        mark = green("✅") if ok else red("❌")
        short_q = question[:28] + ("…" if len(question) > 28 else "")
        print(f"  {i:<3} {expected:<14} {actual:<14} {mark:<4} {result['elapsed']:.2f}s  {short_q}")
        results.append(ok)

    print("  " + "─" * 62)
    correct = sum(results)
    total = len(results)
    pct = correct / total * 100 if total else 0
    print(f"\n  准确率: {bold(f'{correct}/{total}')} ({pct:.1f}%)")

    wrong = [i for i, ok in enumerate(results) if not ok]
    if wrong:
        print(f"\n  {red('误判用例:')}")
        for idx in wrong:
            q, ek, exp = TEST_CASES[idx]
            print(f"    [{idx+1}] 期望={exp}  问题={q}")

    # 分类统计
    cat_count = {"GENERAL": 0, "WEB": 0, "EMOTION_DEEP": 0}
    for i, (q, e, exp) in enumerate(TEST_CASES):
        if results[i]:
            cat_count[exp] = cat_count.get(exp, 0) + 1
    print(f"\n  各分类: ", end="")
    for cat, cnt in cat_count.items():
        cn = CATEGORY_CN.get(cat, cat)
        print(f"{cn} {cnt}/{sum(1 for _,_,e in TEST_CASES if e==cat)}  ", end="")
    print()


# ══════════════════════════════════════════════════════════
#  交互测试
# ══════════════════════════════════════════════════════════

async def interactive_test():
    print()
    print(bold("═" * 68))
    print(bold("  影子 AI — 分类路由器交互测试"))
    print(bold("═" * 68))
    print()
    print("  输入问题进行分类测试，可用命令:")
    print(f"    {cyan('q')}        退出")
    print(f"    {cyan('b')}        切换到批量测试")
    print(f"    {cyan('mbti XX')}  设置 MBTI（默认 INFP）")
    print(f"    {cyan('emotion X')} 设置情绪关键词（默认 焦虑）")
    print()

    mbti = "INFP"
    default_emotion = "焦虑"
    history = []

    while True:
        try:
            question = input(f"  {bold('输入问题>')} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见！")
            break

        if not question:
            continue
        if question.lower() == "q":
            print("  再见！")
            break
        if question.lower() == "b":
            await batch_test()
            continue
        if question.lower().startswith("mbti "):
            mbti = question[5:].strip().upper()
            print(f"  MBTI 已设置为: {bold(mbti)}")
            continue
        if question.lower().startswith("emotion "):
            default_emotion = question[8:].strip()
            print(f"  情绪关键词已设置为: {bold(default_emotion)}")
            continue

        # 输入情绪关键词
        emotion_input = input(f"  {bold('情绪关键词>')} [{default_emotion}] ").strip()
        emotion = emotion_input if emotion_input else default_emotion

        # 调用分类
        print(f"  {dim('分类中…')}")
        result = await classify(question, emotion, mbti)
        cat = result["category"]
        cn = CATEGORY_CN.get(cat, cat)

        # 输出结果
        print()
        print(f"  ┌──────────────────────────────────────┐")
        print(f"  │  分类结果:  {bold(_color(cat, '36'))}（{cn}）")
        print(f"  │  是否联网:  {'是' if result['web_search'] else '否'}")
        print(f"  │  耗    时:  {result['elapsed']:.2f}s")
        print(f"  └──────────────────────────────────────┘")
        print()

        history.append({"question": question, "emotion": emotion, "category": cat, "elapsed": result["elapsed"]})

    # 打印历史
    if history:
        print()
        print(bold("  本次测试历史:"))
        print(f"  {'#':<3} {'分类':<14} {'耗时':<7} {'问题'}")
        print("  " + "─" * 50)
        for i, h in enumerate(history, 1):
            cn = CATEGORY_CN.get(h["category"], h["category"])
            print(f"  {i:<3} {h['category']:<14} {h['elapsed']:.2f}s  {h['question'][:30]}")

        cat_count = {}
        for h in history:
            cat_count[h["category"]] = cat_count.get(h["category"], 0) + 1
        print(f"\n  统计: ", end="")
        for cat, cnt in cat_count.items():
            print(f"{CATEGORY_CN.get(cat, cat)}={cnt}  ", end="")
        print(f"共{len(history)}条")


# ══════════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════════

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        await batch_test()
    else:
        await interactive_test()


if __name__ == "__main__":
    asyncio.run(main())
