# Theme Persistence - Migration & Developer Guide

## For Other Developers

### New Theme Pattern
Instead of manually manipulating the DOM for theme changes, always use the theme utilities:

❌ **Old Way (Don't do this)**
```typescript
// Bad - Direct DOM manipulation, no persistence
document.documentElement.classList.add('dark');
document.documentElement.classList.remove('dark');
```

✅ **New Way (Do this)**
```typescript
// Good - Uses centralized utilities with persistence
import { setTheme } from '@/lib/theme';
setTheme('dark');
```

### Accessing Current Theme

❌ **Old Way**
```typescript
const isDark = document.documentElement.classList.contains('dark');
```

✅ **New Way**
```typescript
import { useTheme } from '@/hooks/useTheme';

function MyComponent() {
  const { isDark, theme } = useTheme();
  // ...
}
```

### Listening to Theme Changes

✅ **New Capability**
```typescript
import { onThemeChange } from '@/lib/theme-utils';

// Listen to theme changes across browser tabs
const unsubscribe = onThemeChange((theme) => {
  console.log('Theme switched to:', theme);
  // Perform any theme-dependent updates
});

// Clean up on unmount
useEffect(() => {
  return unsubscribe;
}, []);
```

## Components That Use Theme

### Settings Page
- File: `web/app/settings/page.tsx`
- Lines: Theme toggle UI and applyTheme() function
- Now uses `setTheme()` from `@/lib/theme`

### Global Provider
- File: `web/context/GlobalContext.tsx`
- Theme initialized on app startup
- Syncs with backend on refresh

### Layout
- File: `web/app/layout.tsx`
- ThemeScript in head prevents flash
- Loads theme before React hydration

## API Endpoints Used

### Get Settings
```
GET /api/v1/settings
```
Response includes `ui.theme: "light" | "dark"`

### Update Settings
```
PUT /api/v1/settings/ui
Body: { theme: "light" | "dark", language: "en" | "zh", ... }
```

### Update Theme Only
```
PUT /api/v1/settings/theme
Body: { theme: "light" | "dark" }
```

## localStorage Key
- **Key**: `deeptutor-theme`
- **Values**: `"light"` or `"dark"`
- **Scope**: Browser/Device local storage

## Troubleshooting

### Theme keeps reverting to light
**Solution**: Ensure `setTheme()` is being called instead of direct DOM manipulation

### Flash of wrong theme on load
**Check**:
1. Is `ThemeScript` component in `layout.tsx` head? 
2. Is it before other scripts?

**Solution**: Make sure `<ThemeScript />` is inside `<head>` in `layout.tsx`

### Theme not syncing to backend
**Check**:
1. Is `PUT /api/v1/settings/ui` endpoint responding?
2. Is `handleSave()` being called in settings page?

**Solution**: Verify backend settings endpoint is working properly

### localStorage not available (SSR environment)
**All functions check** for window availability:
```typescript
if (typeof window === "undefined") return null;
```
This makes all utilities safe to use in SSR/Next.js

## Best Practices

1. **Always use `setTheme()`** for theme changes - it handles all edge cases
2. **Use `useTheme()` hook** in components - provides clean, reactive API
3. **Don't manually toggle classes** - defeats the purpose of centralized management
4. **Listen for changes** with `onThemeChange()` - for cross-tab sync
5. **Test theme persistence** - refresh page after changing theme

## Future Enhancements

Possible improvements:
- [ ] Add theme transition animations
- [ ] Support custom theme colors
- [ ] Add theme preview before saving
- [ ] Theme auto-switch based on time of day
- [ ] Per-page theme settings
- [ ] Theme inheritance from workspace/team settings

## File Structure

```
web/
├── lib/
│   ├── theme.ts              ← Core utilities
│   └── theme-utils.ts        ← Helper functions
├── hooks/
│   └── useTheme.ts           ← React hook
├── components/
│   └── ThemeScript.tsx       ← Flash prevention
└── app/
    └── layout.tsx            ← Uses ThemeScript
```

## Key Files to Review

1. **Start here**: `web/lib/theme.ts` - Core implementation
2. **Then**: `web/hooks/useTheme.ts` - React integration
3. **Then**: `web/components/ThemeScript.tsx` - Flash prevention
4. **Reference**: `THEME_PERSISTENCE.md` - Full documentation
