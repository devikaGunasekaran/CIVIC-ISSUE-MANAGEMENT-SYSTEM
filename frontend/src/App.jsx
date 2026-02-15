import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ReportIssue from './pages/ReportIssue';
import AdminDashboard from './pages/AdminDashboard';
import Tracking from './pages/Tracking';
import ComplaintDetail from './pages/ComplaintDetail';
import NotificationPage from './pages/NotificationPage';
import AboutPage from './pages/AboutPage';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <div className="app-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/report" element={<ReportIssue />} />
            <Route path="/track" element={<Tracking />} />
            <Route path="/complaint/:id" element={<ComplaintDetail />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/notifications" element={<NotificationPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
