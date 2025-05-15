import pandas as pd
import numpy as np

# 24小时时间点
hours = np.arange(24)

# 创建DataFrame
df = pd.DataFrame({
    'Time': [f'{h:02d}:00-{h+1:02d}:00' for h in hours],
    'Green_Power_MW': np.nan,
    'Green_Power_kWh': np.nan,
    'Green_Price': np.nan,
    'Conv_Price': np.nan
})

# 填入已知数据（11:00-12:00）
df.loc[11, 'Green_Power_MW'] = 3.2
df.loc[11, 'Green_Power_kWh'] = 3200
df.loc[11, 'Green_Price'] = 0.3
df.loc[11, 'Conv_Price'] = 1.3

# 保存
df.to_csv('partial_data.csv', index=False)
print("表2-表4已知数据已整理，保存为 partial_data.csv")
print(df.iloc[10:13])