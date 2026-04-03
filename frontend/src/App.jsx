import './index.css';
import RevenueChart from './components/RevenueChart';
import TopCustomersTable from './components/TopCustomersTable';
import CategoryChart from './components/CategoryChart';
import RegionTable from './components/RegionTable';
import SummaryCards from './components/SummaryCards';

function App() {
  return (
    <div className="dashboard-container">
      <header>
        <h1>Executive Dashboard</h1>
        <div className="header-meta">Data Processing Pipeline Overview & Analytics</div>
      </header>

      <main>
        <SummaryCards />
        
        <div className="dashboard-grid">
          <RevenueChart />
          <CategoryChart />
          <TopCustomersTable />
          <RegionTable />
        </div>
      </main>
    </div>
  );
}

export default App;
