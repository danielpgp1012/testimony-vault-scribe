export interface Testimony {
  id: number;
  church_id?: string;
  tags?: string[];
  storage_url?: string;
  transcript_status: 'pending' | 'processing' | 'completed' | 'failed';
  transcript?: string;
  created_at: string;
  updated_at: string;
  audio_hash?: string;
  audio_duration_ms?: number;
  sample_rate?: number;
  channels?: number;
  user_file_name?: string;
  
  // Frontend-specific fields (not in backend)
  title?: string;
  driveId?: string;
}

export interface TestimonyFormData {
  // title: string;
  church_id: string;
  audioFile?: File;
}
