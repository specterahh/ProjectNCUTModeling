import pandas as pd
import numpy as np

# 设置随机种子
np.random.seed(42)
hours = np.arange(24)
n_sets = 2  # 生成2组数据

# 加载原始数据
df_base = pd.read_csv('data_from_tables.csv')

# 提取基线数据
green_power_base = df_base['Green_Power_MW'].values
green_price_base = df_base['Green_Price'].values
conv_price_base = df_base['Conv_Price'].values

# 预测函数
def predict_power():
    datasets = []
    for i in range(n_sets):
        # 添加正弦波动和随机扰动
        green_power = green_power_base + np.sin(np.pi * (hours - 6) / 12) * 0.1  # 小幅波动
        green_power += np.random.normal(0, 0.1, 24)  # 随机扰动
        green_power[11] = 3.2  # 固定11:00数据
        green_power = np.clip(green_power, 0, None)  # 确保非负
        green_power_kwh = green_power * 1000  # 转换为kWh

        green_price = green_price_base + np.sin(np.pi * (hours - 6) / 12) * 0.02  # 小幅波动
        green_price += np.random.normal(0, 0.02, 24)  # 随机扰动
        green_price[11] = 0.3  # 固定11:00数据
        green_price = np.clip(green_price, 0.2, 0.8)  # 限制范围

        conv_price = conv_price_base + np.sin(np.pi * (hours - 6) / 12) * 0.05  # 小幅波动
        conv_price += np.random.normal(0, 0.05, 24)  # 随机扰动
        conv_price[11] = 1.3  # 固定11:00数据
        conv_price = np.clip(conv_price, 0.4, 1.5)  # 限制范围

        # 保留2位小数
        green_power = np.round(green_power, 2)
        green_power_kwh = np.round(green_power_kwh, 2)
        green_price = np.round(green_price, 2)
        conv_price = np.round(conv_price, 2)

        # 保存数据
        df = pd.DataFrame({
            'Time': df_base['Time'],
            'Green_Power_MW': green_power,
            'Green_Power_kWh': green_power_kwh,
            'Green_Price': green_price,
            'Conv_Price': conv_price
        })
        df.to_csv(f'power_pred_{i}.csv', index=False)
        datasets.append(df)
    return datasets

# 运行预测
power_datasets = predict_power()

# 统计分析
print("=== power_pred_0.csv 统计分析 ===")
df_power = power_datasets[0]
print("绿色电力（MW）：")
print(f"- 均值: {df_power['Green_Power_MW'].mean():.2f}")
print(f"- 范围: [{df_power['Green_Power_MW'].min():.2f}, {df_power['Green_Power_MW'].max():.2f}]")
print("绿色电价（元/kWh）：")
print(f"- 均值: {df_power['Green_Price'].mean():.2f}")
print(f"- 范围: [{df_power['Green_Price'].min():.2f}, {df_power['Green_Price'].max():.2f}]")
print("传统电价（元/kWh）：")
print(f"- 均值: {df_power['Conv_Price'].mean():.2f}")
print(f"- 范围: [{df_power['Conv_Price'].min():.2f}, {df_power['Conv_Price'].max():.2f}]")
print("关键时段（11:00-12:00）：")
print(df_power.iloc[11:12])