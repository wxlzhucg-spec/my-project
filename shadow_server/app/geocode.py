# -*- coding: utf-8 -*-
"""
影子 AI — 地理编码模块 (geocode.py)

【职责】
  将中文地址转换为经纬度坐标，供占星计算使用。
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# 主要城市经纬度缓存
_CITY_COORDS = {
    "上海": (31.23, 121.47),
    "上海市": (31.23, 121.47),
    "北京": (39.90, 116.40),
    "北京市": (39.90, 116.40),
    "广州": (23.13, 113.26),
    "广州市": (23.13, 113.26),
    "深圳": (22.54, 114.06),
    "深圳市": (22.54, 114.06),
    "成都": (30.57, 104.07),
    "成都市": (30.57, 104.07),
    "杭州": (30.27, 120.15),
    "杭州市": (30.27, 120.15),
    "南京": (32.06, 118.80),
    "南京市": (32.06, 118.80),
    "武汉": (30.59, 114.31),
    "武汉市": (30.59, 114.31),
    "重庆": (29.56, 106.55),
    "重庆市": (29.56, 106.55),
    "西安": (34.26, 108.94),
    "西安市": (34.26, 108.94),
    "天津": (39.13, 117.20),
    "天津市": (39.13, 117.20),
    "苏州": (31.30, 120.62),
    "苏州市": (31.30, 120.62),
    "长沙": (28.23, 112.94),
    "长沙市": (28.23, 112.94),
}


def geocode(address: str) -> tuple[float, float]:
    """
    将中文地址转换为 (纬度, 经度) 元组。

    优先使用本地缓存，未命中则尝试 geopy。
    """
    # 尝试本地缓存
    for city, coords in _CITY_COORDS.items():
        if city in address:
            logger.info("地理编码命中缓存: %s → %s", address, coords)
            return coords

    # 尝试 geopy
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="shadow-ai", timeout=10)
        location = geolocator.geocode(address)
        if location:
            coords = (location.latitude, location.longitude)
            logger.info("地理编码成功: %s → %s", address, coords)
            return coords
    except Exception as exc:
        logger.warning("geopy 地理编码失败: %s", exc)

    # 默认：上海
    logger.warning("地理编码未命中，使用默认坐标（上海）: %s", address)
    return (31.23, 121.47)
