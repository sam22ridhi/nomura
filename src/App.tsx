import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Auth from './pages/Auth';
import Landing from './pages/Landing';
import OrganizerDashboard from './pages/OrganizerDashboard';
import VolunteerDashboard from './pages/VolunteerDashboard';

function App() {
  return (
    <Routes>
      <Route path="/auth" element={<Auth />} />
      <Route path="/auth/callback" element={<Auth />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Landing />} />
        <Route path="volunteer" element={
          <ProtectedRoute requiredRole="volunteer">
            <VolunteerDashboard />
          </ProtectedRoute>
        } />
        <Route path="organizer" element={
          <ProtectedRoute requiredRole="organizer">
            <OrganizerDashboard />
          </ProtectedRoute>
        } />
      </Route>
    </Routes>
  );
}

export default App;