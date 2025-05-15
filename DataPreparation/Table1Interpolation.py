import pandas as pd
import numpy as np

# 24小时时间点
hours = np.arange(24)

# 已知时段（均匀分配到每小时）
data_dict = {}
# 00:00-06:00 -> 0-5
for h in range(0, 6):
    data_dict[h] = {'High_Priority': 0, 'Mid_Priority': 40, 'Low_Priority': 60}
# 06:00-08:00 -> 6-7
for h in range(6, 8):
    data_dict[h] = {'High_Priority': 0, 'Mid_Priority': 55, 'Low_Priority': 70}
# 08:00-12:00 -> 8-11
for h in range(8, 12):
    data_dict[h] = {'High_Priority': 114, 'Mid_Priority': 72, 'Low_Priority': 0}
# 12:00-14:00 -> 12-13
for h in range(12, 14):
    data_dict[h] = {'High_Priority': 54, 'Mid_Priority': 95, 'Low_Priority': 0}
# 14:00-18:00 -> 14-17
for h in range(14, 18):
    data_dict[h] = {'High_Priority': 152, 'Mid_Priority': 80, 'Low_Priority': 0}
# 18:00-22:00 -> 18-21
for h in range(18, 22):
    data_dict[h] = {'High_Priority': 50, 'Mid_Priority': 50, 'Low_Priority': 40}
# 22:00-24:00 -> 22-23
for h in range(22, 24):
    data_dict[h] = {'High_Priority': 0, 'Mid_Priority': 20, 'Low_Priority': 15}

# 创建DataFrame
df = pd.DataFrame(index=range(24))
for key in ['High_Priority', 'Mid_Priority', 'Low_Priority']:
    df[key] = np.nan
    for h in data_dict:
        df.loc[h, key] = data_dict[h][key]
    df[key] = df[key].interpolate(method='linear').round()  # 线性插值
    df[key] = df[key].ffill().bfill()  # 边界平滑

# 添加时间和功耗
df['Time'] = [f'{h:02d}:00-{h+1:02d}:00' for h in hours]
df['High_Power'] = 80
df['Mid_Power'] = 50
df['Low_Power'] = 30
df = df[['Time', 'High_Priority', 'Mid_Priority', 'Low_Priority', 'High_Power', 'Mid_Power', 'Low_Power']]

# 保存
df.to_csv('tasks.csv', index=False)
print("表1任务量已补全，保存为 tasks.csv")
print(df)