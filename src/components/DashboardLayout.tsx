
import React, { ReactNode, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarTrigger,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/sidebar';
import { FileAudio, Home, Upload, Search, Info, LogOut } from 'lucide-react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { supabase } from '@/integrations/supabase/client';
import { User } from '@supabase/supabase-js';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  
  useEffect(() => {
    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user ?? null);
        
        // Redirect to login if not authenticated
        if (event === 'SIGNED_OUT') {
          navigate('/auth');
        }
      }
    );
    
    // Check current session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      if (!session) {
        navigate('/auth');
      }
    });
    
    return () => subscription.unsubscribe();
  }, [navigate]);
  
  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };
  
  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/' },
    { icon: Upload, label: 'Upload', path: '/upload' },
    { icon: Search, label: 'Search', path: '/search' },
    { icon: Info, label: 'About', path: '/about' },
  ];
  
  // If not authenticated, don't show the dashboard
  if (!user) {
    return null;
  }
  
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <Sidebar>
          <SidebarHeader className="flex justify-center items-center p-4">
            <div className="flex gap-2 items-center">
              <FileAudio className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-semibold">Testimony Vault</h1>
            </div>
          </SidebarHeader>
          
          <SidebarContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.path}>
                  <SidebarMenuButton asChild className={location.pathname === item.path ? "bg-accent" : ""}>
                    <Link to={item.path} className="flex items-center gap-2">
                      <item.icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>
          
          <SidebarFooter className="p-4 flex flex-col gap-4">
            {user && (
              <div className="flex flex-col items-center gap-2">
                <div className="text-sm font-medium">
                  {user.email || user.user_metadata.full_name || 'User'}
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </Button>
              </div>
            )}
            <div className="text-xs text-center text-muted-foreground">
              Testimony Vault © {new Date().getFullYear()}
            </div>
          </SidebarFooter>
        </Sidebar>
        
        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <header className="h-14 border-b flex items-center px-4 sticky top-0 z-10 bg-background">
            <SidebarTrigger className="mr-2 lg:hidden" />
            <div className="w-full flex items-center justify-between">
              <h2 className="text-lg font-medium">
                {menuItems.find(item => item.path === location.pathname)?.label || 'Testimony Vault'}
              </h2>
              <Button asChild variant="ghost" size="sm">
                <Link to="/upload">
                  <Upload className="h-4 w-4 mr-2" />
                  Upload New
                </Link>
              </Button>
            </div>
          </header>
          
          <main className="flex-1 overflow-auto p-4 md:p-6">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
