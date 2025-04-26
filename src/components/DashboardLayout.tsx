
import React, { ReactNode, useState, useEffect } from 'react';
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
import { FileAudio, Home, Upload, Search, Info, LogOut, User } from 'lucide-react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { signOut } from '@/utils/auth';
import { supabase } from '@/integrations/supabase/client';
import { toast } from '@/components/ui/use-toast';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [userEmail, setUserEmail] = useState<string | null>(null);
  
  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/' },
    { icon: Upload, label: 'Upload', path: '/upload' },
    { icon: Search, label: 'Search', path: '/search' },
    { icon: Info, label: 'About', path: '/about' },
  ];
  
  useEffect(() => {
    // Get the current user on component mount
    const fetchUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        setUserEmail(user.email);
      }
    };
    
    fetchUser();
    
    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === 'SIGNED_OUT') {
          navigate('/auth');
        } else if (session?.user) {
          setUserEmail(session.user.email);
        }
      }
    );
    
    return () => subscription.unsubscribe();
  }, [navigate]);
  
  const handleSignOut = async () => {
    try {
      await signOut();
      toast({
        title: "Signed out successfully",
        description: "You have been signed out of your account",
      });
    } catch (error) {
      console.error('Sign out error:', error);
      toast({
        title: "Sign out failed",
        description: "There was a problem signing out",
        variant: "destructive",
      });
    }
  };
  
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
          
          <SidebarFooter className="p-4 space-y-2">
            {userEmail && (
              <div className="px-3 py-2 text-xs font-medium overflow-hidden text-ellipsis">
                Signed in as: {userEmail}
              </div>
            )}
            <Button 
              variant="outline" 
              className="w-full justify-start" 
              onClick={handleSignOut}
              size="sm"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign out
            </Button>
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
              <div className="flex items-center gap-2">
                <Button asChild variant="ghost" size="sm">
                  <Link to="/upload">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload New
                  </Link>
                </Button>
              </div>
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
