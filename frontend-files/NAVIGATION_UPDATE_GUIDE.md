# Navigation Update Guide - Document Generator

This guide shows you how to add the Document Generator to your pace-frontend-modern navigation.

## Files to Update

You need to update 2 files:
1. `src/App.tsx` - Add the route
2. `src/shared/components/layout/Header.tsx` - Add the navigation link
3. `src/pages/index.ts` - Export the DocumentGenerator component

---

## Step 1: Update src/App.tsx

### Current Location
Line 3 (imports) and approximately line 24 (routes)

### Changes Needed

**Add this import** after line 3:
```typescript
import { DocumentGenerator } from '@/pages/DocumentGenerator'
```

**Add this route** after the `/how-to` route (around line 24):
```typescript
<Route path="/document-generator" element={<Layout><DocumentGenerator /></Layout>} />
```

### Complete Updated File

Replace your entire `src/App.tsx` with this:

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/shared/components/layout'
import { Dashboard, InitialMEL, FinalMEL, HowTo } from '@/pages'
import { DocumentGenerator } from '@/pages/DocumentGenerator'
import { TestSupabase } from './TestSupabase'

function App() {

  // Mock login for development - DISABLED for simplified version
  // useEffect(() => {
  //   if (!isAuthenticated) {
  //     mockLogin('editor') // Change to 'admin' or 'super_admin' to test different roles
  //   }
  // }, [isAuthenticated])

  return (
    <BrowserRouter>
      <Routes>
        {/* Main App Routes with Layout */}
        <Route path="/" element={<Layout><Dashboard /></Layout>} />
        <Route path="/initial-mel" element={<Layout><InitialMEL /></Layout>} />
        <Route path="/final-mel" element={<Layout><FinalMEL /></Layout>} />
        <Route path="/how-to" element={<Layout><HowTo /></Layout>} />
        <Route path="/document-generator" element={<Layout><DocumentGenerator /></Layout>} />

        {/* Hidden Routes - Temporarily disabled */}
        {/* <Route path="/memo-generator" element={<Layout><MemoGenerator /></Layout>} /> */}
        {/* <Route path="/reports" element={<Layout><Reports /></Layout>} /> */}
        {/* <Route path="/settings" element={<Layout><Settings /></Layout>} /> */}
        {/* <Route path="/account" element={<Layout><Account /></Layout>} /> */}

        {/* Admin Routes - Protected */}
        {/* <Route
          path="/admin"
          element={
            hasPermission('admin') ? (
              <Layout><AdminDashboard /></Layout>
            ) : (
              <Navigate to="/" replace />
            )
          }
        /> */}

        {/* Test Route (without layout) */}
        <Route path="/test-supabase" element={<TestSupabase />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

---

## Step 2: Update src/shared/components/layout/Header.tsx

### Find the Navigation Section

Look for the section with links like:
- Dashboard
- Master Eligibility List (dropdown)
- How To Guide

### Add Document Generator Link

**Add this code** AFTER the "How To" link and BEFORE the Admin Dashboard section:

```typescript
{/* Document Generator */}
<Link
  to="/document-generator"
  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
    isActive('/document-generator')
      ? 'bg-indigo-700 text-white'
      : 'text-indigo-100 hover:bg-indigo-600 hover:text-white'
  }`}
>
  Document Generator
</Link>
```

### Visual Example

Your navigation should look like this:

```typescript
{/* Dashboard */}
<Link to="/" className="...">
  Dashboard
</Link>

{/* Master Eligibility List Dropdown */}
<Menu as="div" className="relative">
  {/* MEL dropdown content */}
</Menu>

{/* How To Guide */}
<Link to="/how-to" className="...">
  How To
</Link>

{/* Document Generator - NEW! */}
<Link
  to="/document-generator"
  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
    isActive('/document-generator')
      ? 'bg-indigo-700 text-white'
      : 'text-indigo-100 hover:bg-indigo-600 hover:text-white'
  }`}
>
  Document Generator
</Link>

{/* Admin Dashboard (conditional) */}
{hasPermission('admin') && (
  <Link to="/admin" className="...">
    Admin Dashboard
  </Link>
)}
```

---

## Step 3: Update src/pages/index.ts

If you have a `src/pages/index.ts` file that exports all pages, add:

```typescript
export { DocumentGenerator } from './DocumentGenerator'
```

If this file doesn't exist, you can skip this step (the direct import in App.tsx will work).

---

## Alternative: Replace Commented Memo Generator

If you want to replace the commented-out "Memorandum Generator" with the new Document Generator, find this line in Header.tsx:

```typescript
{/* <Link to="/memo-generator">Memorandum Generator</Link> */}
```

And replace it with:

```typescript
<Link
  to="/document-generator"
  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
    isActive('/document-generator')
      ? 'bg-indigo-700 text-white'
      : 'text-indigo-100 hover:bg-indigo-600 hover:text-white'
  }`}
>
  Document Generator
</Link>
```

---

## Step 4: Verify the Changes

After making these updates:

1. **Restart your frontend dev server:**
   ```bash
   cd pace-frontend-modern
   npm run dev
   ```

2. **Check the navigation bar** - You should see "Document Generator" between "How To" and "Admin Dashboard"

3. **Click the link** - Should navigate to `/document-generator`

4. **Test the feature** - Try generating a document

---

## Troubleshooting

### "Cannot find module '@/pages/DocumentGenerator'"

**Solution**: Make sure you copied the DocumentGenerator.tsx file to `src/pages/`:
```bash
# From pace-backend-clean directory
cp frontend-files/pages/DocumentGenerator.tsx ../pace-frontend-modern/src/pages/
```

### "Link is not defined" error in Header.tsx

**Solution**: Ensure Header.tsx imports Link from react-router-dom:
```typescript
import { Link, useLocation } from 'react-router-dom'
```

### Navigation link doesn't highlight when active

**Solution**: Make sure the `isActive` function exists in Header.tsx:
```typescript
const location = useLocation()
const isActive = (path: string) => location.pathname === path
```

### Style doesn't match other nav items

**Solution**: Copy the exact className from another nav link (like "How To") to ensure consistent styling.

---

## Quick Commit Commands

After making the changes, commit them to your branch:

```bash
cd pace-frontend-modern
git add src/App.tsx src/shared/components/layout/Header.tsx
git commit -m "Add Document Generator navigation and routing"
git push origin claude/document-generator-frontend-011CUp15ejs3GMBfxgJBuovn
```

---

## Visual Preview

After the update, your navigation bar will show:

```
[PACE Logo] Dashboard | [MEL ▼] | How To | Document Generator | Admin Dashboard
```

And clicking "Document Generator" will show the 4-step document creation wizard!
