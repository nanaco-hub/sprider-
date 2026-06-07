# 招聘网站数据分析与可视化系统 — 使用教程

## 环境要求

- Python 3.7+
- 操作系统：Windows / Linux / macOS

---

## 一、安装依赖

在 `code/` 目录下打开终端，执行：

```bash
pip install scrapy pymysql sqlalchemy itemadapter pandas numpy scikit-learn matplotlib pyecharts jieba
```

**各依赖用途：**

| 包名 | 用途 |
|------|------|
| `scrapy` | 网络爬虫框架 |
| `pandas` | 数据清洗与分析 |
| `numpy` | 数值计算 |
| `scikit-learn` | 薪资预测模型 |
| `pyecharts` | 交互式可视化图表 |
| `matplotlib` | 静态图表 |
| `pymysql` / `sqlalchemy` | MySQL数据库存储 |
| `itemadapter` | Scrapy Item适配 |
| `jieba` | 中文分词 |

---

## 二、项目文件说明

```
code/
├── items.py              # 数据模型定义（JobItem）
├── spider.py             # Scrapy爬虫（BOSS直聘数据采集）
├── pipelines.py          # 数据清洗管道 + MySQL存储
├── data_cleaner.py       # Pandas数据清洗
├── data_analyzer.py      # 多维度数据分析
├── visualizer.py         # Pyecharts可视化
├── salary_predictor.py   # 薪资预测模型（3种算法对比）
└── main.py               # 系统主入口（一键执行全流程）
```

---

## 三、运行方式

### 方式一：一键全流程（强烈推荐）

```bash
python main.py
```

无需任何配置，无需数据库，自动生成200条演示数据，依次执行：
数据清洗 → 数据分析 → 薪资预测 → 可视化，全程约10秒。

> 如果之前已采集真实数据，系统会自动使用真实数据。

### 方式二：分步运行

#### 1. 数据采集

```bash
python spider.py
```

爬取 BOSS 直聘上 "Python开发工程师" 岗位数据，默认爬取 20 页。
可通过修改 `keyword` 和 `city` 参数调整搜索条件（在 spider.py 第31行）。

#### 2. 数据清洗

```bash
python data_cleaner.py
```

从 MySQL 读取原始数据 → 去重 → 缺失值填充 → IQR异常检测 → 单位转换 → 技能提取。
输出：`cleaned_recruitment_data.csv`

#### 3. 数据分析

```bash
python data_analyzer.py
```

从 CSV 读取清洗后数据，输出：
- 岗位地区分布 Top10
- 各城市平均薪资
- 不同岗位薪资对比
- 薪资与工作经验关系
- 学历与薪资关系
- 热门技能关键词

#### 4. 薪资预测

```bash
python salary_predictor.py
```

训练并对比 **线性回归 / 决策树 / 随机森林** 三种模型，输出：
- MAE、RMSE、R² 指标
- 五折交叉验证结果
- 特征重要性分析
- 示例薪资预测

#### 5. 可视化

```bash
python visualizer.py
```

生成 6 种交互式 HTML 图表至 `output/` 目录：
- `city_distribution.html` — 全国岗位分布地图
- `industry_pie.html` — 行业占比饼图
- `salary_boxplot.html` — 薪资箱线图
- `salary_exp_line.html` — 薪资与年限关系折线图
- `skill_wordcloud.html` — 技能词云
- `edu_salary_bar.html` — 学历薪资柱状图

---

## 四、数据库配置

使用 MySQL 存储时，需在 `data_cleaner.py`（第8行）和 `pipelines.py`（第37行）中修改为你的数据库信息：

```python
engine = create_engine(
    "mysql+pymysql://用户名:密码@localhost:3306/recruitment"
)
```

建议提前创建数据库：
```sql
CREATE DATABASE recruitment DEFAULT CHARSET utf8mb4;
```

如果不使用 MySQL，可跳过 `spider.py` 和 `pipelines.py`，直接准备一个 CSV 文件 `cleaned_recruitment_data.csv` 包含以下字段：
`job_name, salary_avg, city, city_level, experience_years, education_level, tags, job_description` 等。

---

## 五、常见问题

**Q: 运行 spider.py 提示 ModuleNotFoundError: No module named 'items'**
A: 确保 `items.py` 与 `spider.py` 在同一目录，直接运行 `python spider.py` 即可。

**Q: 爬虫报错或返回空数据**
A: 招聘网站可能有反爬更新，可尝试：
- 修改 `DOWNLOAD_DELAY` 增大请求间隔
- 更新 `User-Agent` 为最新浏览器标识
- 使用代理 IP

**Q: 没有 MySQL 数据库怎么办？**
A: 直接运行 `python main.py` 即可，系统会自动生成演示数据（200条），无需数据库。

**Q: 可视化图表在浏览器中打开是空白？**
A: Pyecharts 生成的 HTML 需要网络加载 ECharts 库，确保有网络连接，或使用 `pip install pyecharts-snapshot` 导出图片。
