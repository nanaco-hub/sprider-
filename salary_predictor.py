import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def load_and_prepare_data(filepath="cleaned_recruitment_data.csv"):
    df = pd.read_csv(filepath, encoding="utf-8-sig")

    # 构建特征
    features = ["experience_years", "education_level",
                 "city_level", "skill_count"]

    # 行业类别编码 (one-hot)
    if "company_industry" in df.columns:
        industry_dummies = pd.get_dummies(
            df["company_industry"], prefix="industry"
        )
        df = pd.concat([df, industry_dummies], axis=1)
        features += list(industry_dummies.columns)

    X = df[features].copy()
    y = df["salary_avg"].copy()

    # 处理缺失值
    X = X.fillna(X.median())
    y = y.fillna(y.median())

    return X, y, features


def train_and_evaluate(X, y):
    # 划分训练集和测试集 (8:2)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"训练集样本数: {len(X_train)}")
    print(f"测试集样本数: {len(X_test)}")

    # 特征标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ========== 线性回归 ==========
    print("\n" + "=" * 60)
    print("1. 线性回归 (Linear Regression)")
    lr = LinearRegression()
    lr.fit(X_train_scaled, y_train)
    y_pred_lr = lr.predict(X_test_scaled)

    mae_lr = mean_absolute_error(y_test, y_pred_lr)
    rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
    r2_lr = r2_score(y_test, y_pred_lr)
    print(f"  平均绝对误差 (MAE): {mae_lr:.0f} 元")
    print(f"  均方根误差 (RMSE):  {rmse_lr:.0f} 元")
    print(f"  决定系数 (R²):      {r2_lr:.4f}")

    # 五折交叉验证
    cv_scores_lr = cross_val_score(
        lr, X_train_scaled, y_train, cv=5, scoring="r2"
    )
    print(f"  五折交叉验证 R²:    {cv_scores_lr.mean():.4f} "
          f"(±{cv_scores_lr.std():.4f})")

    # ========== 决策树回归 ==========
    print("\n" + "=" * 60)
    print("2. 决策树回归 (Decision Tree)")
    dt = DecisionTreeRegressor(
        max_depth=8, min_samples_split=10,
        min_samples_leaf=5, random_state=42
    )
    dt.fit(X_train_scaled, y_train)
    y_pred_dt = dt.predict(X_test_scaled)

    mae_dt = mean_absolute_error(y_test, y_pred_dt)
    rmse_dt = np.sqrt(mean_squared_error(y_test, y_pred_dt))
    r2_dt = r2_score(y_test, y_pred_dt)
    print(f"  平均绝对误差 (MAE): {mae_dt:.0f} 元")
    print(f"  均方根误差 (RMSE):  {rmse_dt:.0f} 元")
    print(f"  决定系数 (R²):      {r2_dt:.4f}")

    cv_scores_dt = cross_val_score(
        dt, X_train_scaled, y_train, cv=5, scoring="r2"
    )
    print(f"  五折交叉验证 R²:    {cv_scores_dt.mean():.4f} "
          f"(±{cv_scores_dt.std():.4f})")

    # ========== 随机森林回归 ==========
    print("\n" + "=" * 60)
    print("3. 随机森林回归 (Random Forest)")
    rf = RandomForestRegressor(
        n_estimators=200, max_depth=12,
        min_samples_split=10, min_samples_leaf=5,
        random_state=42, n_jobs=-1
    )
    rf.fit(X_train_scaled, y_train)
    y_pred_rf = rf.predict(X_test_scaled)

    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    r2_rf = r2_score(y_test, y_pred_rf)
    print(f"  平均绝对误差 (MAE): {mae_rf:.0f} 元")
    print(f"  均方根误差 (RMSE):  {rmse_rf:.0f} 元")
    print(f"  决定系数 (R²):      {r2_rf:.4f}")

    cv_scores_rf = cross_val_score(
        rf, X_train_scaled, y_train, cv=5, scoring="r2"
    )
    print(f"  五折交叉验证 R²:    {cv_scores_rf.mean():.4f} "
          f"(±{cv_scores_rf.std():.4f})")

    # ========== 结果对比 ==========
    print("\n" + "=" * 60)
    print("模型性能对比汇总")
    print(f"{'模型':<20} {'MAE':<12} {'RMSE':<12} {'R²':<10} "
          f"{'CV-R²':<10}")
    print("-" * 64)
    print(f"{'线性回归':<20} {mae_lr:<12.0f} {rmse_lr:<12.0f} "
          f"{r2_lr:<10.4f} {cv_scores_lr.mean():<10.4f}")
    print(f"{'决策树回归':<20} {mae_dt:<12.0f} {rmse_dt:<12.0f} "
          f"{r2_dt:<10.4f} {cv_scores_dt.mean():<10.4f}")
    print(f"{'随机森林回归':<20} {mae_rf:<12.0f} {rmse_rf:<12.0f} "
          f"{r2_rf:<10.4f} {cv_scores_rf.mean():<10.4f}")

    return {
        "linear_regression": {
            "model": lr, "mae": mae_lr, "rmse": rmse_lr,
            "r2": r2_lr, "cv_r2": cv_scores_lr.mean(),
        },
        "decision_tree": {
            "model": dt, "mae": mae_dt, "rmse": rmse_dt,
            "r2": r2_dt, "cv_r2": cv_scores_dt.mean(),
        },
        "random_forest": {
            "model": rf, "mae": mae_rf, "rmse": rmse_rf,
            "r2": r2_rf, "cv_r2": cv_scores_rf.mean(),
        },
    }, scaler


def feature_importance_analysis(model, feature_names):
    """特征重要性分析 (适用于线性回归的系数)"""
    if hasattr(model, "coef_"):
        coefs = model.coef_
        importance = pd.DataFrame({
            "feature": feature_names,
            "coefficient": coefs,
        })
        importance["abs_coef"] = importance["coefficient"].abs()
        importance = importance.sort_values("abs_coef", ascending=False)
        return importance
    return None


def predict_salary(model, scaler, features):
    """预测薪资接口"""
    features_scaled = scaler.transform([features])
    salary = model.predict(features_scaled)[0]
    return salary


if __name__ == "__main__":
    X, y, feature_names = load_and_prepare_data()
    results, scaler = train_and_evaluate(X, y)

    # 特征重要性
    lr_model = results["linear_regression"]["model"]
    importance_df = feature_importance_analysis(lr_model, feature_names)
    if importance_df is not None:
        print("\n" + "=" * 60)
        print("特征重要性分析 (线性回归系数)")
        print(importance_df.to_string(index=False))

    # 示例预测
    sample_features = [3.0, 3, 1, 5]  # 3年经验, 本科, 一线城市, 5项技能
    predicted = predict_salary(
        lr_model, scaler, sample_features
    )
    print(f"\n示例预测: 3年经验/本科/一线城市/5项技能 "
          f"=> 预测月薪 {predicted:.0f} 元")
