import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { FindingDetailPage } from './pages/FindingDetailPage';
import { DashboardPage } from './pages/DashboardPage';
import { HistoryPage } from './pages/HistoryPage';
import { LandingPage } from './pages/LandingPage';
import { NewReviewPage } from './pages/NewReviewPage';
import { ProgressPage } from './pages/ProgressPage';
import { ResultPage } from './pages/ResultPage';
import { ToastProvider } from './features/reviews/ToastProvider';
import { ThemeProvider } from './features/theme/ThemeProvider';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/reviews/new" element={<NewReviewPage />} />
              <Route path="/reviews/:id/progress" element={<ProgressPage />} />
              <Route path="/reviews/:id" element={<ResultPage />} />
              <Route path="/reviews/:id/findings/:findingId" element={<FindingDetailPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/review" element={<Navigate to="/reviews/new" replace />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
