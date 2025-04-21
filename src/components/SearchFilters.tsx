
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

interface SearchFiltersProps {
  onSearch: (query: string) => void;
  onFilterChange: (filters: FilterOptions) => void;
}

export interface FilterOptions {
  status: string;
  speaker: string;
  tags: string[];
}

export function SearchFilters({ onSearch, onFilterChange }: SearchFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    speaker: 'all',
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
      speaker: 'all',
      tags: [],
    });
    onFilterChange({
      status: 'all',
      speaker: 'all',
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
            placeholder="Search testimonies..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <Button onClick={handleSearch}>
          Search
        </Button>
        <Button 
          variant="outline" 
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-1"
        >
          <Filter className="h-4 w-4" />
          <span className="hidden sm:inline">Filters</span>
        </Button>
      </div>

      {showFilters && (
        <div className="p-4 border rounded-md space-y-4 bg-background">
          <div className="flex justify-between items-center">
            <h3 className="font-medium">Filters</h3>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={resetFilters}
              className="h-8 text-sm"
            >
              Reset
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <Select
                value={filters.status}
                onValueChange={(value) => handleFilterChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Speaker</label>
              <Select
                value={filters.speaker}
                onValueChange={(value) => handleFilterChange('speaker', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select speaker" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Speakers</SelectItem>
                  {/* These would be populated from data in a real app */}
                  <SelectItem value="john-doe">John Doe</SelectItem>
                  <SelectItem value="jane-smith">Jane Smith</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium">Tags</label>
            <div className="flex">
              <Input
                placeholder="Add tag and press Enter"
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
                Add
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
