"use client"

import { WeatherReading } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Thermometer, Droplets, Gauge } from "lucide-react";
import { format } from "date-fns";

interface CurrentConditionsProps {
  data: WeatherReading | null;
  isLoading?: boolean;
}

export function CurrentConditions({ data, isLoading }: CurrentConditionsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Conditions</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-20 bg-muted rounded" />
            <div className="h-20 bg-muted rounded" />
            <div className="h-20 bg-muted rounded" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Conditions</CardTitle>
          <CardDescription>No data available</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const timestamp = new Date(data.ts);
  const formattedTime = format(timestamp, "PPpp");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Current Conditions</CardTitle>
        <CardDescription>Last updated: {formattedTime}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Temperature */}
        <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-chart-1/10">
            <Thermometer className="h-6 w-6 text-chart-1" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">Temperature</p>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">{data.temp_f.toFixed(1)}°F</p>
              <p className="text-lg text-muted-foreground">({data.temp_c.toFixed(1)}°C)</p>
            </div>
          </div>
        </div>

        {/* Humidity */}
        <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-chart-2/10">
            <Droplets className="h-6 w-6 text-chart-2" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">Humidity</p>
            <p className="text-3xl font-bold">{data.humidity.toFixed(1)}%</p>
          </div>
        </div>

        {/* Pressure */}
        <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-chart-3/10">
            <Gauge className="h-6 w-6 text-chart-3" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">Pressure</p>
            <p className="text-3xl font-bold">{data.pressure.toFixed(1)} hPa</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
