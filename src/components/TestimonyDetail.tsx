import React from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogFooter 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Calendar, MapPin, FileAudio, Tag, File, Clock } from 'lucide-react';
import { Testimony } from '@/types/testimony';
import { format } from 'date-fns';

interface TestimonyDetailProps {
  testimony: Testimony | null;
  open: boolean;
  onClose: () => void;
}

export function TestimonyDetail({ testimony, open, onClose }: TestimonyDetailProps) {
  if (!testimony) return null;

  const statusColors = {
    pending: "bg-yellow-100 text-yellow-800",
    processing: "bg-blue-100 text-blue-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800"
  };

  // Format the recorded date
  const recordedDate = testimony.recorded_at 
    ? format(new Date(testimony.recorded_at), 'PPP')
    : testimony.created_at 
      ? format(new Date(testimony.created_at), 'PPP')
      : 'Unknown';

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <div className="flex justify-between items-center">
            <DialogTitle className="text-xl font-semibold pr-4">
              {testimony.user_file_name || 'Unknown File'}
            </DialogTitle>
            <Badge className={statusColors[testimony.transcript_status]}>
              {testimony.transcript_status.charAt(0).toUpperCase() + testimony.transcript_status.slice(1)}
            </Badge>
          </div>
        </DialogHeader>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-4">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Church Location:</span>
            <span className="font-medium">{testimony.church_id || 'Unknown'}</span>
          </div>
          
          {testimony.user_file_name && (
            <div className="flex items-center gap-2">
              <File className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">File:</span>
              <span className="font-medium truncate">{testimony.user_file_name}</span>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Recorded:</span>
            <span className="font-medium">{recordedDate}</span>
          </div>
          
          <div className="flex items-center gap-2">
            <FileAudio className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Uploaded:</span>
            <span className="font-medium">{format(new Date(testimony.created_at), 'PPP p')}</span>
          </div>
          
          {testimony.tags && testimony.tags.length > 0 && (
            <div className="flex items-center gap-2 md:col-span-2">
              <Tag className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Tags:</span>
              <div className="flex flex-wrap gap-1">
                {testimony.tags.map((tag, i) => (
                  <Badge key={i} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <Separator />
        
        <div className="flex-1 overflow-y-auto py-4">
          <h3 className="font-semibold mb-2">Transcript</h3>
          {testimony.transcript_status === 'completed' && testimony.transcript ? (
            <div className="whitespace-pre-wrap text-sm">
              {testimony.transcript}
            </div>
          ) : testimony.transcript_status === 'processing' ? (
            <div className="flex flex-col items-center justify-center py-8 space-y-2 text-center">
              <div className="rounded-full bg-blue-100 p-3">
                <FileAudio className="h-6 w-6 text-blue-600 animate-pulse-slow" />
              </div>
              <p className="text-muted-foreground">Transcription in progress...</p>
            </div>
          ) : testimony.transcript_status === 'failed' ? (
            <div className="text-sm text-red-500">
              Transcription failed. Please try again later.
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              Transcript not available yet. Transcription will start soon.
            </div>
          )}
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
