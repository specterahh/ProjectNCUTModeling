import pulp
import pandas as pd
import matplotlib.pyplot as plt

# 数据准备
green_supply = [0, 0, 0, 0, 500, 1400, 1800, 2100, 2400, 2400, 2800, 3200, 3400, 3300, 3100, 2900, 2600, 2500, 2300, 1500, 1000, 0, 0, 0]
green_price = [0.6]*4 + [0.5]*2 + [0.4]*2 + [0.4]*3 + [0.3]*4 + [0.4, 0.5, 0.5, 0.5, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
trad_price = [0.5, 0.5, 0.5, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.3, 1.3, 1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 0.8, 0.6]

# 按小时定义任务需求（单位：kWh）
task_demand = {
    'high': [0]*6 + [0]*2 + [80*114/4]*4 + [80*54/2]*2 + [80*152/4]*4 + [80*50/4]*4 + [0]*2,
    'med': [50*40/6]*6 + [50*55/2]*2 + [50*72/4]*4 + [50*95/2]*2 + [50*80/4]*4 + [50*50/4]*4 + [50*20/2]*2,
    'low': [30*60/6]*6 + [30*70/2]*2 + [0]*4 + [0]*2 + [0]*4 + [30*40/4]*4 + [30*15/2]*2
}

# 创建模型
prob = pulp.LpProblem("Power_Scheduling", pulp.LpMinimize)
hours = range(24)

# 定义变量
E_high = pulp.LpVariable.dicts("E_high", hours, lowBound=0)
E_med = pulp.LpVariable.dicts("E_med", hours, lowBound=0)
E_low = pulp.LpVariable.dicts("E_low", hours, lowBound=0)
E_green = pulp.LpVariable.dicts("E_green", hours, lowBound=0)
E_traditional = pulp.LpVariable.dicts("E_traditional", hours, lowBound=0)

# 添加每小时任务需求约束
for h in hours:
    prob += E_high[h] == task_demand['high'][h]
    prob += E_med[h] == task_demand['med'][h]
    prob += E_low[h] == task_demand['low'][h]

# 添加电力分配约束
for h in hours:
    prob += E_green[h] <= green_supply[h]
    prob += E_high[h] + E_med[h] + E_low[h] == E_green[h] + E_traditional[h]

# 目标函数：最小化总成本
prob += pulp.lpSum([E_green[h] * green_price[h] + E_traditional[h] * trad_price[h] for h in hours])

# 求解
prob.solve()

# 提取结果
results = []
for h in hours:
    results.append({
        'hour': h,
        'E_high': E_high[h].value(),
        'E_med': E_med[h].value(),
        'E_low': E_low[h].value(),
        'E_green': E_green[h].value(),
        'E_traditional': E_traditional[h].value(),
        'total_demand': E_high[h].value() + E_med[h].value() + E_low[h].value(),
    })
df = pd.DataFrame(results)

# 绘图
plt.figure(figsize=(14, 6))
plt.bar(df['hour'], df['E_high'], label='High', color='red', alpha=0.7)
plt.bar(df['hour'], df['E_med'], bottom=df['E_high'], label='Medium', color='orange', alpha=0.7)
plt.bar(df['hour'], df['E_low'], bottom=df['E_high'] + df['E_med'], label='Low', color='green', alpha=0.7)
plt.xlabel('Hour of Day', fontsize=12)
plt.ylabel('Power Demand (kWh)', fontsize=12)
plt.title('Hourly Task Power Demand by Priority (All Hours Covered)', fontsize=14)
plt.xticks(range(24), [f'{h}:00' for h in range(24)], rotation=45)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('task_demand_fixed.png')
plt.close()

# 电力使用情况图
plt.figure(figsize=(14, 6))
plt.bar(df['hour'], df['E_green'], label='Green Energy', color='lightgreen', alpha=0.7)
plt.bar(df['hour'], df['E_traditional'], bottom=df['E_green'], label='Traditional Energy', color='gray', alpha=0.7)
plt.xlabel('Hour of Day', fontsize=12)
plt.ylabel('Power Usage (kWh)', fontsize=12)
plt.title('Hourly Power Usage (Green vs. Traditional)', fontsize=14)
plt.xticks(range(24), [f'{h}:00' for h in range(24)], rotation=45)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('power_usage_fixed.png')
plt.close()