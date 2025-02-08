# Development Guide

## Core Architecture
Desktop financial planning app built with FastAPI backend and React frontend. Uses SQLite with direct queries (no ORM). Complex data combinations, particularly for scenarios, are handled through SQL views because scenarios require consistent combining of base facts with various overrides - this is better handled in SQL than building these combinations repeatedly in Python.

## Development Principles
Group code by financial planning domains, keeping calculations separate from API/UI layers. Database views handle complex data relationships (especially scenario overrides) to keep Python code focused on financial calculations rather than data assembly. Data fetching matches natural workflow.

## Project Dependencies
Backend: Python, FastAPI, SQLite
Frontend: React, Vite, Tailwind
Development: DB Browser for SQLite

## Structure
```
fipli/
├── backend/
│   ├── database/     # DB, views, and schema
│   ├── endpoints/    # FastAPI routes
│   ├── finance/     # Business logic by domain
│   └── calculations/ # Financial calculation engine
└── frontend/
    └── src/
        ├── pages/    # Main app screens
        ├── services/ # API communication
        └── shared/   # Reusable components
```

## Data Management
The DB file (/backend/database/FIPLI.db) is fully populated with mock data. No need to create, populate, or manually define tables. Ready to use.

Database views are crucial - they handle the complex task of combining base facts with scenario overrides, making Python code cleaner and more focused on business logic rather than data assembly. Review schema.sql to understand this pattern. The user will evaluate suggested schema modifications and update the database through DB Browser for SQLite if needed.

## Data Flow
Database views combine related data efficiently, particularly for scenarios where base facts, overrides, and adjustments need consistent combining. FastAPI manages API layer while Python focuses on financial calculations. React Query handles frontend data fetching
