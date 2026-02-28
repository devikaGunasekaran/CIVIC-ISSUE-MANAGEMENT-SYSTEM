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
import Footer from './components/Footer';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-white">
        <Sidebar />
        <div className="flex-1 flex flex-col min-h-screen overflow-x-hidden">
          <main className="flex-1">
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
          </main>
          <Footer />
        </div>
      </div>
    </Router>
  );
}

export default App;
