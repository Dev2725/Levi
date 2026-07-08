# Levi Project Setup Guide

This guide explains how to set up and run the Levi project locally.

## Prerequisites

- Node.js 20+
- pnpm
- Git

## 1. Clone the Repository

```bash
git clone https://github.com/Dev2725/Levi.git
cd Levi
```

## 2. Install Dependencies

```bash
pnpm install
```

## 3. Start the Development Server

```bash
pnpm dev
```

This starts:

- API server: http://localhost:3100
- UI: http://localhost:3100

## 4. Verify the Server

```bash
curl http://localhost:3100/api/health
curl http://localhost:3100/api/companies
```

## 5. Reset Local Database (Optional)

```bash
rm -rf data/pglite
pnpm dev
```

## Project Structure

| Folder | Purpose |
|--------|---------|
| `server/` | Express REST API and orchestration |
| `ui/` | React + Vite board UI |
| `packages/db/` | Database schema and migrations |
| `packages/shared/` | Shared types and constants |
| `packages/adapters/` | Agent adapter implementations |
| `doc/` | Documentation |

## Common Commands

```bash
pnpm test          # Run tests
pnpm -r typecheck  # Type check all packages
pnpm build         # Build all packages
```

## Learn More

- Paperclip docs: https://paperclip.ing/docs
- GitHub Issues: https://github.com/Dev2725/Levi/issues
