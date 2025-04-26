
import { useState, useEffect } from 'react';
import { supabase } from "@/integrations/supabase/client";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function UserProfile() {
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState<string | null>(null);
  const [userAvatar, setUserAvatar] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    async function getUserProfile() {
      try {
        setLoading(true);
        
        // Get the current user
        const { data: { user } } = await supabase.auth.getUser();
        
        if (user) {
          setUserEmail(user.email);
          
          // If the user has a profile in the Supabase profiles table
          const { data: profileData } = await supabase
            .from('profiles')
            .select('full_name, avatar_url')
            .eq('id', user.id)
            .single();
            
          if (profileData) {
            setUserName(profileData.full_name || user.email?.split('@')[0] || 'User');
            setUserAvatar(profileData.avatar_url);
          } else {
            // Fallback if no profile exists yet
            setUserName(user.email?.split('@')[0] || 'User');
          }
        }
      } catch (error) {
        console.error('Error fetching user profile:', error);
      } finally {
        setLoading(false);
      }
    }
    
    getUserProfile();
  }, []);

  // Generate initials for the avatar fallback
  const initials = userName 
    ? userName.split(' ').map(name => name[0]).join('').toUpperCase()
    : 'U';

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>User Profile</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center gap-4">
        {loading ? (
          <>
            <Skeleton className="h-12 w-12 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-[200px]" />
              <Skeleton className="h-4 w-[150px]" />
            </div>
          </>
        ) : (
          <>
            <Avatar className="h-12 w-12">
              {userAvatar ? (
                <AvatarImage src={userAvatar} alt={userName || 'User'} />
              ) : null}
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{userName || 'User'}</p>
              <p className="text-xs text-muted-foreground">{userEmail}</p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
