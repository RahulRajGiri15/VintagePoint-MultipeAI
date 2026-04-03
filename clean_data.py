import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    CLEAN_CUSTOMERS, CLEAN_ORDERS, PROCESSED_DATA_PATH,
    RAW_CUSTOMERS, RAW_DATA_PATH, RAW_ORDERS,
    STATUS_NORMALIZATION, VALID_STATUSES,
)

def is_valid_email(email):
    # simple check for @ and dot
    if not isinstance(email, str) or not email.strip():
        return False
    email = email.strip()
    return "@" in email and "." in email.split("@")[-1]


def parse_order_date(date_str):
    # tries a bunch of formats because data is messy
    if not isinstance(date_str, str) or not date_str.strip():
        return pd.NaT

    date_str = date_str.strip()
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]

    for fmt in formats:
        try:
            return pd.Timestamp(datetime.strptime(date_str, fmt))
        except:
            continue

    # fallback
    try:
        return pd.to_datetime(date_str)
    except:
        return pd.NaT


def load_data(customers_path=RAW_CUSTOMERS, orders_path=RAW_ORDERS):
    print("loading raw CSVs...")
    if not customers_path.exists():
        raise FileNotFoundError(f"Missing customers file: {customers_path}")
    if not orders_path.exists():
        raise FileNotFoundError(f"Missing orders file: {orders_path}")

    c_df = pd.read_csv(customers_path)
    o_df = pd.read_csv(orders_path)
    print(f"loaded {len(c_df)} customers and {len(o_df)} orders.")
    return c_df, o_df


def clean_customers(df):
    print("cleaning customers...")
    df = df.copy()

    # drop whitespaces so deduplication actually works
    for col in ["name", "region"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": np.nan, "": np.nan})

    df["signup_date"] = df["signup_date"].apply(parse_order_date)

    # keep the newest signup date if dupes exist
    df = df.sort_values("signup_date", ascending=False, na_position="last")
    df = df.drop_duplicates(subset=["customer_id"], keep="first")
    df = df.sort_values("customer_id").reset_index(drop=True)

    df["email"] = df["email"].astype(str).str.strip().str.lower()
    df["email"] = df["email"].replace({"nan": np.nan, "": np.nan})

    df["is_valid_email"] = df["email"].apply(is_valid_email)

    df["signup_date"] = pd.to_datetime(df["signup_date"]).dt.strftime("%Y-%m-%d")
    df["signup_date"] = df["signup_date"].replace({"NaT": np.nan})

    # fill empty regions
    df["region"] = df["region"].fillna("Unknown")

    return df


def clean_orders(df):
    print("cleaning orders...")
    df = df.copy()

    # drop garbage rows if everything is basically missing
    mask = df["customer_id"].isna() & df["order_id"].isna()
    df = df[~mask].reset_index(drop=True)

    df["order_date"] = df["order_date"].apply(parse_order_date)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    
    # fill amount with product median, or overall median if totally broke
    prod_medians = df.groupby("product")["amount"].transform("median")
    df["amount"] = df["amount"].fillna(prod_medians)
    df["amount"] = df["amount"].fillna(df["amount"].median())

    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["status"] = df["status"].replace(STATUS_NORMALIZATION)
    
    # warn if weird statuses pop up
    weird = ~df["status"].isin(VALID_STATUSES)
    if weird.any():
        print("warning: found some weird order statuses.")

    df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")

    return df


def generate_report(cb, ca, ob, oa):
    print("\n--- Cleaning Report ---")
    print(f"Customers: dropped {len(cb) - len(ca)} dupes. Final count: {len(ca)}")
    print(f"Orders: dropped {len(ob) - len(oa)} bad rows. Final count: {len(oa)}")
    print("-----------------------\n")


def save_data(c_df, o_df, c_out=CLEAN_CUSTOMERS, o_out=CLEAN_ORDERS):
    c_out.parent.mkdir(parents=True, exist_ok=True)
    c_df.to_csv(c_out, index=False)
    o_df.to_csv(o_out, index=False)
    print("saved cleaned csvs to processed folder.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=RAW_DATA_PATH)
    parser.add_argument("--output-dir", type=Path, default=PROCESSED_DATA_PATH)
    args = parser.parse_args()

    try:
        raw_cust, raw_ord = load_data(args.input_dir / "customers.csv", args.input_dir / "orders.csv")
        clean_cust = clean_customers(raw_cust)
        clean_ord = clean_orders(raw_ord)

        generate_report(raw_cust, clean_cust, raw_ord, clean_ord)
        
        save_data(clean_cust, clean_ord, args.output_dir / "customers_clean.csv", args.output_dir / "orders_clean.csv")
        print("data cleaning completely done!")
    
    except Exception as e:
        print(f"Error during clean data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
