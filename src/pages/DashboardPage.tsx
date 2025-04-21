
import { UserProfile } from '@/components/UserProfile';

export default function DashboardPage() {
  return (
    <div className="grid gap-4 md:gap-8 max-w-4xl mx-auto">
      <UserProfile />
      
      <div className="grid gap-4 md:grid-cols-2">
        <div className="border rounded-lg p-4">
          <h3 className="text-lg font-medium mb-2">Recent Uploads</h3>
          <p className="text-muted-foreground">No recent uploads found.</p>
        </div>
        
        <div className="border rounded-lg p-4">
          <h3 className="text-lg font-medium mb-2">Quick Stats</h3>
          <p className="text-muted-foreground">No data available yet.</p>
        </div>
      </div>
    </div>
  );
}
