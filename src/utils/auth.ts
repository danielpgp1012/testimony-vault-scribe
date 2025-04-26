
import { supabase } from "@/integrations/supabase/client";
import { Session } from "@supabase/supabase-js";

// Check if user is authenticated
export const isAuthenticated = async (): Promise<boolean> => {
  const { data: { session } } = await supabase.auth.getSession();
  return session !== null;
};

// Get current session
export const getCurrentSession = async (): Promise<Session | null> => {
  const { data: { session } } = await supabase.auth.getSession();
  return session;
};

// Sign out the user
export const signOut = async (): Promise<void> => {
  await supabase.auth.signOut();
};
