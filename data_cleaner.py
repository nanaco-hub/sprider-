import pandas as pd


def load_data_from_db():
    from sqlalchemy import create_engine
    engine = create_engine(
        "mysql+pymysql://root:123456@localhost:3306/recruitment"
    )
    query = "SELECT * FROM jobs"
    df = pd.read_sql(query, engine)
    return df


def clean_data(df):
    print(f"原始数据量: {len(df)}")

    if df.empty:
        print("  数据为空，跳过清洗步骤。")
        return df

    df_clean = df.copy()

    # 1. 去除完全重复记录
    subset_cols = [c for c in ["job_name", "company_name", "city"]
                   if c in df_clean.columns]
    if subset_cols:
        dup_before = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=subset_cols)
        print(f"去除完全重复: {dup_before - len(df_clean)} 条")
    else:
        print("  缺少去重所需字段，跳过去重。")

    # 2. 处理缺失值
    null_counts = df_clean.isnull().sum()
    print(f"缺失值统计:\n{null_counts[null_counts > 0]}")

    for col in df_clean.columns:
        null_rate = df_clean[col].isnull().mean()

        if null_rate < 0.05:
            if df_clean[col].dtype in ["float64", "int64"]:
                df_clean[col] = df_clean[col].fillna(
                    df_clean[col].median()
                )
            else:
                df_clean[col] = df_clean[col].fillna(
                    df_clean[col].mode().iloc[0]
                    if not df_clean[col].mode().empty else "未知"
                )
        elif null_rate < 0.20:
            df_clean = df_clean.dropna(subset=[col])
        else:
            df_clean = df_clean.drop(columns=[col])

    # 3. 异常值检测 (IQR 方法)
    if "salary_avg" in df_clean.columns:
        Q1 = df_clean["salary_avg"].quantile(0.25)
        Q3 = df_clean["salary_avg"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outlier_mask = (df_clean["salary_avg"] < lower_bound) | \
                       (df_clean["salary_avg"] > upper_bound)
        print(f"薪资异常值: {outlier_mask.sum()} 条")
        df_clean = df_clean[~outlier_mask]

    # 4. 薪资单位统一处理 (k -> 元)
    if "salary_avg" in df_clean.columns:
        df_clean["salary_avg"] = df_clean["salary_avg"] * 1000

    # 5. 技能关键词提取
    if "tags" in df_clean.columns:
        df_clean["skills_list"] = df_clean["tags"].apply(
            lambda x: [s.strip() for s in str(x).split(";") if s.strip()]
            if pd.notna(x) else []
        )
        df_clean["skill_count"] = df_clean["skills_list"].apply(len)
    else:
        df_clean["skills_list"] = [[] for _ in range(len(df_clean))]
        df_clean["skill_count"] = 0

    print(f"清洗后数据量: {len(df_clean)}")
    return df_clean


def transform_features(df):
    if df.empty:
        return df
    df_t = df.copy()

    if "education_level" in df_t.columns:
        edu_mapping = {0: "不限", 1: "高中", 2: "大专",
                       3: "本科", 4: "硕士", 5: "博士"}
        df_t["education_label"] = df_t["education_level"].map(edu_mapping)
    else:
        df_t["education_label"] = "未知"

    if "city_level" in df_t.columns:
        city_level_mapping = {1: "一线城市", 2: "新一线城市",
                              3: "其他城市"}
        df_t["city_level_label"] = df_t["city_level"].map(city_level_mapping)
    else:
        df_t["city_level_label"] = "未知"

    return df_t


if __name__ == "__main__":
    df = load_data_from_db()
    df_clean = clean_data(df)
    df_final = transform_features(df_clean)
    df_final.to_csv("cleaned_recruitment_data.csv", index=False,
                     encoding="utf-8-sig")
    print("清洗完成，已保存至 cleaned_recruitment_data.csv")
