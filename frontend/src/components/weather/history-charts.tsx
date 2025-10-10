"use client"

import { WeatherReading } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { format } from "date-fns";

interface HistoryChartsProps {
  data: WeatherReading[];
  isLoading?: boolean;
  hours: number;
}

export function HistoryCharts({ data, isLoading, hours }: HistoryChartsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Historical Data</CardTitle>
          <CardDescription>Loading {hours} hour history...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse h-96 bg-muted rounded" />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Historical Data</CardTitle>
          <CardDescription>No historical data available</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  // Transform data for charts - filter out invalid readings
  const chartData = data
    .filter((reading) => {
      // Validate that the reading has all required fields and a valid timestamp
      if (!reading.ts || !reading.temp_f || !reading.humidity || !reading.pressure) {
        console.warn('Invalid reading found, skipping:', reading);
        return false;
      }
      // Check if timestamp is valid
      const date = new Date(reading.ts);
      if (isNaN(date.getTime())) {
        console.warn('Invalid timestamp found, skipping:', reading.ts);
        return false;
      }
      return true;
    })
    .map((reading) => ({
      time: format(new Date(reading.ts), "MMM d HH:mm"),
      temp_f: reading.temp_f,
      temp_from_humidity: reading.temp_from_humidity ? reading.temp_from_humidity * 1.8 + 32 : undefined,
      temp_from_pressure: reading.temp_from_pressure ? reading.temp_from_pressure * 1.8 + 32 : undefined,
      humidity: reading.humidity,
      pressure: reading.pressure,
    }));

  return (
    <div className="space-y-6">
      {/* Temperature Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Temperature</CardTitle>
          <CardDescription>Last {hours} hours</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
                className="text-muted-foreground"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
                label={{ value: '°F', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--popover))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="temp_f" 
                stroke="hsl(var(--chart-1))" 
                name="Calibrated Temp (°F)"
                strokeWidth={2}
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="temp_from_humidity" 
                stroke="hsl(var(--chart-2))" 
                name="Temp from Humidity (°F)"
                strokeWidth={2}
                dot={false}
                strokeDasharray="5 5"
              />
              <Line 
                type="monotone" 
                dataKey="temp_from_pressure" 
                stroke="hsl(var(--chart-4))" 
                name="Temp from Pressure (°F)"
                strokeWidth={2}
                dot={false}
                strokeDasharray="3 3"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Humidity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Humidity</CardTitle>
          <CardDescription>Last {hours} hours</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
                className="text-muted-foreground"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
                label={{ value: '%', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--popover))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="humidity" 
                stroke="hsl(var(--chart-2))" 
                name="Humidity (%)"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Pressure Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Barometric Pressure</CardTitle>
          <CardDescription>Last {hours} hours</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
                className="text-muted-foreground"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
                label={{ value: 'hPa', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--popover))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="pressure" 
                stroke="hsl(var(--chart-3))" 
                name="Pressure (hPa)"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

