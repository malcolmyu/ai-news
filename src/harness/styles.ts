export interface Styles {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
  };
  fonts: {
    heading: string;
    body: string;
    code: string;
  };
  layout: {
    maxWidth: string;
    spacing: string;
    borderRadius: string;
  };
}

export const defaultStyles: Styles = {
  colors: {
    primary: '#3b82f6',
    secondary: '#f8fafc',
    accent: '#60a5fa',
    background: '#f8fafc',
    surface: '#ffffff',
    text: '#334155',
    textSecondary: '#64748b',
    border: '#e2e8f0',
  },
  fonts: {
    heading: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    body: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    code: "'Fira Code', 'Consolas', monospace",
  },
  layout: {
    maxWidth: '1200px',
    spacing: '1.5rem',
    borderRadius: '8px',
  },
};

export function validateStyles(styles: any): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!styles) {
    errors.push('Styles object is required');
    return { valid: false, errors };
  }

  const requiredSections = ['colors', 'fonts'];
  for (const section of requiredSections) {
    if (!styles[section]) {
      errors.push(`Missing required section: ${section}`);
    }
  }

  const requiredColors = ['primary', 'secondary'];
  if (styles.colors) {
    for (const color of requiredColors) {
      if (!styles.colors[color]) {
        errors.push(`Missing required color: ${color}`);
      } else if (!/^#[0-9A-Fa-f]{6}$/.test(styles.colors[color])) {
        errors.push(`Invalid color format for ${color}: ${styles.colors[color]}`);
      }
    }
  }

  const requiredFonts = ['heading', 'body'];
  if (styles.fonts) {
    for (const font of requiredFonts) {
      if (!styles.fonts[font]) {
        errors.push(`Missing required font: ${font}`);
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
