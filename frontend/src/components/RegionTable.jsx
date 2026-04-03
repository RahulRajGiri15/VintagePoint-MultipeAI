import { useState, useEffect } from 'react';
import api from '../api';

const RegionTable = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRegions = async () => {
      try {
        const response = await api.get('/regions');
        setData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRegions();
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner"></div>Loading Regions...</div>;
  if (error) return <div className="error-container">Error loading regions: {error}</div>;

  return (
    <div className="card">
      <div className="panel-header">
        <h2 className="panel-title">Regional Performance</h2>
      </div>
      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Region</th>
              <th className="right-align">Customers</th>
              <th className="right-align">Orders</th>
              <th className="right-align">Revenue</th>
              <th className="right-align">Avg Rev/Cust</th>
            </tr>
          </thead>
          <tbody>
            {data.map((region) => (
              <tr key={region.region}>
                <td>{region.region}</td>
                <td className="currency">{region.number_of_customers}</td>
                <td className="currency">{region.number_of_orders}</td>
                <td className="currency">${region.total_revenue.toLocaleString()}</td>
                <td className="currency">${region.average_revenue_per_customer.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RegionTable;
