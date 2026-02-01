# Receipts Frontend

React/Next.js frontend for the Receipts proof-first social platform.

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Stack

- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Zustand (state)
- TanStack Query (data fetching)

## Structure

```
src/
├── app/          # Next.js pages
├── components/   # UI components
├── lib/          # Utilities, API client, types
└── state/        # Zustand stores
```

## API

Set `NEXT_PUBLIC_API_URL` in `.env.local` (defaults to http://localhost:8000)
