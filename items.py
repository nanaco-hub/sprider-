from scrapy import Item, Field


class JobItem(Item):
    job_name = Field()
    company_name = Field()
    salary_range = Field()
    city = Field()
    district = Field()
    experience = Field()
    education = Field()
    tags = Field()
    job_description = Field()
    source = Field()
    job_detail_url = Field()
    crawl_time = Field()
