import { QueryClient } from '@tanstack/react-query'

// Configure default options for React Query
const defaultOptions = {
  queries: {
    staleTime: 5 * 60 * 1000, // Data considered fresh for 5 minutes
    cacheTime: 30 * 60 * 1000, // Cache persists for 30 minutes
    retry: 3, // Retry failed requests 3 times
    retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  },
  mutations: {
    retry: 2,
    retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
  },
}

// Create and export the QueryClient instance
export const queryClient = new QueryClient({
  defaultOptions,
})

// Common query keys for cache management
export const queryKeys = {
  user: {
    current: ['currentUser'],
    details: (userId: string) => ['user', userId],
  },
  research: {
    all: ['deep-research'],
    detail: (id: string) => ['deep-research', id],
    byTag: (tagId: string) => ['deep-research', 'tag', tagId],
  },
  tags: {
    all: ['tags'],
    detail: (id: string) => ['tag', id],
  },
}
