"use client"

import { WeatherReading } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUp, ArrowDown, Activity } from "lucide-react";

interface DailySummaryProps {
  data: WeatherReading | null;
  isLoading?: boolean;
}

export function DailySummary({ data, isLoading }: DailySummaryProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Today's Summary</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse h-32 bg-muted rounded" />
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.daily_temp_min) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Today's Summary</CardTitle>
          <CardDescription>Accumulating data...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const tempRange = data.daily_temp_max && data.daily_temp_min 
    ? (data.daily_temp_max - data.daily_temp_min).toFixed(1)
    : null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Today's Summary</CardTitle>
        <CardDescription>Rolling statistics since midnight</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Temperature Stats */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Activity className="h-4 w-4" />
              Temperature
            </div>
            <div className="space-y-2">
              {data.daily_temp_max != null && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ArrowUp className="h-4 w-4 text-red-500" />
                    <span className="text-sm text-muted-foreground">High</span>
                  </div>
                  <span className="font-semibold">{data.daily_temp_max.toFixed(1)}°F</span>
                </div>
              )}
              {data.daily_temp_avg != null && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-blue-500" />
                    <span className="text-sm text-muted-foreground">Avg</span>
                  </div>
                  <span className="font-semibold">{data.daily_temp_avg.toFixed(1)}°F</span>
                </div>
              )}
              {data.daily_temp_min != null && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ArrowDown className="h-4 w-4 text-blue-500" />
                    <span className="text-sm text-muted-foreground">Low</span>
                  </div>
                  <span className="font-semibold">{data.daily_temp_min.toFixed(1)}°F</span>
                </div>
              )}
              {tempRange && (
                <div className="flex items-center justify-between pt-2 border-t">
                  <span className="text-xs text-muted-foreground">Range</span>
                  <span className="text-sm font-medium">{tempRange}°F</span>
                </div>
              )}
            </div>
          </div>

          {/* Humidity Stats */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Activity className="h-4 w-4" />
              Humidity
            </div>
            {data.daily_humidity_avg != null ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Average</span>
                  <span className="font-semibold">{data.daily_humidity_avg.toFixed(1)}%</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Calculating...</p>
            )}
          </div>

          {/* Pressure Stats */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Activity className="h-4 w-4" />
              Pressure
            </div>
            {data.daily_pressure_avg != null ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Average</span>
                  <span className="font-semibold">{data.daily_pressure_avg.toFixed(1)} hPa</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Calculating...</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

