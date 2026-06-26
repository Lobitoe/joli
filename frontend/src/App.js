import "@/App.css";
import { BrowserRouter, Routes, Route, Outlet, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ProtectedRoute from "@/components/ProtectedRoute";

// Role gates — extracted to module scope so the ProtectedRoute prop array
// reference is stable across renders (prevents unnecessary re-renders).
const CLIENT_ROLES = ["client"];
const PRACTITIONER_ROLES = ["practitioner"];
const ADMIN_ROLES = ["admin"];

import LandingPage from "@/pages/LandingPage";
import BrowsePage from "@/pages/BrowsePage";
import PractitionerProfilePage from "@/pages/PractitionerProfilePage";
import BookingPage from "@/pages/BookingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ClientDashboard from "@/pages/ClientDashboard";
import PractitionerDashboard from "@/pages/PractitionerDashboard";
import PractitionerOnboarding from "@/pages/PractitionerOnboarding";
import ServicesManager from "@/pages/ServicesManager";
import PortfolioManager from "@/pages/PortfolioManager";
import AvailabilityManager from "@/pages/AvailabilityManager";
import AdminDashboard from "@/pages/AdminDashboard";
import HowItWorksPage from "@/pages/HowItWorksPage";
import DirectBookingPage from "@/pages/DirectBookingPage";
import BlogIndexPage from "@/pages/BlogIndexPage";
import BlogPostPage from "@/pages/BlogPostPage";
import VerificationPage from "@/pages/VerificationPage";
import AdminVerificationQueue from "@/pages/AdminVerificationQueue";
import AdminUsersPage from "@/pages/AdminUsersPage";
import NotFoundPage from "@/pages/NotFoundPage";

// Sends a logged-in user to their role-specific dashboard, and anyone
// unauthenticated to login. Backs the bare /dashboard route.
function DashboardRedirect() {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-[#6E5F50]">
        Loading...
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  const dest =
    user.role === "practitioner"
      ? "/dashboard/practitioner"
      : user.role === "admin"
      ? "/dashboard/admin"
      : "/dashboard/client";
  return <Navigate to={dest} replace />;
}

function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-[#F7F1E8] text-[#1F1A17]">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-center" richColors />
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/browse" element={<BrowsePage />} />
            <Route path="/practitioner/:id" element={<PractitionerProfilePage />} />
            <Route path="/book/:practitionerId/:serviceId" element={
              <ProtectedRoute roles={CLIENT_ROLES}>
                <BookingPage />
              </ProtectedRoute>
            } />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/how-it-works" element={<HowItWorksPage />} />
            <Route path="/blog" element={<BlogIndexPage />} />
            <Route path="/blog/:slug" element={<BlogPostPage />} />
            <Route path="/p/:slug" element={<DirectBookingPage />} />
            <Route path="/dashboard" element={<DashboardRedirect />} />
            <Route path="/dashboard/client" element={
              <ProtectedRoute roles={CLIENT_ROLES}>
                <ClientDashboard />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/practitioner" element={
              <ProtectedRoute roles={PRACTITIONER_ROLES}>
                <PractitionerDashboard />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/practitioner/onboarding" element={
              <ProtectedRoute roles={PRACTITIONER_ROLES}>
                <PractitionerOnboarding />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/practitioner/services" element={
              <ProtectedRoute roles={PRACTITIONER_ROLES}>
                <ServicesManager />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/practitioner/portfolio" element={
              <ProtectedRoute roles={PRACTITIONER_ROLES}>
                <PortfolioManager />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/practitioner/availability" element={
              <ProtectedRoute roles={PRACTITIONER_ROLES}>
                <AvailabilityManager />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/practitioner/verification" element={
              <ProtectedRoute roles={PRACTITIONER_ROLES}>
                <VerificationPage />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/admin" element={
              <ProtectedRoute roles={ADMIN_ROLES}>
                <AdminDashboard />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/admin/verifications" element={
              <ProtectedRoute roles={ADMIN_ROLES}>
                <AdminVerificationQueue />
              </ProtectedRoute>
            } />
            <Route path="/dashboard/admin/users" element={
              <ProtectedRoute roles={ADMIN_ROLES}>
                <AdminUsersPage />
              </ProtectedRoute>
            } />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
