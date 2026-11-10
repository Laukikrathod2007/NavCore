/**
 * Design Tokens & Theme Configuration
 * Extracted and customized from https://www.moss.dev/
 */

export const MOSS_THEME = {
  colors: {
    // Backgrounds
    bgDefault: "#fafafa",
    bgSubtle: "#fbfbfa",
    bgCard: "#ffffff",
    bgCardHover: "#f8f9f8",
    bgDark: "#0a0a0a",
    bgCode: "#0f0f0f",
    
    // Brand & Moss Accents
    mossAccent: "#2d5016",      // Deep Forest Moss
    mossSage: "#5c8a5c",        // Sage Green
    mossLight: "#dbf0e0",       // Tinted highlight
    mossSurface: "#f0f7f2",     // Soft pill background
    mossBorder: "#abe6c7",      // Active green border
    mossPulse: "#05df72",       // Live ping green
    
    // Text / Foregrounds
    fgDefault: "#0f1410",       // Deep Charcoal / Forest Black
    fgSecondary: "#525252",     // Neutral gray
    fgTertiary: "#888888",      // Muted caption
    fgAccent: "#2d5016",        // Accent link
    fgInvert: "#ffffff",        // Crisp white
    
    // Borders & Dividers
    borderDefault: "#e5e5e0",   // Subtle card border
    borderLight: "#f0f0ec",     // Delicate divider
    borderHover: "#d0d0c8",     // Border on hover
    
    // Status
    success: "#00a544",
    warning: "#dd7400",
    error: "#e40014",
    info: "#3080ff",
  },
  shadows: {
    card: "0 1px 3px rgba(0, 0, 0, 0.04), 0 8px 24px -4px rgba(0, 0, 0, 0.03)",
    cardHover: "0 8px 28px -4px rgba(0, 0, 0, 0.08), 0 2px 8px -2px rgba(0, 0, 0, 0.04)",
    elevated: "0 16px 48px -12px rgba(0, 0, 0, 0.12)",
    navcore: "0 10px 40px -10px rgba(45, 80, 22, 0.15)",
  },
  typography: {
    fontSans: "var(--font-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif)",
    fontMono: "var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace)",
    fontSerif: "var(--font-serif, 'Playfair Display', Georgia, serif)",
  }
};

