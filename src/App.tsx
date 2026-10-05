import { Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import Dashboard from "./pages/Dashboard";
import ActiveRules from "./pages/ActiveRules";
import CompareRules from "./pages/CompareRules";
import Documents from "./pages/Documents";


function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/rules" element={<ActiveRules />} />
        <Route path="/compare" element={<CompareRules />} />
        <Route path="/documents" element={<Documents />} />

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />
      </Route>
    </Routes>
  );
}

export default App;