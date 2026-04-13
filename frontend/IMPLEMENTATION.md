# Context Compression Engine - Implementation Guide

## Overview

This is a production-grade frontend for the Context Compression Engine - a SaaS application that transforms long chat conversations and development notes into structured, actionable insights using AI.

## Key Features Implemented

### 1. **Dark Theme & Premium UI**
- Dark mode color scheme (#0e1117 background, #e94560 primary, #0f3460 accent)
- Glassmorphic card design with gradient overlays
- Smooth transitions and hover effects
- Responsive design (mobile-first)

### 2. **Input Management**
- Auto-expanding textarea with live character counter
- Drag & drop file upload support (.txt, .md, .log)
- Sample input button for quick testing
- Input validation with warnings for large texts (>10k chars)
- Clear input button for quick reset

### 3. **API Integration**
- `useCompression` hook with proper state management (loading, error, success)
- Support for `/compress` and `/extract` endpoints
- Response handling with correct field mapping (`structured` instead of `structured_data`)
- API key input field (optional, uses backend default)
- Model selection dropdown (GPT-4, Claude 3, etc.)

### 4. **Results Display**
- Animated stat cards showing:
  - Token count
  - Compression ratio
  - Processing time
- Tabbed interface for different views:
  - **Context Pack**: Full compressed summary with syntax highlighting
  - **Structured**: Expandable sections for goal, tech stack, decisions, problems, solutions
  - **Code**: Collapsible code snippets with syntax highlighting
  - **JSON**: Raw structured data for programmatic use
- Copy-to-clipboard functionality with toast notifications
- Download features:
  - Download Context Pack as .txt
  - Download structured data as .json

### 5. **State Persistence**
- LocalStorage integration to save:
  - Current input text
  - Compression history (last 20 items)
  - Selected model
  - API key (if provided)
- Auto-restore on page reload
- Non-intrusive persistence (doesn't block UI)

### 6. **History Management**
- Sidebar with previous compressions (desktop only)
- Each history item shows:
  - Preview of input (first 50 chars)
  - Timestamp with relative time formatting (e.g., "5m ago")
  - Delete button for individual items
- Clear all history option
- Click to reload previous input
- Hidden on mobile, revealed on desktop (responsive)

### 7. **UX Enhancements**
- Empty state with call-to-action
- Loading skeleton with spinner
- Error handling with toast notifications
- Keyboard shortcut: `Ctrl + Enter` to compress
- Disabled states for buttons during loading
- Mobile-responsive sidebar (hidden on mobile)
- Smooth animations and transitions
- Success toasts on copy/download

### 8. **Error Handling**
- Network error handling with user-friendly messages
- Input validation (no empty input compression)
- Large input warnings
- API error responses with meaningful messages
- Toast notifications for all errors

## File Structure

```
/app
  /page.tsx                 # Main page component with state management
  /layout.tsx              # Root layout with metadata
  /globals.css             # Theme colors and global styles

/components
  /input-section.tsx       # Input textarea with file upload
  /controls-section.tsx    # Model selection, API key, compress buttons
  /results-display.tsx     # Results tabs, export features
  /history-sidebar.tsx     # Previous compressions list

/hooks
  /use-compression.ts      # API integration hook
  /use-toast.ts           # Toast notification hook (provided)

.env.example              # Environment variable template
```

## Environment Variables

### `NEXT_PUBLIC_API_URL` (Optional)
- Backend API URL for compression endpoints
- Default: `https://packgpt.onrender.com`
- Set to your production API URL for deployment
- Must support `/compress` and `/extract` POST endpoints

## API Integration

### Expected Backend Endpoints

#### POST `/compress`
Request:
```json
{
  "input": "long text...",
  "model": "gpt-4"
}
```

Response:
```json
{
  "context_pack": "compressed summary text...",
  "structured": {
    "goal": "main objective",
    "tech_stack": ["Next.js", "React", ...],
    "key_decisions": ["decision 1", ...],
    "problems_faced": ["problem 1", ...],
    "solutions_applied": ["solution 1", ...],
    "code_snippets": ["code 1", ...]
  },
  "token_count": 1500,
  "compression_ratio": 8.5,
  "processing_time": 2.3
}
```

#### POST `/extract`
Same request format, returns same response format (JSON-only extraction).

## Component Details

### InputSection
- Auto-expanding textarea
- Character counter with large input warning (>10k)
- File upload support
- Sample input loader
- Clear button

### ControlsSection
- Model dropdown (gpt-4, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet)
- API key input (optional)
- Primary "Compress" button
- Secondary "Extract JSON" button
- Keyboard shortcut hint (Ctrl + Enter)

### ResultsDisplay
- Stats cards with token count, compression ratio, processing time
- 4 main tabs: Context Pack, Structured, Code, JSON
- Expandable sections for structured data
- Copy & download buttons for each section
- Syntax highlighting for code snippets

### HistorySidebar
- Collapsible history list
- Timestamp formatting (relative time)
- Individual delete buttons
- Clear all history option
- Click to restore previous input
- Desktop-only (hidden on mobile)

## Styling System

### Color Palette (Dark Mode - Default)
- **Background**: #0e1117 (deep dark)
- **Foreground**: #e8eaed (light text)
- **Primary**: #e94560 (vibrant red)
- **Accent**: #0f3460 (dark blue)
- **Secondary**: #21262d (dark gray)
- **Border**: #30363d (medium gray)

### Design Tokens
All colors use CSS custom properties:
- `--background`, `--foreground`
- `--primary`, `--primary-foreground`
- `--accent`, `--accent-foreground`
- `--card`, `--card-foreground`
- `--border`, `--muted`, `--input`

### Tailwind Classes
- Flexbox for layouts: `flex items-center justify-between`
- Spacing scale: `p-4`, `gap-3`, `mb-2`
- Responsive prefixes: `md:grid-cols-2`, `lg:col-span-2`
- Semantic classes: `text-foreground`, `bg-card`, `border-border`

## Data Flow

1. **User Input**: Paste text or upload file → stored in state
2. **Compression**: Click "Compress" → calls `useCompression.compress()`
3. **API Call**: POST to backend with input text
4. **Response**: Parse response and extract `structured` fields
5. **Display**: Show results in tabbed interface
6. **Persistence**: Auto-save to localStorage
7. **History**: Add to history list, store last 20 items
8. **Export**: Download as .txt or .json

## Responsive Design

### Mobile (< 768px)
- Single column layout
- History sidebar hidden (accessible via button)
- Full-width input and controls
- Stacked buttons

### Tablet (768px - 1024px)
- 2-column layout (input + results)
- Small sidebar (if shown)
- Responsive grid for stats

### Desktop (> 1024px)
- 3-column layout (sidebar + input + controls on left, results on right)
- Fixed sidebar (width: 16rem / 256px)
- Full-featured UI
- All features visible

## Performance Optimizations

- Client-side state management (no unnecessary re-renders)
- Lazy loading for history items
- Efficient localStorage updates
- Debounced textarea resize
- Memoized callbacks in hooks
- Optimized re-renders with proper dependencies

## Security Considerations

1. **API Key Input**: Optional, securely handled in state
2. **LocalStorage**: Stores input and history locally (no sensitive data on server)
3. **CORS**: Handled by backend (frontend uses `fetch` with proper headers)
4. **Input Validation**: Server-side validation recommended in backend
5. **XSS Protection**: React handles HTML escaping automatically

## Future Enhancements

1. Dark/Light mode toggle
2. Export to Markdown with frontmatter
3. Real-time collaboration
4. Advanced filters and search in history
5. Compression presets (aggressive, balanced, conservative)
6. Integration with external storage (Google Drive, S3)
7. Batch processing multiple files
8. Custom prompt templates

## Development

### Local Development
```bash
# Set environment variable
NEXT_PUBLIC_API_URL=https://packgpt.onrender.com npm run dev

# Or create .env.local
echo "NEXT_PUBLIC_API_URL=https://packgpt.onrender.com" > .env.local
npm run dev
```

### Building
```bash
npm run build
npm run start
```

### Deployment
Push to Vercel or any Next.js hosting provider and set `NEXT_PUBLIC_API_URL` environment variable.

## Troubleshooting

### "Cannot POST /compress"
- Verify backend is running on the correct port
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Ensure backend has `/compress` endpoint

### Empty results
- Backend might not be returning `structured` field
- Check network tab for actual API response
- Verify response format matches expected structure

### LocalStorage not saving
- Check browser privacy settings
- Verify localStorage is not disabled
- Check browser console for errors

### API key not working
- Ensure API key is valid and has correct permissions
- Backend should handle API key validation
- Check backend logs for authentication errors
