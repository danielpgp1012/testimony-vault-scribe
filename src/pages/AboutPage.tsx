import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileAudio, Upload, Search, Filter, FileText } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const AboutPage = () => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold md:text-3xl">{t('about.title')}</h1>
        <p className="text-muted-foreground">
          {t('about.subtitle')}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary" />
              {t('about.easyUpload')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {t('about.easyUploadDesc')}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <FileAudio className="h-5 w-5 text-primary" />
              {t('about.automaticTranscription')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {t('about.automaticTranscriptionDesc')}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5 text-primary" />
              {t('about.powerfulSearch')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {t('about.powerfulSearchDesc')}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-primary" />
              {t('about.advancedFiltering')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {t('about.advancedFilteringDesc')}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              {t('about.secureStorage')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {t('about.secureStorageDesc')}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>{t('about.howItWorks')}</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-4 list-decimal list-inside text-sm">
            <li>
              <span className="font-medium">{t('about.step1')}</span>: {t('about.step1Desc')}
            </li>
            <li>
              <span className="font-medium">{t('about.step2')}</span>: {t('about.step2Desc')}
            </li>
            <li>
              <span className="font-medium">{t('about.step3')}</span>: {t('about.step3Desc')}
            </li>
            <li>
              <span className="font-medium">{t('about.step4')}</span>: {t('about.step4Desc')}
            </li>
            <li>
              <span className="font-medium">{t('about.step5')}</span>: {t('about.step5Desc')}
            </li>
          </ol>
        </CardContent>
      </Card>

      <div className="text-center text-sm text-muted-foreground pt-6">
        <p>{t('footer.copyright')} {new Date().getFullYear()}</p>
        <p className="mt-1">{t('about.footerTagline')}</p>
      </div>
    </div>
  );
};

export default AboutPage;
