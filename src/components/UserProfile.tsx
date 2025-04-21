
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { supabase } from '@/integrations/supabase/client';
import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

export function UserProfile() {
  const navigate = useNavigate();
  const user = supabase.auth.getUser();
  
  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle>Welcome to Testimony Vault</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <Avatar className="h-12 w-12">
            <div className="bg-primary h-full w-full grid place-items-center text-primary-foreground font-medium">
              {user ? user.data.user?.email?.charAt(0).toUpperCase() || 'U' : 'U'}
            </div>
          </Avatar>
          <div>
            <div className="font-medium">
              {user ? user.data.user?.email || user.data.user?.user_metadata?.full_name || 'User' : 'Guest'}
            </div>
            <div className="text-sm text-muted-foreground">
              {user ? user.data.user?.email : 'Not signed in'}
            </div>
          </div>
        </div>
        <p className="text-muted-foreground">
          You are successfully signed in. You can now upload and manage testimony recordings.
        </p>
        <Button onClick={() => navigate('/upload')} className="mt-2">
          Upload Testimony
        </Button>
      </CardContent>
    </Card>
  );
}
