#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas闯关模式 - 主程序
通过8个关卡全面掌握Pandas数据分析技能

使用方法：
1. 首先生成数据：python data_generator.py
2. 然后运行闯关：python pandas_challenge.py
"""

import pandas as pd
import numpy as np
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt

class PandasChallenge:
    """Pandas闯关游戏主类"""
    
    def __init__(self, data_dir='.'):
        self.data_dir = data_dir
        self.orders_path = os.path.join(data_dir, 'orders.csv')
        self.users_path = os.path.join(data_dir, 'users.csv')
        self.products_path = os.path.join(data_dir, 'products.csv')
        
        # 进度文件
        self.progress_file = os.path.join(data_dir, 'challenge_progress.json')
        self.progress = self._load_progress()
        
        # 数据
        self.orders_df = None
        self.users_df = None
        self.products_df = None
        self.combined_df = None
        
        # 关卡定义
        self.levels = self._define_levels()
        
    def _load_progress(self) -> Dict:
        """加载进度"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'current_level': 1,
            'completed_levels': [],
            'total_points': 0,
            'start_time': datetime.now().isoformat()
        }
    
    def _save_progress(self):
        """保存进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def _define_levels(self) -> List[Dict]:
        """定义关卡"""
        return [
            {
                'id': 1,
                'name': '数据加载与探索',
                'description': '学会加载数据并了解数据的基本情况',
                'tasks': [
                    '读取三个CSV文件：orders.csv, users.csv, products.csv',
                    '查看每个DataFrame的基本信息（shape, info, describe）',
                    '检查缺失值情况',
                    '检查重复值'
                ],
                'hint': '使用pd.read_csv()读取文件，使用.info()和.describe()查看信息',
                'points': 10,
                'validate': self._validate_level_1
            },
            {
                'id': 2,
                'name': '数据清洗',
                'description': '处理缺失值和异常值，优化数据类型',
                'tasks': [
                    '填充orders_df中缺失的price（用该产品类别的平均价格填充）',
                    '删除order_date为NaT的记录',
                    '将quantity为负的记录修正为1',
                    '将order_date和register_date转换为datetime类型'
                ],
                'hint': '使用fillna()处理缺失值，使用astype()转换类型',
                'points': 15,
                'validate': self._validate_level_2
            },
            {
                'id': 3,
                'name': '数据合并与关联',
                'description': '合并多个数据集并创建衍生字段',
                'tasks': [
                    '将orders_df与users_df合并（左连接）',
                    '再将结果与products_df合并（左连接）',
                    '计算总金额：total_amount = price * quantity',
                    '从order_date提取：年、月、日、星期几'
                ],
                'hint': '使用pd.merge()合并数据，使用.dt访问器提取日期信息',
                'points': 15,
                'validate': self._validate_level_3
            },
            {
                'id': 4,
                'name': '数据分组与聚合',
                'description': '使用groupby进行多维度统计分析',
                'tasks': [
                    '按城市分组，统计订单数量和总销售额',
                    '按产品类别分组，统计平均价格和平均评分',
                    '按用户性别分组，统计平均订单金额',
                    '使用agg同时计算：总和、均值、最大值、最小值、标准差'
                ],
                'hint': '使用groupby()和agg()进行聚合计算',
                'points': 20,
                'validate': self._validate_level_4
            },
            {
                'id': 5,
                'name': '时间序列分析',
                'description': '分析销售趋势和时间模式',
                'tasks': [
                    '将order_date设置为索引',
                    '按周重采样，统计周销售额',
                    '按月重采样，统计月度订单量',
                    '计算7日滚动平均销售额'
                ],
                'hint': '使用set_index()设置索引，使用resample()重采样，使用rolling()计算滚动平均',
                'points': 20,
                'validate': self._validate_level_5
            },
            {
                'id': 6,
                'name': '用户行为分析',
                'description': '分析用户消费行为和RFM模型',
                'tasks': [
                    '找出消费金额最高的TOP 10用户',
                    '统计每个用户的平均订单金额',
                    '计算每个用户的R（最近购买时间）、F（购买频率）、M（消费金额）值',
                    '将用户分为8个层级（RFM各分高低两组）'
                ],
                'hint': '使用groupby()聚合计算，使用qcut()进行分箱',
                'points': 20,
                'validate': self._validate_level_6
            },
            {
                'id': 7,
                'name': '数据可视化',
                'description': '使用图表展示分析结果',
                'tasks': [
                    '绘制每日销售额折线图',
                    '绘制各城市销售额柱状图',
                    '绘制产品类别占比饼图',
                    '绘制用户年龄分布直方图'
                ],
                'hint': '使用matplotlib或seaborn绘图，使用subplot创建多图',
                'points': 15,
                'validate': self._validate_level_7
            },
            {
                'id': 8,
                'name': '性能优化与高级技巧',
                'description': '优化代码性能和使用高级功能',
                'tasks': [
                    '将user_id转换为categorical类型，对比内存占用',
                    '使用query()优化查询性能',
                    '使用eval()进行表达式求值',
                    '使用向量化操作替代for循环'
                ],
                'hint': '使用.astype("category")转换类型，使用%timeit测试性能',
                'points': 15,
                'validate': self._validate_level_8
            }
        ]
    
    def load_data(self):
        """加载数据"""
        print("📂 正在加载数据...")
        
        # 检查数据文件是否存在
        for path in [self.orders_path, self.users_path, self.products_path]:
            if not os.path.exists(path):
                print(f"❌ 数据文件不存在: {path}")
                print("请先运行: python data_generator.py")
                sys.exit(1)
        
        # 读取数据
        self.orders_df = pd.read_csv(self.orders_path)
        self.users_df = pd.read_csv(self.users_path)
        self.products_df = pd.read_csv(self.products_path)
        
        print("✅ 数据加载完成！")
        print(f"  订单数据: {self.orders_df.shape}")
        print(f"  用户数据: {self.users_df.shape}")
        print(f"  产品数据: {self.products_df.shape}")
    
    def show_level(self, level_id: int):
        """显示关卡信息"""
        level = self.levels[level_id - 1]
        
        print("\n" + "="*60)
        print(f"🎯 第 {level_id} 关: {level['name']}")
        print("="*60)
        print(f"📝 描述: {level['description']}")
        print(f"🏆 积分: {level['points']} 分")
        print("\n📋 任务列表:")
        for i, task in enumerate(level['tasks'], 1):
            print(f"  {i}. {task}")
        
        print(f"\n💡 提示: {level['hint']}")
        print("\n🔄 开始编写代码吧！完成后输入 'check' 检查结果。")
        print("   输入 'hint' 查看详细提示，输入 'skip' 跳过此关。")
        print("="*60)
    
    def _validate_level_1(self) -> bool:
        """验证第一关"""
        print("\n🔍 正在验证第1关...")
        
        # 检查数据是否加载
        if self.orders_df is None or self.users_df is None or self.products_df is None:
            print("❌ 请先加载数据！")
            return False
        
        # 检查是否读取了三个文件
        expected_columns = {
            'orders.csv': ['order_id', 'user_id', 'product_id', 'order_date', 'price', 'quantity', 'status'],
            'users.csv': ['user_id', 'username', 'city', 'age', 'gender', 'register_date'],
            'products.csv': ['product_id', 'product_name', 'category', 'cost', 'rating']
        }
        
        all_passed = True
        
        # 检查orders_df
        missing_cols = set(expected_columns['orders.csv']) - set(self.orders_df.columns)
        if missing_cols:
            print(f"❌ orders.csv缺少列: {missing_cols}")
            all_passed = False
        else:
            print("✅ orders.csv列名正确")
        
        # 检查形状
        if self.orders_df.shape[0] == 1000:
            print("✅ orders.csv行数正确 (1000行)")
        else:
            print(f"❌ orders.csv行数不正确: {self.orders_df.shape[0]}行")
            all_passed = False
        
        # 检查info和describe是否被调用（通过检查用户是否了解数据）
        print("\n📊 数据概览:")
        print("订单数据形状:", self.orders_df.shape)
        print("订单数据列名:", list(self.orders_df.columns))
        print("缺失值数量:", self.orders_df.isnull().sum().sum())
        print("重复行数量:", self.orders_df.duplicated().sum())
        
        if all_passed:
            print("\n🎉 第1关验证通过！")
            return True
        else:
            print("\n❌ 第1关验证失败，请检查代码。")
            return False
    
    def _validate_level_2(self) -> bool:
        """验证第二关"""
        print("\n🔍 正在验证第2关...")
        
        # 检查数据清洗
        if self.orders_df is None:
            print("❌ 请先加载数据！")
            return False
        
        # 检查缺失值处理
        missing_price = self.orders_df['price'].isnull().sum()
        missing_date = self.orders_df['order_date'].isnull().sum()
        negative_quantity = (self.orders_df['quantity'] < 0).sum()
        
        print(f"📊 数据清洗检查:")
        print(f"  - 缺失价格数量: {missing_price}")
        print(f"  - 缺失日期数量: {missing_date}")
        print(f"  - 负数量记录数: {negative_quantity}")
        
        # 检查数据类型
        date_type = str(self.orders_df['order_date'].dtype)
        if 'datetime' in date_type:
            print(f"  - order_date类型: {date_type} ✅")
        else:
            print(f"  - order_date类型: {date_type} ❌ (应为datetime)")
        
        if missing_price == 0 and missing_date == 0 and negative_quantity == 0 and 'datetime' in date_type:
            print("\n🎉 第2关验证通过！")
            return True
        else:
            print("\n❌ 第2关验证失败，请完成所有清洗任务。")
            return False
    
    def _validate_level_3(self) -> bool:
        """验证第三关"""
        print("\n🔍 正在验证第3关...")
        
        # 检查数据合并
        if self.combined_df is None:
            print("❌ 请先合并数据！")
            return False
        
        # 检查合并后的列
        expected_cols = {'order_id', 'user_id', 'product_id', 'order_date', 'price', 
                        'quantity', 'status', 'username', 'city', 'age', 'gender', 
                        'register_date', 'product_name', 'category', 'cost', 'rating'}
        
        actual_cols = set(self.combined_df.columns)
        missing_cols = expected_cols - actual_cols
        
        if missing_cols:
            print(f"❌ 合并后缺少列: {missing_cols}")
            return False
        
        # 检查衍生字段
        has_total_amount = 'total_amount' in self.combined_df.columns
        has_year = 'year' in self.combined_df.columns or any('year' in col.lower() for col in self.combined_df.columns)
        has_month = 'month' in self.combined_df.columns or any('month' in col.lower() for col in self.combined_df.columns)
        
        print(f"📊 数据合并检查:")
        print(f"  - 合并后形状: {self.combined_df.shape}")
        print(f"  - 是否有total_amount字段: {'✅' if has_total_amount else '❌'}")
        print(f"  - 是否有年份字段: {'✅' if has_year else '❌'}")
        print(f"  - 是否有月份字段: {'✅' if has_month else '❌'}")
        
        if has_total_amount and has_year and has_month:
            print("\n🎉 第3关验证通过！")
            return True
        else:
            print("\n❌ 第3关验证失败，请完成所有合并和衍生字段任务。")
            return False
    
    def _validate_level_4(self) -> bool:
        """验证第四关"""
        print("\n🔍 正在验证第4关...")
        
        # 检查分组聚合结果
        if self.combined_df is None:
            print("❌ 请先完成数据合并！")
            return False
        
        print("📊 分组聚合检查:")
        print("✅ 如果能看到按城市、产品类别、性别的分组统计结果，则任务完成。")
        print("   请确保你使用了groupby()和agg()函数。")
        
        # 这里不做过严格检查，只要用户尝试了即可
        return True
    
    def _validate_level_5(self) -> bool:
        """验证第五关"""
        print("\n🔍 正在验证第5关...")
        
        # 检查时间序列分析
        if self.combined_df is None:
            print("❌ 请先完成数据合并！")
            return False
        
        print("📊 时间序列检查:")
        print("✅ 如果能看到按周、按月重采样的结果，以及7日滚动平均，则任务完成。")
        
        return True
    
    def _validate_level_6(self) -> bool:
        """验证第六关"""
        print("\n🔍 正在验证第6关...")
        
        # 检查RFM分析
        print("📊 RFM分析检查:")
        print("✅ 如果能看到TOP 10用户、RFM值和用户分层结果，则任务完成。")
        
        return True
    
    def _validate_level_7(self) -> bool:
        """验证第七关"""
        print("\n🔍 正在验证第7关...")
        
        # 检查可视化
        print("📊 可视化检查:")
        print("✅ 如果能看到折线图、柱状图、饼图、直方图等图表，则任务完成。")
        print("   图表已保存到当前目录。")
        
        return True
    
    def _validate_level_8(self) -> bool:
        """验证第八关"""
        print("\n🔍 正在验证第8关...")
        
        # 检查性能优化
        print("📊 性能优化检查:")
        print("✅ 如果能看到内存使用对比、查询优化结果，则任务完成。")
        
        return True
    
    def run(self):
        """运行闯关游戏"""
        print("="*60)
        print("🎮 Pandas数据分析闯关模式")
        print("="*60)
        print("通过8个关卡，全面掌握Pandas数据分析技能！")
        print(f"当前进度: 第{self.progress['current_level']}关")
        print(f"已获得积分: {self.progress['total_points']}")
        print("="*60)
        
        # 加载数据
        self.load_data()
        
        # 主循环
        while self.progress['current_level'] <= len(self.levels):
            level_id = self.progress['current_level']
            level = self.levels[level_id - 1]
            
            # 显示关卡信息
            self.show_level(level_id)
            
            # 获取用户输入
            while True:
                command = input("\n请输入命令 (check/hint/skip/quit): ").strip().lower()
                
                if command == 'check':
                    # 验证关卡
                    if level['validate']():
                        # 关卡通过
                        self.progress['completed_levels'].append(level_id)
                        self.progress['total_points'] += level['points']
                        self.progress['current_level'] += 1
                        self._save_progress()
                        
                        print(f"\n🎉 恭喜通过第{level_id}关！获得{level['points']}积分")
                        print(f"总积分: {self.progress['total_points']}")
                        break
                    else:
                        print("❌ 验证失败，请修改代码后重试。")
                
                elif command == 'hint':
                    print(f"\n💡 详细提示:")
                    print(f"{level['hint']}")
                    print("\n示例代码:")
                    self._show_example(level_id)
                
                elif command == 'skip':
                    confirm = input("确定要跳过此关吗？(y/n): ").strip().lower()
                    if confirm == 'y':
                        print(f"⏭️ 跳过第{level_id}关")
                        self.progress['current_level'] += 1
                        self._save_progress()
                        break
                
                elif command == 'quit':
                    print("👋 退出闯关游戏")
                    self._save_progress()
                    sys.exit(0)
                
                else:
                    print("❓ 未知命令，请输入 check/hint/skip/quit")
            
            # 检查是否完成所有关卡
            if self.progress['current_level'] > len(self.levels):
                print("\n" + "="*60)
                print("🏆 恭喜完成所有关卡！")
                print("="*60)
                print(f"总积分: {self.progress['total_points']}")
                print("🎉 你已经掌握了Pandas数据分析的核心技能！")
                print("\n接下来可以尝试:")
                print("1. 分析真实数据集（如泰坦尼克号、房价预测）")
                print("2. 学习更高级的机器学习库（如scikit-learn）")
                print("3. 参与Kaggle竞赛项目")
                print("="*60)
                break
        
        # 保存最终进度
        self._save_progress()
    
    def _show_example(self, level_id: int):
        """显示示例代码"""
        examples = {
            1: '''
# 示例代码 - 第1关
import pandas as pd

# 读取数据
orders_df = pd.read_csv('orders.csv')
users_df = pd.read_csv('users.csv')
products_df = pd.read_csv('products.csv')

# 查看基本信息
print("订单数据形状:", orders_df.shape)
print("订单数据信息:")
print(orders_df.info())
print(orders_df.describe())

# 检查缺失值
print("缺失值统计:")
print(orders_df.isnull().sum())

# 检查重复值
print("重复行数量:", orders_df.duplicated().sum())
            ''',
            2: '''
# 示例代码 - 第2关
# 填充缺失价格（用类别平均价格填充）
# 首先需要合并数据获取产品类别
combined = pd.merge(orders_df, products_df, on='product_id', how='left')
category_avg_price = combined.groupby('category')['price'].mean()

# 填充缺失值
orders_df['price'] = orders_df['price'].fillna(
    orders_df['product_id'].map(products_df.set_index('product_id')['category'])
    .map(category_avg_price)
)

# 删除缺失日期的记录
orders_df = orders_df.dropna(subset=['order_date'])

# 修正负数量
orders_df.loc[orders_df['quantity'] < 0, 'quantity'] = 1

# 转换日期类型
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
users_df['register_date'] = pd.to_datetime(users_df['register_date'])
            ''',
            3: '''
# 示例代码 - 第3关
# 合并数据
merged_df = pd.merge(orders_df, users_df, on='user_id', how='left')
combined_df = pd.merge(merged_df, products_df, on='product_id', how='left')

# 计算总金额
combined_df['total_amount'] = combined_df['price'] * combined_df['quantity']

# 提取日期信息
combined_df['order_year'] = combined_df['order_date'].dt.year
combined_df['order_month'] = combined_df['order_date'].dt.month
combined_df['order_day'] = combined_df['order_date'].dt.day
combined_df['order_weekday'] = combined_df['order_date'].dt.weekday

# 保存合并后的数据供后续使用（重要！）
self.combined_df = combined_df
            ''',
            4: '''
# 示例代码 - 第4关
# 按城市分组统计
city_stats = self.combined_df.groupby('city').agg(
    order_count=('order_id', 'count'),
    total_sales=('total_amount', 'sum'),
    avg_order_value=('total_amount', 'mean')
).round(2)

# 按产品类别分组统计
category_stats = self.combined_df.groupby('category').agg(
    avg_price=('price', 'mean'),
    avg_rating=('rating', 'mean'),
    total_quantity=('quantity', 'sum')
).round(2)

# 按性别分组统计
gender_stats = self.combined_df.groupby('gender').agg(
    avg_order_amount=('total_amount', 'mean'),
    order_count=('order_id', 'count')
).round(2)

# 使用agg计算多个统计量
detailed_stats = self.combined_df.groupby('city').agg({
    'total_amount': ['sum', 'mean', 'max', 'min', 'std'],
    'quantity': ['sum', 'mean']
}).round(2)
            ''',
            5: '''
# 示例代码 - 第5关
# 设置时间索引
time_df = self.combined_df.set_index('order_date')

# 按周重采样，统计周销售额
weekly_sales = time_df['total_amount'].resample('W').sum()

# 按月重采样，统计月度订单量
monthly_orders = time_df['order_id'].resample('M').count()

# 计算7日滚动平均销售额
rolling_avg = time_df['total_amount'].rolling('7D').mean()

print("周销售额:")
print(weekly_sales.head())
print("\\n月度订单量:")
print(monthly_orders.head())
print("\\n7日滚动平均销售额:")
print(rolling_avg.head())
            ''',
            6: '''
# 示例代码 - 第6关
# 找出消费金额最高的TOP 10用户
top_users = self.combined_df.groupby('user_id')['total_amount'].sum().sort_values(ascending=False).head(10)

# 统计每个用户的平均订单金额
avg_order_per_user = self.combined_df.groupby('user_id')['total_amount'].mean()

# 计算RFM值
rfm_df = self.combined_df.groupby('user_id').agg({
    'order_date': lambda x: (self.combined_df['order_date'].max() - x.max()).days,  # R (最近购买时间)
    'order_id': 'count',  # F (购买频率)
    'total_amount': 'sum'  # M (消费金额)
}).rename(columns={'order_date': 'R', 'order_id': 'F', 'total_amount': 'M'})

# 将RFM值分箱（高低两组）
rfm_df['R_rank'] = pd.qcut(rfm_df['R'], 2, labels=['High', 'Low'])
rfm_df['F_rank'] = pd.qcut(rfm_df['F'], 2, labels=['Low', 'High'])  # 频率越高越好
rfm_df['M_rank'] = pd.qcut(rfm_df['M'], 2, labels=['Low', 'High'])  # 金额越高越好

print("TOP 10用户:")
print(top_users)
print("\\nRFM分析:")
print(rfm_df.head())
            ''',
            7: '''
# 示例代码 - 第7关
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体（如果可用）
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 1. 每日销售额折线图
daily_sales = self.combined_df.set_index('order_date')['total_amount'].resample('D').sum()
plt.figure(figsize=(12, 6))
plt.plot(daily_sales.index, daily_sales.values)
plt.title('每日销售额趋势')
plt.xlabel('日期')
plt.ylabel('销售额')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('daily_sales.png')
plt.close()

# 2. 各城市销售额柱状图
city_sales = self.combined_df.groupby('city')['total_amount'].sum().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
city_sales.plot(kind='bar')
plt.title('各城市销售额对比')
plt.xlabel('城市')
plt.ylabel('销售额')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('city_sales.png')
plt.close()

print("✅ 图表已保存为 daily_sales.png 和 city_sales.png")
            ''',
            8: '''
# 示例代码 - 第8关
# 1. 将user_id转换为categorical类型，对比内存占用
print("转换前内存使用:")
print(self.combined_df.memory_usage(deep=True).sum() / 1024 ** 2, "MB")

self.combined_df['user_id'] = self.combined_df['user_id'].astype('category')

print("转换后内存使用:")
print(self.combined_df.memory_usage(deep=True).sum() / 1024 ** 2, "MB")

# 2. 使用query()优化查询性能
# 传统方法
filtered_traditional = self.combined_df[(self.combined_df['city'] == '北京') & (self.combined_df['total_amount'] > 1000)]

# 使用query()
filtered_query = self.combined_df.query("city == '北京' and total_amount > 1000")

print(f"传统方法结果: {len(filtered_traditional)} 行")
print(f"query方法结果: {len(filtered_query)} 行")

# 3. 使用eval()进行表达式求值
# 计算新的衍生字段
self.combined_df['profit'] = self.combined_df.eval('price - cost')

# 4. 向量化操作 vs for循环
# 向量化操作（推荐）
self.combined_df['price_with_tax'] = self.combined_df['price'] * 1.13

print("✅ 性能优化示例完成！")
            '''
        }
        
        if level_id in examples:
            print(examples[level_id])
        else:
            print("暂无示例代码，请参考提示自行实现。")

def main():
    """主函数"""
    # 检查是否安装了pandas
    try:
        import pandas as pd
    except ImportError:
        print("❌ 请先安装pandas: pip install pandas")
        sys.exit(1)
    
    # 创建闯关游戏实例
    challenge = PandasChallenge()
    
    # 运行游戏
    try:
        challenge.run()
    except KeyboardInterrupt:
        print("\n👋 游戏中断，进度已保存。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 导入datetime
    from datetime import datetime
    main()