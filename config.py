from pathlib import Path

# basic paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# source files
RAW_DATA_PATH = DATA_DIR / "raw"
RAW_CUSTOMERS = RAW_DATA_PATH / "customers.csv"
RAW_ORDERS = RAW_DATA_PATH / "orders.csv"
RAW_PRODUCTS = RAW_DATA_PATH / "products.csv"

# save locs for cleaned data
PROCESSED_DATA_PATH = DATA_DIR / "processed"
CLEAN_CUSTOMERS = PROCESSED_DATA_PATH / "customers_clean.csv"
CLEAN_ORDERS = PROCESSED_DATA_PATH / "orders_clean.csv"

# end output files for dashboard
MONTHLY_REVENUE = PROCESSED_DATA_PATH / "monthly_revenue.csv"
TOP_CUSTOMERS = PROCESSED_DATA_PATH / "top_customers.csv"
CATEGORY_PERFORMANCE = PROCESSED_DATA_PATH / "category_performance.csv"
REGIONAL_ANALYSIS = PROCESSED_DATA_PATH / "regional_analysis.csv"

# general config
CHURN_DAYS_THRESHOLD = 90
TOP_N_CUSTOMERS = 10

VALID_STATUSES = {"completed", "pending", "cancelled", "refunded"}
STATUS_NORMALIZATION = {
    "done": "completed",
    "complete": "completed",
    "canceled": "cancelled",
}
