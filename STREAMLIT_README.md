# 🌊 Streamlit Dashboard 使用指南

## 快速启动

### 1. 确保已导出数据
首先在Jupyter Notebook中运行最后的数据导出单元格（Cell 42），确保 `streamlit_data/` 目录中包含以下文件：

- ✅ `env_df_for_app.csv`
- ✅ `scenario_results.csv`
- ✅ `transactions_df.csv`
- ✅ `classification_data.csv`
- ✅ `feature_importance.csv`

### 2. 安装Streamlit（如果还没安装）

```bash
pip install streamlit
```

或者使用项目虚拟环境：

```bash
source venv/bin/activate  # macOS/Linux
pip install streamlit
```

### 3. 运行Dashboard

在项目根目录下运行：

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

---

## Dashboard功能

### 📊 五个主要Tab页面

#### 1️⃣ 季节性分析
- 月度平均评分柱状图
- 全年时间序列趋势
- 评分分布直方图
- 高质量天数统计

#### 2️⃣ 策略对比
- 三种运营策略对比（每晚运营 vs 高评分 vs 周末+评分）
- 总利润、运营天数、每晚平均利润对比
- 最优策略推荐

#### 3️⃣ 交互式模拟 ⭐ **课堂演示亮点**
- **实时调整参数**:
  - 评分阈值滑块 (0.0-1.0)
  - 仅周末运营开关
  - 基础票价设置
  - 高分加价系数
- **即时查看结果**:
  - 运营天数、总收入、总利润
  - 月度利润趋势图
  - 开团日历热力图

#### 4️⃣ 深度分析
- 机器学习模型特征重要性
- 环境因素分布（水温、浪高、风速、月相）
- 交易数据统计
- 产品类型收入对比

#### 5️⃣ 商业建议
- 关键发现（优势 vs 挑战）
- 三阶段运营策略推荐
- 第一年财务预测
- 风险管理矩阵
- 行动计划清单

---

## 课堂演示建议流程

### 🎯 演示脚本（5-10分钟）

**1. 开场（1分钟）**
- 打开Dashboard主页
- 介绍项目背景：La Jolla蓝眼泪观光可行性
- 强调数据来源：26万+真实NOAA/NDBC记录

**2. 季节性分析（2分钟）**
- Tab 1: 展示月度趋势图
- 指出最佳月份（通常是4-8月）
- 强调高质量天数统计

**3. 交互式模拟 ⭐ （3-4分钟 - 重点！）**
- Tab 3: 现场操作
- **场景1**: 设置阈值=0.5，展示激进策略
  - 运营天数多，但利润可能不高
- **场景2**: 设置阈值=0.8，展示保守策略
  - 运营天数少，但每晚利润高
- **场景3**: 开启"仅周末"，调整票价
  - 展示如何平衡运营频率和收益
- **互动**: 请观众建议一个阈值，现场测试

**4. 策略对比（1分钟）**
- Tab 2: 快速展示三策略对比
- 指出最优策略（通常是Strategy B）

**5. 商业建议（1分钟）**
- Tab 5: 展示推荐的三阶段策略
- 强调风险管理
- 展示第一年财务预测

**6. Q&A（剩余时间）**
- 根据问题跳转到相关Tab
- 利用交互式模拟回答假设性问题

---

## 技术亮点（适合技术评审）

- ✅ **实时交互**: Streamlit滑块实时重新计算
- ✅ **数据驱动**: 基于26万+真实环境数据
- ✅ **机器学习**: RandomForest预测模型
- ✅ **可视化**: Matplotlib/Seaborn专业图表
- ✅ **响应式布局**: 多列布局，Tab导航
- ✅ **商业洞察**: 不仅是数据展示，更有策略建议

---

## 故障排除

### 问题1: `ModuleNotFoundError: No module named 'streamlit'`
**解决**: 
```bash
pip install streamlit
```

### 问题2: `FileNotFoundError: streamlit_data/xxx.csv`
**解决**: 
1. 返回Jupyter Notebook
2. 运行Cell 42（数据导出单元格）
3. 确认`streamlit_data/`目录已创建

### 问题3: 浏览器没有自动打开
**解决**: 
手动访问终端中显示的URL，通常是: `http://localhost:8501`

### 问题4: 图表显示不正常
**解决**: 
```bash
pip install --upgrade matplotlib seaborn pandas numpy
```

---

## 自定义修改

### 修改颜色主题
编辑 `app.py` 中的CSS部分（第15-30行）

### 添加新的Tab
在 `st.tabs()` 中添加新的tab名称，然后添加对应的 `with tabX:` 代码块

### 修改默认参数
在Tab 3的滑块部分修改 `value=` 参数

---

## 联系与反馈

如有任何问题或建议，欢迎在课后讨论！

**Good Luck with your presentation! 🎉**
