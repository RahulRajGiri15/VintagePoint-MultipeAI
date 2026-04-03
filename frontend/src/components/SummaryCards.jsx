import { useState, useEffect } from 'react';
import api from '../api';

const SummaryCards = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/summary');
        setData(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading || !data) return null; // Or skeleton loader

  return (
    <div className="summary-cards">
      <div className="card">
        <div className="card-title">Total Revenue</div>
        <div className="card-value">${data.total_revenue.toLocaleString()}</div>
      </div>
      <div className="card">
        <div className="card-title">Total Customers</div>
        <div className="card-value">{data.total_customers.toLocaleString()}</div>
      </div>
      <div className="card">
        <div className="card-title">Total Orders</div>
        <div className="card-value">{data.total_orders.toLocaleString()}</div>
      </div>
      <div className="card">
        <div className="card-title">Overall Churn Rate</div>
        <div className="card-value" style={{ color: data.churn_rate > 30 ? 'var(--danger)' : 'var(--success)' }}>
          {data.churn_rate}%
        </div>
      </div>
    </div>
  );
};

export default SummaryCards;
