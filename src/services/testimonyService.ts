import { Testimony, TestimonyFormData, PaginatedResponse, PaginationParams } from '@/types/testimony';

const API_BASE_URL = 'http://localhost:8000';

export const fetchTestimonies = async (
  params?: PaginationParams & {
    church_id?: string;
    transcript_status?: string;
    tags?: string[];
  }
): Promise<PaginatedResponse<Testimony>> => {
  // Build query parameters
  const queryParams = new URLSearchParams();
  
  if (params?.page) queryParams.append('page', params.page.toString());
  if (params?.size) queryParams.append('size', params.size.toString());
  if (params?.church_id) queryParams.append('church_id', params.church_id);
  if (params?.transcript_status) queryParams.append('transcript_status', params.transcript_status);
  if (params?.tags && params.tags.length > 0) {
    params.tags.forEach(tag => queryParams.append('tags', tag));
  }
  
  const url = `${API_BASE_URL}/testimonies${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch testimonies: ${response.status} ${response.statusText}`);
  }
  
  return await response.json() as PaginatedResponse<Testimony>;
};

// Backward-compatible function for existing code
export const fetchTestimoniesSimple = async (): Promise<Testimony[]> => {
  const result = await fetchTestimonies({ page: 1, size: 50 });
  return result.items;
};

export const searchTestimonies = async (query: string): Promise<Testimony[]> => {
  if (!query || query.trim() === '') {
    // If no query, return all testimonies
    return fetchTestimoniesSimple();
  }
  
  const encodedQuery = encodeURIComponent(query.trim());
  const response = await fetch(`${API_BASE_URL}/testimonies/search/${encodedQuery}`);
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.status} ${response.statusText}`);
  }
  
  const searchResults = await response.json() as Testimony[];
  
  // Sort by recorded_at in descending order, with fallback to created_at for null values
  return searchResults.sort((a, b) => {
    const dateA = a.recorded_at || a.created_at;
    const dateB = b.recorded_at || b.created_at;
    return new Date(dateB).getTime() - new Date(dateA).getTime();
  });
};

// Enhanced search function with additional filters
export const searchTestimoniesWithFilters = async (
  query: string,
  filters?: {
    church_id?: string;
    transcript_status?: string;
    tags?: string[];
  }
): Promise<Testimony[]> => {
  // If no query, return filtered testimonies using the standard fetch method
  if (!query || query.trim() === '') {
    const result = await fetchTestimonies({ 
      page: 1, 
      size: 50,
      church_id: filters?.church_id,
      transcript_status: filters?.transcript_status,
      tags: filters?.tags
    });
    return result.items;
  }
  
  const encodedQuery = encodeURIComponent(query.trim());
  const queryParams = new URLSearchParams();
  
  if (filters?.church_id) queryParams.append('church_id', filters.church_id);
  if (filters?.transcript_status) queryParams.append('transcript_status', filters.transcript_status);
  if (filters?.tags && filters.tags.length > 0) {
    filters.tags.forEach(tag => queryParams.append('tags', tag));
  }
  
  const url = `${API_BASE_URL}/testimonies/search/${encodedQuery}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Search with filters failed: ${response.status} ${response.statusText}`);
  }
  
  const searchResults = await response.json() as Testimony[];
  
  // Sort by recorded_at in descending order, with fallback to created_at for null values
  return searchResults.sort((a, b) => {
    const dateA = a.recorded_at || a.created_at;
    const dateB = b.recorded_at || b.created_at;
    return new Date(dateB).getTime() - new Date(dateA).getTime();
  });
};

export const filterTestimonies = async (
  testimonies: Testimony[],
  filters: {
    status: string;
    church_id: string;
    tags: string[];
  }
): Promise<Testimony[]> => {
  const filteredTestimonies = testimonies.filter(testimony => {
    // Filter by status
    if (filters.status !== 'all' && testimony.transcript_status !== filters.status) {
      return false;
    }
    
    // Filter by church_id
    if (filters.church_id !== 'all' && testimony.church_id !== filters.church_id) {
      return false;
    }
    
    // Filter by tags (if any tag is selected, the testimony must have at least one of the selected tags)
    if (filters.tags.length > 0 && (!testimony.tags || !testimony.tags.some(tag => filters.tags.includes(tag)))) {
      return false;
    }
    
    return true;
  });
  
  // Sort by recorded_at in descending order, with fallback to created_at for null values
  return filteredTestimonies.sort((a, b) => {
    const dateA = a.recorded_at || a.created_at;
    const dateB = b.recorded_at || b.created_at;
    return new Date(dateB).getTime() - new Date(dateA).getTime();
  });
};

export const uploadTestimony = async (formData: TestimonyFormData): Promise<Testimony> => {
  // Create a new FormData instance for the HTTP request
  const requestFormData = new FormData();
  
  // Add church_id (convert enum to string value)
  requestFormData.append('church_id', formData.church_id);
  
  // Add recorded_at if provided
  if (formData.recorded_at) {
    requestFormData.append('recorded_at', formData.recorded_at);
  }
  
  // Add tags as a comma-separated string
  if (formData.tags && formData.tags.length > 0) {
    requestFormData.append('tags', formData.tags.join(','));
  }
  
  // Add the audio file - this is required by the backend
  if (formData.audioFile) {
    requestFormData.append('file', formData.audioFile);
  } else {
    throw new Error('Audio file is required');
  }
  
  // Send POST request to the backend API
  const response = await fetch(`${API_BASE_URL}/testimonies`, {
    method: 'POST',
    body: requestFormData,
    // No need to set Content-Type header as it's automatically set with FormData
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Upload failed: ${response.status} ${response.statusText} - ${errorText}`);
  }
  
  const result = await response.json();
  
  // Map the backend response to our frontend Testimony type
  const newTestimony: Testimony = {
    id: result.id,
    church_id: formData.church_id,
    tags: result.tags || formData.tags,
    transcript_status: result.transcript_status,
    transcript: result.transcript || undefined,
    created_at: result.created_at,
    updated_at: result.updated_at,
    recorded_at: result.recorded_at,
  };
  
  return newTestimony;
};
