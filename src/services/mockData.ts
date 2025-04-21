
import { Testimony } from '@/types/testimony';
import { format } from 'date-fns';

// Generate random dates between 1 month ago and now
const getRandomDate = () => {
  const now = new Date();
  const oneMonthAgo = new Date();
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
  
  return new Date(
    oneMonthAgo.getTime() + Math.random() * (now.getTime() - oneMonthAgo.getTime())
  );
};

const sampleTranscript = `Thank you for giving me this opportunity to share my testimony. 
I want to share how God worked in my life during a particularly challenging time last year.

When I lost my job unexpectedly, I felt lost and afraid about the future. For weeks, I struggled with doubt and worry about how I would support my family. During this difficult season, our church community stepped up in amazing ways. People brought meals, helped with job searches, and most importantly, prayed with us consistently.

Three months later, I received a job offer that was actually better than my previous position. The new role not only provided for our needs but also gave me more time with my family. Looking back, I can see how God was working even when I couldn't feel His presence.

This experience taught me to trust God's timing and provision. As Proverbs 3:5-6 says, "Trust in the LORD with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight."

I'm grateful for this church family and for God's faithfulness in my life. Thank you for listening.`;

// Generate sample testimonies
export const generateMockTestimonies = (): Testimony[] => {
  const speakers = ['John Smith', 'Mary Johnson', 'David Wilson', 'Sarah Davis', 'Michael Brown', 'Jennifer Lee'];
  const tagOptions = ['faith', 'healing', 'provision', 'family', 'guidance', 'prayer', 'community', 'service'];
  const statuses: ('pending' | 'processing' | 'completed' | 'failed')[] = ['pending', 'processing', 'completed', 'failed'];
  
  return Array.from({ length: 15 }, (_, i) => {
    const createdAt = getRandomDate();
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const randomTags = tagOptions
      .sort(() => 0.5 - Math.random())
      .slice(0, Math.floor(Math.random() * 4) + 1);
    
    return {
      id: `test-${i + 1}`,
      title: `Sunday Testimony ${i + 1}`,
      speaker: speakers[Math.floor(Math.random() * speakers.length)],
      date: format(createdAt, 'yyyy-MM-dd'),
      tags: randomTags,
      driveId: `mock-drive-id-${i}`,
      storageUrl: `https://example.com/storage/testimony-${i}.mp3`,
      transcriptStatus: status,
      transcript: status === 'completed' ? sampleTranscript : undefined,
      createdAt: createdAt.toISOString(),
      updatedAt: new Date().toISOString(),
    };
  });
};

// Mock testimony data
export const mockTestimonies = generateMockTestimonies();
