import argparse
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

from config import (
    CATEGORY_PERFORMANCE, CHURN_DAYS_THRESHOLD, CLEAN_CUSTOMERS,
    CLEAN_ORDERS, MONTHLY_REVENUE, PROCESSED_DATA_PATH,
    RAW_PRODUCTS, REGIONAL_ANALYSIS, TOP_CUSTOMERS, TOP_N_CUSTOMERS,
)

def load_data(customers_path=CLEAN_CUSTOMERS, orders_path=CLEAN_ORDERS, products_path=RAW_PRODUCTS):
    print("loading up cleaned data and product catalog...")
    c = pd.read_csv(customers_path)
    o = pd.read_csv(orders_path)
    p = pd.read_csv(products_path)
    o["order_date"] = pd.to_datetime(o["order_date"], errors="coerce")
    return c, o, p


def merge_data(o, c, p):
    print("merging everything together...")
    
    # attach customer info
    merged = o.merge(c, on="customer_id", how="left")
    missing_custs = merged["name"].isna().sum()
    if missing_custs > 0:
        print(f"note: {missing_custs} orders are mapped to customers that don't exist.")

    # attach products info
    full = merged.merge(p, left_on="product", right_on="product_name", how="left")
    
    return full


def calc_monthly_revenue(df, out_path=MONTHLY_REVENUE):
    comps = df[df["status"] == "completed"].copy()
    req = comps.groupby("order_year_month", as_index=False).agg(total_revenue=("amount", "sum")).sort_values("order_year_month")
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req.to_csv(out_path, index=False)
    print("saved monthly revenue.")
    return req


def calc_top_customers(df, n=TOP_N_CUSTOMERS, out_path=TOP_CUSTOMERS):
    comps = df[df["status"] == "completed"].copy()
    
    stats = comps.groupby("customer_id", as_index=False).agg(
        total_spend=("amount", "sum"),
        order_count=("order_id", "count")
    )
    
    # AOV and basic lifetime value
    stats["average_order_value"] = (stats["total_spend"] / stats["order_count"]).round(2)
    stats["customer_lifetime_value"] = stats["total_spend"]

    # pull in their demographic details
    info = df[["customer_id", "name", "region"]].drop_duplicates(subset=["customer_id"])
    res = stats.merge(info, on="customer_id", how="left")
    
    res = res.sort_values("total_spend", ascending=False).head(n).reset_index(drop=True)
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out_path, index=False)
    print("saved top customers.")
    return res


def calc_categories(df, out_path=CATEGORY_PERFORMANCE):
    comps = df[df["status"] == "completed"].copy()
    res = comps.groupby("category", as_index=False).agg(
        total_revenue=("amount", "sum"),
        average_order_value=("amount", "mean"),
        number_of_orders=("order_id", "count")
    )
    res["average_order_value"] = res["average_order_value"].round(2)
    res = res.sort_values("total_revenue", ascending=False)
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out_path, index=False)
    print("saved categories.")
    return res


def calc_regions(df, c_df, out_path=REGIONAL_ANALYSIS):
    comps = df[df["status"] == "completed"].copy()
    
    cust_counts = c_df.groupby("region", as_index=False).agg(number_of_customers=("customer_id", "nunique"))
    ord_counts = comps.groupby("region", as_index=False).agg(number_of_orders=("order_id", "count"), total_revenue=("amount", "sum"))
    
    res = cust_counts.merge(ord_counts, on="region", how="left")
    res["total_revenue"] = res["total_revenue"].fillna(0)
    res["number_of_orders"] = res["number_of_orders"].fillna(0).astype(int)
    res["average_revenue_per_customer"] = (res["total_revenue"] / res["number_of_customers"]).round(2)
    
    res = res.sort_values("total_revenue", ascending=False)
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out_path, index=False)
    print("saved regions.")
    return res


def flag_churn(df, top_cust_path=TOP_CUSTOMERS, days=CHURN_DAYS_THRESHOLD):
    comps = df[df["status"] == "completed"].copy()
    
    # evaluate churn based off the most recent date we have data for
    current_date = comps["order_date"].max()
    cutoff = current_date - timedelta(days=days)
    
    last_orders = comps.groupby("customer_id", as_index=False).agg(last_order=("order_date", "max"))
    last_orders["churned"] = last_orders["last_order"] < cutoff
    
    # write it back directly into the top customers dataframe
    top = pd.read_csv(top_cust_path)
    top = top.merge(last_orders[["customer_id", "churned"]], on="customer_id", how="left")
    top["churned"] = top["churned"].fillna(True) 
    
    top.to_csv(top_cust_path, index=False)
    print("added churn flags.")
    return top


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument("--output-dir", type=Path, default=PROCESSED_DATA_PATH)
    args = parser.parse_args()

    try:
        c, o, p = load_data(args.input_dir / "customers_clean.csv", args.input_dir / "orders_clean.csv")
        full = merge_data(o, c, p)

        # compute all the tables needed for the frontend
        calc_monthly_revenue(full, args.output_dir / "monthly_revenue.csv")
        calc_top_customers(full, output_path=args.output_dir / "top_customers.csv")
        calc_categories(full, args.output_dir / "category_performance.csv")
        calc_regions(full, c, args.output_dir / "regional_analysis.csv")
        flag_churn(full, args.output_dir / "top_customers.csv")

        print("analytics generation done!")

    except Exception as e:
        print(f"Error in analytics: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
