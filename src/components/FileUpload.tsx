
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import { Calendar as CalendarIcon, X, UploadCloud } from 'lucide-react';
import { format } from 'date-fns';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { toast } from 'sonner';
import { TestimonyFormData } from '@/types/testimony';

interface FileUploadProps {
  onUpload: (data: TestimonyFormData) => Promise<void>;
}

const formSchema = z.object({
  title: z.string().min(1, "Title is required"),
  speaker: z.string().min(1, "Speaker name is required"),
  date: z.date({
    required_error: "Date is required",
  }),
  tags: z.array(z.string()).default([]),
  audioFile: z.instanceof(File, { message: "Audio file is required" })
});

export function FileUpload({ onUpload }: FileUploadProps) {
  const [tagInput, setTagInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: '',
      speaker: '',
      tags: [],
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.type !== 'audio/mpeg' && !file.name.endsWith('.mp3')) {
        toast.error('Please upload an MP3 file');
        return;
      }
      
      // Set default title from filename if empty
      if (!form.getValues().title) {
        const fileName = file.name.replace(/\.[^/.]+$/, ""); // Remove extension
        form.setValue('title', fileName);
      }
      
      form.setValue('audioFile', file);
    }
  }, [form]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/mpeg': ['.mp3']
    },
    maxFiles: 1
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

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      setIsUploading(true);
      await onUpload({
        title: values.title,
        speaker: values.speaker,
        date: format(values.date, 'yyyy-MM-dd'),
        tags: values.tags,
        audioFile: values.audioFile,
      });
      form.reset();
      toast.success('Testimony uploaded successfully');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload testimony');
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <Card className="w-full max-w-xl mx-auto">
      <CardContent className="pt-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div 
              {...getRootProps()} 
              className={cn(
                "dropzone",
                isDragActive && "active",
                audioFile && "border-green-500 bg-green-50"
              )}
            >
              <input {...getInputProps()} />
              <UploadCloud className="h-12 w-12 text-primary mb-2" />
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
                  <p className="text-sm text-muted-foreground">or click to browse</p>
                </div>
              )}
            </div>

            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title</FormLabel>
                  <FormControl>
                    <Input placeholder="Testimony title" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="speaker"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Speaker</FormLabel>
                  <FormControl>
                    <Input placeholder="Speaker name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="date"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Date</FormLabel>
                  <Popover>
                    <PopoverTrigger asChild>
                      <FormControl>
                        <Button
                          variant={"outline"}
                          className={cn(
                            "w-full pl-3 text-left font-normal",
                            !field.value && "text-muted-foreground"
                          )}
                        >
                          {field.value ? (
                            format(field.value, "PPP")
                          ) : (
                            <span>Pick a date</span>
                          )}
                          <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                        </Button>
                      </FormControl>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={field.value}
                        onSelect={field.onChange}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
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
              disabled={isUploading}
            >
              {isUploading ? 'Uploading...' : 'Upload Testimony'}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
