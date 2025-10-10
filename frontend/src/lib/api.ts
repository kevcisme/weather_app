/**
 * API client for weather backend
 */

/**
 * Determine the API URL based on environment and context
 * - NEXT_PUBLIC_API_URL env var takes precedence (for local Mac development)
 * - In browser: use window.location to determine the right URL
 * - On server (SSR): default to localhost:8000 (assumes backend on same machine)
 */
function getApiUrl(): string {
  // Environment variable takes precedence (used for local development)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Browser context - determine based on hostname
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Local development on Mac
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // Accessing Pi directly via IP or hostname
    // Backend is on the same machine, so use the same host
    return `http://${hostname}:8000`;
  }

  // Server-side rendering fallback
  // Assumes frontend and backend are on the same machine (Pi deployment)
  return 'http://localhost:8000';
}

const API_URL = getApiUrl();

export interface WeatherReading {
  // Bronze layer fields (raw sensor data)
  ts: string;
  temp_c: number;
  temp_f: number;
  humidity: number;
  pressure: number;
  temp_from_humidity?: number;
  temp_from_pressure?: number;
  cpu_temp?: number | null;
  
  // Silver layer fields (calculated metrics)
  dew_point_c?: number;
  dew_point_f?: number;
  comfort_index?: string;
  pressure_trend_3h?: number | null;
  pressure_trend_6h?: number | null;
  pressure_trend_label?: string;
  daily_temp_min?: number | null;
  daily_temp_max?: number | null;
  daily_temp_avg?: number | null;
  daily_humidity_avg?: number | null;
  daily_pressure_avg?: number | null;
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
  
  const data = await response.json();
  
  // Check if the response contains an error
  if ('error' in data) {
    throw new Error(data.error);
  }
  
  // Validate that we have the expected data structure
  if (!data.ts || typeof data.temp_f !== 'number' || typeof data.humidity !== 'number' || typeof data.pressure !== 'number') {
    throw new Error('Invalid data structure received from backend');
  }
  
  return data;
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
  
  const data = await response.json();
  
  // Check if the response contains an error
  if ('error' in data) {
    console.warn('Backend returned error:', data.error);
    // Return empty readings rather than throwing, since the UI handles empty data gracefully
    return {
      hours: hours,
      count: 0,
      readings: []
    };
  }
  
  // Ensure readings array exists
  if (!Array.isArray(data.readings)) {
    console.error('Invalid history data structure:', data);
    return {
      hours: hours,
      count: 0,
      readings: []
    };
  }
  
  return data;
}
