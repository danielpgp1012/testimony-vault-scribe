
import React, { useState, useEffect } from 'react';
import { TestimonyCard } from '@/components/TestimonyCard';
import { TestimonyDetail } from '@/components/TestimonyDetail';
import { SearchFilters, FilterOptions } from '@/components/SearchFilters';
import { Skeleton } from '@/components/ui/skeleton';
import { Testimony } from '@/types/testimony';
import { fetchTestimonies, searchTestimonies, filterTestimonies } from '@/services/testimonyService';
import { FileAudio } from 'lucide-react';

const DashboardPage = () => {
  const [testimonies, setTestimonies] = useState<Testimony[]>([]);
  const [filteredTestimonies, setFilteredTestimonies] = useState<Testimony[]>([]);
  const [selectedTestimony, setSelectedTestimony] = useState<Testimony | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    speaker: 'all',
    tags: [],
  });

  useEffect(() => {
    loadTestimonies();
  }, []);

  const loadTestimonies = async () => {
    setIsLoading(true);
    try {
      const data = await fetchTestimonies();
      setTestimonies(data);
      setFilteredTestimonies(data);
    } catch (error) {
      console.error('Failed to load testimonies:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    
    if (!query && Object.values(filters).every(val => 
      val === 'all' || (Array.isArray(val) && val.length === 0)
    )) {
      setFilteredTestimonies(testimonies);
      return;
    }
    
    setIsLoading(true);
    try {
      let results = query ? await searchTestimonies(query) : testimonies;
      results = await filterTestimonies(results, filters);
      setFilteredTestimonies(results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = async (newFilters: FilterOptions) => {
    setFilters(newFilters);
    setIsLoading(true);
    
    try {
      let results = testimonies;
      if (searchQuery) {
        results = await searchTestimonies(searchQuery);
      }
      results = await filterTestimonies(results, newFilters);
      setFilteredTestimonies(results);
    } catch (error) {
      console.error('Filter error:', error);
    } finally {
      setIsLoading(false);
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
        <h1 className="text-2xl font-bold md:text-3xl">Testimony Dashboard</h1>
        <p className="text-muted-foreground">
          Manage and explore church testimonies
        </p>
      </div>

      <SearchFilters 
        onSearch={handleSearch} 
        onFilterChange={handleFilterChange} 
      />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="border rounded-md p-4 space-y-3">
              <Skeleton className="h-6 w-2/3" />
              <Skeleton className="h-4 w-4/5" />
              <Skeleton className="h-4 w-3/5" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-10 w-full mt-4" />
            </div>
          ))}
        </div>
      ) : filteredTestimonies.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTestimonies.map((testimony) => (
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
            <FileAudio className="h-10 w-10 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium">No testimonies found</h3>
          <p className="text-muted-foreground mt-1 max-w-md">
            {searchQuery || Object.values(filters).some(val => 
              val !== 'all' && !(Array.isArray(val) && val.length === 0)
            ) 
              ? "Try adjusting your search or filters to find what you're looking for."
              : "Start by uploading your first testimony."}
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

export default DashboardPage;
