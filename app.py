import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as plt_st
import streamlit as st

# 1. 页面基本配置
st.set_page_config(page_title="定投模拟资产看板", layout="wide")

# 2. 尝试自动配置中文字体（兼容 Linux/Colab/Windows/Mac 环境）
plt.rcParams['axes.unicode_minus'] = False
possible_fonts = ['SimHei', 'Arial Unicode MS', 'WenQuanYi Micro Hei', 'Microsoft YaHei']
font_fixed = False
for font in possible_fonts:
    try:
        plt.rcParams['font.sans-serif'] = [font]
        # 尝试渲染一个字测试是否报错
        fig = plt.figure()
        plt.text(0, 0, '测试')
        plt.close(fig)
        font_fixed = True
        break
    except:
        continue

# 3. 检查并读取 CSV 涨跌幅数据
csv_filename = 'annual_returns.csv'
if not os.path.exists(csv_filename):
    st.error(f"未找到数据文件：{csv_filename}，请确保该 CSV 文件与 app.py 在同一目录下。")
    st.stop()

df_ret = pd.read_csv(csv_filename)

# 4. 后台核心逻辑计算：通过涨跌幅生成资产终值演变表
ANNUAL_INVESTMENT = 10400  # 每年初定投金额

init_row = {
    '年份': 0, '累计总本金': 0, 
    '纯纳斯达克100': 0.0, '纯科创50': 0.0, '纯黄金': 0.0, '纯低波红利': 0.0, '纯银行存款': 0.0,
    '8:2纳指黄金': 0.0, '8:2科创黄金': 0.0
}
evolution_rows = [init_row]

current_principal = 0
v_nasdaq = 0.0
v_kc50 = 0.0
v_gold = 0.0
v_low_vol = 0.0
v_deposit = 0.0
v_82_nasdaq_gold = 0.0
v_82_kc50_gold = 0.0

for idx, row in df_ret.iterrows():
    year = int(row['年份'])
    current_principal += ANNUAL_INVESTMENT
    
    r_nasdaq = row['纳斯达克100'] / 100.0
    r_kc50 = row['科创50'] / 100.0
    r_gold = row['黄金'] / 100.0
    r_low_vol = row['低波红利'] / 100.0
    r_deposit = row['银行存款'] / 100.0
    
    # 纯单资产定投复利
    v_nasdaq = (v_nasdaq + ANNUAL_INVESTMENT) * (1 + r_nasdaq)
    v_kc50 = (v_kc50 + ANNUAL_INVESTMENT) * (1 + r_kc50)
    v_gold = (v_gold + ANNUAL_INVESTMENT) * (1 + r_gold)
    v_low_vol = (v_low_vol + ANNUAL_INVESTMENT) * (1 + r_low_vol)
    v_deposit = (v_deposit + ANNUAL_INVESTMENT) * (1 + r_deposit)
    
    # 8:2 动态平衡组合复利（每年末强制调仓回 8:2）
    v_82_nasdaq_gold = (v_82_nasdaq_gold + ANNUAL_INVESTMENT) * (0.8 * (1 + r_nasdaq) + 0.2 * (1 + r_gold))
    v_82_kc50_gold = (v_82_kc50_gold + ANNUAL_INVESTMENT) * (0.8 * (1 + r_kc50) + 0.2 * (1 + r_gold))
    
    evolution_rows.append({
        '年份': year, '累计总本金': current_principal,
        '纯纳斯达克100': round(v_nasdaq), '纯科创50': round(v_kc50), '纯黄金': round(v_gold),
        '纯低波红利': round(v_low_vol), '纯银行存款': round(v_deposit),
        '8:2纳指黄金': round(v_82_nasdaq_gold), '8:2科创黄金': round(v_82_kc50_gold)
    })

df_evo = pd.DataFrame(evolution_rows)

# 5. 定义统一的基础资产颜色映射
color_map = {
    '纯纳斯达克100': '#1f77b4',
    '纯科创50': '#d62728',
    '纯黄金': '#bcbd22',
    '纯低波红利': '#2ca02c',
    '纯银行存款': '#7f7f7f',
    '8:2纳指黄金': '#9400D3',  # 显眼的深紫色
    '8:2科创黄金': '#FF7F0E'   # 显眼的亮橙色
}

# ==================== 图表 1：每年涨跌幅柱状图 ====================
fig1, axes = plt.subplots(5, 1, figsize=(14, 10), sharex=True)
fig1.suptitle('40年多资产年度涨跌幅百分比图', fontsize=16, fontweight='bold', y=0.97)

assets = ['纳斯达克100', '科创50', '黄金', '低波红利', '银行存款']
bar_colors = ['#1f77b4', '#d62728', '#bcbd22', '#2ca02c', '#7f7f7f']

for i, asset in enumerate(assets):
    ax = axes[i]
    ax.bar(df_ret['年份'], df_ret[asset], color=bar_colors[i], width=0.6)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_ylabel(asset, fontsize=11, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    if asset == '银行存款':
        ax.set_ylim(0, 2.0)
        ax.set_yticklabels([f"{y:.1f}%" for y in ax.get_yticks()])
    else:
        ax.set_ylim(-65, 65)
        ax.set_yticklabels([f"{int(y)}%" for y in ax.get_yticks()])

plt.xticks(range(2026, 2066, 2))
plt.xlabel('年份', fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.95])

# 在 Streamlit 展示图 1
st.pyplot(fig1)

st.write("---") # 分割线

# ==================== 图表 2：40年定投总资产终值演变折线图 ====================
fig2, ax2 = plt.subplots(figsize=(14, 8))

# 绘制基准本金线
ax2.plot(df_evo['年份'], df_evo['累计总本金'], label='累计总本金', color='#b0b0b0', linestyle='--', linewidth=1.5)

# 循环绘制所有资产曲线
for column in color_map.keys():
    linewidth = 2.6 if '8:2' in column else 1.8
    ax2.plot(df_evo['年份'], df_evo[column], label=column, color=color_map[column], linewidth=linewidth)

# 精准终点右侧数值标签
final_year = 2065
final_values = {
    '8:2纳指黄金': (1926455, '#9400D3'),
    '纯纳斯达克100': (1913382, '#1f77b4'),
    '8:2科创黄金': (1411920, '#FF7F0E'),
    '纯科创50': (1222013, '#d62728'),
    '纯低波红利': (822171, '#2ca02c'),
    '纯黄金': (816427, '#bcbd22'),
    '纯银行存款': (471940, '#7f7f7f'),
}

for label, (val, col) in final_values.items():
    ax2.text(final_year + 0.4, val, f"{val/10000:.1f}万", color=col, fontweight='bold', va='center', fontsize=10)

ax2.set_title('40年定投总资产终值演变折线图', fontsize=16, fontweight='bold', pad=15)
ax2.set_xlabel('年份', fontsize=11)
ax2.set_ylabel('资产总额 (元)', fontsize=11)
ax2.set_xlim(2025, 2068)
ax2.set_xticks(range(2026, 2066, 2))
ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}元".format(int(x))))
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='none', fontsize=11)

plt.tight_layout()

# 在 Streamlit 展示图 2
st.pyplot(fig2)
