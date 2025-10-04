/**
 * API Service for WTF Podcast RAG Backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  question: string;
  top_k?: number;
  diversity?: boolean;
}

export interface Source {
  guest: string;
  guest_expertise: string;
  episode_id: string;
  youtube_url: string;
  text: string;
  industry_tags: string[];
  episode_themes: string[];
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
  query: string;
}

/**
 * Query the podcast RAG system
 */
export async function queryPodcast(
  question: string,
  top_k: number = 5
): Promise<QueryResponse> {
  console.log('🔍 Querying API:', API_URL);
  console.log('📝 Question:', question);
  
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        top_k,
        diversity: true,
      }),
    });

    console.log('📡 Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ API error:', errorText);
      throw new Error(`API error: ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();
    console.log('✅ Response received:', data);
    return data;
  } catch (error) {
    console.error('❌ Fetch failed:', error);
    throw error;
  }
}

/**
 * Health check
 */
export async function checkHealth(): Promise<{
  status: string;
  message: string;
  episodes_loaded: number;
  total_chunks: number;
  model: string;
}> {
  const response = await fetch(`${API_URL}/health`);
  
  if (!response.ok) {
    throw new Error('Backend not available');
  }
  
  return response.json();
}

/**
 * Get system stats
 */
export async function getStats() {
  const response = await fetch(`${API_URL}/stats`);
  return response.json();
}

