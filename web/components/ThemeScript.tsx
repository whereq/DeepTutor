"use client";

/**
 * ThemeScript - Initializes theme from localStorage before React hydration
 * This prevents the flash of wrong theme on page load
 */
export default function ThemeScript() {
  const themeScript = `
    (function() {
      try {
        const stored = localStorage.getItem('deeptutor-theme');
        console.log('[ThemeScript] localStorage theme:', stored);
        
        if (stored === 'dark') {
          console.log('[ThemeScript] Applying dark theme from localStorage');
          document.documentElement.classList.add('dark');
        } else if (stored === 'light') {
          console.log('[ThemeScript] Applying light theme from localStorage');
          document.documentElement.classList.remove('dark');
        } else {
          console.log('[ThemeScript] No theme in localStorage, checking system preference');
          // Use system preference if not set
          if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            console.log('[ThemeScript] System prefers dark, applying dark theme');
            document.documentElement.classList.add('dark');
            localStorage.setItem('deeptutor-theme', 'dark');
          } else {
            console.log('[ThemeScript] System prefers light, applying light theme');
            localStorage.setItem('deeptutor-theme', 'light');
          }
        }
      } catch (e) {
        console.error('[ThemeScript] Error:', e);
      }
    })();
  `;

  return (
    <script
      dangerouslySetInnerHTML={{ __html: themeScript }}
      suppressHydrationWarning
    />
  );
}
