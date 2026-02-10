---
schema: "2.0"
name: fullstack-nextjs
workdir: nextjs-app
---

# Full-Stack Next.js App

Build a complete Next.js application with authentication, database, and deployment config.

<input id="app-config">
Configure your Next.js application:

<form type="json">
{
  "fields": [
    {
      "name": "appName",
      "type": "text",
      "label": "App Name",
      "required": true
    },
    {
      "name": "authProvider",
      "type": "select",
      "label": "Auth Provider",
      "options": [
        { "value": "nextauth-github", "label": "Nextauth Github" },
        { "value": "nextauth-google", "label": "Nextauth Google" },
        { "value": "clerk", "label": "Clerk" },
        { "value": "none", "label": "None" }
      ]
    },
    {
      "name": "database",
      "type": "select",
      "label": "Database",
      "options": [
        { "value": "prisma-sqlite", "label": "Prisma Sqlite" },
        { "value": "prisma-postgres", "label": "Prisma Postgres" },
        { "value": "drizzle-sqlite", "label": "Drizzle Sqlite" }
      ]
    },
    {
      "name": "uiLibrary",
      "type": "select",
      "label": "UI Library",
      "options": [
        { "value": "tailwind", "label": "Tailwind" },
        { "value": "shadcn", "label": "Shadcn" },
        { "value": "chakra", "label": "Chakra" }
      ]
    }
  ]
}
</form>
</input>

<task id="init">
Create a new Next.js 14 project with:
- App Router
- TypeScript
- The selected UI library (Tailwind/shadcn/Chakra)
- ESLint configuration
- Project name from appName input
</task>

<task id="database">
Set up the database based on user selection:
- Install the selected ORM (Prisma or Drizzle)
- Create initial schema with User and Session models
- Generate database client
- Create a db utility file for connections
- Add seed script for development data
</task>

<task id="auth">
Set up authentication based on authProvider selection:
- Install and configure the auth library
- Create login/logout pages
- Set up protected routes middleware
- Create a useAuth hook for client components
- Add environment variable templates to .env.example
</task>

<break id="verify-setup">
Verify the base setup before adding features:
1. Check that the dev server runs
2. Test database connection
3. Verify auth flow works

Continue when ready to add features.
</break>

<task id="dashboard">
Create a protected dashboard page:
- Show user profile information
- Display a simple data table (use mock data)
- Add navigation with logout button
- Make it responsive for mobile
</task>

<task id="api-routes">
Create API routes:
- GET/POST /api/users - User management
- GET /api/profile - Current user profile
- Add proper error handling and validation
- Use the database ORM for data operations
</task>

<shell id="format">
cd nextjs-app && npm run lint -- --fix
</shell>

<note id="complete">
## Full-Stack App Ready!

Your Next.js app includes:
- Authentication with {authProvider}
- Database with {database}
- Protected dashboard
- RESTful API routes
- Responsive UI

### Getting Started

```bash
cd nextjs-app

# Set up environment
cp .env.example .env.local
# Edit .env.local with your credentials

# Initialize database
npm run db:push
npm run db:seed

# Start development
npm run dev
```

Open http://localhost:3000 to see your app!
</note>
