# Pagination Implementation

This document describes the pagination implementation using `fastapi-pagination` to ensure API payloads are not too large.

## Backend Implementation

### Dependencies

Added `fastapi-pagination==0.12.24` to `requirements.txt`.

### API Changes

The `/testimonies` endpoint now returns paginated results using the `fastapi-pagination` library:

```python
from fastapi_pagination import Page, add_pagination, paginate

@app.get("/testimonies", response_model=Page[TestimonyOut])
def list_testimonies(
    church_id: Optional[str] = None,
    transcript_status: Optional[str] = None,
    supabase=Depends(get_supabase)
):
    # ... filtering logic ...
    return paginate(data)
```

### Response Format

The API now returns responses in this format:

```json
{
  "items": [...],           // Array of testimony objects
  "total": 150,            // Total number of items
  "page": 1,               // Current page number
  "size": 50,              // Items per page
  "pages": 3               // Total number of pages
}
```

### Query Parameters

The endpoint supports these pagination and filtering parameters:

- `page`: Page number (default: 1)
- `size`: Items per page (default: 50, max: 100)
- `church_id`: Filter by church location
- `transcript_status`: Filter by transcription status

### Examples

```bash
# Get first page with default size (50 items)
GET /testimonies

# Get second page with 20 items per page
GET /testimonies?page=2&size=20

# Filter by church and get first page
GET /testimonies?church_id=Lausanne&page=1&size=10

# Filter by status and paginate
GET /testimonies?transcript_status=completed&page=1&size=25
```

## Frontend Implementation

### Types

Added pagination types in `src/types/testimony.ts`:

```typescript
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PaginationParams {
  page?: number;
  size?: number;
}
```

### Service Layer

Updated `fetchTestimonies` function to support pagination:

```typescript
export const fetchTestimonies = async (
  params?: PaginationParams & {
    church_id?: string;
    transcript_status?: string;
  }
): Promise<PaginatedResponse<Testimony>>
```

### UI Components

#### Pagination Component

Created `src/components/Pagination.tsx` with:
- Page navigation (first, previous, next, last)
- Page number buttons with ellipsis for large page counts
- Items count display
- Loading state support

#### Dashboard Updates

Updated `DashboardPage` to:
- Use paginated API calls
- Display pagination controls
- Handle page changes
- Maintain filters across page navigation

### Backward Compatibility

For components that still expect `Testimony[]`, added a helper function:

```typescript
export const fetchTestimoniesSimple = async (): Promise<Testimony[]> => {
  const result = await fetchTestimonies({ page: 1, size: 1000 });
  return result.items;
};
```

## Benefits

1. **Performance**: Reduces API payload size, especially important as the testimony database grows
2. **User Experience**: Faster page loads and better responsiveness
3. **Scalability**: Can handle large datasets without memory issues
4. **Flexibility**: Supports filtering combined with pagination
5. **Standards**: Uses industry-standard pagination patterns

## Configuration

### Default Settings

- Default page size: 50 items
- Maximum page size: 100 items (enforced by fastapi-pagination)
- Frontend page size: 20 items (configurable in DashboardPage)

### Customization

To change default pagination settings, modify the fastapi-pagination configuration in `main.py`:

```python
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

# Configure pagination defaults
add_pagination(app)
```

## Testing

Use the provided test script to verify pagination:

```bash
cd backend
python test_pagination.py
```

This tests:
- Basic pagination
- Different page sizes
- Filtering with pagination
- Default behavior

## Future Enhancements

1. **Search with Pagination**: Implement server-side search with pagination
2. **Cursor-based Pagination**: For real-time data scenarios
3. **Caching**: Add response caching for frequently accessed pages
4. **Infinite Scroll**: Alternative UI pattern for mobile/web apps
