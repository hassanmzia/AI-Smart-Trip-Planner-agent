# AI Travel Agent Frontend

A modern, responsive React TypeScript frontend for the AI Travel Agent application with goal-based flight optimization and utility-based hotel recommendations.

## Features

- **Smart Search**: AI-powered flight and hotel search with goal-based optimization
- **Real-time Updates**: WebSocket integration for live notifications and price updates
- **Dark Mode**: Full dark mode support with system preference detection
- **Responsive Design**: Mobile-first design that works on all devices
- **AI Assistant**: Floating AI chat widget for travel assistance
- **Modern UI**: Built with TailwindCSS, Headless UI, and Heroicons
- **Type Safety**: Full TypeScript support with strict mode
- **State Management**: Zustand for global state, React Query for server state
- **Authentication**: JWT-based authentication with automatic token refresh
- **Payment Integration**: Stripe payment integration (UI ready)

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router v6** - Client-side routing
- **React Query** - Server state management
- **Zustand** - Global state management
- **Axios** - HTTP client
- **Socket.io Client** - WebSocket client
- **Headless UI** - Unstyled UI components
- **Heroicons** - Icon library
- **React Hot Toast** - Toast notifications
- **Framer Motion** - Animation library
- **date-fns** - Date utilities

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

3. Update environment variables in `.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_STRIPE_PUBLIC_KEY=your_stripe_public_key_here
```

### Development

Start the development server on port 3090:

```bash
npm run dev
```

The app will be available at `http://localhost:3090`

### Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

### Linting

Run ESLint:

```bash
npm run lint
```

Type check:

```bash
npm run type-check
```

## Docker

Build and run with Docker:

```bash
# Build
docker build -t ai-travel-agent-frontend .

# Run
docker run -p 3090:3090 ai-travel-agent-frontend
```

## Project Structure

```
src/
├── components/         # React components
│   ├── common/        # Reusable UI components
│   ├── layout/        # Layout components (Header, Footer)
│   ├── flight/        # Flight-specific components
│   ├── hotel/         # Hotel-specific components
│   └── booking/       # Booking components & AI chat
├── pages/             # Page components
├── services/          # API services
├── store/             # Zustand stores
├── hooks/             # Custom React hooks
├── types/             # TypeScript type definitions
├── utils/             # Utility functions
│   ├── constants.ts   # App constants
│   ├── helpers.ts     # Helper functions
│   └── formatters.ts  # Formatting utilities
├── App.tsx           # Main app component
├── main.tsx          # Entry point
└── index.css         # Global styles
```

## Key Components

### Pages

- **HomePage** - Landing page with search
- **SearchPage** - Advanced search interface
- **FlightResultsPage** - Flight search results with goal-based evaluation
- **HotelResultsPage** - Hotel search results with utility scores
- **BookingPage** - Booking flow
- **PaymentPage** - Payment processing
- **DashboardPage** - User dashboard
- **ProfilePage** - User profile
- **ItineraryPage** - Trip itinerary builder
- **AdminDashboardPage** - Admin analytics

### Components

- **Header** - Navigation with auth, theme toggle, notifications
- **Footer** - Site footer with links
- **AgentChat** - Floating AI assistant chat widget
- **FlightCard** - Flight result card with goal evaluation
- **HotelCard** - Hotel result card with utility scores
- **Button** - Reusable button component
- **Input** - Form input component
- **Card** - Card container component
- **Modal** - Modal dialog component
- **Loading** - Loading spinner component

## Features Implementation

### Authentication

- JWT-based authentication
- Automatic token refresh
- Protected routes
- Role-based access control

### AI Agent Chat

- Floating chat widget
- Real-time responses
- Context-aware suggestions
- Chat history

### Goal-Based Flight Search

- Budget constraint evaluation
- Multi-criteria optimization
- Utility scoring
- Visual recommendation badges

### Utility-Based Hotel Recommendations

- Price value scoring
- Location scoring
- Rating scoring
- Amenities scoring
- Overall utility calculation

### Real-time Features

- WebSocket connection
- Price alerts
- Booking updates
- Notifications

### Dark Mode

- System preference detection
- Manual toggle
- Persistent preference
- Smooth transitions

## API Integration

The frontend connects to the backend API at the URL specified in `VITE_API_URL`. All API calls are made through service modules in `src/services/`.

### Available Services

- **authService** - Authentication
- **flightService** - Flight search and booking
- **hotelService** - Hotel search and booking
- **bookingService** - Booking management
- **agentService** - AI agent interactions
- **websocketService** - WebSocket connections
- **paymentService** - Payment processing
- **priceAlertService** - Price alerts
- **itineraryService** - Trip itineraries
- **notificationService** - Notifications

## State Management

### Zustand Stores

- **authStore** - User authentication state
- **searchStore** - Search parameters and results
- **bookingStore** - Current booking state
- **notificationStore** - Notifications

### React Query

Used for server state management with automatic caching, refetching, and error handling.

## Contributing

1. Follow the existing code style
2. Use TypeScript for all new files
3. Add types for all props and function parameters
4. Use functional components with hooks
5. Follow the component structure in existing files
6. Test your changes before committing

## License

MIT
