/**
 * API client for weather backend
 */

// In production (deployed on Pi with nginx), use relative /api/ path
// In development, use localhost:8000 directly
const API_URL = process.env.NEXT_PUBLIC_API_URL || (
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? '/api'  // Production: use nginx proxy
    : 'http://localhost:8000'  // Development: direct connection
);

export interface WeatherReading {
  ts: string;
  temp_c: number;
  temp_f: number;
  humidity: number;
  pressure: number;
}

export interface HistoryResponse {
  hours: number;
  count: number;
  readings: WeatherReading[];
}

/**
 * Fetch the latest weather reading
 */
export async function getLatest(): Promise<WeatherReading> {
  const response = await fetch(`${API_URL}/latest`, {
    cache: 'no-store',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch latest reading: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch historical weather readings
 * @param hours - Number of hours to look back (1-168)
 */
export async function getHistory(hours: number = 24): Promise<HistoryResponse> {
  const response = await fetch(`${API_URL}/history?hours=${hours}`, {
    cache: 'no-store',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.statusText}`);
  }
  
  return response.json();
}
