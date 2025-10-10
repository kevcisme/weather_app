"use client"

import { useEffect, useState } from "react";
import { getLatest, getHistory, WeatherReading, HistoryResponse } from "@/lib/api";
import { CurrentConditions } from "@/components/weather/current-conditions";
import { DailySummary } from "@/components/weather/daily-summary";
import { HistoryCharts } from "@/components/weather/history-charts";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Cloud } from "lucide-react";

export default function Dashboard() {
  const [currentData, setCurrentData] = useState<WeatherReading | null>(null);
  const [historyData, setHistoryData] = useState<WeatherReading[]>([]);
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [hours, setHours] = useState(24);
  const [error, setError] = useState<string | null>(null);

  // Fetch current conditions
  useEffect(() => {
    async function fetchCurrent() {
      try {
        setIsLoadingCurrent(true);
        const data = await getLatest();
        console.log("Latest data:", data);
        console.log("Daily stats:", {
          daily_temp_min: data.daily_temp_min,
          daily_temp_max: data.daily_temp_max,
          daily_temp_avg: data.daily_temp_avg,
          daily_humidity_avg: data.daily_humidity_avg,
          daily_pressure_avg: data.daily_pressure_avg
        });
        setCurrentData(data);
        setError(null);
      } catch (err) {
        console.error("Error fetching current conditions:", err);
        setError("Failed to load current conditions. Make sure the backend is running.");
      } finally {
        setIsLoadingCurrent(false);
      }
    }

    fetchCurrent();
    // Refresh every 60 seconds
    const interval = setInterval(fetchCurrent, 60000);
    return () => clearInterval(interval);
  }, []);

  // Fetch historical data
  useEffect(() => {
    async function fetchHistory() {
      try {
        setIsLoadingHistory(true);
        const data = await getHistory(hours);
        setHistoryData(data.readings);
      } catch (err) {
        console.error("Error fetching history:", err);
      } finally {
        setIsLoadingHistory(false);
      }
    }

    fetchHistory();
  }, [hours]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary">
              <Cloud className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">The Manoa Manor Weather Station</h1>
              <p className="text-sm text-muted-foreground">
                Real-time environmental monitoring dashboard
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 rounded-lg border border-destructive bg-destructive/10 p-4">
            <p className="text-sm text-destructive">{error}</p>
            <p className="text-xs text-muted-foreground mt-2">
              Backend API: {process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? '/api (via nginx)' : 'http://localhost:8000')}
            </p>
          </div>
        )}

        {/* Daily Summary - Full Width */}
        <div className="mb-6">
          <DailySummary data={currentData} isLoading={isLoadingCurrent} />
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Current Conditions - Left Sidebar */}
          <div className="lg:col-span-1">
            <CurrentConditions data={currentData} isLoading={isLoadingCurrent} />
          </div>

          {/* Historical Charts - Main Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Time Range Selector */}
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold tracking-tight">Historical Data</h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Time range:</span>
                <Select
                  value={hours.toString()}
                  onValueChange={(value) => setHours(parseInt(value))}
                >
                  <SelectTrigger className="w-[140px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 hour</SelectItem>
                    <SelectItem value="6">6 hours</SelectItem>
                    <SelectItem value="12">12 hours</SelectItem>
                    <SelectItem value="24">24 hours</SelectItem>
                    <SelectItem value="48">48 hours</SelectItem>
                    <SelectItem value="72">3 days</SelectItem>
                    <SelectItem value="168">7 days</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Charts */}
            <HistoryCharts 
              data={historyData} 
              isLoading={isLoadingHistory} 
              hours={hours}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted-foreground">
            Weather Station Dashboard • Built with Next.js, Shadcn UI & FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}