import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { X, UploadCloud } from 'lucide-react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { toast } from 'sonner';
import { TestimonyFormData, ChurchLocation } from '@/types/testimony';

interface FileUploadProps {
  onUpload: (data: TestimonyFormData) => Promise<void>;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB in bytes

const formSchema = z.object({
  church_id: z.nativeEnum(ChurchLocation, { message: "Please select a church location" }),
  audioFile: z.instanceof(File, { message: "Audio file is required" })
    .refine((file) => file.size <= MAX_FILE_SIZE, "File size must be less than 10 MB"),
  tags: z.array(z.string()).default([]),
  recorded_at: z.string().optional()
});

export function FileUpload({ onUpload }: FileUploadProps) {
  const [tagInput, setTagInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      church_id: ChurchLocation.LAUSANNE,
      tags: [],
      recorded_at: ''
    },
  });

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors.some((error: any) => error.code === 'file-too-large')) {
        toast.error('File size must be less than 10 MB');
        return;
      }
      if (rejection.errors.some((error: any) => error.code === 'file-invalid-type')) {
        toast.error('Please upload an MP3 file');
        return;
      }
    }
    
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      form.setValue('audioFile', file);
    }
  }, [form]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/mpeg': ['.mp3']
    },
    maxFiles: 1,
    maxSize: MAX_FILE_SIZE
  });

  const addTag = () => {
    if (tagInput.trim() && !form.getValues().tags.includes(tagInput.trim())) {
      const updatedTags = [...form.getValues().tags, tagInput.trim()];
      form.setValue('tags', updatedTags);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    const updatedTags = form.getValues().tags.filter(tag => tag !== tagToRemove);
    form.setValue('tags', updatedTags);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  const audioFile = form.watch('audioFile');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const values = form.getValues();
    
    if (!values.audioFile) {
      toast.error('Please select an audio file');
      return;
    }

    if (!values.church_id) {
      toast.error('Please select a church location');
      return;
    }

    try {
      setIsUploading(true);
      await onUpload({
        church_id: values.church_id,
        audioFile: values.audioFile,
        recorded_at: values.recorded_at || undefined,
      });
      form.reset();
      form.setValue('church_id', ChurchLocation.LAUSANNE); // Reset to default
      toast.success('Testimony uploaded successfully');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload testimony');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="w-full max-w-xl mx-auto">
      <CardContent className="pt-6">
        <Form {...form}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div 
              {...getRootProps()} 
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
                "hover:border-primary/50 hover:bg-muted/50",
                isDragActive && "border-primary bg-muted",
                audioFile && "border-green-500 bg-green-50"
              )}
            >
              <input {...getInputProps()} />
              <UploadCloud className="h-12 w-12 text-primary mb-2 mx-auto" />
              {audioFile ? (
                <div className="text-center">
                  <p className="font-medium">{audioFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="font-medium">Drag &amp; drop your MP3 file here</p>
                  <p className="text-sm text-muted-foreground">or click to browse (max 10 MB)</p>
                </div>
              )}
            </div>

            <FormField
              control={form.control}
              name="church_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Church Location</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a church location" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {Object.values(ChurchLocation).map((location) => (
                        <SelectItem key={location} value={location}>
                          {location}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="recorded_at"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Recorded Date (Optional)</FormLabel>
                  <FormControl>
                    <Input 
                      type="date" 
                      placeholder="When was this recorded?" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormItem>
              <FormLabel>Tags</FormLabel>
              <div className="flex">
                <Input
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Add tags (press Enter)"
                  className="flex-1"
                />
                <Button 
                  type="button" 
                  onClick={addTag} 
                  variant="secondary"
                  className="ml-2"
                >
                  Add
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {form.watch('tags').map((tag, i) => (
                  <Badge key={i} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => removeTag(tag)}
                    />
                  </Badge>
                ))}
              </div>
            </FormItem>

            <Button 
              type="submit" 
              className="w-full" 
              disabled={isUploading || !audioFile}
            >
              {isUploading ? 'Uploading...' : 'Upload Testimony'}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
