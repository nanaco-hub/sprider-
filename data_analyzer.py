import pandas as pd
from collections import Counter
import jieba
import jieba.analyse


def load_cleaned_data(filepath="cleaned_recruitment_data.csv"):
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    # 补充可能缺失的计算列
    if "education_label" not in df.columns and "education_level" in df.columns:
        edu_map = {0: "不限", 1: "高中", 2: "大专", 3: "本科", 4: "硕士", 5: "博士"}
        df["education_label"] = df["education_level"].map(edu_map)
    if "education_label" not in df.columns:
        df["education_label"] = "未知"
    if "city_level_label" not in df.columns and "city_level" in df.columns:
        cl_map = {1: "一线城市", 2: "新一线城市", 3: "其他城市"}
        df["city_level_label"] = df["city_level"].map(cl_map)
    if "city_level_label" not in df.columns:
        df["city_level_label"] = "未知"
    if "skills_list" not in df.columns and "tags" in df.columns:
        df["skills_list"] = df["tags"].apply(
            lambda x: [s.strip() for s in str(x).split(";") if s.strip()]
            if pd.notna(x) else []
        )
    if "skill_count" not in df.columns and "skills_list" in df.columns:
        df["skill_count"] = df["skills_list"].apply(len)
    return df


def analyze_job_distribution(df):
    """岗位地区分布与行业分布分析"""
    print("=" * 50)
    print("1. 岗位地区分布 Top 10")
    city_counts = df["city"].value_counts().head(10)
    for city, count in city_counts.items():
        print(f"  {city}: {count} 个岗位")

    print("\n2. 各城市平均薪资 Top 10")
    city_salary = df.groupby("city")["salary_avg"].mean() \
        .sort_values(ascending=False).head(10)
    for city, salary in city_salary.items():
        print(f"  {city}: {salary:.0f} 元/月")

    return city_counts, city_salary


def analyze_salary_distribution(df):
    """薪资分布多维度分析"""
    print("=" * 50)
    print("3. 不同岗位类型薪资对比")
    if "job_name" in df.columns:
        job_salary = df.groupby("job_name")["salary_avg"] \
            .agg(["mean", "median", "std", "count"]) \
            .sort_values("mean", ascending=False)
        print(job_salary.head(10).to_string())
    else:
        print("  缺少 job_name 字段，跳过。")
        job_salary = pd.DataFrame()

    print("\n4. 薪资与工作经验关系")
    if "experience_years" in df.columns:
        exp_bins = [0, 1, 3, 5, 10, 50]
        exp_labels = ["应届", "1-3年", "3-5年", "5-10年", "10年以上"]
        df["exp_group"] = pd.cut(
            df["experience_years"], bins=exp_bins,
            labels=exp_labels, right=False
        )
        exp_salary = df.groupby("exp_group", observed=True)["salary_avg"] \
            .agg(["mean", "median", "count"])
        print(exp_salary.to_string())
    else:
        print("  缺少 experience_years 字段，跳过。")
        df["exp_group"] = "未知"
        exp_salary = pd.DataFrame()

    print("\n5. 学历与薪资关系")
    if "education_level" in df.columns:
        edu_salary = df.groupby("education_level")["salary_avg"] \
            .agg(["mean", "median", "count"])
        print(edu_salary.to_string())
    else:
        print("  缺少 education_level 字段，跳过。")
        edu_salary = pd.DataFrame()

    return job_salary, exp_salary, edu_salary


def analyze_skill_requirements(df):
    """技能需求词频分析"""
    print("=" * 50)
    print("6. 热门技能关键词 Top 20")

    all_skills = []
    if "skills_list" in df.columns:
        for skills in df["skills_list"]:
            if isinstance(skills, str):
                try:
                    skills = eval(skills)
                except:
                    skills = []
            elif isinstance(skills, list):
                pass
            else:
                skills = []
            all_skills.extend(skills)

        skill_counter = Counter(all_skills)
        top_skills = skill_counter.most_common(20)
        for skill, count in top_skills:
            print(f"  {skill}: {count} 次")
    else:
        print("  缺少 skills_list 字段，跳过。")
        top_skills = []

    # 岗位描述文本关键词提取
    print("\n7. 岗位描述关键词 (TF-IDF)")
    if "job_description" in df.columns:
        all_descriptions = " ".join(
            df["job_description"].dropna().astype(str).tolist()
        )
        keywords = jieba.analyse.extract_tags(
            all_descriptions, topK=30, withWeight=True
        )
        for word, weight in keywords:
            print(f"  {word}: {weight:.4f}")
    else:
        print("  缺少 job_description 字段，跳过。")
        keywords = []

    return top_skills, keywords


def analyze_education_experience(df):
    """学历与经验要求交叉分析"""
    print("=" * 50)
    print("8. 各学历层次的经验要求分布")
    if "education_label" in df.columns and "exp_group" in df.columns:
        cross = pd.crosstab(
            df["education_label"],
            df["exp_group"],
            margins=True
        )
        print(cross.to_string())
    else:
        print("  缺少 education_label 或 exp_group 字段，跳过。")
        cross = pd.DataFrame()

    return cross


if __name__ == "__main__":
    df = load_cleaned_data()
    analyze_job_distribution(df)
    analyze_salary_distribution(df)
    analyze_skill_requirements(df)
    analyze_education_experience(df)
