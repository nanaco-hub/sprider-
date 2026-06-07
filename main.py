"""
招聘网站数据分析与可视化系统 - 主入口
支持自动生成演示数据，无需外接数据库即可运行
"""
import os
import sys
import random


def generate_demo_data():
    """生成演示数据，供无数据库环境使用"""
    print("  正在生成演示数据...")
    import pandas as pd

    random.seed(42)
    n = 200

    cities = ["北京", "上海", "深圳", "广州", "杭州", "成都",
              "武汉", "南京", "西安", "长沙"]
    city_levels = {"北京": 1, "上海": 1, "深圳": 1, "广州": 1,
                   "杭州": 2, "成都": 2, "武汉": 2, "南京": 2,
                   "西安": 3, "长沙": 3}
    jobs = ["Python开发工程师", "Java开发工程师", "前端工程师",
            "数据分析师", "算法工程师", "产品经理",
            "测试工程师", "运维工程师", "UI设计师", "人工智能工程师"]
    companies = ["腾讯", "阿里巴巴", "字节跳动", "百度", "华为",
                 "美团", "京东", "网易", "小米", "快手"]
    skills_pool = ["Python", "Java", "JavaScript", "SQL", "Linux",
                   "Docker", "Kubernetes", "React", "Vue", "Spring",
                   "TensorFlow", "PyTorch", "Hadoop", "Spark", "Redis",
                   "MySQL", "MongoDB", "AWS", "Git", "Nginx",
                   "数据分析", "机器学习", "深度学习", "微服务", "DevOps"]

    data = []
    for _ in range(n):
        city = random.choice(cities)
        job = random.choice(jobs)
        exp = random.choice([0, 1, 2, 3, 5, 8, 10])
        edu = random.choice([2, 3, 3, 3, 4, 4, 5])

        base_salary = {
            "Python开发工程师": 18, "Java开发工程师": 17,
            "前端工程师": 15, "数据分析师": 18, "算法工程师": 25,
            "产品经理": 20, "测试工程师": 14, "运维工程师": 14,
            "UI设计师": 15, "人工智能工程师": 26
        }.get(job, 15)

        exp_bonus = exp * 1.2
        edu_bonus = (edu - 2) * 1.5
        city_bonus = {1: 1.3, 2: 1.0, 3: 0.8}.get(city_levels[city], 1.0)
        salary = round((base_salary + exp_bonus + edu_bonus) * city_bonus
                       * random.uniform(0.8, 1.2) * 1000, 0)

        n_skills = random.randint(2, 6)
        skills = ";".join(random.sample(skills_pool, n_skills))

        data.append({
            "job_name": job,
            "company_name": random.choice(companies),
            "salary_avg": salary,
            "city": city,
            "city_level": city_levels[city],
            "experience_years": exp,
            "education_level": edu,
            "tags": skills,
            "job_description": f"负责{job}相关工作，"
                              f"要求{exp}年经验，薪资面议。",
            "source": "演示数据",
        })

    df = pd.DataFrame(data)
    df["skills_list"] = df["tags"].apply(
        lambda x: [s.strip() for s in str(x).split(";") if s.strip()]
    )
    df["skill_count"] = df["skills_list"].apply(len)
    edu_map = {2: "大专", 3: "本科", 4: "硕士", 5: "博士"}
    df["education_label"] = df["education_level"].map(edu_map)
    city_label = {1: "一线城市", 2: "新一线城市", 3: "其他城市"}
    df["city_level_label"] = df["city_level"].map(city_label)
    df.to_csv("cleaned_recruitment_data.csv", index=False,
              encoding="utf-8-sig")
    print(f"  已生成 {n} 条演示数据至 cleaned_recruitment_data.csv")
    return df


def main():
    print("=" * 60)
    print("  招聘网站数据分析与可视化系统")
    print("=" * 60)

    # Step 1: 数据采集
    print("\n[步骤 1] 数据采集")
    print("  运行爬虫: scrapy crawl boss_zhipin")
    print("  建议先运行爬虫采集数据，或使用已有数据集。")
    print("  本次将使用", end="")

    # Step 2: 数据清洗
    print("\n[步骤 2] 数据清洗")
    from data_cleaner import clean_data, transform_features

    if os.path.exists("cleaned_recruitment_data.csv"):
        import pandas as pd
        print("  检测到已清洗数据文件，跳过清洗步骤。")
        df = pd.read_csv("cleaned_recruitment_data.csv",
                         encoding="utf-8-sig")
        # 补充可能缺失的计算列
        if "education_label" not in df.columns and "education_level" in df.columns:
            edu_map = {0:"不限",1:"高中",2:"大专",3:"本科",4:"硕士",5:"博士"}
            df["education_label"] = df["education_level"].map(edu_map)
        if "city_level_label" not in df.columns and "city_level" in df.columns:
            cl_map = {1:"一线城市",2:"新一线城市",3:"其他城市"}
            df["city_level_label"] = df["city_level"].map(cl_map)
        if "skills_list" not in df.columns and "tags" in df.columns:
            df["skills_list"] = df["tags"].apply(
                lambda x: [s.strip() for s in str(x).split(";") if s.strip()]
                if pd.notna(x) else []
            )
        if "skill_count" not in df.columns:
            df["skill_count"] = 0
    else:
        print("  尝试从数据库加载数据...")
        try:
            from data_cleaner import load_data_from_db
            df_raw = load_data_from_db()
            if df_raw.empty:
                print("  数据库无数据，生成演示数据代替。")
                df = generate_demo_data()
            else:
                print(f"  从数据库加载 {len(df_raw)} 条数据。")
                df_clean = clean_data(df_raw)
                df_final = transform_features(df_clean)
                df_final.to_csv(
                    "cleaned_recruitment_data.csv",
                    index=False, encoding="utf-8-sig"
                )
                print("  数据清洗完成并保存。")
                df = pd.read_csv("cleaned_recruitment_data.csv",
                                 encoding="utf-8-sig")
                # Jump to analysis
                from data_analyzer import (
                    load_cleaned_data, analyze_job_distribution,
                    analyze_salary_distribution, analyze_skill_requirements,
                    analyze_education_experience,
                )
                print("\n[步骤 3] 数据分析")
                analyze_job_distribution(df)
                analyze_salary_distribution(df)
                analyze_skill_requirements(df)
                analyze_education_experience(df)
                _run_prediction(df)
                _run_visualization(df)
                return
        except Exception as e:
            print(f"  数据库连接失败: {e}")
            print("  将生成演示数据代替。")
            df = generate_demo_data()

    # Step 3: 数据分析
    print("\n[步骤 3] 数据分析")
    from data_analyzer import (
        analyze_job_distribution,
        analyze_salary_distribution,
        analyze_skill_requirements,
        analyze_education_experience,
    )
    analyze_job_distribution(df)
    analyze_salary_distribution(df)
    analyze_skill_requirements(df)
    analyze_education_experience(df)

    _run_prediction(df)
    _run_visualization(df)


def _run_prediction(df):
    print("\n[步骤 4] 薪资预测模型")
    from salary_predictor import (
        load_and_prepare_data,
        train_and_evaluate,
        feature_importance_analysis,
    )
    X, y, feature_names = load_and_prepare_data()
    results, scaler = train_and_evaluate(X, y)

    lr_model = results["linear_regression"]["model"]
    importance_df = feature_importance_analysis(lr_model, feature_names)
    if importance_df is not None:
        print("\n特征重要性排名 (Top 5):")
        print(importance_df.head(5).to_string(index=False))

    # 示例预测
    from salary_predictor import predict_salary
    sample = [3.0, 3, 1, 5]
    pred = predict_salary(lr_model, scaler, sample)
    print(f"\n示例预测: 3年经验/本科/一线城市/5项技能 "
          f"=> 预测月薪 {pred:.0f} 元")


def _run_visualization(df):
    print("\n[步骤 5] 生成可视化图表")
    from visualizer import generate_all_charts
    generate_all_charts(df)

    print("\n" + "=" * 60)
    print("  系统运行完成!")
    print("  可视化图表已保存至 output/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
