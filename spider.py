import scrapy
import json
import re
from scrapy import Request
from scrapy.exceptions import CloseSpider
from items import JobItem


class BossZhipinSpider(scrapy.Spider):
    name = "boss_zhipin"
    allowed_domains = ["zhipin.com"]
    base_url = "https://www.zhipin.com"

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.zhipin.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
        "DOWNLOAD_DELAY": 3.0,
        "CONCURRENT_REQUESTS": 8,
        "ITEM_PIPELINES": {
            "pipelines.DataCleaningPipeline": 300,
            "pipelines.MySQLPipeline": 400,
        },
    }

    def __init__(self, keyword="Python开发工程师", city="101280100", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        self.city = city
        self.page = 1
        self.max_pages = 20

    def start_requests(self):
        url = f"{self.base_url}/api/jobs/list"
        params = f"?query={self.keyword}&city={self.city}&page={self.page}"
        yield Request(url + params, callback=self.parse_job_list)

    def parse_job_list(self, response):
        data = json.loads(response.text)
        jobs = data.get("zpData", {}).get("jobList", [])
        if not jobs:
            self.logger.info("No more jobs found, stopping spider.")
            raise CloseSpider("No more data")

        for job in jobs:
            item = JobItem()
            item["job_name"] = job.get("jobName", "")
            item["company_name"] = job.get("brandName", "")
            item["salary_range"] = job.get("salaryDesc", "")
            item["city"] = job.get("cityName", "")
            item["district"] = job.get("districtName", "")
            item["experience"] = job.get("jobExperience", "")
            item["education"] = job.get("jobDegree", "")
            item["tags"] = ";".join(job.get("skills", []))
            item["source"] = "BOSS直聘"
            item["job_detail_url"] = self.base_url + \
                f"/job_detail/{job.get('jobId')}.html"

            yield Request(
                item["job_detail_url"],
                callback=self.parse_job_detail,
                meta={"item": item},
                dont_filter=True,
            )

        self.page += 1
        if self.page <= self.max_pages:
            next_url = f"{self.base_url}/api/jobs/list" \
                       f"?query={self.keyword}&city={self.city}&page={self.page}"
            yield Request(next_url, callback=self.parse_job_list)

    def parse_job_detail(self, response):
        item = response.meta["item"]
        desc_text = " ".join(
            response.css(".job-detail-section::text").getall()
        )
        item["job_description"] = desc_text.strip()
        yield item


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(BossZhipinSpider)
    process.start()
