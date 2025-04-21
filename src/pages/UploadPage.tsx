
import React from 'react';
import { FileUpload } from '@/components/FileUpload';
import { TestimonyFormData } from '@/types/testimony';
import { uploadTestimony } from '@/services/testimonyService';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const UploadPage = () => {
  const navigate = useNavigate();

  const handleUpload = async (data: TestimonyFormData) => {
    try {
      // In a real app, this would handle the full upload flow
      await uploadTestimony(data);
      toast.success('Testimony uploaded successfully!');
      
      // Redirect to dashboard
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload testimony');
      throw error; // Re-throw to let the component handle the error state
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold md:text-3xl">Upload Testimony</h1>
        <p className="text-muted-foreground">
          Upload an MP3 recording of a testimony to transcribe
        </p>
      </div>

      <div className="mt-6">
        <FileUpload onUpload={handleUpload} />
      </div>

      <div className="bg-secondary/50 rounded-md p-4 mt-8">
        <h3 className="font-medium mb-2">Instructions</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
          <li>File must be in MP3 format</li>
          <li>Maximum file size: 50MB</li>
          <li>Recommended recording length: 2-5 minutes</li>
          <li>Fill in all required metadata for better organization</li>
          <li>Transcription will begin automatically after upload</li>
        </ul>
      </div>
    </div>
  );
};

export default UploadPage;
