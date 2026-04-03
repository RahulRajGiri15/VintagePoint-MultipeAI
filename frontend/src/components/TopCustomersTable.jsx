import { useState, useEffect } from 'react';
import api from '../api';

const TopCustomersTable = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sorting state
  const [sortConfig, setSortConfig] = useState({ key: 'total_spend', direction: 'desc' });

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const response = await api.get('/top-customers');
        setData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner"></div>Loading Customers...</div>;
  if (error) return <div className="error-container">Error loading customers: {error}</div>;

  // Sorting logic
  const sortedData = [...data].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }
    return 0;
  });

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortIndicator = (key) => {
    if (sortConfig.key === key) {
      return sortConfig.direction === 'asc' ? ' 🔼' : ' 🔽';
    }
    return '';
  };

  return (
    <div className="card">
      <div className="panel-header">
        <h2 className="panel-title">Top 10 Customers</h2>
      </div>
      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th onClick={() => requestSort('name')} style={{cursor: 'pointer'}}>
                Name{getSortIndicator('name')}
              </th>
              <th onClick={() => requestSort('region')} style={{cursor: 'pointer'}}>
                Region{getSortIndicator('region')}
              </th>
              <th className="right-align" onClick={() => requestSort('total_spend')} style={{cursor: 'pointer'}}>
                Total Spend{getSortIndicator('total_spend')}
              </th>
              <th onClick={() => requestSort('churned')} style={{cursor: 'pointer'}}>
                Status{getSortIndicator('churned')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((customer) => (
              <tr key={customer.customer_id}>
                <td>{customer.name}</td>
                <td>{customer.region}</td>
                <td className="currency">${customer.total_spend.toLocaleString()}</td>
                <td>
                  <span className={`status-badge ${customer.churned ? 'status-churned' : 'status-active'}`}>
                    {customer.churned ? 'Churned' : 'Active'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TopCustomersTable;
