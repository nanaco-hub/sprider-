import pandas as pd
from pyecharts.charts import Map, Pie, Boxplot, Line, Bar, WordCloud
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import matplotlib.pyplot as plt


def create_city_distribution_map(df):
    """全国岗位分布热力图"""
    city_counts = df["city"].value_counts()
    data = [(city, int(count)) for city, count in city_counts.items()]

    map_chart = (
        Map(init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT, width="900px", height="600px"
        ))
        .add(
            series_name="岗位数量",
            data_pair=data,
            maptype="china",
            is_map_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=True, font_size=10),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="全国IT岗位分布"),
            visualmap_opts=opts.VisualMapOpts(
                min_=min(city_counts),
                max_=max(city_counts),
                is_piecewise=True,
                pieces=[
                    {"min": 100, "label": "≥100"},
                    {"min": 50, "max": 99, "label": "50-99"},
                    {"min": 20, "max": 49, "label": "20-49"},
                    {"min": 1, "max": 19, "label": "1-19"},
                ],
            ),
        )
    )
    map_chart.render("output/city_distribution.html")
    print("已生成: output/city_distribution.html")


def create_industry_pie(df):
    """行业招聘需求占比饼图"""
    industry_counts = df["company_industry"].value_counts() \
        if "company_industry" in df.columns \
        else df["source"].value_counts()
    data = [(name, int(val)) for name, val in industry_counts.items()]

    pie = (
        Pie(init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT, width="800px", height="500px"
        ))
        .add(
            series_name="行业分布",
            data_pair=data,
            radius=["30%", "60%"],
            label_opts=opts.LabelOpts(
                formatter="{b}: {d}%"
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="招聘需求行业分布"),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_top="10%", pos_left="left"
            ),
        )
    )
    pie.render("output/industry_pie.html")
    print("已生成: output/industry_pie.html")


def create_salary_boxplot(df):
    """薪资箱线图"""
    job_types = df["job_name"].value_counts().head(8).index.tolist()
    data = []
    for job in job_types:
        salaries = df[df["job_name"] == job]["salary_avg"].tolist()
        data.append(salaries)

    boxplot = (
        Boxplot(init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT, width="1000px", height="600px"
        ))
        .add_xaxis(job_types)
        .add_yaxis(
            series_name="薪资分布",
            y_axis=data,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="各岗位薪资分布"),
            yaxis_opts=opts.AxisOpts(name="月薪 (元)"),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=30, font_size=10)
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )
    boxplot.render("output/salary_boxplot.html")
    print("已生成: output/salary_boxplot.html")


def create_salary_exp_line(df):
    """薪资与工作年限关系折线图"""
    exp_groups = df.groupby("experience_years")["salary_avg"].mean()
    exp_groups = exp_groups[exp_groups.index <= 20]

    line = (
        Line(init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT, width="800px", height="500px"
        ))
        .add_xaxis(
            [f"{x:.0f}年" for x in exp_groups.index]
        )
        .add_yaxis(
            series_name="平均月薪",
            y_axis=[round(v, 0) for v in exp_groups.values],
            label_opts=opts.LabelOpts(is_show=True),
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max")]
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="薪资与工作年限关系"),
            xaxis_opts=opts.AxisOpts(name="工作年限"),
            yaxis_opts=opts.AxisOpts(name="平均月薪 (元)"),
            tooltip_opts=opts.TooltipOpts(
                formatter="{b}: {c}元",
                trigger="axis",
            ),
        )
    )
    line.render("output/salary_exp_line.html")
    print("已生成: output/salary_exp_line.html")


def create_skill_wordcloud(df):
    """技能要求词云图"""
    all_skills = []
    for skills in df["skills_list"]:
        if isinstance(skills, str):
            import ast
            skills = ast.literal_eval(skills)
        all_skills.extend(skills)

    from collections import Counter
    skill_counter = Counter(all_skills)
    data = [(word, count) for word, count in skill_counter.most_common(50)]

    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT, width="800px", height="500px"
        ))
        .add(
            series_name="技能关键词",
            data_pair=data,
            word_size_range=[15, 80],
            shape="circle",
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="热门技能要求词云"),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
    )
    wordcloud.render("output/skill_wordcloud.html")
    print("已生成: output/skill_wordcloud.html")


def create_edu_salary_bar(df):
    """学历与平均薪资柱状图"""
    edu_salary = df.groupby("education_label")["salary_avg"] \
        .mean().sort_index()
    edu_order = ["不限", "高中", "大专", "本科", "硕士", "博士"]
    edu_salary = edu_salary.reindex(
        [e for e in edu_order if e in edu_salary.index]
    )

    bar = (
        Bar(init_opts=opts.InitOpts(
            theme=ThemeType.LIGHT, width="800px", height="500px"
        ))
        .add_xaxis(edu_salary.index.tolist())
        .add_yaxis(
            series_name="平均月薪",
            y_axis=[round(v, 0) for v in edu_salary.values],
            label_opts=opts.LabelOpts(
                is_show=True,
                formatter="{c}元",
                position="top",
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="学历与平均薪资关系"),
            xaxis_opts=opts.AxisOpts(name="学历"),
            yaxis_opts=opts.AxisOpts(name="平均月薪 (元)"),
        )
    )
    bar.render("output/edu_salary_bar.html")
    print("已生成: output/edu_salary_bar.html")


def generate_all_charts(df):
    import os
    os.makedirs("output", exist_ok=True)

    create_city_distribution_map(df)
    create_industry_pie(df)
    create_salary_boxplot(df)
    create_salary_exp_line(df)
    create_skill_wordcloud(df)
    create_edu_salary_bar(df)
    print("\n所有图表已生成至 output/ 目录")


if __name__ == "__main__":
    df = pd.read_csv("cleaned_recruitment_data.csv", encoding="utf-8-sig")
    generate_all_charts(df)
