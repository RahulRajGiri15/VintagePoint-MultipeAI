from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

app = FastAPI()

# basic cors to allow react
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://vintage-point-multipe-ai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_csv(filename):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"couldn't find {filepath}")
        raise HTTPException(status_code=404, detail="File not found")
    
    df = pd.read_csv(filepath)
    # clean up nans for json processing
    df = df.where(pd.notna(df), None)
    return df.to_dict(orient="records")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/revenue")
def get_revenue():
    return load_csv("monthly_revenue.csv")


@app.get("/api/top-customers")
def get_top_customers():
    return load_csv("top_customers.csv")


@app.get("/api/categories")
def get_categories():
    return load_csv("category_performance.csv")


@app.get("/api/regions")
def get_regions():
    return load_csv("regional_analysis.csv")


@app.get("/api/summary")
def get_summary():
    # this endpoint just aggregates some top line info for the dashboard header
    try:
        customers = pd.read_csv(DATA_DIR / "customers_clean.csv")
        orders = pd.read_csv(DATA_DIR / "orders_clean.csv")
        revenue_df = pd.read_csv(DATA_DIR / "monthly_revenue.csv")
        top_cust = pd.read_csv(DATA_DIR / "top_customers.csv")

        total_customers = int(customers["customer_id"].nunique())
        total_orders = int(len(orders))
        total_revenue = float(revenue_df["total_revenue"].sum())

        churn_rate = 0.0
        if "churned" in top_cust.columns:
            full_orders = pd.read_csv(DATA_DIR / "orders_clean.csv")
            full_orders["order_date"] = pd.to_datetime(full_orders["order_date"], errors="coerce")
            
            completed = full_orders[full_orders["status"] == "completed"]
            unique_customers = completed["customer_id"].nunique()
            
            if unique_customers > 0:
                ref_date = completed["order_date"].max()
                cutoff = ref_date - timedelta(days=90)
                
                last_orders = completed.groupby("customer_id")["order_date"].max()
                churned_count = int((last_orders < cutoff).sum())
                churn_rate = round(churned_count / unique_customers * 100, 1)

        return {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "churn_rate": churn_rate,
        }

    except Exception as e:
        print(f"Summary endpoint error: {e}")
        raise HTTPException(status_code=404, detail="Run your pipeline first!")


if __name__ == "__main__":
    import uvicorn
    # run locally only
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
