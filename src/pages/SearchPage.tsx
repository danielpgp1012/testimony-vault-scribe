import React, { useState, useEffect } from 'react';
import { TestimonyCard } from '@/components/TestimonyCard';
import { TestimonyDetail } from '@/components/TestimonyDetail';
import { Testimony } from '@/types/testimony';
import { searchTestimonies } from '@/services/testimonyService';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Search } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const SearchPage = () => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Testimony[]>([]);
  const [selectedTestimony, setSelectedTestimony] = useState<Testimony | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setHasSearched(true);

    try {
      const results = await searchTestimonies(searchQuery);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleViewDetails = (testimony: Testimony) => {
    setSelectedTestimony(testimony);
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold md:text-3xl">{t('searchPage.title')}</h1>
        <p className="text-muted-foreground">
          {t('searchPage.subtitle')}
        </p>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder={t('searchPage.placeholder')}
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <Button onClick={handleSearch}>
          {t('nav.search')}
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="border rounded-md p-4 space-y-3">
              <Skeleton className="h-6 w-2/3" />
              <Skeleton className="h-4 w-4/5" />
              <Skeleton className="h-4 w-3/5" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-10 w-full mt-4" />
            </div>
          ))}
        </div>
      ) : hasSearched ? (
        searchResults.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
            {searchResults.map((testimony) => (
              <TestimonyCard
                key={testimony.id}
                testimony={testimony}
                onViewDetails={handleViewDetails}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-muted p-6 mb-4">
              <Search className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium">{t('searchPage.noResults')}</h3>
            <p className="text-muted-foreground mt-1 max-w-md">
              {t('searchPage.noResultsSubtitle')}
            </p>
          </div>
        )
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-6 mb-4">
            <Search className="h-10 w-10 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium">{t('searchPage.startSearching')}</h3>
          <p className="text-muted-foreground mt-1 max-w-md">
            {t('searchPage.startSearchingSubtitle')}
          </p>
        </div>
      )}

      <TestimonyDetail
        testimony={selectedTestimony}
        open={isDialogOpen}
        onClose={handleCloseDialog}
      />
    </div>
  );
};

export default SearchPage;
