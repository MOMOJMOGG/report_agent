# Multi-Agent RAG Dashboard

A modern, dark-themed React dashboard for monitoring and managing the Multi-Agent RAG system with a technology agent aesthetic.

## Features

🌙 **Dark Mode Technology Theme**
- Professional dark color palette with cyan/blue technology accents
- Glass morphism effects and subtle animations
- Technology-inspired typography with JetBrains Mono

🎛️ **Intuitive Dashboard Interface**
- Real-time job monitoring and status updates
- Interactive analytics with charts and visualizations
- Comprehensive system health monitoring
- Agent performance tracking

📊 **Analytics & Monitoring**
- Job execution trends and success rates
- Agent performance metrics with pie charts
- Execution time analysis over 24h periods
- System resource monitoring

📋 **Job Management**
- Start new analysis jobs with custom parameters
- Real-time progress tracking with animated progress bars
- Job status filtering and search functionality
- Detailed job execution history

📄 **Report Management**
- Download generated Excel reports
- File size and metadata display
- Worksheet content preview
- Organized report library

⚙️ **System Configuration**
- Database connection settings
- RAG agent parameters (similarity threshold, API limits)
- Report generation options
- Dashboard server configuration

## Technology Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for responsive styling
- **Recharts** for interactive data visualizations
- **Lucide React** for modern icons
- **Framer Motion** for smooth animations
- **React Router** for navigation
- **Axios** for API communication

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Development

### Project Structure
```
src/
├── components/           # Reusable UI components
│   ├── Layout.tsx       # Main layout with sidebar
│   ├── Sidebar.tsx      # Navigation sidebar
│   ├── Header.tsx       # Top header with search
│   └── widgets/         # Dashboard widgets
├── pages/               # Page components
│   ├── Dashboard.tsx    # Main dashboard
│   ├── Analytics.tsx    # Analytics page
│   ├── Jobs.tsx         # Job management
│   ├── Reports.tsx      # Report management
│   └── Settings.tsx     # System settings
├── hooks/               # Custom React hooks
├── utils/               # Utility functions
├── types/               # TypeScript type definitions
└── context/             # React context providers
```

### API Integration

The dashboard automatically proxies API requests to the FastAPI backend running on port 8000. All API endpoints are available under `/api/v1/`.

### Theming

The dashboard uses a custom dark theme with technology-inspired colors:

- **Primary**: Cyan/Blue (#0ea5e9) for main actions and highlights
- **Success**: Green (#22c55e) for positive states
- **Warning**: Amber (#f59e0b) for caution states
- **Accent**: Red (#ef4444) for errors and critical states
- **Dark**: Zinc grays (#18181b to #fafafa) for backgrounds and text

### Responsive Design

The dashboard is fully responsive and works on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

## Features Implementation

### Real-time Updates
- Job status polling every 5 seconds
- Health check every 30 seconds
- Automatic refresh on status changes

### Interactive Charts
- Bar charts for job trends
- Pie charts for agent performance
- Line charts for execution time analysis
- Responsive and animated

### Status Indicators
- Color-coded status badges
- Animated progress bars
- Pulse animations for active states
- Real-time system monitoring

### User Experience
- Smooth page transitions
- Loading states with spinners
- Toast notifications for feedback
- Intuitive navigation patterns

## Backend Integration

The dashboard integrates with the FastAPI backend through:

1. **Health Monitoring** - `/health` endpoint
2. **Job Management** - `/analysis/*` endpoints
3. **Report Access** - `/reports/*` endpoints
4. **File Upload** - `/data/upload` endpoint

All API calls include proper error handling and loading states.

## Customization

### Colors
Modify the color palette in `tailwind.config.js` under the `colors` section.

### Components
All components are modular and can be easily customized or replaced.

### Layouts
The layout system is flexible and supports different page structures.

This dashboard provides a comprehensive interface for monitoring and managing your Multi-Agent RAG system with a modern, professional appearance that emphasizes the technology and AI aspects of the platform.