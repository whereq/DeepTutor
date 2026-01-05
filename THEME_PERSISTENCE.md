# Theme Persistence Implementation

## Overview
Implemented persistent light/dark theme support using localStorage with fallback to system preferences. The theme preference is now:
1. **Persisted locally** - Theme preference saved to localStorage
2. **Synced to backend** - Theme synced with backend settings.json  
3. **Flash-free** - Theme applied before React hydration to prevent flash
4. **System preference aware** - Falls back to system theme if not set

## Changes Made

### 1. New Files Created

#### `/web/lib/theme.ts`
Core theme utilities providing:
- `getStoredTheme()` - Get theme from localStorage
- `saveThemeToStorage()` - Save theme to localStorage
- `getSystemTheme()` - Detect system color scheme preference
- `applyThemeToDocument()` - Apply theme class to HTML element
- `initializeTheme()` - Initialize theme on startup (prioritizes localStorage → system → default)
- `setTheme()` - Set and persist theme (applies to DOM + localStorage)

#### `/web/components/ThemeScript.tsx`
Inline script that runs before React hydration to:
- Read localStorage theme preference
- Apply theme class to DOM immediately
- Prevent flash of wrong theme on page load

#### `/web/hooks/useTheme.ts`
Custom React hook for using theme anywhere in the app:
```typescript
const { theme, isDark, isLight, setTheme, isLoaded } = useTheme();
```

### 2. Modified Files

#### `/web/app/layout.tsx`
- Added `ThemeScript` component in `<head>` to initialize theme before hydration
- Prevents theme flash on page load

#### `/web/context/GlobalContext.tsx`
- Imported theme utilities
- Updated `refreshSettings()` to persist theme to localStorage when fetched from backend
- Updated `useEffect` to initialize theme immediately using `initializeTheme()`
- Falls back to localStorage if backend fetch fails

#### `/web/app/settings/page.tsx`
- Imported `setTheme` utility
- Updated `applyTheme()` to use `setTheme()` which persists to localStorage
- Updated `handleSave()` to sync theme immediately when settings are saved
- Theme changes now persist both locally and to backend

## How It Works

### On Page Load
1. **ThemeScript** (in head) runs immediately:
   - Reads `deeptutor-theme` from localStorage
   - Applies `dark` class to `<html>` if needed
   - No flash because this runs before React

2. **GlobalProvider** (React):
   - Calls `initializeTheme()` to get current theme
   - Fetches theme from backend `/api/v1/settings`
   - If backend differs, updates state and localStorage

### On Theme Change
1. User toggles theme in Settings page
2. `handleUIChange()` calls `applyTheme()`
3. `applyTheme()` calls `setTheme()` which:
   - Applies theme class to DOM immediately
   - Saves to localStorage
4. On save, theme is also synced to backend via `/api/v1/settings/ui`

### Priority Order
When determining theme, the app uses:
1. **localStorage** (`deeptutor-theme`) - User's last selection
2. **System preference** - `prefers-color-scheme: dark` media query
3. **Default** - Light mode

## Usage Examples

### In Components
```typescript
import { useTheme } from '@/hooks/useTheme';

function MyComponent() {
  const { theme, isDark, setTheme } = useTheme();
  
  return (
    <button onClick={() => setTheme(isDark ? 'light' : 'dark')}>
      Toggle Theme
    </button>
  );
}
```

### In Global Context
```typescript
import { setTheme } from '@/lib/theme';

// Apply theme immediately
setTheme('dark');
```

### Direct Theme Control
```typescript
import { setTheme, initializeTheme, getStoredTheme } from '@/lib/theme';

// Get stored preference
const theme = getStoredTheme(); // 'light' | 'dark' | null

// Initialize theme
const currentTheme = initializeTheme(); // 'light' | 'dark'

// Set and persist theme
setTheme('dark');
```

## Benefits
✅ **No Flash** - Theme applied before hydration  
✅ **Persistent** - Saved to localStorage and backend  
✅ **Responsive** - System preference detection  
✅ **Resilient** - Falls back to localStorage if API fails  
✅ **Accessible** - Uses standard `prefers-color-scheme` media query  
✅ **Flexible** - Can be used anywhere in the app via hook or utilities

## Testing
1. **Verify no flash** - Open app and check theme loads immediately
2. **Toggle theme** - Change theme in settings and refresh page
3. **Offline mode** - Disconnect from backend, theme should persist
4. **System preference** - Change system theme, verify fallback works on first visit
