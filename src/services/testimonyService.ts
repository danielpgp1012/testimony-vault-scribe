import { Testimony, TestimonyFormData } from '@/types/testimony';
import { supabase } from '@/integrations/supabase/client';

// Simulate delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// In-memory storage for the mock data
let testimonies: Testimony[] = [];

export const fetchTestimonies = async (): Promise<Testimony[]> => {
  try {
    const { data, error } = await supabase
      .from('testimonies')
      .select('*')
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching testimonies from Supabase:', error);
      throw error;
    }
    
    // Map the database response to our Testimony type and convert the fields
    const mappedTestimonies = data.map(testimony => ({
      ...testimony,
      // Include any frontend-specific mappings/transformations
    })) as Testimony[];
    
    // Update our local cache
    testimonies = mappedTestimonies;
    
    return mappedTestimonies;
  } catch (error) {
    console.error('Failed to fetch testimonies from Supabase:', error);
    console.warn('Falling back to mock data');
    return [...testimonies];
  }
};

export const searchTestimonies = async (query: string): Promise<Testimony[]> => {
  try {
    if (!query) {
      // If no query, return all testimonies
      return fetchTestimonies();
    }
    
    const lowercaseQuery = query.toLowerCase();
    
    // Use Supabase search capabilities - this is a simple approach
    // For more advanced search, you might want to use PostgreSQL full-text search
    const { data, error } = await supabase
      .from('testimonies')
      .select('*')
      .or(`transcript.ilike.%${lowercaseQuery}%`)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Error searching testimonies in Supabase:', error);
      throw error;
    }
    
    // Also check tags (more complex to do in a single query)
    // We filter in memory after initial query
    return data.filter(testimony => 
      testimony.tags && testimony.tags.some(tag => 
        tag.toLowerCase().includes(lowercaseQuery)
      )
    ) as Testimony[];
  } catch (error) {
    console.error('Failed to search testimonies in Supabase:', error);
    console.warn('Falling back to local search');
    
    // Fallback to searching the local cache
    if (!query) return testimonies;
    
    const lowercaseQuery = query.toLowerCase();
    return testimonies.filter(
      testimony => 
        (testimony.title && testimony.title.toLowerCase().includes(lowercaseQuery)) ||
        (testimony.church_id && testimony.church_id.toLowerCase().includes(lowercaseQuery)) ||
        testimony.tags.some(tag => tag.toLowerCase().includes(lowercaseQuery)) ||
        (testimony.transcript && testimony.transcript.toLowerCase().includes(lowercaseQuery))
    );
  }
};

export const filterTestimonies = async (
  testimonies: Testimony[],
  filters: {
    status: string;
    church_id: string;
    tags: string[];
  }
): Promise<Testimony[]> => {
  return testimonies.filter(testimony => {
    // Filter by status
    if (filters.status !== 'all' && testimony.transcript_status !== filters.status) {
      return false;
    }
    
    // Filter by church_id
    if (filters.church_id !== 'all' && testimony.church_id !== filters.church_id) {
      return false;
    }
    
    // Filter by tags (if any tag is selected, the testimony must have at least one of the selected tags)
    if (filters.tags.length > 0 && !testimony.tags.some(tag => filters.tags.includes(tag))) {
      return false;
    }
    
    return true;
  });
};

export const uploadTestimony = async (formData: TestimonyFormData): Promise<Testimony> => {
  // Create a new FormData instance for the HTTP request
  const requestFormData = new FormData();
  
  // Add optional church_id (Currently not in our form, but backend expects it)
  requestFormData.append('church_id', formData.church_id); // Uncomment if church_id is needed
  
  // Add tags as a comma-separated string
  // if (formData.tags.length > 0) {
  //   requestFormData.append('tags', formData.tags.join(','));
  // }
  
  // Add the audio file - this is required by the backend
  if (formData.audioFile) {
    requestFormData.append('file', formData.audioFile);
  } else {
    throw new Error('Audio file is required');
  }
  
  try {
    // Send POST request to the backend API
    const response = await fetch('http://localhost:8000/testimonies', {
      method: 'POST',
      body: requestFormData,
      // No need to set Content-Type header as it's automatically set with FormData
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed with status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Map the backend response to our frontend Testimony type
    const newTestimony: Testimony = {
      id: result.id,
      // title: formData.title, // Using frontend values for fields not returned by backend
      church_id: formData.church_id,
      // date: formData.date,
      // tags: result.tags || formData.tags,
      storage_url: result.storage_url,
      transcript_status: result.transcript_status,
      transcript: result.transcript || undefined,
      created_at: result.created_at,
      updated_at: result.updated_at,
    };
    
    // Add to the local list to maintain consistency
    testimonies = [newTestimony, ...testimonies];
    
    return newTestimony;
  } catch (error) {
    console.error('Error uploading testimony:', error);
    
    // For backward compatibility, fallback to mock implementation
    console.warn('Falling back to mock implementation due to API error');
    
    // Simulate API delay and processing
    await delay(1500);
    
    // Generate a unique ID for mock data
    const mockId = Date.now();
    
    // Create a new testimony object
    const newTestimony: Testimony = {
      id: mockId,
      // title: formData.title,
      // speaker: formData.speaker,
      // date: formData.date,
      // tags: formData.tags,
      // In a real implementation, these would come from the APIs
      storage_url: formData.audioFile ? URL.createObjectURL(formData.audioFile) : undefined,
      transcript_status: 'pending',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    // Add to the list
    testimonies = [newTestimony, ...testimonies];
    
    return newTestimony;
  }
};
