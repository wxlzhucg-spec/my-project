# -*- coding: utf-8 -*-
"""
影子 AI — 分类路由器准确率测试

用法:
  cd shadow_server
  python -m app.scripts.test_router

会依次向 router_node 发送测试用例，打印实际分类 vs 期望分类，最后汇总准确率。
"""
import asyncio
import sys
import os

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.common.models import UserRequest
from app.core.router import router_node, ALL_CATEGORIES


# ── 测试用例 ──────────────────────────────────────────────
# (question, emotion_keyword, expected_category)
TEST_CASES = [
    # ── GENERAL（普通聊天） ──
    ("今天天气真好啊", "平静", "GENERAL"),
    ("你好，给我讲个笑话", "开心", "GENERAL"),
    ("推荐一部好看的电影", "无聊", "GENERAL"),
    ("你觉得人生的意义是什么", "平静", "GENERAL"),
    ("帮我取个网名", "无聊", "GENERAL"),
    ("你最最喜欢的食物是什么", "好奇", "GENERAL"),

    # ── WEB（需要联网信息） ──
    ("最近有什么新闻", "好奇", "WEB"),
    ("2024年奥运会赛程安排", "好奇", "WEB"),
    ("今天A股大盘多少点", "焦虑", "WEB"),
    ("最近有什么新政策出台", "好奇", "WEB"),
    ("iPhone 16价格是多少", "好奇", "WEB"),
    ("最近流行什么歌", "无聊", "WEB"),

    # ── EMOTION_DEEP（情绪深度分析） ──
    ("工作压力太大了，每天加班到很晚，感觉自己快撑不住了", "焦虑", "EMOTION_DEEP"),
    ("最近和男朋友吵架了，不知道这段感情还能不能继续", "失落", "EMOTION_DEEP"),
    ("觉得自己什么都做不好，什么都比不上别人", "自卑", "EMOTION_DEEP"),
    ("妈妈生病了，但我又不能回去陪她，好无助", "无助", "EMOTION_DEEP"),
    ("被领导当众批评，觉得自己特别丢脸", "愤怒", "EMOTION_DEEP"),
    ("一直在纠结要不要辞职，但又怕找不到更好的", "迷茫", "EMOTION_DEEP"),
    ("感觉自己活得好累，好像没什么值得期待的事", "疲惫", "EMOTION_DEEP"),

    # ── 边界模糊（可能被误判） ──
    ("我最近心情不太好", "低落", "EMOTION_DEEP"),     # 短但情绪明确
    ("帮我看看最近的新闻，感觉世界好乱", "焦虑", "WEB"),  # 情绪+联网需求
    ("我总是拖延，怎么办", "焦虑", "EMOTION_DEEP"),    # 自助类，偏深度
    ("最近房价跌了吗", "好奇", "WEB"),                  # 联网+微弱情绪
]


async def run_test():
    results = []
    print("=" * 72)
    print("  影子 AI — 分类路由器准确率测试")
    print("=" * 72)
    print(f"  {'#':<3} {'期望':<14} {'实际':<14} {'结果':<6} {'问题（前30字）'}")
    print("-" * 72)

    for i, (question, emotion_keyword, expected) in enumerate(TEST_CASES, 1):
        req = UserRequest(
            question=question,
            emotion_keyword=emotion_keyword,
            mbti="INFP",
        )
        state = {"request": req}
        try:
            updates = await router_node(state)
            actual = updates.get("category", "UNKNOWN")
        except Exception as e:
            actual = f"ERROR:{e}"

        ok = "✅" if actual == expected else "❌"
        short_q = question[:30] + ("..." if len(question) > 30 else "")
        print(f"  {i:<3} {expected:<14} {actual:<14} {ok:<6} {short_q}")
        results.append(actual == expected)

    print("-" * 72)
    correct = sum(results)
    total = len(results)
    pct = correct / total * 100 if total else 0
    print(f"\n  准确率: {correct}/{total} ({pct:.1f}%)")

    # 打印误判详情
    wrong = [i for i, ok in enumerate(results) if not ok]
    if wrong:
        print(f"\n  ❌ 误判用例 ({len(wrong)} 个):")
        for idx in wrong:
            q, ek, exp = TEST_CASES[idx]
            print(f"     [{idx+1}] 期望={exp}  问题={q}")

    print()
    return correct, total


if __name__ == "__main__":
    asyncio.run(run_test())
