
import { Testimony, TestimonyFormData } from '@/types/testimony';
import { mockTestimonies } from './mockData';

// Simulate delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// In-memory storage for the mock data
let testimonies = [...mockTestimonies];

export const fetchTestimonies = async (): Promise<Testimony[]> => {
  // Simulate API delay
  await delay(800);
  return [...testimonies];
};

export const searchTestimonies = async (query: string): Promise<Testimony[]> => {
  await delay(500);
  
  if (!query) return testimonies;
  
  const lowercaseQuery = query.toLowerCase();
  return testimonies.filter(
    testimony => 
      testimony.title.toLowerCase().includes(lowercaseQuery) ||
      testimony.speaker.toLowerCase().includes(lowercaseQuery) ||
      testimony.tags.some(tag => tag.toLowerCase().includes(lowercaseQuery)) ||
      (testimony.transcript && testimony.transcript.toLowerCase().includes(lowercaseQuery))
  );
};

export const filterTestimonies = async (
  testimonies: Testimony[],
  filters: {
    status: string;
    speaker: string;
    tags: string[];
  }
): Promise<Testimony[]> => {
  return testimonies.filter(testimony => {
    // Filter by status
    if (filters.status !== 'all' && testimony.transcriptStatus !== filters.status) {
      return false;
    }
    
    // Filter by speaker
    if (filters.speaker !== 'all' && testimony.speaker !== filters.speaker) {
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
  // Simulate API delay and processing
  await delay(1500);
  
  // Generate a unique ID
  const id = `testimony-${Date.now()}`;
  
  // Create a new testimony object
  const newTestimony: Testimony = {
    id,
    title: formData.title,
    speaker: formData.speaker,
    date: formData.date,
    tags: formData.tags,
    // In a real implementation, these would come from the APIs
    driveId: `mock-drive-id-${id}`,
    storageUrl: formData.audioFile ? URL.createObjectURL(formData.audioFile) : undefined,
    transcriptStatus: 'pending',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  
  // Add to the list
  testimonies = [newTestimony, ...testimonies];
  
  // Simulate the async transcription process
  simulateTranscriptionProcess(id);
  
  return newTestimony;
};

// Helper function to simulate the transcription process
const simulateTranscriptionProcess = async (testimonyId: string) => {
  // Change status to processing
  await delay(2000);
  testimonies = testimonies.map(t => 
    t.id === testimonyId 
      ? { ...t, transcriptStatus: 'processing' as const, updatedAt: new Date().toISOString() }
      : t
  );
  
  // Simulate transcription completion
  await delay(5000);
  
  // 90% chance of success, 10% chance of failure
  const success = Math.random() > 0.1;
  
  if (success) {
    const sampleTranscript = `This is a simulated transcript for testimony ${testimonyId}.
    
Thank you for giving me this opportunity to share my testimony. I've been attending this church for about three years now, and I want to share how God has been working in my life.

Before I found this community, I was struggling with feelings of isolation and purpose. I had moved to a new city for work, and while my career was going well, I felt disconnected from any meaningful relationships or spiritual guidance.

One Sunday morning, I decided to visit this church after seeing a flyer in my neighborhood. From the moment I walked in, I felt a sense of welcome that I hadn't experienced in a long time. The worship touched my heart, and the message that day spoke directly to my situation.

Over the past three years, I've grown in my faith through small groups, serving opportunities, and the consistent teaching from God's word. I've built friendships that feel like family, and I've found purpose in using my talents to serve others.

I just want to encourage anyone who might be feeling alone or searching for meaning - God has a place for you in His family. Thank you for listening to my story.`;
    
    testimonies = testimonies.map(t => 
      t.id === testimonyId 
        ? { 
            ...t, 
            transcriptStatus: 'completed' as const, 
            transcript: sampleTranscript,
            updatedAt: new Date().toISOString() 
          }
        : t
    );
  } else {
    testimonies = testimonies.map(t => 
      t.id === testimonyId 
        ? { ...t, transcriptStatus: 'failed' as const, updatedAt: new Date().toISOString() }
        : t
    );
  }
};
