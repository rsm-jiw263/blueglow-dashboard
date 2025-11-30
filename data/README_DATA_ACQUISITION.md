# 真实环境数据获取指南

本项目支持使用真实的海洋和气象观测数据。以下是获取和准备数据的步骤。

## 📥 需要下载的数据文件

将以下CSV文件放置到 `data/` 目录：

### 1. 水温数据 (Water Temperature)
**文件名**: `data/water_temp_lajolla.csv`

**数据源**: NOAA Tides & Currents  
**站点**: 9410230 (La Jolla, Scripps Pier)  
**产品类型**: Water Temperature

**下载步骤**:
1. 访问: https://tidesandcurrents.noaa.gov/waterlevels.html?id=9410230
2. 选择 "Water Temperature"
3. 设置日期范围（建议2024年全年）
4. 选择 "GMT" 时区
5. 选择 "Metric" 单位
6. 点击 "Download" → CSV格式

**所需列**:
- `t`: 时间戳
- `water_temp_c` 或 `v`: 水温（摄氏度）

### 2. 浪高数据 (Wave Height)
**文件名**: `data/waves_lajolla.csv`

**数据源**: NDBC (National Data Buoy Center)  
**浮标**: 46254 (SCRIPPS Nearshore)

**下载步骤**:
1. 访问: https://www.ndbc.noaa.gov/station_page.php?station=46254
2. 点击 "Historical data"
3. 选择年份（如2024）
4. 下载 "Standard Meteorological Data" (stdmet)
5. 解压并转换为CSV格式

**所需列**:
- `t` 或 `datetime`: 时间戳
- `WVHT` 或 `wave_height_m`: 显著浪高（米）

### 3. 风速数据 (Wind Speed)
**文件名**: `data/wind_lajolla.csv`

**数据源**: NOAA Tides & Currents 或 NDBC

**选项A - NOAA**:
1. 访问: https://tidesandcurrents.noaa.gov/waterlevels.html?id=9410230
2. 选择 "Wind"
3. 下载CSV

**选项B - NDBC**:
- 使用上面浮标46254的数据
- 提取 `WSPD` 列（风速，m/s）

**所需列**:
- `t`: 时间戳
- `wind_speed_mps` 或 `s` 或 `WSPD`: 风速（米/秒）

### 4. (可选) 潮位数据
**文件名**: `data/tide_lajolla.csv`

**数据源**: NOAA Tides & Currents  
**产品类型**: Water Level

## 📊 CSV格式示例

### water_temp_lajolla.csv
```csv
t,water_temp_c
2024-01-01 00:00,15.2
2024-01-01 01:00,15.3
2024-01-01 02:00,15.1
...
```

### waves_lajolla.csv
```csv
t,wave_height_m
2024-01-01 00:00,1.2
2024-01-01 01:00,1.3
2024-01-01 02:00,1.1
...
```

### wind_lajolla.csv
```csv
t,wind_speed_mps
2024-01-01 00:00,4.5
2024-01-01 01:00,5.2
2024-01-01 02:00,4.8
...
```

## 🔧 API方式获取（高级）

如果你熟悉编程，可以直接用API获取数据：

### NOAA API示例
```python
import requests
import pandas as pd

url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
params = {
    "product": "water_temperature",
    "application": "my_project",
    "begin_date": "20240101",
    "end_date": "20241231",
    "station": "9410230",
    "time_zone": "gmt",
    "units": "metric",
    "format": "json"
}

response = requests.get(url, params=params)
data = response.json()["data"]
df = pd.DataFrame(data)
df.to_csv("data/water_temp_lajolla.csv", index=False)
```

### NDBC数据直接读取
```python
import pandas as pd

# 2024年数据
url = "https://www.ndbc.noaa.gov/view_text_file.php?filename=46254h2024.txt.gz&dir=data/historical/stdmet/"
df = pd.read_csv(url, sep=r'\s+', skiprows=[1])
# 选择需要的列并保存
```

## ⚙️ 自动回退机制

如果CSV文件不存在或读取失败，notebook会自动使用**演示数据**：
- 基于季节性模式生成合理的环境数据
- 保证代码可以正常运行
- 在输出中会明确标注使用的是演示数据

## ✅ 验证数据

运行notebook时，你会看到类似输出：

```
✅ 成功读取 data/water_temp_lajolla.csv: 8760 条记录
✅ 成功读取 data/waves_lajolla.csv: 8760 条记录
✅ 成功读取 data/wind_lajolla.csv: 8760 条记录
✅ 成功合并所有数据源
```

或者：

```
⚠️  文件不存在: data/water_temp_lajolla.csv
📊 使用演示数据模式
```

## 📚 数据引用

如果在报告中使用真实数据，请引用：

**NOAA数据**:
> National Oceanic and Atmospheric Administration (NOAA). (2024). 
> Tides & Currents Station 9410230 - La Jolla, CA. 
> Retrieved from https://tidesandcurrents.noaa.gov/

**NDBC数据**:
> National Data Buoy Center (NDBC). (2024). 
> Station 46254 - SCRIPPS Nearshore, CA. 
> Retrieved from https://www.ndbc.noaa.gov/

## 🆘 常见问题

**Q: CSV列名和代码中的不一样怎么办？**  
A: 在notebook的 `load_series()` 函数调用中修改 `value_col` 参数为你实际的列名。

**Q: 数据有缺失值怎么办？**  
A: Notebook会自动用插值和回填方法处理缺失值。

**Q: 可以用其他年份的数据吗？**  
A: 可以！只需修改notebook中的日期筛选条件。

**Q: 我只下载了部分数据，其他的能自动填充吗？**  
A: 可以。如果某个文件不存在，只有该特征会使用演示数据，其他特征仍保持真实。

---

**准备好数据后，直接运行notebook即可！** 🚀
