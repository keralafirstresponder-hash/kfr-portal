import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import LandingPage from "@/pages/LandingPage";
import RegisterPage from "@/pages/RegisterPage";
import AdminLogin from "@/pages/AdminLogin";
import AdminLayout from "@/components/AdminLayout";
import AdminDashboard from "@/pages/AdminDashboard";
import AdminCandidates from "@/pages/AdminCandidates";
import AdminEvents from "@/pages/AdminEvents";
import AdminOrganisations from "@/pages/AdminOrganisations";
import AdminQuestions from "@/pages/AdminQuestions";
import AdminReports from "@/pages/AdminReports";
import TestPage from "@/pages/TestPage";
import CertificatePage from "@/pages/CertificatePage";

function Protected({ children }) {
  const { admin, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center text-slate-500">Loading…</div>;
  if (!admin) return <Navigate to="/admin/login" replace />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" richColors />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/test/:token" element={<TestPage />} />
          <Route path="/certificate/:token" element={<CertificatePage />} />

          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<Protected><AdminLayout /></Protected>}>
            <Route index element={<AdminDashboard />} />
            <Route path="candidates" element={<AdminCandidates />} />
            <Route path="events" element={<AdminEvents />} />
            <Route path="organisations" element={<AdminOrganisations />} />
            <Route path="questions" element={<AdminQuestions />} />
            <Route path="reports" element={<AdminReports />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
