# La Jolla 蓝眼泪可行性分析 - 项目文件结构
## MGTA 452 Final Project

## 📁 项目组织架构

按照Business Analytics课程要求组织的项目结构:

```
blueglow_code/
│
├── 📋 核心文档
│   ├── README.md                    # 项目主文档 (课程项目介绍)
│   ├── PROJECT_OVERVIEW.md          # 可行性分析完整报告
│   ├── PPT_OUTLINE.md              # 演讲大纲 (课程展示结构)
│   └── PROJECT_STRUCTURE.md        # 本文件 (项目结构说明)
│
├── 🔧 环境配置
│   ├── requirements.txt            # Python依赖包列表 (含Polars)
│   ├── run.sh                      # 环境设置脚本
│   ├── config/
│   │   ├── .env.example           # 配置模板
│   │   └── .env                   # 实际配置 (可选)
│   └── .vscode/                   # VS Code任务配置
│       └── tasks.json             # 自动化任务定义
│
├── 📓 分析笔记本 (课程作业核心)
│   └── La_Jolla_Blue_Tears_Feasibility_Study.ipynb
│       ├── Part 1: 项目介绍与商业背景
│       ├── Part 2: 数据伦理与API使用
│       ├── Part 3: Descriptive Analytics (环境数据)
│       ├── Part 4: Predictive Analytics (ML模型)
│       ├── Part 5: Transaction Data Analytics (Polars)
│       └── Part 6: Prescriptive Analytics (策略优化)
│
├── 🎬 演示步骤脚本 (按顺序执行)
│   ├── step1_skeleton.sh          # Step 1: 创建骨架 & 演示数据
│   ├── step2_fetch_data.sh        # Step 2: 获取真实环境数据 (可选)
│   ├── step3_train.sh             # Step 3: 训练ML模型 (可选)
│   ├── step4_forecast.sh          # Step 4: 生成未来7天预测 (可选)
│   └── step5_build_site.sh        # Step 5: 构建交互式网站
│
├── 📊 数据文件
│   └── data/
│       ├── climatology.json       # 气候学数据 (366天中位值)
│       ├── astronomy_next7.json   # 天文潮汐数据 (未来7天)
│       ├── forecast.json          # ML预测结果
│       ├── transactions.csv       # 模拟交易数据 (用于课程分析)
│       └── raw/                   # 原始NDBC数据 (可选,Step2生成)
│           ├── ndbc_46254_2024_2024.csv
│           └── ndbc_46254_2024_2025.csv
│
├── 🤖 机器学习模型
│   └── models/
│       └── biolum_rf.pkl          # 训练好的Random Forest模型
│
├── 🐍 Python脚本 (支持笔记本分析)
│   └── scripts/
│       ├── compute_climatology.py      # 计算气候学特征
│       ├── compute_astronomy.py        # 计算天文潮汐
│       ├── train_model.py             # 训练Random Forest模型
│       ├── forecast_next7.py          # 生成7天预测
│       ├── forecast_detailed.py       # 生成详细预测 (Best Week)
│       ├── generate_year_data.py      # 生成全年预测数据
│       ├── generate_all_forecasts.py  # 生成所有预测
│       ├── generate_demo_forecast.py  # 生成演示数据
│       ├── find_best_week.py          # 查找最佳观测周
│       ├── build_site.py              # 构建静态网站
│       ├── fetch_data.py              # 下载NDBC数据 (Step2)
│       ├── fetch_static.py            # 下载静态数据
│       └── validate_data.py           # 数据验证工具
│
├── 🌐 网站文件 (可部署到Vercel展示成果)
│   └── site/
│       ├── index.html                 # 主页面 (交互式预测展示)
│       ├── forecast_year.json         # 全年预测数据 (365天)
│       ├── forecast_detailed.json     # 最佳周详细数据
│       ├── forecast.json              # 7天预测数据
│       ├── sw.js                      # Service Worker (PWA)
│       ├── manifest.json              # PWA manifest
│       ├── vercel.json                # Vercel部署配置
│       └── assets/                    # 静态资源 (CSS/JS)
│           ├── css/
│           │   └── style.css
│           └── js/
│               └── main.js
│
└── 📚 文档目录
    └── docs/
        └── PROJECT_OVERVIEW.md        # 完整可行性分析报告

```

## 🎯 课程学习目标映射

### Part 1: Business Context (商业背景)
- **文件**: La_Jolla_Blue_Tears_Feasibility_Study.ipynb (Cells 1-3)
- **内容**: 问题定义、目标客户、市场机会
- **对应课程**: Business Problem Framing, Stakeholder Analysis

### Part 2: Data Ethics (数据伦理)
- **文件**: La_Jolla_Blue_Tears_Feasibility_Study.ipynb (Cells 4-5)
- **内容**: API使用规范、Web Scraping伦理、数据合规
- **对应课程**: Data Ethics, Legal Compliance

### Part 3: Descriptive Analytics (描述性分析)
- **文件**: La_Jolla_Blue_Tears_Feasibility_Study.ipynb (Cells 6-8)
- **数据**: data/climatology.json, data/astronomy_next7.json
- **方法**: 时间序列分析、季节性模式、可视化
- **对应课程**: Exploratory Data Analysis, Data Visualization

### Part 4: Predictive Analytics (预测性分析)
- **文件**: La_Jolla_Blue_Tears_Feasibility_Study.ipynb (Cell 9)
- **模型**: Random Forest Regressor
- **评估**: RMSE, MAE, R², Feature Importance
- **对应课程**: Supervised Learning, Model Evaluation

### Part 5: Transaction Data Analytics (交易数据分析)
- **文件**: La_Jolla_Blue_Tears_Feasibility_Study.ipynb (Cells 10-13)
- **工具**: Polars (高性能数据处理)
- **分析**:
  - 多场次tour设计 (0-3场/天)
  - 多渠道收入分析 (website, OTA, walk-in)
  - 产品类型对比 (standard, premium)
  - 价格弹性分析
- **对应课程**: Transaction Analytics, Revenue Optimization

### Part 6: Prescriptive Analytics (规范性分析)
- **文件**: La_Jolla_Blue_Tears_Feasibility_Study.ipynb (Cells 14-19)
- **策略对比**:
  - Strategy A: 全年开放
  - Strategy B: 高分筛选 (score > 0.7)
  - Strategy C: 周末+高分
- **优化目标**: 利润最大化、客户满意度、运营效率
- **对应课程**: Decision Analytics, Optimization

## 🔄 工作流程

### 学术分析流程 (Jupyter Notebook)
```
1. 商业背景 → 2. 数据伦理 → 3. Descriptive Analytics
                                      ↓
                              4. Predictive Analytics
                                      ↓
                         5. Transaction Data Analytics
                                      ↓
                         6. Prescriptive Analytics
                                      ↓
                              7. 结论与建议
```

### 技术实现流程 (Shell Scripts)
```
Step 0: run.sh                    → 环境准备
Step 1: step1_skeleton.sh         → 骨架+演示数据
Step 2: step2_fetch_data.sh       → 获取真实数据 (可选)
Step 3: step3_train.sh            → 训练ML模型 (可选)
Step 4: step4_forecast.sh         → 生成预测 (可选)
Step 5: step5_build_site.sh       → 构建网站
```

## 📦 依赖包清单

### Core Data Analysis
- pandas >= 2.0.0         # 数据处理
- polars >= 0.19.0        # 高性能数据分析
- numpy >= 1.21.0         # 数值计算

### Machine Learning
- scikit-learn >= 1.0.0   # Random Forest模型

### Visualization
- matplotlib >= 3.4.0     # 绘图

### Additional
- requests >= 2.26.0      # API请求
- astral >= 3.0           # 天文计算

### Optional
- jupyter >= 1.0.0        # 笔记本环境
- ipykernel >= 6.0.0      # Jupyter内核

## 🎓 课程概念应用示例

| MGTA 452 概念 | 项目中的应用 | 文件位置 |
|--------------|------------|---------|
| Descriptive Analytics | 环境数据季节性分析 | Notebook Cells 6-8 |
| Predictive Analytics | Random Forest预测模型 | Notebook Cell 9 |
| Prescriptive Analytics | 运营策略优化 | Notebook Cells 14-19 |
| Transaction Analytics | Polars多维交易分析 | Notebook Cells 10-13 |
| Data Ethics | API使用与Scraping规范 | Notebook Cells 4-5 |
| Feature Engineering | 环境特征×月相交互项 | scripts/train_model.py |
| Model Evaluation | RMSE, MAE, R²指标 | Notebook Cell 9 |
| Business Metrics | Revenue, Profit, ROI | Notebook Cells 12-13 |
| Data Visualization | Matplotlib时间序列图 | Notebook Cells 7-8, 12 |
| Decision Support | 策略A/B/C对比表 | Notebook Cell 18 |

## 🚀 快速开始

### 查看课程笔记本
# 1. 配置Python环境
bash run.sh

# 2. 在VS Code中打开笔记本
code La_Jolla_Blue_Tears_Feasibility_Study.ipynb

# 3. 运行所有cell (Ctrl+Enter 或 Run All)
```

### 构建交互式网站 (可选)
```bash
# 生成网站文件
bash step5_build_site.sh

# 预览网站
python3 -m http.server 5500
# 访问 http://localhost:5500
```

## 💡 项目亮点

### 1. 完整的Business Analytics框架
- ✅ 从商业问题到决策建议的端到端分析
- ✅ 系统性展示所有分析类型 (Descriptive, Predictive, Prescriptive)
- ✅ 真实的业务场景和运营约束

### 2. 先进的数据分析工具
- ✅ **Polars**: 比Pandas快10倍的DataFrame处理
- ✅ **Random Forest**: 可解释的非线性模型
- ✅ 多维度交易数据设计 (多场次/渠道/产品)

### 3. 学术与实践结合
- ✅ 符合MGTA 452课程要求
- ✅ 可部署的Web应用展示成果
- ✅ 包含数据伦理和局限性讨论

### 4. 可扩展性
- ✅ 模块化脚本便于修改
- ✅ 支持真实数据接入 (Step 2-4)
- ✅ 可扩展到其他地点或业务

## 📊 数据说明

### 环境数据 (data/climatology.json)
```json
{
  "day_of_year": [1, 2, ..., 366],
  "water_temp": [14.5, 14.6, ...],  // 水温 (°C)
  "wave_height": [1.2, 1.3, ...],   // 浪高 (m)
  "wind_speed": [5.1, 5.2, ...]     // 风速 (m/s)
}
```

### 交易数据 (模拟)
```csv
date,tour_time,num_tours_today,tour_index,channel,product_type,num_customers,price_per_person,revenue,cost,profit
2024-01-15,20:00,2,0,website,standard,12,50.0,600,300,300
```

**关键字段**:
- `num_tours_today`: 当日开团数 (0-3)
- `channel`: website, OTA, walk-in
- `product_type`: standard, premium
- `price_per_person`: 动态定价 ($40-$80)

### 预测数据 (site/forecast.json)
```json
{
  "date": "2024-06-15",
  "score": 0.85,              // 0-1评分
  "rating": 8.5,              // 0-10星级
  "water_temp": 18.5,
  "moon_phase": 0.15,         // 0=新月, 1=满月
  "recommendation": "Excellent night!"
}
```

## 🎬 VS Code任务配置

在VS Code中可以通过 **Terminal → Run Task** 运行以下任务:

1. **Env: Setup venv & deps** - 环境配置
2. **Step1: Skeleton (demo forecast)** - 创建骨架
3. **Step2: Fetch (optional)** - 获取真实数据
4. **Step3: Train (optional)** - 训练模型
5. **Step4: Forecast next7 (optional)** - 生成7天预测
6. **Step5: Build site** - 构建网站
7. **Site: Preview (python http.server)** - 预览网站

## 📚 相关文档

- **README.md**: 快速开始指南和项目介绍
- **PROJECT_OVERVIEW.md**: 完整可行性分析报告 (含执行摘要、方法论、结论)
- **PPT_OUTLINE.md**: 课程展示演讲稿大纲
- **requirements.txt**: Python依赖清单

## 🔗 在线演示

- **网站**: https://bluelajolla000.vercel.app/
- **Notebook**: La_Jolla_Blue_Tears_Feasibility_Study.ipynb (本地运行)

---

**作者**: Mindy Chen
**课程**: MGTA 452 - Business Analytics
**日期**: November 30, 2025
**项目类型**: Feasibility Study

**完整路径** (需要真实数据和模型训练):
```bash
bash run.sh
bash step1_skeleton.sh
bash step2_fetch_data.sh   # 可选,需要时间
bash step3_train.sh        # 可选
bash step4_forecast.sh     # 可选
bash step5_build_site.sh
```

## 📝 注意事项

1. **Step2是可选的**: 项目默认使用气候学数据,不需要下载实时卫星数据
2. **Step3-4也是可选的**: 已有预训练模型和演示数据
3. **Step1+Step5可以直接运行**: 快速查看最终效果
4. **所有数据都是离线的**: 不依赖实时API
5. **网站已部署**: https://bluelajolla000.vercel.app/

## 🎤 演讲材料

详见 `PPT_OUTLINE.md`:
- 18页PPT结构
- 每页详细演讲稿
- 技术细节和图表建议
- Q&A准备

---

**项目状态**: ✅ 生产就绪 | **最后更新**: 2025-11-26
