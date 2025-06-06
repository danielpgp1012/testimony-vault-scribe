
import React from 'react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const NotFound = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-bold text-primary">404</h1>
        <h2 className="text-2xl font-semibold">{t('notFound.title')}</h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          {t('notFound.description')}
        </p>
        <Button asChild className="mt-4">
          <Link to="/">{t('notFound.returnToDashboard')}</Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
