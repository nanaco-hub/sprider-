## 环境要求

- Python 3.7+
- 操作系统：Windows

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
## 二、数据库配置

使用 MySQL 存储时，需在 `data_cleaner.py`（第8行）和 `pipelines.py`（第37行）中修改为你的数据库信息：

```python
engine = create_engine(
    "mysql+pymysql://用户名:密码@localhost:3306/recruitment"
)
```

建议提前创建数据库：
```sql
CREATE DATABASE IF NOT EXISTS recruitment;
USE recruitment;

CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(200),
    company_name VARCHAR(200),
    salary_min FLOAT,
    salary_max FLOAT,
    city VARCHAR(50),
    province VARCHAR(50),
    experience VARCHAR(50),
    education VARCHAR(50),
    tags TEXT,
    job_description TEXT,
    source VARCHAR(50),
    crawl_time DATETIME
);
```

如果不使用 MySQL，可跳过 `spider.py` 和 `pipelines.py`，直接准备一个 CSV 文件 `cleaned_recruitment_data.csv` 包含以下字段：
`job_name, salary_avg, city, city_level, experience_years, education_level, tags, job_description` 等。
