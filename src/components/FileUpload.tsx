import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { X, UploadCloud, FileAudio, Trash2, Calendar } from 'lucide-react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { toast } from 'sonner';
import { TestimonyFormData, ChurchLocation } from '@/types/testimony';
import { useTranslation } from 'react-i18next';

interface FileUploadProps {
  onUpload: (data: TestimonyFormData) => Promise<void>;
}

interface FileWithDate {
  file: File;
  recorded_at?: string;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB in bytes

export function FileUpload({ onUpload }: FileUploadProps) {
  const { t } = useTranslation();
  const [tagInput, setTagInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{[key: string]: boolean}>({});
  const [fileDates, setFileDates] = useState<{[key: string]: string}>({});

  // Create form schema with translated messages
  const formSchema = z.object({
    church_id: z.nativeEnum(ChurchLocation, { message: t('form.selectChurch') }),
    audioFiles: z.array(z.instanceof(File))
      .min(1, t('form.minOneFile'))
      .refine((files) => files.every(file => file.size <= MAX_FILE_SIZE), t('form.fileSizeLimit')),
    tags: z.array(z.string()).default([])
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      church_id: ChurchLocation.LAUSANNE,
      audioFiles: [],
      tags: []
    },
  });

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors.some((error: any) => error.code === 'file-too-large')) {
        toast.error(t('toast.fileTooLarge'));
        return;
      }
      if (rejection.errors.some((error: any) => error.code === 'file-invalid-type')) {
        toast.error(t('toast.invalidFileType'));
        return;
      }
    }

    if (acceptedFiles.length > 0) {
      const currentFiles = form.getValues().audioFiles || [];
      const newFiles = [...currentFiles, ...acceptedFiles];
      form.setValue('audioFiles', newFiles);

      // Automatically set the last modified date for each new file as the default recorded_at date
      setFileDates(prev => {
        const newDates = { ...prev };

        acceptedFiles.forEach(file => {
          const fileKey = `${file.name}-${file.size}`;

          // Only set the date if it's not already set (to preserve manual overrides)
          if (!newDates[fileKey]) {
            // Get the last modified date from the file and format it as YYYY-MM-DD
            const lastModified = new Date(file.lastModified);
            const formattedDate = lastModified.toISOString().split('T')[0]; // YYYY-MM-DD format
            newDates[fileKey] = formattedDate;
          }
        });

        return newDates;
      });
    }
  }, [form]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/mpeg': ['.mp3']
    },
    multiple: true,
    maxSize: MAX_FILE_SIZE
  });

  const removeFile = (indexToRemove: number) => {
    const currentFiles = form.getValues().audioFiles;
    const fileToRemove = currentFiles[indexToRemove];
    const updatedFiles = currentFiles.filter((_, index) => index !== indexToRemove);
    form.setValue('audioFiles', updatedFiles);

    // Remove the date for this file
    if (fileToRemove) {
      const fileKey = `${fileToRemove.name}-${fileToRemove.size}`;
      setFileDates(prev => {
        const newDates = { ...prev };
        delete newDates[fileKey];
        return newDates;
      });
    }
  };

  const updateFileDate = (file: File, date: string) => {
    const fileKey = `${file.name}-${file.size}`;
    setFileDates(prev => {
      const newDates = { ...prev, [fileKey]: date };

      // If this is the first date being set, apply it to all unset files
      if (date && Object.keys(prev).filter(key => prev[key]).length === 0) {
        const currentFiles = form.getValues().audioFiles;
        const updatedDates = { ...newDates };

        currentFiles.forEach(f => {
          const fKey = `${f.name}-${f.size}`;
          if (!prev[fKey]) {
            updatedDates[fKey] = date;
          }
        });

        return updatedDates;
      }

      return newDates;
    });
  };

  const getFileDate = (file: File): string => {
    const fileKey = `${file.name}-${file.size}`;
    return fileDates[fileKey] || '';
  };

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

  const audioFiles = form.watch('audioFiles');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const values = form.getValues();

    if (!values.audioFiles || values.audioFiles.length === 0) {
      toast.error(t('toast.selectFiles'));
      return;
    }

    if (!values.church_id) {
      toast.error(t('toast.selectChurchLocation'));
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress({});

      let successCount = 0;
      let failureCount = 0;

      // Upload each file separately with its individual date
      for (const file of values.audioFiles) {
        try {
          setUploadProgress(prev => ({ ...prev, [file.name]: true }));

          const fileDate = getFileDate(file);

          await onUpload({
            church_id: values.church_id,
            audioFile: file,
            recorded_at: fileDate || undefined,
          });

          successCount++;
          setUploadProgress(prev => ({ ...prev, [file.name]: false }));
        } catch (error) {
          console.error(`Upload error for ${file.name}:`, error);
          failureCount++;
          setUploadProgress(prev => ({ ...prev, [file.name]: false }));
        }
      }

      // Show summary toast
      if (successCount > 0 && failureCount === 0) {
        toast.success(t('toast.uploadSuccess'));
      } else if (successCount > 0 && failureCount > 0) {
        toast.warning(`${successCount} ${t('toast.uploadSuccess').toLowerCase()}, ${failureCount} ${t('toast.uploadError').toLowerCase()}`);
      } else {
        toast.error(t('toast.uploadError'));
      }

      // Reset form only if at least one upload succeeded
      if (successCount > 0) {
        form.reset();
        form.setValue('church_id', ChurchLocation.LAUSANNE); // Reset to default
        setFileDates({});
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(t('toast.uploadError'));
    } finally {
      setIsUploading(false);
      setUploadProgress({});
    }
  };

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardContent className="pt-6">
        <Form {...form}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div
              {...getRootProps()}
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
                "hover:border-primary/50 hover:bg-muted/50",
                isDragActive && "border-primary bg-muted",
                audioFiles && audioFiles.length > 0 && "border-emerald-500 bg-emerald-50"
              )}
            >
              <input {...getInputProps()} />
              <UploadCloud className="h-12 w-12 text-primary mb-2 mx-auto" />
              {audioFiles && audioFiles.length > 0 ? (
                <div className="text-center">
                  <p className="font-medium">{audioFiles.length} {t('files.selected')}</p>
                  <p className="text-sm text-muted-foreground">
                    {t('files.totalSize')}: {(audioFiles.reduce((sum, file) => sum + file.size, 0) / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="font-medium">{t('fileUpload.dropzone')}</p>
                  <p className="text-sm text-muted-foreground">({t('upload.instruction2')})</p>
                </div>
              )}
            </div>

            {/* File List */}
            {audioFiles && audioFiles.length > 0 && (
              <div className="space-y-2">
                <FormLabel>Archivos Seleccionados</FormLabel>
                <div className="max-h-60 overflow-y-auto space-y-3">
                  {audioFiles.map((file, index) => (
                    <div key={`${file.name}-${index}`} className="flex items-center justify-between p-4 bg-muted rounded-lg">
                      <div className="flex items-center gap-3 flex-1">
                        <FileAudio className="h-4 w-4 text-primary flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm truncate">{file.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {(file.size / (1024 * 1024)).toFixed(2)} MB
                            {uploadProgress[file.name] && (
                              <span className="ml-2 text-primary">{t('fileUpload.uploading')}</span>
                            )}
                          </p>
                        </div>
                      </div>

                      {/* Date input for each file */}
                      <div className="flex items-center gap-2 ml-4">
                        <Calendar className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <Input
                          type="date"
                          value={getFileDate(file)}
                          onChange={(e) => updateFileDate(file, e.target.value)}
                          className="w-36 text-xs"
                          disabled={isUploading}
                          placeholder={t('fileUpload.recordedDate')}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
                          disabled={isUploading}
                          className="flex-shrink-0"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  {t('files.tip')}
                </p>
              </div>
            )}

            <FormField
              control={form.control}
              name="church_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t('fileUpload.churchLocation')}</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder={t('fileUpload.selectChurch')} />
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

            <FormItem>
              <FormLabel>{t('fileUpload.tags')}</FormLabel>
              <div className="flex">
                <Input
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={t('fileUpload.tagsPlaceholder')}
                  className="flex-1"
                />
                <Button
                  type="button"
                  onClick={addTag}
                  variant="secondary"
                  className="ml-2"
                >
                  {t('fileUpload.addTag')}
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
              disabled={isUploading || !audioFiles || audioFiles.length === 0}
            >
              {isUploading ? t('fileUpload.uploading') : t('fileUpload.uploadFiles')}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
