import React, { useState, useEffect } from 'react';
import { TestimonyCard } from '@/components/TestimonyCard';
import { TestimonyDetail } from '@/components/TestimonyDetail';
import { SearchFilters, FilterOptions } from '@/components/SearchFilters';
import { Pagination } from '@/components/Pagination';
import { Skeleton } from '@/components/ui/skeleton';
import { Testimony, PaginatedResponse } from '@/types/testimony';
import { fetchTestimonies, searchTestimonies, filterTestimonies, searchTestimoniesWithFilters } from '@/services/testimonyService';
import { FileAudio } from 'lucide-react';

const DashboardPage = () => {
  const [paginatedData, setPaginatedData] = useState<PaginatedResponse<Testimony> | null>(null);
  const [selectedTestimony, setSelectedTestimony] = useState<Testimony | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    church_id: 'all',
    tags: [],
  });

  useEffect(() => {
    loadTestimonies();
  }, [currentPage, filters]);

  const loadTestimonies = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = {
        page: currentPage,
        size: pageSize,
        church_id: filters.church_id !== 'all' ? filters.church_id : undefined,
        transcript_status: filters.status !== 'all' ? filters.status : undefined,
        tags: filters.tags.length > 0 ? filters.tags : undefined,
      };
      
      const data = await fetchTestimonies(params);
      setPaginatedData(data);
    } catch (error) {
      console.error('Failed to load testimonies:', error);
      setError('Failed to load testimonies. Please check if the backend server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1); // Reset to first page when searching
    setError(null);
    
    if (!query) {
      // If no search query, reload with current filters
      loadTestimonies();
      return;
    }
    
    // Use the enhanced search with filters
    setIsLoading(true);
    try {
      const results = await searchTestimoniesWithFilters(query, {
        church_id: filters.church_id !== 'all' ? filters.church_id : undefined,
        transcript_status: filters.status !== 'all' ? filters.status : undefined,
        tags: filters.tags,
      });
      
      // Convert to paginated format for consistency
      setPaginatedData({
        items: results,
        total: results.length,
        page: 1,
        size: results.length,
        pages: 1
      });
    } catch (error) {
      console.error('Search error:', error);
      setError('Search failed. Please check if the backend server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = async (newFilters: FilterOptions) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filtering
    // loadTestimonies will be called by useEffect due to filters change
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // loadTestimonies will be called by useEffect due to currentPage change
  };

  function handleViewDetails(testimony: Testimony) {
    setSelectedTestimony(testimony);
    setIsDialogOpen(true);
  }

  function handleCloseDialog() {
    setIsDialogOpen(false);
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold md:text-3xl">Testimony Dashboard</h1>
        <p className="text-muted-foreground">
          Manage and explore church testimonies
        </p>
      </div>

      <div className="space-y-6">
        <SearchFilters 
          onSearch={handleSearch} 
          onFilterChange={handleFilterChange} 
        />

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-red-100 p-6 mb-4">
              <FileAudio className="h-10 w-10 text-red-600" />
            </div>
            <h3 className="text-lg font-medium text-red-800">Connection Error</h3>
            <p className="text-red-600 mt-1 max-w-md">
              {error}
            </p>
            <button 
              onClick={loadTestimonies}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        ) : paginatedData && paginatedData.items.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {paginatedData.items.map((testimony) => (
                <TestimonyCard
                  key={testimony.id}
                  testimony={testimony}
                  onViewDetails={handleViewDetails}
                />
              ))}
            </div>
            
            <Pagination
              currentPage={paginatedData.page}
              totalPages={paginatedData.pages}
              totalItems={paginatedData.total}
              itemsPerPage={paginatedData.size}
              onPageChange={handlePageChange}
              isLoading={isLoading}
            />
          </>
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
      </div>

      <TestimonyDetail
        testimony={selectedTestimony}
        open={isDialogOpen}
        onClose={handleCloseDialog}
      />
    </div>
  );
};

export default DashboardPage;
