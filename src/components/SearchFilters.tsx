import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, Filter, X } from 'lucide-react';
import { ChurchLocation } from '@/types/testimony';
import { useTranslation } from 'react-i18next';

interface SearchFiltersProps {
  onSearch: (query: string) => void;
  onFilterChange: (filters: FilterOptions) => void;
}

export interface FilterOptions {
  status: string;
  church_id: string;
  tags: string[];
}

export function SearchFilters({ onSearch, onFilterChange }: SearchFiltersProps) {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    church_id: 'all',
    tags: [],
  });
  const [tagInput, setTagInput] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = () => {
    onSearch(searchQuery);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    const updatedFilters = { ...filters, [key]: value };
    setFilters(updatedFilters);
    onFilterChange(updatedFilters);
  };

  const addTag = () => {
    if (tagInput.trim() && !filters.tags.includes(tagInput.trim())) {
      const updatedTags = [...filters.tags, tagInput.trim()];
      handleFilterChange('tags', updatedTags);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    const updatedTags = filters.tags.filter(tag => tag !== tagToRemove);
    handleFilterChange('tags', updatedTags);
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  const resetFilters = () => {
    setFilters({
      status: 'all',
      church_id: 'all',
      tags: [],
    });
    onFilterChange({
      status: 'all',
      church_id: 'all',
      tags: [],
    });
  };

  return (
    <div className="w-full space-y-4">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder={t('search.placeholder')}
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <Button onClick={handleSearch}>
          {t('nav.search')}
        </Button>
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-1"
        >
          <Filter className="h-4 w-4" />
          <span className="hidden sm:inline">{t('filters.title')}</span>
        </Button>
      </div>

      {showFilters && (
        <div className="p-4 border rounded-md space-y-4 bg-background">
          <div className="flex justify-between items-center">
            <h3 className="font-medium">{t('filters.title')}</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={resetFilters}
              className="h-8 text-sm"
            >
              {t('filters.reset')}
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('filters.status')}</label>
              <Select
                value={filters.status}
                onValueChange={(value) => handleFilterChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('filters.selectStatus')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.allStatuses')}</SelectItem>
                  <SelectItem value="pending">{t('filters.pending')}</SelectItem>
                  <SelectItem value="processing">{t('filters.processing')}</SelectItem>
                  <SelectItem value="completed">{t('filters.completed')}</SelectItem>
                  <SelectItem value="failed">{t('filters.failed')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">{t('filters.church')}</label>
              <Select
                value={filters.church_id}
                onValueChange={(value) => handleFilterChange('church_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('filters.selectChurchLocation')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.allLocations')}</SelectItem>
                  {Object.values(ChurchLocation).map((location) => (
                    <SelectItem key={location} value={location}>
                      {location}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">{t('filters.tags')}</label>
            <div className="flex">
              <Input
                placeholder={t('filters.addTag')}
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleTagKeyDown}
                className="flex-1"
              />
              <Button
                type="button"
                variant="secondary"
                onClick={addTag}
                className="ml-2"
              >
                {t('fileUpload.addTag')}
              </Button>
            </div>

            <div className="flex flex-wrap gap-2 mt-2">
              {filters.tags.map((tag, i) => (
                <Badge key={i} variant="secondary" className="flex items-center gap-1">
                  {tag}
                  <X
                    className="h-3 w-3 cursor-pointer"
                    onClick={() => removeTag(tag)}
                  />
                </Badge>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
