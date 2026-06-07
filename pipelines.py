import re
import pymysql
from itemadapter import ItemAdapter


class DataCleaningPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        salary_raw = adapter.get("salary_range")
        salary_min, salary_max = self._parse_salary(salary_raw)
        adapter["salary_min"] = salary_min
        adapter["salary_max"] = salary_max

        city_raw = adapter.get("city", "")
        adapter["province"] = self._infer_province(city_raw)
        adapter["city_level"] = self._get_city_level(city_raw)

        exp_raw = adapter.get("experience", "")
        adapter["experience_years"] = self._parse_experience(exp_raw)

        edu_raw = adapter.get("education", "")
        adapter["education_level"] = self._parse_education(edu_raw)

        adapter["crawl_time"] = spider.crawler.stats.get_value(
            "start_time"
        ).strftime("%Y-%m-%d %H:%M:%S")

        return item

    def _parse_salary(self, text):
        if not text:
            return None, None
        pattern = r"(\d+)[kK]?[-~–—](\d+)[kK]?"
        match = re.search(pattern, text)
        if match:
            return float(match.group(1)), float(match.group(2))
        single = re.search(r"(\d+)[kK]", text)
        if single:
            val = float(single.group(1))
            return val, val
        return None, None

    def _infer_province(self, city):
        province_map = {
            "北京": "北京", "上海": "上海", "广州": "广东",
            "深圳": "广东", "杭州": "浙江", "成都": "四川",
            "武汉": "湖北", "南京": "江苏", "西安": "陕西",
        }
        for key, prov in province_map.items():
            if key in city:
                return prov
        return "其他"

    def _get_city_level(self, city):
        tier1 = ["北京", "上海", "广州", "深圳"]
        tier1_5 = ["成都", "杭州", "武汉", "南京", "重庆",
                   "西安", "苏州", "天津", "长沙", "郑州"]
        for c in tier1:
            if c in city:
                return 1
        for c in tier1_5:
            if c in city:
                return 2
        return 3

    def _parse_experience(self, text):
        if not text:
            return 0
        pattern = r"(\d+)[-~–—](\d+)"
        match = re.search(pattern, text)
        if match:
            return (float(match.group(1)) + float(match.group(2))) / 2
        single = re.search(r"(\d+)", text)
        if single:
            return float(single.group(1))
        return 0

    def _parse_education(self, text):
        level_map = {
            "博士": 5, "硕士": 4, "本科": 3,
            "大专": 2, "高中": 1, "不限": 0,
        }
        for key, val in level_map.items():
            if key in text:
                return val
        return 0


class MySQLPipeline:
    def open_spider(self, spider):
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="recruitment",
            charset="utf8mb4",
        )
        self.cursor = self.connection.cursor()
        self._create_table()

    def close_spider(self, spider):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def _create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_name VARCHAR(200),
            company_name VARCHAR(200),
            salary_min FLOAT,
            salary_max FLOAT,
            salary_avg FLOAT GENERATED ALWAYS AS
                ((salary_min + salary_max) / 2) STORED,
            city VARCHAR(50),
            province VARCHAR(50),
            city_level INT,
            experience VARCHAR(50),
            experience_years FLOAT,
            education VARCHAR(50),
            education_level INT,
            tags TEXT,
            job_description TEXT,
            source VARCHAR(50),
            crawl_time DATETIME,
            INDEX idx_job_name (job_name),
            INDEX idx_city (city),
            INDEX idx_salary_avg (salary_avg)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        self.cursor.execute(sql)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        sql = """
        INSERT INTO jobs (
            job_name, company_name, salary_min, salary_max,
            city, province, city_level, experience,
            experience_years, education, education_level,
            tags, job_description, source, crawl_time
        ) VALUES (
            %(job_name)s, %(company_name)s,
            %(salary_min)s, %(salary_max)s,
            %(city)s, %(province)s, %(city_level)s,
            %(experience)s, %(experience_years)s,
            %(education)s, %(education_level)s,
            %(tags)s, %(job_description)s,
            %(source)s, %(crawl_time)s
        )
        """
        self.cursor.execute(sql, adapter.asdict())
        self.connection.commit()
        return item
