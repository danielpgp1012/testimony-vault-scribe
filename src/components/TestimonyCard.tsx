import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, User, FileAudio, Search, File, Clock, MapPin } from 'lucide-react';
import { Testimony } from '@/types/testimony';
import { format } from 'date-fns';
import { useTranslation } from 'react-i18next';

interface TestimonyCardProps {
  testimony: Testimony;
  onViewDetails: (testimony: Testimony) => void;
}

export function TestimonyCard({ testimony, onViewDetails }: TestimonyCardProps) {
  const { t } = useTranslation();
  const statusColors = {
    pending: "bg-accent/20 text-accent-foreground border-accent/30",
    processing: "bg-primary/15 text-primary border-primary/30",
    completed: "bg-emerald-50 text-emerald-700 border-emerald-200",
    failed: "bg-red-50 text-red-700 border-red-200"
  };

  // Get the first 50 characters of transcription
  const transcriptPreview = testimony.transcript
    ? testimony.transcript.length > 50
      ? `${testimony.transcript.substring(0, 50)}...`
      : testimony.transcript
    : null;

  // Format the recorded date
  const recordedDate = testimony.recorded_at
    ? format(new Date(testimony.recorded_at), 'PPP')  // Date string in YYYY-MM-DD format
    : testimony.created_at
      ? format(new Date(testimony.created_at), 'PPP')
      : 'Unknown';

  return (
    <Card className="w-full hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg font-semibold line-clamp-1">
            {testimony.user_file_name || t('testimonyCard.unknownFile')}
          </CardTitle>
          <Badge className={statusColors[testimony.transcript_status]}>
            {testimony.transcript_status.charAt(0).toUpperCase() + testimony.transcript_status.slice(1)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pb-3">
        <div className="space-y-3">
          {/* Church location */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4" />
            <span>{testimony.church_id || t('testimonyCard.unknownChurch')}</span>
          </div>

          {/* Recorded date */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{t('testimonyCard.recorded')}: {recordedDate}</span>
          </div>

          {/* Tags */}
          {testimony.tags && testimony.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {testimony.tags.map((tag, i) => (
                <Badge key={i} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}

          {/* Transcript preview */}
          {transcriptPreview && (
            <div className="bg-muted/50 rounded-md p-3 mt-3">
              <p className="text-sm text-muted-foreground italic">
                "{transcriptPreview}"
              </p>
            </div>
          )}

          {/* Status indicator */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <FileAudio className="h-4 w-4" />
            <span>
              {testimony.transcript_status === 'completed'
                ? 'Transcription complete'
                : testimony.transcript_status === 'processing'
                ? 'Transcribing...'
                : testimony.transcript_status === 'failed'
                ? 'Transcription failed'
                : 'Awaiting transcription'
              }
            </span>
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
