"use client"

import { WeatherReading } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Thermometer, Droplets, Gauge, Wind, TrendingDown, TrendingUp, Minus } from "lucide-react";
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

  // Validate timestamp before parsing
  const timestamp = new Date(data.ts);
  if (isNaN(timestamp.getTime())) {
    console.error('Invalid timestamp in current data:', data.ts);
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Conditions</CardTitle>
          <CardDescription>Invalid data received from backend</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const formattedTime = format(timestamp, "PPpp");

  // Helper to get pressure trend icon and color
  const getPressureTrendDisplay = () => {
    const label = data.pressure_trend_label;
    const trend3h = data.pressure_trend_3h;
    
    if (!label || label === "unknown" || label === "calculating") {
      return { icon: Minus, color: "text-muted-foreground", text: "Calculating..." };
    }
    
    if (label === "rapidly_falling" || label === "falling") {
      return { 
        icon: TrendingDown, 
        color: "text-orange-500", 
        text: `${label === "rapidly_falling" ? "Rapidly " : ""}Falling ${trend3h ? `(${trend3h} hPa)` : ""}`
      };
    }
    
    if (label === "rapidly_rising" || label === "rising") {
      return { 
        icon: TrendingUp, 
        color: "text-green-500", 
        text: `${label === "rapidly_rising" ? "Rapidly " : ""}Rising ${trend3h ? `(${trend3h > 0 ? '+' : ''}${trend3h} hPa)` : ""}`
      };
    }
    
    return { 
      icon: Minus, 
      color: "text-blue-500", 
      text: `Steady ${trend3h ? `(${trend3h > 0 ? '+' : ''}${trend3h} hPa)` : ""}`
    };
  };

  const pressureTrend = getPressureTrendDisplay();
  const PressureTrendIcon = pressureTrend.icon;

  // Helper to get comfort color
  const getComfortColor = () => {
    const comfort = data.comfort_index;
    if (!comfort) return "text-muted-foreground";
    if (comfort === "comfortable") return "text-green-500";
    if (comfort === "too_hot" || comfort === "too_cold") return "text-orange-500";
    if (comfort === "too_humid" || comfort === "too_dry") return "text-yellow-500";
    return "text-muted-foreground";
  };

  const getComfortText = () => {
    const comfort = data.comfort_index;
    if (!comfort) return "Unknown";
    return comfort.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
  };

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

        {/* Dew Point */}
        {data.dew_point_f !== undefined && (
          <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-chart-5/10">
              <Droplets className="h-6 w-6 text-chart-5" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-muted-foreground">Dew Point</p>
                <span className={`text-xs font-semibold ${getComfortColor()}`}>
                  {getComfortText()}
                </span>
              </div>
              <div className="flex items-baseline gap-2">
                <p className="text-3xl font-bold">{data.dew_point_f.toFixed(1)}°F</p>
                <p className="text-lg text-muted-foreground">({data.dew_point_c?.toFixed(1)}°C)</p>
              </div>
            </div>
          </div>
        )}

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

        {/* Pressure with Trend */}
        <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-chart-3/10">
            <Gauge className="h-6 w-6 text-chart-3" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">Pressure</p>
            <div className="flex items-baseline gap-3">
              <p className="text-3xl font-bold">{data.pressure.toFixed(1)} hPa</p>
              <div className={`flex items-center gap-1 ${pressureTrend.color}`}>
                <PressureTrendIcon className="h-4 w-4" />
                <span className="text-xs font-medium">{pressureTrend.text}</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
