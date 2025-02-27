import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useApi } from '../../hooks/useApi';
import type { DeepResearch } from '../../types/deep_research';
import type { Tag } from '../../types/tags';
import NavBar from '../../components/common/NavBar';
import Footer from '../../components/common/Footer';
import { Typography } from '@mui/material';

export const HomePage: React.FC = () => {
  const api = useApi();

  const { data: recentResearch, isLoading: isLoadingResearch } = useQuery({
    queryKey: ['recentResearch'],
    queryFn: () => api.deepResearchApi.getResearchItems({ limit: 10 }),
    enabled: true, // Always fetch public items
  });

  const { data: trendingTags, isLoading: isLoadingTags } = useQuery({
    queryKey: ['trendingTags'],
    queryFn: () => api.tagsApi.getTags(),
    enabled: true,
  });

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <Typography variant="h4">DRKR</Typography>
      </header>

      <NavBar />

      <main style={{ flex: 1 }}>
        <div className="container mx-auto px-4 py-8">
          {/* Hero Section */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg p-8 mb-8 text-white">
            <h1 className="text-4xl font-bold mb-4">Welcome to DRKR</h1>
            <p className="text-xl mb-6">Your AI-powered deep research companion</p>
          </div>

          {/* Recent Research Grid */}
          <div className="mb-12">
            <h2 className="text-2xl font-semibold mb-6">Recent Research</h2>
            {isLoadingResearch ? (
              <div className="animate-pulse space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
                ))}
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {recentResearch?.map((item: DeepResearch) => (
                  <Link
                    key={item.id}
                    to={`/research/${item.id}`}
                    className="block bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
                  >
                    <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {item.prompt_text}
                    </p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        item.visibility === 'public'
                          ? 'bg-green-100 text-green-800'
                          : item.visibility === 'org'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {item.visibility}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Trending Tags */}
          <div>
            <h2 className="text-2xl font-semibold mb-6">Trending Topics</h2>
            {isLoadingTags ? (
              <div className="animate-pulse flex gap-2 flex-wrap">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-8 w-24 bg-gray-200 rounded-full"></div>
                ))}
              </div>
            ) : (
              <div className="flex gap-2 flex-wrap">
                {trendingTags?.map((tag: Tag) => (
                  <Link
                    key={tag.id}
                    to={`/tags/${tag.name}`}
                    className="px-4 py-2 bg-gray-100 text-gray-800 rounded-full hover:bg-gray-200 transition-colors"
                  >
                    {tag.name}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default HomePage; 