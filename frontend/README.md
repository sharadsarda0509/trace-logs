# TraceID Log Search - Frontend

React frontend for querying Splunk logs by trace ID.

## Features

- 🔍 Simple trace ID search interface
- ⚙️ Advanced options (collapsible)
  - AEM Service configuration
  - Index selection
  - AEM Tier (author/publish)
  - Time range adjustment
  - Result limit control
- 📊 JSON viewer with syntax highlighting
- 📋 Copy logs to clipboard
- 🎨 Clean, modern UI
- 📱 Responsive design

## Development

### Prerequisites

- Node.js 18+ or Bun
- Backend API running at `http://localhost:8002`

### Install Dependencies

```bash
bun install
```

or

```bash
npm install
```

### Run Development Server

```bash
bun run dev
```

or

```bash
npm run dev
```

The dev server will start at `http://localhost:5173` with proxy configuration to forward API requests to the backend.

### Build for Production

```bash
bun run build
```

or

```bash
npm run build
```

This builds the React app and outputs static files to `../static/` directory, which the FastAPI backend will serve.

## Architecture

```
User Browser → React App (port 5173 in dev, :8002 in prod)
                    ↓
              POST /api/logs/search
                    ↓
            FastAPI Backend (:8002)
                    ↓
              Splunk API
```

### Components

- **App.jsx** - Main application with state management
- **SearchForm.jsx** - Search form with trace ID input and advanced options
- **LogViewer.jsx** - JSON viewer for displaying log results
- **api.js** - API client for backend communication

### API Integration

The frontend calls the backend API:

**Endpoint:** `POST /api/logs/search`

**Request:**
```json
{
  "trace_id": "abc-123-def-456",
  "aem_service": "cm-p153560-e1607906",
  "index": "dx_aem_engineering",
  "aem_tier": "author",
  "time_range_hours": 24,
  "limit": 500
}
```

**Response:**
```json
{
  "success": true,
  "trace_id": "abc-123-def-456",
  "total_count": 42,
  "logs": [...],
  "query_time_seconds": 1.23
}
```

## Configuration

### Default Values

Default values are configured in `SearchForm.jsx`:

```javascript
const [aemService, setAemService] = useState('cm-p153560-e1607906');
const [index, setIndex] = useState('dx_aem_engineering');
const [aemTier, setAemTier] = useState('author');
const [timeRangeHours, setTimeRangeHours] = useState(24);
const [limit, setLimit] = useState(500);
```

You can modify these defaults to match your environment.

### API Base URL

The API base URL is automatically determined:
- **Development:** Uses Vite proxy to `http://localhost:8002`
- **Production:** Uses relative paths (served by FastAPI)

To change the backend URL, modify `api.js`:

```javascript
const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:8002';
```

## Dependencies

- **react** - UI library
- **react-dom** - React DOM rendering
- **axios** - HTTP client
- **react-json-view** - JSON viewer component
- **vite** - Build tool and dev server

## Styling

The app uses vanilla CSS with:
- Flexbox layouts
- Responsive design (mobile-friendly)
- Clean color scheme
- Smooth transitions and hover effects

CSS files:
- `App.css` - Main app layout and header
- `SearchForm.css` - Search form styling
- `LogViewer.css` - Log viewer and results styling
- `index.css` - Global styles and resets
