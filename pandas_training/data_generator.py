#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas闯关模式 - 数据生成器
生成模拟的电商数据供练习使用
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_data(output_dir='.'):
    """生成模拟数据并保存为CSV文件"""
    
    # 设置随机种子，保证结果可复现
    np.random.seed(42)
    random.seed(42)
    
    print("=" * 60)
    print("开始生成模拟数据...")
    print("=" * 60)
    
    # ==================== 1. 创建订单数据 ====================
    n_orders = 1000
    order_ids = [f'ORD{i:05d}' for i in range(1, n_orders + 1)]
    user_ids = [f'USER{random.randint(1, 200):03d}' for _ in range(n_orders)]
    product_ids = [f'PROD{random.randint(1, 50):02d}' for _ in range(n_orders)]
    
    # 生成日期（过去一年）
    start_date = datetime.now() - timedelta(days=365)
    order_dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(n_orders)]
    
    # 生成价格和数量
    prices = np.random.uniform(10, 1000, n_orders).round(2)
    quantities = np.random.randint(1, 10, n_orders)
    
    # 创建订单DataFrame
    orders_df = pd.DataFrame({
        'order_id': order_ids,
        'user_id': user_ids,
        'product_id': product_ids,
        'order_date': order_dates,
        'price': prices,
        'quantity': quantities,
        'status': np.random.choice(['completed', 'pending', 'cancelled', 'shipped'], 
                                  n_orders, p=[0.7, 0.1, 0.1, 0.1])
    })
    
    # 添加一些缺失值和异常值（用于数据清洗练习）
    orders_df.loc[50:55, 'price'] = np.nan  # 缺失价格
    orders_df.loc[100:102, 'quantity'] = -1  # 异常数量
    orders_df.loc[200, 'order_date'] = pd.NaT  # 缺失日期
    
    # ==================== 2. 创建用户数据 ====================
    n_users = 200
    user_data = pd.DataFrame({
        'user_id': [f'USER{i:03d}' for i in range(1, n_users + 1)],
        'username': [f'User_{i}' for i in range(1, n_users + 1)],
        'city': np.random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉'], n_users),
        'age': np.random.randint(18, 65, n_users),
        'gender': np.random.choice(['男', '女', '未知'], n_users, p=[0.48, 0.48, 0.04]),
        'register_date': [start_date + timedelta(days=random.randint(0, 300)) for _ in range(n_users)]
    })
    
    # ==================== 3. 创建产品数据 ====================
    n_products = 50
    product_data = pd.DataFrame({
        'product_id': [f'PROD{i:02d}' for i in range(1, n_products + 1)],
        'product_name': [f'Product_{i}' for i in range(1, n_products + 1)],
        'category': np.random.choice(['电子产品', '服装', '家居', '食品', '图书'], n_products),
        'cost': np.random.uniform(5, 500, n_products).round(2),
        'rating': np.random.uniform(3.0, 5.0, n_products).round(1)
    })
    
    # 保存为 CSV 文件
    orders_path = os.path.join(output_dir, 'orders.csv')
    users_path = os.path.join(output_dir, 'users.csv')
    products_path = os.path.join(output_dir, 'products.csv')
    
    orders_df.to_csv(orders_path, index=False, encoding='utf-8')
    user_data.to_csv(users_path, index=False, encoding='utf-8')
    product_data.to_csv(products_path, index=False, encoding='utf-8')
    
    print("✅ 数据生成完成！")
    print(f"📁 数据保存目录: {os.path.abspath(output_dir)}")
    print(f"📄 orders.csv: {orders_df.shape} (订单数据)")
    print(f"📄 users.csv: {user_data.shape} (用户数据)")
    print(f"📄 products.csv: {product_data.shape} (产品数据)")
    print()
    print("数据集说明:")
    print("- orders.csv: 订单记录，包含缺失值和异常值（用于数据清洗练习）")
    print("- users.csv: 用户信息，包含城市、年龄、性别等")
    print("- products.csv: 产品信息，包含成本、评分、类别等")
    print("- 数据量: 1000个订单，200个用户，50个产品")
    print("- 数据包含: 缺失值、异常值、时间序列、分类变量等")
    print("=" * 60)
    
    return orders_path, users_path, products_path

def check_data_files(output_dir='.'):
    """检查数据文件是否存在"""
    required_files = ['orders.csv', 'users.csv', 'products.csv']
    missing_files = []
    
    for file in required_files:
        path = os.path.join(output_dir, file)
        if not os.path.exists(path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少数据文件: {', '.join(missing_files)}")
        print("请运行: python data_generator.py")
        return False
    else:
        print("✅ 所有数据文件已就绪！")
        return True

if __name__ == "__main__":
    # 如果直接运行此脚本，生成数据
    generate_data()
    
    print("\n📝 接下来可以运行闯关游戏:")
    print("python pandas_challenge.py")