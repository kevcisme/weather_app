# Weather Station Dashboard

A modern, real-time weather monitoring dashboard built with Next.js 15, TypeScript, Shadcn UI, and FastAPI.

## Features

- **Real-time Monitoring**: Live display of current temperature, humidity, and barometric pressure
- **Historical Data Visualization**: Interactive charts showing weather trends over time
- **Flexible Time Ranges**: View data from 1 hour to 7 days
- **Auto-refresh**: Current conditions update every 60 seconds
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Beautiful UI**: Built with Shadcn UI components and Tailwind CSS

## Prerequisites

- Node.js 18+ and npm
- FastAPI backend running (see `/backend` directory)

## Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update this to your production API URL.

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start the development server
npm run dev
```

The dashboard will be available at [http://localhost:3000](http://localhost:3000)

## Building for Production

```bash
# Build the application
npm run build

# Start the production server
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js app directory
│   │   ├── page.tsx           # Main dashboard page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles and theme
│   ├── components/
│   │   ├── ui/                # Shadcn UI components
│   │   └── weather/           # Weather-specific components
│   │       ├── current-conditions.tsx
│   │       └── history-charts.tsx
│   └── lib/
│       ├── api.ts             # API client for backend
│       └── utils.ts           # Utility functions
├── components.json            # Shadcn UI configuration
└── package.json
```

## API Integration

The frontend connects to the FastAPI backend via two endpoints:

- `GET /latest` - Fetches current weather reading
- `GET /history?hours={n}` - Fetches historical data (1-168 hours)

All API calls are defined in `src/lib/api.ts`.

## Customization

### Theme

The dashboard uses Shadcn UI with a neutral color scheme. To customize:

1. Edit CSS variables in `src/app/globals.css`
2. Modify the `:root` and `.dark` sections for light/dark themes

### Time Ranges

To add more time range options, edit the `Select` component in `src/app/page.tsx`:

```tsx
<SelectItem value="168">7 days</SelectItem>
<SelectItem value="336">14 days</SelectItem> // Add custom ranges
```

### Charts

Charts are built with Recharts. Customize in `src/components/weather/history-charts.tsx`:

- Line colors: `stroke` property
- Chart height: `height` in `ResponsiveContainer`
- Axis labels and formatting

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Library**: Shadcn UI (Radix UI + Tailwind CSS)
- **Charts**: Recharts
- **Date Handling**: date-fns
- **Styling**: Tailwind CSS v4

## Troubleshooting

### "Failed to load current conditions"

- Ensure the FastAPI backend is running
- Check that `NEXT_PUBLIC_API_URL` in `.env.local` is correct
- Verify CORS is configured in the backend

### Charts not displaying

- Check browser console for errors
- Ensure historical data is available in S3
- Verify the backend `/history` endpoint returns data

## License

MIT