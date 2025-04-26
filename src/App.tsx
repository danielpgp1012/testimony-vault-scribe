
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { DashboardLayout } from '@/components/DashboardLayout';
import DashboardPage from "@/pages/DashboardPage";
import UploadPage from "@/pages/UploadPage";
import SearchPage from "@/pages/SearchPage";
import AboutPage from "@/pages/AboutPage";
import AuthPage from "@/pages/AuthPage";
import NotFound from "@/pages/NotFound";
import { AuthGuard } from "@/components/AuthGuard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          
          {/* Protected routes */}
          <Route element={<AuthGuard />}>
            <Route path="/" element={
              <DashboardLayout>
                <DashboardPage />
              </DashboardLayout>
            } />
            <Route path="/upload" element={
              <DashboardLayout>
                <UploadPage />
              </DashboardLayout>
            } />
            <Route path="/search" element={
              <DashboardLayout>
                <SearchPage />
              </DashboardLayout>
            } />
            <Route path="/about" element={
              <DashboardLayout>
                <AboutPage />
              </DashboardLayout>
            } />
          </Route>
          
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
