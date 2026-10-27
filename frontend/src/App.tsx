import { Navigate, Outlet, Route, Routes } from 'react-router-dom';

import { AppShell } from './app/AppShell';
import { useMode } from './features/mode/ModeContext';
import { BusinessHomePage } from './pages/BusinessHomePage';
import { ChooseModePage } from './pages/ChooseModePage';
import { HistoryPage } from './pages/HistoryPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { NotBuiltYetPage } from './pages/NotBuiltYetPage';
import { SettingsPage } from './pages/SettingsPage';
import { SharedHisaabPage } from './pages/SharedHisaabPage';
import { WorkerHomePage } from './pages/WorkerHomePage';

/** Requires a chosen mode before any dashboard can render. */
function ModeGate() {
  const { hasChosenMode } = useMode();
  return hasChosenMode ? <Outlet /> : <Navigate to="/choose-mode" replace />;
}

/** Sends "/" to the dashboard for the current mode. */
function ModeHomeRedirect() {
  const { mode } = useMode();
  return <Navigate to={mode === 'worker' ? '/worker' : '/business'} replace />;
}

export function App() {
  return (
    <Routes>
      <Route path="/choose-mode" element={<ChooseModePage />} />
      <Route element={<ModeGate />}>
        <Route element={<AppShell />}>
          <Route index element={<ModeHomeRedirect />} />
          <Route path="business" element={<BusinessHomePage />} />
          <Route path="worker" element={<WorkerHomePage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="shared" element={<SharedHisaabPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="not-built" element={<NotBuiltYetPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
