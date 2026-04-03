import { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer
} from 'recharts';
import api from '../api';

const RevenueChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRevenue = async () => {
      try {
        const response = await api.get('/revenue');
        setData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRevenue();
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner"></div>Loading Revenue...</div>;
  if (error) return <div className="error-container">Error loading revenue: {error}</div>;

  const formatYAxis = (tickItem) => {
    return `$${(tickItem / 1000).toFixed(1)}k`;
  };

  return (
    <div className="card full-width">
      <div className="panel-header">
        <h2 className="panel-title">Monthly Revenue Trend</h2>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(26,67,20,0.1)" vertical={false} />
            <XAxis dataKey="order_year_month" stroke="#426b38" tick={{fill: '#426b38'}} />
            <YAxis tickFormatter={formatYAxis} stroke="#426b38" tick={{fill: '#426b38'}} />
            <Tooltip 
              formatter={(value) => [`$${value.toLocaleString()}`, 'Total Revenue']}
              labelStyle={{ color: '#1a4314' }}
            />
            <Line 
              type="monotone" 
              dataKey="total_revenue" 
              stroke="#2f8522" 
              strokeWidth={3}
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RevenueChart;
