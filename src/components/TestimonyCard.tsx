import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, User, FileAudio, Search } from 'lucide-react';
import { Testimony } from '@/types/testimony';
import { format } from 'date-fns';

interface TestimonyCardProps {
  testimony: Testimony;
  onViewDetails: (testimony: Testimony) => void;
}

export function TestimonyCard({ testimony, onViewDetails }: TestimonyCardProps) {
  const statusColors = {
    pending: "bg-yellow-100 text-yellow-800",
    processing: "bg-blue-100 text-blue-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800"
  };

  return (
    <Card className="w-full hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg font-semibold line-clamp-1">{testimony.church_id}</CardTitle>
          <Badge className={statusColors[testimony.transcript_status]}>
            {testimony.transcript_status.charAt(0).toUpperCase() + testimony.transcript_status.slice(1)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <User className="h-4 w-4" />
            <span>{testimony.church_id}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>{testimony.created_at ? format(new Date(testimony.created_at), 'PPP') : 'Unknown'}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <FileAudio className="h-4 w-4" />
            <span>{testimony.transcript_status === 'completed' ? 'Transcribed' : 'Awaiting transcription'}</span>
          </div>
          <div className="flex flex-wrap gap-1 mt-2">
            {testimony.tags?.map((tag, i) => (
              <Badge key={i} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          variant="outline" 
          className="w-full" 
          onClick={() => onViewDetails(testimony)}
        >
          <Search className="mr-2 h-4 w-4" />
          View Details
        </Button>
      </CardFooter>
    </Card>
  );
}
