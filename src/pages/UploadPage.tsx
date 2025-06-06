import React from 'react';
import { FileUpload } from '@/components/FileUpload';
import { TestimonyFormData } from '@/types/testimony';
import { uploadTestimony } from '@/services/testimonyService';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const UploadPage = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleUpload = async (data: TestimonyFormData) => {
    try {
      // In a real app, this would handle the full upload flow
      await uploadTestimony(data);
      toast.success(t('toast.uploadSuccess'));

      // Keep user on upload page to allow multiple uploads
      // No redirect - user can upload more testimonies
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(t('toast.uploadError'));
      throw error; // Re-throw to let the component handle the error state
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold md:text-3xl">{t('upload.title')}</h1>
        <p className="text-muted-foreground">
          {t('upload.subtitle')}
        </p>
      </div>

      <div className="mt-6">
        <FileUpload onUpload={handleUpload} />
      </div>

      <div className="bg-secondary/50 rounded-md p-4 mt-8">
        <h3 className="font-medium mb-2">{t('upload.instructions')}</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
          <li>{t('upload.instruction1')}</li>
          <li>{t('upload.instruction2')}</li>
          <li>{t('upload.instruction3')}</li>
          <li>{t('upload.instruction4')}</li>
          <li>{t('upload.instruction5')}</li>
          <li>{t('upload.instruction6')}</li>
          <li>{t('upload.instruction7')}</li>
          <li>{t('upload.instruction8')}</li>
          <li>{t('upload.instruction9')}</li>
          <li>{t('upload.instruction10')}</li>
          <li>{t('upload.instruction11')}</li>
        </ul>
      </div>
    </div>
  );
};

export default UploadPage;
