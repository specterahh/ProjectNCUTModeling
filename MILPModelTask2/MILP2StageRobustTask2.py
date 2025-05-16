import pulp
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# ======================
# 字体设置（解决中文显示问题）
# ======================
try:
    # 尝试使用Windows自带字体
    mpl.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
    mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    print("已设置SimHei字体")
except:
    # 回退到系统默认字体
    mpl.rcParams['font.sans-serif'] = [
        'Arial Unicode MS'] if 'Arial Unicode MS' in mpl.font_manager.findSystemFonts() else ['DejaVu Sans']
    print(f"使用回退字体: {mpl.rcParams['font.sans-serif']}")

# ======================
# 数据准备（完整24小时数据）
# ======================
hours = list(range(24))  # 24小时时段

# 电力参数（确保所有列表都有24个元素）
green_supply = [0, 0, 0, 0, 500, 1400, 1800, 2100, 2400, 2400, 2800, 3200,
                3400, 3300, 3100, 2900, 2600, 2500, 2300, 1500, 1000, 0, 0, 0]  # 绿电供应上限(kWh)
green_price = [0.6, 0.6, 0.6, 0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3,
               0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]  # 绿电价格(元/kWh)
trad_price = [0.5, 0.5, 0.5, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.3, 1.3,
              1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 0.8, 0.6]  # 传统电价

# 算力需求（单位：计算任务量）
tasks = {
    'high': [0, 0, 0, 0, 20, 30, 40, 50, 60, 60, 70, 80,
             90, 80, 70, 60, 50, 40, 30, 20, 10, 0, 0, 0],  # 高优先级
    'medium': [40, 30, 20, 10, 50, 60, 70, 80, 90, 100, 90, 80,
               70, 60, 50, 40, 30, 20, 10, 5, 0, 0, 0, 0],  # 中优先级
    'low': [60, 50, 40, 30, 20, 10, 5, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 低优先级
}

# 每单位算力的电力需求（kWh/任务量）
power_per_task = {
    'high': 80,  # 高优先级
    'medium': 50,  # 中优先级
    'low': 30  # 低优先级
}

# ======================
# 建立优化模型
# ======================
model = pulp.LpProblem("Data_Center_Co_Scheduling", pulp.LpMinimize)

# 决策变量
E_green = pulp.LpVariable.dicts("GreenPower", hours, lowBound=0)  # 绿电使用量
E_trad = pulp.LpVariable.dicts("TraditionalPower", hours, lowBound=0)  # 传统电力
task_alloc = {p: pulp.LpVariable.dicts(f"Task_{p}", hours, lowBound=0)
              for p in ['high', 'medium', 'low']}  # 任务分配量

# 辅助变量
delay_medium = pulp.LpVariable.dicts("DelayMedium", hours, cat='Binary')  # 中优先级延迟标志
delay_low = pulp.LpVariable.dicts("DelayLow", hours, cat='Binary')  # 低优先级延迟标志

# ======================
# 目标函数
# ======================
model += (
    # 电力成本
        pulp.lpSum([E_green[h] * green_price[h] + E_trad[h] * trad_price[h] for h in hours]) +
        # 延迟惩罚（高优先级不允许延迟）
        pulp.lpSum([delay_medium[h] * 1000 + delay_low[h] * 500 for h in hours])
)

# ======================
# 约束条件
# ======================
for h in hours:
    # 1. 电力供应约束
    model += E_green[h] <= green_supply[h]
    model += E_trad[h] >= 0

    # 2. 算力-电力平衡
    required_power = pulp.lpSum([
        task_alloc['high'][h] * power_per_task['high'],
        task_alloc['medium'][h] * power_per_task['medium'],
        task_alloc['low'][h] * power_per_task['low']
    ])
    model += E_green[h] + E_trad[h] >= required_power

    # 3. 任务分配约束
    model += task_alloc['high'][h] == tasks['high'][h]
    model += task_alloc['medium'][h] >= tasks['medium'][h] - delay_medium[h] * tasks['medium'][h] * 2
    model += task_alloc['low'][h] >= tasks['low'][h] - delay_low[h] * tasks['low'][h] * 2

# 4. 绿电比例约束（至少30%）
model += pulp.lpSum([E_green[h] for h in hours]) >= 0.3 * pulp.lpSum([E_green[h] + E_trad[h] for h in hours])

# ======================
# 模型求解
# ======================
model.solve(pulp.PULP_CBC_CMD(timeLimit=300))

# ======================
# 结果处理与可视化
# ======================
if model.status == pulp.LpStatusOptimal:
    print("优化成功！")

    # 结果提取
    results = []
    for h in hours:
        results.append({
            'Hour': h,
            'GreenPower': E_green[h].varValue,
            'TraditionalPower': E_trad[h].varValue,
            'HighTask': task_alloc['high'][h].varValue,
            'MediumTask': task_alloc['medium'][h].varValue,
            'LowTask': task_alloc['low'][h].varValue,
            'DelayMedium': delay_medium[h].varValue,
            'DelayLow': delay_low[h].varValue
        })
    df = pd.DataFrame(results)

    # 保存结果
    df.to_csv('scheduling_results.csv', index=False)

    # 可视化（优化后的字体设置）
    plt.figure(figsize=(12, 6))
    plt.bar(df['Hour'], df['GreenPower'], label='绿色电力')
    plt.bar(df['Hour'], df['TraditionalPower'], bottom=df['GreenPower'], label='传统电力')
    plt.xlabel('时间 (小时)', fontproperties='SimHei')
    plt.ylabel('电力分配 (kWh)', fontproperties='SimHei')
    plt.title('电力调度结果', fontproperties='SimHei')
    plt.legend(prop={'family': 'SimHei'})
    plt.tight_layout()  # 防止标签重叠
    plt.savefig('power_allocation.png', dpi=300, bbox_inches='tight')

    # 控制台输出
    total_cost = pulp.value(model.objective)
    green_ratio = df['GreenPower'].sum() / (df['GreenPower'].sum() + df['TraditionalPower'].sum())
    print(f"总成本: {total_cost:.2f}元")
    print(f"绿电比例: {green_ratio:.1%}")
    print("结果已保存至 scheduling_results.csv 和 power_allocation.png")
else:
    print("优化失败！请检查模型")