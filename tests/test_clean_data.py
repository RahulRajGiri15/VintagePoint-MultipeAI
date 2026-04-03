"""
tests/test_clean_data.py — Unit Tests for Data Cleaning Pipeline

Tests cover:
    - Email validation logic
    - Multi-format date parsing
    - Median filling logic
    - Status normalization
"""

import numpy as np
import pandas as pd
import pytest

# Add parent directory to path so we can import from project root
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from clean_data import is_valid_email, parse_order_date, clean_customers, clean_orders


class TestEmailValidation:
    """Tests for the is_valid_email function."""

    def test_valid_email(self):
        assert is_valid_email("user@example.com") is True

    def test_valid_email_subdomain(self):
        assert is_valid_email("user@mail.example.com") is True

    def test_missing_at_symbol(self):
        assert is_valid_email("userexample.com") is False

    def test_missing_dot_after_at(self):
        assert is_valid_email("user@examplecom") is False

    def test_empty_string(self):
        assert is_valid_email("") is False

    def test_none_value(self):
        assert is_valid_email(None) is False

    def test_nan_value(self):
        assert is_valid_email(np.nan) is False

    def test_whitespace_only(self):
        assert is_valid_email("   ") is False

    def test_email_with_spaces(self):
        assert is_valid_email(" user@example.com ") is True


class TestDateParsing:
    """Tests for the parse_order_date function."""

    def test_iso_format(self):
        result = parse_order_date("2023-01-15")
        assert result == pd.Timestamp("2023-01-15")

    def test_dd_mm_yyyy_format(self):
        result = parse_order_date("15/03/2023")
        assert result == pd.Timestamp("2023-03-15")

    def test_mm_dd_yyyy_format(self):
        result = parse_order_date("07-01-2023")
        assert result == pd.Timestamp("2023-07-01")

    def test_invalid_date(self):
        result = parse_order_date("invalid_date")
        assert pd.isna(result)

    def test_empty_string(self):
        result = parse_order_date("")
        assert pd.isna(result)

    def test_none_value(self):
        result = parse_order_date(None)
        assert pd.isna(result)

    def test_whitespace_handling(self):
        result = parse_order_date("  2023-01-15  ")
        assert result == pd.Timestamp("2023-01-15")


class TestMedianFilling:
    """Tests for median filling logic in clean_orders."""

    def test_median_fill_by_product(self):
        """Amount should be filled with median of same product."""
        df = pd.DataFrame({
            "order_id": ["O1", "O2", "O3"],
            "customer_id": ["C1", "C2", "C3"],
            "product": ["Laptop", "Laptop", "Laptop"],
            "amount": [1000.0, np.nan, 1200.0],
            "status": ["completed", "completed", "completed"],
            "order_date": ["2023-01-01", "2023-02-01", "2023-03-01"],
        })
        result = clean_orders(df)
        # Median of 1000 and 1200 = 1100
        assert result.loc[1, "amount"] == 1100.0

    def test_status_normalization(self):
        """Status values should be normalized."""
        df = pd.DataFrame({
            "order_id": ["O1", "O2", "O3"],
            "customer_id": ["C1", "C2", "C3"],
            "product": ["X", "X", "X"],
            "amount": [100, 200, 300],
            "status": ["done", "complete", "canceled"],
            "order_date": ["2023-01-01", "2023-02-01", "2023-03-01"],
        })
        result = clean_orders(df)
        assert result["status"].tolist() == ["completed", "completed", "cancelled"]

    def test_drop_rows_both_ids_missing(self):
        """Rows with both customer_id and order_id missing should be dropped."""
        df = pd.DataFrame({
            "order_id": ["O1", np.nan, "O3"],
            "customer_id": ["C1", np.nan, "C3"],
            "product": ["X", "X", "X"],
            "amount": [100, 200, 300],
            "status": ["completed", "completed", "completed"],
            "order_date": ["2023-01-01", "2023-02-01", "2023-03-01"],
        })
        result = clean_orders(df)
        assert len(result) == 2

    def test_order_year_month_column(self):
        """order_year_month column should be added in YYYY-MM format."""
        df = pd.DataFrame({
            "order_id": ["O1"],
            "customer_id": ["C1"],
            "product": ["X"],
            "amount": [100],
            "status": ["completed"],
            "order_date": ["2023-06-15"],
        })
        result = clean_orders(df)
        assert result.loc[0, "order_year_month"] == "2023-06"


class TestCustomerCleaning:
    """Tests for customer cleaning logic."""

    def test_email_lowercase(self):
        """Emails should be lowercased."""
        df = pd.DataFrame({
            "customer_id": ["C1"],
            "name": ["Test"],
            "email": ["USER@EMAIL.COM"],
            "signup_date": ["2023-01-01"],
            "region": ["North"],
        })
        result = clean_customers(df)
        assert result.loc[0, "email"] == "user@email.com"

    def test_whitespace_strip(self):
        """Name and region should have whitespace stripped."""
        df = pd.DataFrame({
            "customer_id": ["C1"],
            "name": ["  Test User  "],
            "email": ["test@email.com"],
            "signup_date": ["2023-01-01"],
            "region": ["  North  "],
        })
        result = clean_customers(df)
        assert result.loc[0, "name"] == "Test User"
        assert result.loc[0, "region"] == "North"

    def test_missing_region_filled(self):
        """Missing region should be filled with 'Unknown'."""
        df = pd.DataFrame({
            "customer_id": ["C1"],
            "name": ["Test"],
            "email": ["test@email.com"],
            "signup_date": ["2023-01-01"],
            "region": [np.nan],
        })
        result = clean_customers(df)
        assert result.loc[0, "region"] == "Unknown"

    def test_duplicate_removal(self):
        """Duplicate customer_ids should be removed, keeping most recent."""
        df = pd.DataFrame({
            "customer_id": ["C1", "C1"],
            "name": ["Old", "New"],
            "email": ["old@e.com", "new@e.com"],
            "signup_date": ["2023-01-01", "2024-01-01"],
            "region": ["North", "South"],
        })
        result = clean_customers(df)
        assert len(result) == 1
        assert result.loc[0, "email"] == "new@e.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
