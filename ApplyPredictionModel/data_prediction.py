import pandas as pd
import numpy as np

# 设置随机种子
np.random.seed(42)
hours = np.arange(24)
n_sets = 2  # 生成2组数据

# 表1：任务量预测
def predict_tasks():
    # 初始数据：7个时段的任务量
    time_ranges = [(0, 6), (6, 8), (8, 12), (12, 14), (14, 18), (18, 22), (22, 24)]
    high_tasks = [0, 0, 114, 54, 152, 50, 0]
    mid_tasks = [40, 55, 72, 95, 80, 50, 20]
    low_tasks = [60, 70, 0, 0, 0, 40, 15]

    # 均匀分配到逐小时
    tasks_high = np.zeros(24)
    tasks_mid = np.zeros(24)
    tasks_low = np.zeros(24)
    for (start, end), h, m, l in zip(time_ranges, high_tasks, mid_tasks, low_tasks):
        duration = end - start
        for h_idx in range(start, end):
            tasks_high[h_idx] = h / duration
            tasks_mid[h_idx] = m / duration
            tasks_low[h_idx] = l / duration

    datasets = []
    for i in range(n_sets):
        # 添加正弦波动和随机扰动（调整幅度）
        high_adj = tasks_high + np.sin(np.pi * (hours - 6) / 12) * 1  # 波动幅度减小
        mid_adj = tasks_mid + np.sin(np.pi * (hours - 6) / 12) * 0.5
        low_adj = tasks_low + np.sin(np.pi * (hours - 6) / 12) * 0.5
        high_adj += np.random.normal(0, 1, 24)  # 扰动幅度减小
        mid_adj += np.random.normal(0, 1, 24)
        low_adj += np.random.normal(0, 1, 24)
        high_adj = np.clip(np.round(high_adj, 0), 0, None)
        mid_adj = np.clip(np.round(mid_adj, 0), 0, None)
        low_adj = np.clip(np.round(low_adj, 0), 0, None)

        # 保存数据
        df = pd.DataFrame({
            'Time': [f'{h:02d}:00-{h+1:02d}:00' for h in hours],
            'High_Tasks': high_adj,
            'Mid_Tasks': mid_adj,
            'Low_Tasks': low_adj
        })
        df.to_csv(f'tasks_pred_{i}.csv', index=False)
        datasets.append(df)
    return datasets

# 表2-4：电力数据预测
def predict_power():
    # 初始数据（从表2-4提取）
    green_power_base = [0, 0, 0, 0, 0.5, 1.4, 1.8, 2.1, 2.4, 2.4, 2.8, 3.2, 3.4, 3.3, 3.1, 2.9, 2.6, 2.5, 2.3, 1.5, 1.0, 0, 0, 0]
    green_price_base = [0.6, 0.6, 0.6, 0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
    conv_price_base = [0.5, 0.5, 0.5, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.3, 1.3, 1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 0.8, 0.6]

    datasets = []
    for i in range(n_sets):
        # 添加随机扰动（调整幅度）
        green_power = [max(0, round(x + np.random.normal(0, 0.2), 2)) for x in green_power_base]
        green_power[11] = 3.2  # 固定11:00数据
        green_power_kwh = [x * 1000 for x in green_power]

        green_price = [round(x + np.random.normal(0, 0.02), 2) for x in green_price_base]  # 扰动减小
        green_price[11] = 0.3  # 固定11:00数据
        green_price = [max(0.2, min(0.8, x)) for x in green_price]

        conv_price = [round(x + np.random.normal(0, 0.05), 2) for x in conv_price_base]  # 扰动减小
        conv_price[11] = 1.3  # 固定11:00数据
        conv_price = [max(0.4, min(1.5, x)) for x in conv_price]

        # 保存数据
        df = pd.DataFrame({
            'Time': [f'{h:02d}:00-{h+1:02d}:00' for h in hours],
            'Green_Power_MW': green_power,
            'Green_Power_kWh': green_power_kwh,
            'Green_Price': green_price,
            'Conv_Price': conv_price
        })
        df.to_csv(f'power_pred_{i}.csv', index=False)
        datasets.append(df)
    return datasets

# 运行预测
tasks_datasets = predict_tasks()
power_datasets = predict_power()

# 统计分析
print("=== tasks_pred_0.csv 统计分析 ===")
df_tasks = tasks_datasets[0]
print("高优先级任务：")
print(f"- 均值: {df_tasks['High_Tasks'].mean():.0f}")
print(f"- 范围: [{df_tasks['High_Tasks'].min():.0f}, {df_tasks['High_Tasks'].max():.0f}]")
print("中优先级任务：")
print(f"- 均值: {df_tasks['Mid_Tasks'].mean():.0f}")
print(f"- 范围: [{df_tasks['Mid_Tasks'].min():.0f}, {df_tasks['Mid_Tasks'].max():.0f}]")
print("低优先级任务：")
print(f"- 均值: {df_tasks['Low_Tasks'].mean():.0f}")
print(f"- 范围: [{df_tasks['Low_Tasks'].min():.0f}, {df_tasks['Low_Tasks'].max():.0f}]")
print("关键时段（08:00-12:00）：")
print(df_tasks.iloc[8:12])

print("\n=== power_pred_0.csv 统计分析 ===")
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