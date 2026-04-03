import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import api from '../api';

const CategoryChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await api.get('/categories');
        setData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchCategories();
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner"></div>Loading Categories...</div>;
  if (error) return <div className="error-container">Error loading categories: {error}</div>;

  const colors = ['#1a4314', '#2f8522', '#426b38', '#5b8c5a', '#85a882'];

  const formatYAxis = (tickItem) => {
    return `$${(tickItem / 1000).toFixed(0)}k`;
  };

  return (
    <div className="card">
      <div className="panel-header">
        <h2 className="panel-title">Revenue by Category</h2>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(26,67,20,0.1)" horizontal={true} vertical={false}/>
            <XAxis type="number" tickFormatter={formatYAxis} stroke="#426b38" tick={{fill: '#426b38'}} />
            <YAxis dataKey="category" type="category" stroke="#426b38" tick={{fill: '#426b38'}} width={80} />
            <Tooltip 
              formatter={(value) => [`$${value.toLocaleString()}`, 'Revenue']}
              cursor={{fill: 'rgba(26,67,20,0.05)'}}
            />
            <Bar dataKey="total_revenue" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CategoryChart;
