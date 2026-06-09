import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st

# 1. 页面基本配置
st.set_page_config(page_title="定投模拟资产看板", layout="wide")

# ==================== ☁️ 云端字体直接外链加载（无需下载上传） ====================
@st.cache_data # 使用 Streamlit 缓存，避免每次刷新页面都重复去网上抓字体
def load_cloud_font():
    import urllib.request
    # 直接去标准开源镜像站拉取轻量化中文字体（仅不到 2MB，加载极快）
    font_url = "https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc"
    local_path = "/tmp/wqy-microhei.ttc" # 借用 Linux 系统的临时缓存目录
    
    if not os.path.exists(local_path):
        try:
            urllib.request.urlretrieve(font_url, local_path)
        except Exception:
            return None
    return local_path

font_path = load_cloud_font()

if font_path and os.path.exists(font_path):
    # 强制让 Matplotlib 认识这个云端抓下来的字体
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = [prop.get_name()]
else:
    # 备用方案
    plt.rcParams['font.sans-serif'] = ['sans-serif']

plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
# =====================================================================

# 2. 检查并读取 CSV 涨跌幅数据
csv_filename = 'annual_returns.csv'
if not os.path.exists(csv_filename):
    st.error(f"未找到数据文件：{csv_filename}，请确保该 CSV 文件与 app.py 在同一目录下。")
    st.stop()

df_ret = pd.read_csv(csv_filename)

# 3. 后台核心逻辑计算：通过涨跌幅生成资产终值演变表
ANNUAL_INVESTMENT = 10400  

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
    
    v_nasdaq = (v_nasdaq + ANNUAL_INVESTMENT) * (1 + r_nasdaq)
    v_kc50 = (v_kc50 + ANNUAL_INVESTMENT) * (1 + r_kc50)
    v_gold = (v_gold + ANNUAL_INVESTMENT) * (1 + r_gold)
    v_low_vol = (v_low_vol + ANNUAL_INVESTMENT) * (1 + r_low_vol)
    v_deposit = (v_deposit + ANNUAL_INVESTMENT) * (1 + r_deposit)
    
    v_82_nasdaq_gold = (v_82_nasdaq_gold + ANNUAL_INVESTMENT) * (0.8 * (1 + r_nasdaq) + 0.2 * (1 + r_gold))
    v_82_kc50_gold = (v_82_kc50_gold + ANNUAL_INVESTMENT) * (0.8 * (1 + r_kc50) + 0.2 * (1 + r_gold))
    
    evolution_rows.append({
        '年份': year, '累计总本金': current_principal,
        '纯纳斯达克100': round(v_nasdaq), '纯科创50': round(v_kc50), '纯黄金': round(v_gold),
        '纯低波红利': round(v_low_vol), '纯银行存款': round(v_deposit),
        '8:2纳指黄金': round(v_82_nasdaq_gold), '8:2科创黄金': round(v_82_kc50_gold)
    })

df_evo = pd.DataFrame(evolution_rows)

# 4. 定义统一的基础资产颜色映射
color_map = {
    '纯纳斯达克100': '#1f77b4',
    '纯科创50': '#d62728',
    '纯黄金': '#bcbd22',
    '纯低波红利': '#2ca02c',
    '纯银行存款': '#7f7f7f',
    '8:2纳指黄金': '#9400D3',  
    '8:2科创黄金': '#FF7F0E'   
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

st.pyplot(fig1)

st.write("---") 

# ==================== 图表 2：40年定投总资产终值演变折线图 ====================
fig2, ax2 = plt.subplots(figsize=(14, 8))

# 过滤掉初始的0年份，获取实际年份范围
valid_df = df_evo[df_evo['年份'] > 0]
start_year = int(valid_df['年份'].min())
final_year = int(valid_df['年份'].max())

ax2.plot(df_evo['年份'], df_evo['累计总本金'], label='累计总本金', color='#b0b0b0', linestyle='--', linewidth=1.5)

for column in color_map.keys():
    linewidth = 2.6 if '8:2' in column else 1.8
    ax2.plot(df_evo['年份'], df_evo[column], label=column, color=color_map[column], linewidth=linewidth)

# 动态标注逻辑
last_row = df_evo.iloc[-1]
final_assets = {col: last_row[col] for col in color_map.keys()}
sorted_assets = sorted(final_assets.items(), key=lambda x: x[1], reverse=True)

for label, val in sorted_assets:
    col = color_map[label]
    ax2.text(final_year + 0.4, val, f"{val/10000:.1f}万", color=col, fontweight='bold', va='center', fontsize=10)

ax2.set_title('40年定投总资产终值演变折线图', fontsize=16, fontweight='bold', pad=15)
ax2.set_xlabel('年份', fontsize=11)
ax2.set_ylabel('资产总额 (元)', fontsize=11)
ax2.set_xlim(start_year - 1, final_year + 5)
ax2.set_xticks(range(start_year, final_year + 1, 2))
ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}元".format(int(x))))
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='none', fontsize=11)

plt.tight_layout()
st.pyplot(fig2)

# ==================== 新增：资产终值与增值分析表格 ====================
st.write("---")
st.subheader("📊 最终资产表现总结（竖向表格）")

last_row = df_evo.iloc[-1]
total_principal = last_row['累计总本金']

summary_data = []
for asset in color_map.keys():
    final_value = last_row[asset]
    growth = (final_value - total_principal)/total_principal * 100
    summary_data.append({
        "资产名称": asset,
        "最终资产金额 (元)": final_value,
        "相比投入资金增值 (%)": growth
    })

df_summary = pd.DataFrame(summary_data)
st.table(df_summary.style.format({
    "最终资产金额 (元)": "{:,.0f}",
    "相比投入资金增值 (%)": "{:,.0f}%"
}))
