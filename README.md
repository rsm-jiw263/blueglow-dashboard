# La Jolla 蓝眼泪可行性分析项目
## MGTA 452 - Business Analytics Final Project

**作者**: Mindy Chen
**日期**: November 30, 2025
**课程**: MGTA 452 - Business Analytics

## 项目概述

本项目以 La Jolla 海域的"蓝眼泪"现象为研究对象，利用公开的环境数据与预测模型，评估在该区域开展"蓝眼泪主题夜间活动"的可行性。

本项目演示了完整的商业分析流程：
- **Descriptive Analytics**: 环境数据季节性分析
- **Predictive Analytics**: 机器学习预测模型
- **Prescriptive Analytics**: 运营策略优化
- **Transaction Data Analytics**: 交易数据分析与Polars应用

## 核心特性

- **环境数据分析**: 基于NDBC海洋数据、月相、潮汐等因素
- **机器学习模型**: Random Forest预测蓝眼泪观赏评分
- **模拟交易数据**: 构造多场次、多渠道、多产品类型的交易数据
- **策略对比**: 不同运营策略的收入与利润分析
- **数据伦理**: 包含API使用和Web Scraping的伦理讨论

## 项目结构

```
blueglow_code/
├── La_Jolla_Blue_Tears_Feasibility_Study.ipynb  # 主要分析笔记本
├── data/                                         # 数据文件
│   ├── blue_tears_environment.csv               # 环境数据（可选）
│   └── raw/                                     # 原始NDBC数据
├── models/                                       # 训练好的模型
│   └── biolum_lr.pkl                            # 预测模型
├── scripts/                                      # 辅助脚本
│   ├── compute_climatology.py                   # 气候学计算
│   ├── compute_astronomy.py                     # 天文计算
│   └── generate_demo_forecast.py                # 演示数据生成
├── requirements.txt                              # Python依赖
└── README.md                                     # 本文件
```

## 快速开始

### 1. 环境设置

首先安装Python 3.7+，然后安装依赖：

```bash
pip install -r requirements.txt
```

主要依赖包：
- `pandas` - 数据处理
- `polars` - 高性能数据分析
- `numpy` - 数值计算
- `scikit-learn` - 机器学习
- `matplotlib` - 数据可视化

### 2. 运行分析笔记本

在VS Code或Jupyter中打开：
```
La_Jolla_Blue_Tears_Feasibility_Study.ipynb
```

按顺序执行所有单元格即可看到完整的分析流程。

## 笔记本内容概览

### 1. Business Scenario & Research Questions
- 商业背景介绍
- La Jolla蓝眼泪tour的可行性问题
- 描述性、预测性、规范性分析问题

### 2. Data Sources & Acquisition
- 环境数据来源（NDBC、天文数据）
- API获取示例代码
- Web Scraping伦理讨论

### 3. Environmental Data Preparation
- 加载和清洗环境数据
- 特征工程：生成蓝眼泪评分
- 季节性描述分析

### 4. Descriptive Analytics
- 月度蓝眼泪评分分布
- 环境因素的时间序列分析
- 季节性模式识别

### 5. Synthetic Booking Transaction Data
- 构造多场次交易数据
- 包含渠道、产品类型、定价策略
- 使用Polars进行高效数据分析

### 6. Predictive Modeling
- Random Forest模型训练
- 特征重要性分析
- 模型性能评估（RMSE, MAE, R²）

### 7. Prescriptive Analytics
- 设计三种运营策略（A/B/C）
- 对比收入、利润和风险
- 提供决策建议

### 8. Course Concepts Mapping
- 将项目与课程概念对应
- 展示各类Analytics的应用

### 9. Limitations & Future Work
- 讨论项目局限性
- 提出改进方向

## 核心分析技术

### Descriptive Analytics
- **月度汇总**: 使用Polars按月份聚合收入、利润、客户数
- **渠道分析**: 对比不同预订渠道的表现
- **价格弹性**: 分析价格与需求的关系

### Predictive Analytics
- **特征工程**: 水温、浪高、风速、月相
- **模型选择**: Random Forest Regressor
- **评估指标**: RMSE, MAE, R²
- **可解释性**: Feature Importance分析

### Prescriptive Analytics
- **策略A**: 每晚都开团（baseline）
- **策略B**: 仅在预测评分>0.7时开团
- **策略C**: 周末且评分>0.6时开团
- **决策指标**: 开团次数、总收入、总利润、平均利润

### Transaction Data Analytics
- **Polars应用**: 高性能groupby和聚合
- **多维分析**: 按月份、产品类型、渠道分组
- **交易粒度**: 每场tour作为一条记录
- **业务指标**: Revenue, Cost, Profit计算

## 数据说明

### 环境数据
- **来源**: NDBC Station 46254 (Scripps Nearshore)
- **时间范围**: 2024年全年
- **变量**:
  - water_temp: 海水温度 (°C)
  - wave_height: 浪高 (米)
  - wind_speed: 风速 (m/s)
  - moon_phase: 月相 (0-1, 0=新月)

### 交易数据（模拟）
- **粒度**: 每场tour一条记录
- **场次**: 每天0-3场 (20:00, 21:30, 23:00)
- **渠道**: website, OTA, walk-in
- **产品**: standard (标准团), premium (高级团)
- **定价**: 基础价 + 周末溢价 + 评分溢价

## 项目亮点

### 1. 真实商业场景
- 基于La Jolla实际地理位置和海洋条件
- 考虑真实的运营约束（时间、人力、成本）
- 可应用的决策框架

### 2. 完整分析流程
- 从数据获取到决策建议的端到端流程
- 包含数据伦理和法律合规讨论
- 展示专业的数据分析方法论

### 3. 先进技术应用
- **Polars**: 比Pandas更快的数据处理
- **Random Forest**: 可解释的机器学习模型
- **多维分析**: 时间、产品、渠道等多角度

### 4. 课程概念整合
- 系统性地展示Descriptive、Predictive、Prescriptive三类分析
- Transaction Data Analytics的实践应用
- 商业决策与数据驱动结合

## 技术栈

- **Python 3.7+**: 主要编程语言
- **Pandas**: 数据处理和转换
- **Polars**: 高性能数据分析
- **NumPy**: 数值计算
- **Scikit-learn**: 机器学习建模
- **Matplotlib**: 数据可视化
- **Jupyter/VS Code**: 开发环境

## 项目成果

### 学术价值
- 完整的feasibility study案例
- 可复用的分析框架
- 适合作为课程项目参考

### 实践价值
- 可直接应用于真实业务场景
- 提供决策支持工具
- 包含风险评估和策略对比

## 局限性与改进方向

### 当前局限
1. **模拟数据**: 交易数据基于假设构造，非真实订单
2. **简化模型**: 环境-蓝眼泪关系采用简化公式
3. **单一地点**: 仅针对La Jolla，未考虑其他海域

### 未来改进
1. 收集真实蓝眼泪观测数据和游客反馈
2. 整合社交媒体数据（搜索热度、帖子数量）
3. 考虑竞争对手和市场饱和度
4. 引入动态定价和库存管理
5. 多地点对比分析

## 参考资源

### 数据源
- [NDBC - National Data Buoy Center](https://www.ndbc.noaa.gov/)
- [Astral - Python天文计算库](https://astral.readthedocs.io/)

### 相关文档
- La Jolla海域介绍
- 蓝眼泪（生物发光）科学背景
- 旅游业数据分析最佳实践

## 作者信息

**Mindy Chen**
MGTA 452 - Business Analytics
University of California, San Diego

## 许可证

本项目仅用于教育目的。所有数据和分析结果均为学术演示，不构成实际商业建议。

---

**项目状态**: 课程作业完成
**最后更新**: November 30, 2025
**版本**: v2.0-feasibility-study

**数据输出:**
- 所有数据保存在 `data/raw/` 目录
- SST/Chl-a: 按月分块的 NetCDF 文件
- NDBC: 合并的 CSV 文件

### Step 3: 训练模型 (可选)
```bash
bash step3_train.sh
```

### Step 4: 生成预测 (可选)
```bash
bash step4_forecast.sh
```

## VS Code 任务

本项目配置了以下 VS Code 任务,可通过 `Cmd+Shift+P` (macOS) 运行 "Tasks: Run Task":

1. **Env: Setup venv & deps** - 设置环境
2. **Step1: Skeleton (demo forecast)** - 创建结构和演示数据
3. **Step2: Fetch (optional)** - 获取真实数据
4. **Step3: Train (optional)** - 训练模型
5. **Step4: Forecast next7 (optional)** - 生成预测
6. **Step5: Build site** - 构建网站
7. **Site: Preview (python http.server)** - 预览网站

## 依赖

- Python 3.7+
- numpy
- pandas
- scikit-learn
- matplotlib
- requests

## 特性

- 🌌 7天蓝光指数预测
- ☁️ 云量、能见度、月相信息
- 📊 可视化预测质量
- 📱 响应式设计
- 🎨 现代化 UI

## 开发说明

- Steps 2-4 是可选的,用于集成真实数据和机器学习
- 默认使用演示数据,可以直接运行 Step1 和 Step5
- 所有脚本使用 bash,在 macOS/Linux 上运行

## 许可

MIT License
