export enum ChurchLocation {
  LAUSANNE = "Lausanne",
  ZURICH = "Zurich",
  BERN = "Bern",
  GINEBRA = "Ginebra"
}

export interface Testimony {
  id: number | string;
  church_id?: ChurchLocation | string;
  tags?: string[];
  transcript_status: 'pending' | 'processing' | 'completed' | 'failed';
  transcript?: string;
  created_at: string;
  updated_at: string;
  recorded_at?: string;
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
  church_id: ChurchLocation;
  audioFile?: File;
  recorded_at?: string;
  tags?: string[];
}

// Pagination types for fastapi-pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PaginationParams {
  page?: number;
  size?: number;
}
