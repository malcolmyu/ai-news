"""
Style constraints and design system for AI News System.

This module provides a centralized style management system that defines
consistent visual presentation across all outputs.
"""

from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class StyleConstraints:
    """Manages visual style constraints and design system for the AI News System."""

    # Color System - Tailwind-inspired but more refined
    COLORS = {
        # Primary Palette - Professional AI theme
        "primary": {
            "50": "#f0f9ff",
            "100": "#e0f2fe",
            "200": "#bae6fd",
            "300": "#7dd3fc",
            "400": "#38bdf8",
            "500": "#0ea5e9",  # Main AI blue
            "600": "#0284c7",
            "700": "#0369a1",
            "800": "#075985",
            "900": "#0c4a6e"
        },
        # Secondary Palette - Data visualization
        "secondary": {
            "50": "#f5f3ff",
            "100": "#ede9fe",
            "200": "#ddd6fe",
            "300": "#c4b5fd",
            "400": "#a78bfa",
            "500": "#8b5cf6",  # Main accent purple
            "600": "#7c3aed",
            "700": "#6d28d9",
            "800": "#5b21b6",
            "900": "#4c1d95"
        },
        # Neutral Palette - Text and backgrounds
        "neutral": {
            "50": "#fafafa",
            "100": "#f5f5f5",
            "200": "#e5e5e5",
            "300": "#d4d4d4",
            "400": "#a3a3a3",
            "500": "#737373",
            "600": "#525252",
            "700": "#404040",
            "800": "#262626",
            "900": "#171717"
        },
        # Semantic Colors
        "semantic": {
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "info": "#3b82f6"
        },
        # Gradients - Modern AI aesthetics
        "gradients": {
            "primary": "linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%)",
            "secondary": "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
            "accent": "linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%)",
            "dark": "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
            "ai-gradient": "linear-gradient(135deg, #0ea5e9 0%, #7c3aed 50%, #8b5cf6 100%)"
        }
    }

    # Font System - Modern typography
    FONTS = {
        "families": {
            "sans": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            "mono": "'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace",
            "serif": "'Crimson Pro', 'Source Serif Pro', Georgia, 'Times New Roman', serif"
        },
        "sizes": {
            "xs": "0.75rem",    # 12px
            "sm": "0.875rem",   # 14px
            "base": "1rem",     # 16px
            "lg": "1.125rem",   # 18px
            "xl": "1.25rem",    # 20px
            "2xl": "1.5rem",    # 24px
            "3xl": "1.875rem",  # 30px
            "4xl": "2.25rem",   # 36px
            "5xl": "3rem",      # 48px
            "6xl": "3.75rem"    # 60px
        },
        "weights": {
            "light": 300,
            "normal": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700,
            "extrabold": 800
        },
        "letter_spacing": {
            "tight": "-0.025em",
            "normal": "0",
            "wide": "0.025em"
        },
        "line_heights": {
            "none": 1,
            "tight": 1.25,
            "normal": 1.5,
            "relaxed": 1.625,
            "loose": 2
        }
    }

    # Layout System - Responsive and modern
    LAYOUTS = {
        "breakpoints": {
            "sm": "640px",
            "md": "768px",
            "lg": "1024px",
            "xl": "1280px",
            "2xl": "1536px"
        },
        "spacing": {
            "xs": "0.5rem",   # 8px
            "sm": "0.75rem",  # 12px
            "md": "1rem",     # 16px
            "lg": "1.5rem",   # 24px
            "xl": "2rem",     # 32px
            "2xl": "3rem",    # 48px
            "3xl": "4rem",    # 64px
            "4xl": "6rem"     # 96px
        },
        "max_widths": {
            "none": "none",
            "xs": "20rem",    # 320px
            "sm": "24rem",    # 384px
            "md": "28rem",    # 448px
            "lg": "32rem",    # 512px
            "xl": "36rem",    # 576px
            "2xl": "42rem",   # 672px
            "3xl": "48rem",   # 768px
            "4xl": "56rem",   # 896px
            "5xl": "64rem",   # 1024px
            "6xl": "72rem",   # 1152px
            "7xl": "80rem"    # 1280px
        },
        "borders": {
            "width": {
                "hairline": "0.5px",
                "thin": "1px",
                "medium": "2px",
                "thick": "4px"
            },
            "radius": {
                "none": "0px",
                "sm": "0.125rem",   # 2px
                "md": "0.25rem",    # 4px
                "lg": "0.5rem",     # 8px
                "xl": "0.75rem",    # 12px
                "2xl": "1rem",      # 16px
                "3xl": "1.5rem",    # 24px
                "full": "9999px"
            }
        },
        "shadows": {
            "xs": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            "sm": "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
            "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
            "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
            "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
            "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
            "inner": "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
            "ai-glow": "0 0 20px -5px #0ea5e9, 0 0 10px -2px #8b5cf6"
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize StyleConstraints with optional configuration."""
        self.config = config or {}
        logger.info("StyleConstraints initialized")

    def get_color(self, palette: str, shade: str) -> str:
        """Get a specific color from the color system."""
        try:
            return self.COLORS[palette][shade]
        except KeyError:
            logger.warning(f"Color not found: {palette}.{shade}, returning neutral.700")
            return self.COLORS["neutral"]["700"]

    def get_gradient(self, name: str) -> str:
        """Get a specific gradient from the color system."""
        try:
            return self.COLORS["gradients"][name]
        except KeyError:
            logger.warning(f"Gradient not found: {name}, returning primary gradient")
            return self.COLORS["gradients"]["primary"]

    def get_css(self, theme: str = "default") -> str:
        """
        Generate complete CSS stylesheet based on the style system.

        Args:
            theme: Theme variant (default, dark, minimal)

        Returns:
            Complete CSS stylesheet as string
        """
        logger.info(f"Generating CSS for theme: {theme}")

        # Base CSS variables
        css_vars = f"""
/* AI News System Design Tokens */
:root {{
    /* Color Tokens */
    --color-primary-50: {self.get_color('primary', '50')};
    --color-primary-100: {self.get_color('primary', '100')};
    --color-primary-200: {self.get_color('primary', '200')};
    --color-primary-300: {self.get_color('primary', '300')};
    --color-primary-400: {self.get_color('primary', '400')};
    --color-primary-500: {self.get_color('primary', '500')};
    --color-primary-600: {self.get_color('primary', '600')};
    --color-primary-700: {self.get_color('primary', '700')};
    --color-primary-800: {self.get_color('primary', '800')};
    --color-primary-900: {self.get_color('primary', '900')};

    --color-secondary-50: {self.get_color('secondary', '50')};
    --color-secondary-100: {self.get_color('secondary', '100')};
    --color-secondary-200: {self.get_color('secondary', '200')};
    --color-secondary-300: {self.get_color('secondary', '300')};
    --color-secondary-400: {self.get_color('secondary', '400')};
    --color-secondary-500: {self.get_color('secondary', '500')};
    --color-secondary-600: {self.get_color('secondary', '600')};
    --color-secondary-700: {self.get_color('secondary', '700')};
    --color-secondary-800: {self.get_color('secondary', '800')};
    --color-secondary-900: {self.get_color('secondary', '900')};

    --color-neutral-50: {self.get_color('neutral', '50')};
    --color-neutral-100: {self.get_color('neutral', '100')};
    --color-neutral-200: {self.get_color('neutral', '200')};
    --color-neutral-300: {self.get_color('neutral', '300')};
    --color-neutral-400: {self.get_color('neutral', '400')};
    --color-neutral-500: {self.get_color('neutral', '500')};
    --color-neutral-600: {self.get_color('neutral', '600')};
    --color-neutral-700: {self.get_color('neutral', '700')};
    --color-neutral-800: {self.get_color('neutral', '800')};
    --color-neutral-900: {self.get_color('neutral', '900')};

    --color-success: {self.COLORS['semantic']['success']};
    --color-warning: {self.COLORS['semantic']['warning']};
    --color-error: {self.COLORS['semantic']['error']};
    --color-info: {self.COLORS['semantic']['info']};

    /* Gradient Tokens */
    --gradient-primary: {self.get_gradient('primary')};
    --gradient-secondary: {self.get_gradient('secondary')};
    --gradient-accent: {self.get_gradient('accent')};
    --gradient-dark: {self.get_gradient('dark')};
    --gradient-ai: {self.get_gradient('ai-gradient')};

    /* Font Tokens */
    --font-sans: {self.FONTS['families']['sans']};
    --font-mono: {self.FONTS['families']['mono']};
    --font-serif: {self.FONTS['families']['serif']};

    --font-size-xs: {self.FONTS['sizes']['xs']};
    --font-size-sm: {self.FONTS['sizes']['sm']};
    --font-size-base: {self.FONTS['sizes']['base']};
    --font-size-lg: {self.FONTS['sizes']['lg']};
    --font-size-xl: {self.FONTS['sizes']['xl']};
    --font-size-2xl: {self.FONTS['sizes']['2xl']};
    --font-size-3xl: {self.FONTS['sizes']['3xl']};
    --font-size-4xl: {self.FONTS['sizes']['4xl']};
    --font-size-5xl: {self.FONTS['sizes']['5xl']};
    --font-size-6xl: {self.FONTS['sizes']['6xl']};

    --font-weight-light: {self.FONTS['weights']['light']};
    --font-weight-normal: {self.FONTS['weights']['normal']};
    --font-weight-medium: {self.FONTS['weights']['medium']};
    --font-weight-semibold: {self.FONTS['weights']['semibold']};
    --font-weight-bold: {self.FONTS['weights']['bold']};
    --font-weight-extrabold: {self.FONTS['weights']['extrabold']};

    --letter-spacing-tight: {self.FONTS['letter_spacing']['tight']};
    --letter-spacing-normal: {self.FONTS['letter_spacing']['normal']};
    --letter-spacing-wide: {self.FONTS['letter_spacing']['wide']};

    --line-height-none: {self.FONTS['line_heights']['none']};
    --line-height-tight: {self.FONTS['line_heights']['tight']};
    --line-height-normal: {self.FONTS['line_heights']['normal']};
    --line-height-relaxed: {self.FONTS['line_heights']['relaxed']};
    --line-height-loose: {self.FONTS['line_heights']['loose']};

    /* Spacing Tokens */
    --spacing-xs: {self.LAYOUTS['spacing']['xs']};
    --spacing-sm: {self.LAYOUTS['spacing']['sm']};
    --spacing-md: {self.LAYOUTS['spacing']['md']};
    --spacing-lg: {self.LAYOUTS['spacing']['lg']};
    --spacing-xl: {self.LAYOUTS['spacing']['xl']};
    --spacing-2xl: {self.LAYOUTS['spacing']['2xl']};
    --spacing-3xl: {self.LAYOUTS['spacing']['3xl']};
    --spacing-4xl: {self.LAYOUTS['spacing']['4xl']};

    /* Border Tokens */
    --border-width-hairline: {self.LAYOUTS['borders']['width']['hairline']};
    --border-width-thin: {self.LAYOUTS['borders']['width']['thin']};
    --border-width-medium: {self.LAYOUTS['borders']['width']['medium']};
    --border-width-thick: {self.LAYOUTS['borders']['width']['thick']};

    --border-radius-sm: {self.LAYOUTS['borders']['radius']['sm']};
    --border-radius-md: {self.LAYOUTS['borders']['radius']['md']};
    --border-radius-lg: {self.LAYOUTS['borders']['radius']['lg']};
    --border-radius-xl: {self.LAYOUTS['borders']['radius']['xl']};
    --border-radius-2xl: {self.LAYOUTS['borders']['radius']['2xl']};
    --border-radius-3xl: {self.LAYOUTS['borders']['radius']['3xl']};
    --border-radius-full: {self.LAYOUTS['borders']['radius']['full']};

    /* Shadow Tokens */
    --shadow-xs: {self.LAYOUTS['shadows']['xs']};
    --shadow-sm: {self.LAYOUTS['shadows']['sm']};
    --shadow-md: {self.LAYOUTS['shadows']['md']};
    --shadow-lg: {self.LAYOUTS['shadows']['lg']};
    --shadow-xl: {self.LAYOUTS['shadows']['xl']};
    --shadow-2xl: {self.LAYOUTS['shadows']['2xl']};
    --shadow-inner: {self.LAYOUTS['shadows']['inner']};
    --shadow-ai-glow: {self.LAYOUTS['shadows']['ai-glow']};

    /* Max Width Tokens */
    --max-w-xs: {self.LAYOUTS['max_widths']['xs']};
    --max-w-sm: {self.LAYOUTS['max_widths']['sm']};
    --max-w-md: {self.LAYOUTS['max_widths']['md']};
    --max-w-lg: {self.LAYOUTS['max_widths']['lg']};
    --max-w-xl: {self.LAYOUTS['max_widths']['xl']};
    --max-w-2xl: {self.LAYOUTS['max_widths']['2xl']};
    --max-w-3xl: {self.LAYOUTS['max_widths']['3xl']};
    --max-w-4xl: {self.LAYOUTS['max_widths']['4xl']};
    --max-w-5xl: {self.LAYOUTS['max_widths']['5xl']};
    --max-w-6xl: {self.LAYOUTS['max_widths']['6xl']};
    --max-w-7xl: {self.LAYOUTS['max_widths']['7xl']};
}}
"""

        # Theme-specific overrides
        theme_overrides = {
            "dark": """
/* Dark Mode Overrides */
[data-theme="dark"] {
    --color-neutral-50: {self.get_color('neutral', '900')};
    --color-neutral-100: {self.get_color('neutral', '800')};
    --color-neutral-200: {self.get_color('neutral', '700')};
    --color-neutral-300: {self.get_color('neutral', '600')};
    --color-neutral-400: {self.get_color('neutral', '500')};
    --color-neutral-500: {self.get_color('neutral', '400')};
    --color-neutral-600: {self.get_color('neutral', '300')};
    --color-neutral-700: #e5e5e5;
    --color-neutral-800: #f5f5f5;
    --color-neutral-900: #fafafa;
}
""",
            "minimal": """
/* Minimal Theme - Reduced color palette */
:root {
    --color-secondary-500: var(--color-primary-500);
    --gradient-secondary: var(--gradient-primary);
    --shadow-ai-glow: none;
}
"""
        }

        # Utility classes
        utilities = """
/* AI News System Utility Classes */

/* Typography */
.text-gradient {
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.text-gradient-secondary {
    background: var(--gradient-secondary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Layout */
.container {
    width: 100%;
    max-width: var(--max-w-6xl);
    margin-left: auto;
    margin-right: auto;
    padding-left: var(--spacing-lg);
    padding-right: var(--spacing-lg);
}

.section {
    padding-top: var(--spacing-2xl);
    padding-bottom: var(--spacing-2xl);
}

/* Cards */
.card {
    background: white;
    border-radius: var(--border-radius-xl);
    box-shadow: var(--shadow-lg);
    padding: var(--spacing-xl);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: var(--shadow-xl);
    transform: translateY(-2px);
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-sm) var(--spacing-lg);
    border-radius: var(--border-radius-md);
    font-weight: var(--font-weight-medium);
    text-decoration: none;
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
    font-size: var(--font-size-sm);
}

.btn-primary {
    background: var(--gradient-primary);
    color: white;
}

.btn-primary:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

.btn-secondary {
    background: var(--color-neutral-100);
    color: var(--color-neutral-800);
}

.btn-secondary:hover {
    background: var(--color-neutral-200);
}

/* AI Elements */
.ai-badge {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--gradient-ai);
    color: white;
    border-radius: var(--border-radius-full);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    text-transform: uppercase;
    letter-spacing: var(--letter-spacing-wide);
}

.ai-glow {
    box-shadow: var(--shadow-ai-glow);
}

/* Animations */
.fade-in {
    animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.slide-in {
    animation: slideIn 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
"""

        # Combine all CSS
        css = css_vars
        if theme in theme_overrides:
            css += theme_overrides[theme]
        css += utilities

        logger.info(f"Generated CSS stylesheet ({len(css)} characters)")
        return css
