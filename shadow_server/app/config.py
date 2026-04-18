# -*- coding: utf-8 -*-
"""
影子 AI — 配置模块 (config.py)
"""
from __future__ import annotations
import os
from pathlib import Path

def _load_dotenv():
    candidates = [Path(".env"), Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env"]
    for p in candidates:
        if p.is_file():
            try:
                from dotenv import load_dotenv
                load_dotenv(p)
            except ImportError:
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        if "=" in line:
                            key, _, value = line.partition("=")
                            os.environ.setdefault(key.strip(), value.strip())
            break

_load_dotenv()

DEEPSEEK_API_KEY: str = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL: str = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL: str = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_MAX_TOKENS: int = int(os.environ.get("DEEPSEEK_MAX_TOKENS", "1024"))
DEEPSEEK_TEMPERATURE: float = float(os.environ.get("DEEPSEEK_TEMPERATURE", "0.7"))

HOST: str = os.environ.get("SHADOW_HOST", "127.0.0.1")
PORT: int = int(os.environ.get("SHADOW_PORT", "8000"))
DEBUG: bool = os.environ.get("SHADOW_DEBUG", "").lower() in ("1", "true", "yes")
CORS_ORIGINS: list[str] = os.environ.get("SHADOW_CORS_ORIGINS", "*").split(",")

CHAT_TIMEOUT_SECONDS: float = float(os.environ.get("SHADOW_CHAT_TIMEOUT_SECONDS", "180"))
EMOTION_PIPELINE_TIMEOUT_SECONDS: float = float(os.environ.get("SHADOW_EMOTION_TIMEOUT_SECONDS", "120"))
EMOTION_DETECT_TIMEOUT_SECONDS: float = float(os.environ.get("SHADOW_EMOTION_DETECT_TIMEOUT_SECONDS", "60"))

_ENABLE_TEST_ENV = os.environ.get("SHADOW_ENABLE_TEST_ROUTES", "").lower() in ("1", "true", "yes")
ENABLE_TEST_ROUTES: bool = DEBUG or _ENABLE_TEST_ENV

MYSQL_HOST: str = os.environ.get("MYSQL_HOST", "43.143.169.226")
MYSQL_PORT: int = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER: str = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD: str = os.environ.get("MYSQL_PASSWORD", "010824Wy?")
MYSQL_DATABASE: str = os.environ.get("MYSQL_DATABASE", "xintujie")
