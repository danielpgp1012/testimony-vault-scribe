
export interface Testimony {
  id: string;
  title: string;
  speaker: string;
  date: string;
  tags: string[];
  driveId?: string;
  storageUrl?: string;
  transcriptStatus: 'pending' | 'processing' | 'completed' | 'failed';
  transcript?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TestimonyFormData {
  title: string;
  speaker: string;
  date: string;
  tags: string[];
  audioFile?: File;
}
