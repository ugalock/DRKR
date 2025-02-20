
---

## Explanation of Each File / Folder

### `main.tsx`
- **Purpose**: Application entry point for Vite + React.  
- **Key Responsibilities**:
  - Renders the root `<App />` component into the DOM.  
  - Wraps the entire app with global providers such as React Query’s `<QueryClientProvider>`, `<BrowserRouter>`, or any context providers that need to be global.  

### `App.tsx`
- **Purpose**: The top-level React component.  
- **Key Responsibilities**:
  - Declares the main application layout, including navigation bars, footers, or persistent UI elements.  
  - Renders `<Routes />` or references the routing structure from `routes/index.tsx`.  
  - Often the place for global error boundaries or catch-all error states.

### `index.css` (or `index.scss`)
- **Purpose**: Global CSS or Tailwind directives.  
- **Key Responsibilities**:
  - Imports Tailwind’s `@tailwind base; @tailwind components; @tailwind utilities;`.  
  - Sets any global or reset styles.  

### `assets/`
- **Purpose**: Houses static assets such as images, logos, and icons.  
- **Key Responsibilities**:
  - Make sure large files or media are optimized or stored on a CDN if needed.

---

### `components/`
- **Purpose**: Reusable presentational components or small building blocks that don’t belong to a single page or feature.  
- **Structure**:
  - `common/`: Atoms or molecules used widely (e.g., `<Button />`, `<Modal />`, `<Spinner />`).  
  - Additional folders or files for shared UI elements, such as `<Navbar />`, `<Footer />`, etc.

---

### `pages/`
Holds **page-level** or **route-level** components. Each folder typically represents a route or group of routes.

1. **`pages/Home/`**  
   - A landing page or dashboard.  
   - Summarizes the platform’s purpose or highlights trending “deep research” items.

2. **`pages/Auth/`**  
   - Contains login, logout, register, or OAuth callback pages.  
   - Integrates with the `AuthContext` or `authService.ts` to handle tokens (JWT) or session data.

3. **`pages/Research/`**  
   - Displays lists of deep research items, detail views for a single research entry, forms to create new research, etc.  
   - Possibly a route like `/research/:id` showing the prompt, final report, ratings, comments, etc.

4. **`pages/Organization/`**  
   - Pages for organization management (view org members, roles, private research, etc.).  
   - Ties into RBAC (admin, owner, etc.).

5. **`pages/Tags/`**  
   - Subreddit-like channels grouped by tags.  
   - List deep research items that have a particular tag.  
   - Moderators can manage the tag or approve new items in that channel.

6. Additional pages as needed, e.g., a `Search/` page for advanced searching or a dedicated page for multi-length summaries.

---

### `features/`
This folder is an optional **feature-based** approach that can store domain-specific logic (reducers, slices, subcomponents) for each major concept. It can be used in conjunction with or as an alternative to a purely “pages” approach.

1. **`features/deepResearch/`**  
   - Domain logic for deep research items (if using Redux or Recoil).  
   - Service calls to fetch or mutate research records.  
   - Reusable components specific to deep research domain (e.g., `<ResearchItemCard />`).
   - `useResearch` hook for fetching and mutating research records.

2. **`features/tags/`**  
   - Manages how tags are handled (global, org, user-specific).  
   - Logic for sub-reddit style channels.

3. **`features/organizations/`**  
   - Manage org membership, roles, invites, etc.

4. **`features/search/`**  
   - Hooks or logic for semantic search queries to Pinecone or the backend.  
   - Possibly orchestrates advanced filtering, chunk retrieval, or multi-length summary fetching.

5. And so on, for each major “feature” or domain chunk of your app.

---

### `routes/`
- **Purpose**: Central place to define your application’s route structure using **React Router**.  
- **`index.tsx`**:
  - Exports a `<Routes>` element that defines all top-level paths, nested routes, and 404 handling.  
  - Helps keep `App.tsx` clean.  
  - Example:
    ```tsx
    import { Routes, Route } from "react-router-dom";
    import HomePage from "../pages/Home/HomePage";
    import ResearchList from "../pages/Research/ResearchList";
    // ...

    export function AppRoutes() {
      return (
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/research" element={<ResearchList />} />
          {/* ... */}
        </Routes>
      );
    }
    ```

---

### `services/`
- **Purpose**: Abstract API calls, authentication, or external integrations. Generally stores logic that *talks to the backend or external services (like Pinecone)*.

1. **`services/api/`**  
   - `axiosConfig.ts`: Configures base URL, interceptors, or headers for all HTTP requests.  
   - `userApi.ts`: Functions to call `/users` endpoints (create user, get user info, etc.).  
   - `researchApi.ts`: Functions to call `/deep-research` endpoints (CRUD operations).  
   - `tagsApi.ts`: Functions to handle creating/editing tags, retrieving sub-reddit style channels, etc.

2. **`services/queryClient.ts`**  
   - Sets up a **React Query** `QueryClient`, possibly customizing behaviors like retries or caching.

3. **`services/authService.ts`**  
   - Encapsulates login, logout, token storage, and validation logic.  
   - Could store the JWT in localStorage or cookies, handle refresh flows, etc.

---

### `store/`
- **Purpose**: If you use a global state management library (e.g., Redux, Zustand, Recoil), you keep store definitions here.  
- **`userStore.ts`** (example):  
  - Centralized user session info, profile data, or tokens.  
  - Could also handle role-based checks if not handled in a context/hook approach.

*(If you’re not using Redux or a global store, you can remove or adapt this folder.)*

---

### `hooks/`
- **Purpose**: Custom React hooks. Typically:
  - **useAuth**: Encapsulate login state, user roles, permission checks, or token refresh.  
  - **useFetchOrg**: Retrieve or cache organization data (members, roles).  
  - Additional domain-specific hooks: `useResearch()`, `useTags()`, etc.

---

### `context/`
- **Purpose**: React Context providers for global or app-wide states.  
- **Examples**:
  - `AuthContext.tsx`: Houses user credentials and login status.  
  - `OrgContext.tsx`: Context for the currently active organization, membership role, etc.

*(Alternatively, you might merge these into `store/` if using a single global store or rely on feature-based contexts in `features/`.)*

---

### `utils/`
- **Purpose**: General-purpose helpers or utility functions that don’t fall under a specific domain.  
- **Examples**:
  - `constants.ts`: Shared constants, enumerations (like “visibility: private, org, public”).  
  - `formatters.ts`: Utility functions for date/time formatting, string manipulation, etc.

---

### `types/`
- **Purpose**: Global TypeScript typings and interfaces.  
- **Examples**:
  - `user.d.ts`: Defines the `User` interface matching the backend (id, username, email, roles).  
  - `research.d.ts`: Types for a `DeepResearch` item, chunk structure, summaries, etc.  
  - `org.d.ts`: Organization membership shapes.  
  - `index.d.ts`: Possibly used for global declarations or module augmentations.

*(File extensions can be `.ts` or `.d.ts` depending on how you structure your type definitions.)*

---

### `vite-env.d.ts`
- **Purpose**: Vite-specific type declarations.  
- **Key Responsibilities**:
  - Typically auto-generated by Vite to declare types for `import.meta.env`.

---

## Conclusion

This **frontend folder structure** is designed to align with **the comprehensive project’s features**:

1. **Research** pages and features handle multi-length summaries, chunked retrieval, and advanced RAG.  
2. **Tag** pages (or features) support sub-reddit style channels, with tools for moderation and post validation.  
3. **Organization** sections and contexts handle RBAC, private vs. org vs. public scoping.  
4. **Services** connect to the backend’s REST API and Pinecone or other vector-based endpoints for semantic search.  
5. **React Query** is integrated for caching/fetching resource data, while custom hooks provide reusability across pages.  

This structure should **scale** as your knowledge repository grows in complexity, fosters collaborative features, and integrates advanced AI workflows. Feel free to tweak or rename folders to match your team’s preferences or coding standards.
