---
name: Axiom Archive
colors:
  surface: '#051424'
  surface-dim: '#051424'
  surface-bright: '#2c3a4c'
  surface-container-lowest: '#010f1f'
  surface-container-low: '#0d1c2d'
  surface-container: '#122131'
  surface-container-high: '#1c2b3c'
  surface-container-highest: '#273647'
  on-surface: '#d4e4fa'
  on-surface-variant: '#bac9cc'
  inverse-surface: '#d4e4fa'
  inverse-on-surface: '#233143'
  outline: '#849396'
  outline-variant: '#3b494c'
  surface-tint: '#00daf3'
  primary: '#c3f5ff'
  on-primary: '#00363d'
  primary-container: '#00e5ff'
  on-primary-container: '#00626e'
  inverse-primary: '#006875'
  secondary: '#b7c8e1'
  on-secondary: '#213145'
  secondary-container: '#3a4a5f'
  on-secondary-container: '#a9bad3'
  tertiary: '#e8ecff'
  on-tertiary: '#283044'
  tertiary-container: '#c8d0ea'
  on-tertiary-container: '#51596f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#9cf0ff'
  primary-fixed-dim: '#00daf3'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#004f58'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#dae2fd'
  tertiary-fixed-dim: '#bec6e0'
  on-tertiary-fixed: '#131b2e'
  on-tertiary-fixed-variant: '#3f465c'
  background: '#051424'
  on-background: '#d4e4fa'
  surface-variant: '#273647'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0.05em
  body-md:
    fontFamily: IBM Plex Serif
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-sm:
    fontFamily: IBM Plex Serif
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  label-caps:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.1em
  mono-data:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 48px
  container-max: 1440px
---

## Brand & Style
The design system is built upon a **Scientific Noir** aesthetic, tailored for high-fidelity research and deep-data investigation. It avoids stereotypical extraterrestrial tropes in favor of an **Intelligence Agency** or **Academic Repository** atmosphere. The personality is authoritative, cold, and meticulously organized.

The style leverages a **Modern-Technical** approach:
- **Minimalism with Purpose:** Heavy use of negative space to isolate complex data points.
- **Structural Integrity:** Elements are aligned to a strict grid to evoke stability and institutional trust.
- **Data-Density:** Interfaces are designed to maximize information throughput without visual clutter, using thin lines and precise labeling.
- **Subtle Noir:** Depth is created through tonal layering rather than aggressive shadows, mimicking the look of specialized reconnaissance software.

## Colors
The palette is rooted in a "Deep Space" dark mode, utilizing high-contrast accents for critical data indicators.

- **Primary (Cyan):** Reserved for active states, data points, and precise call-to-actions. It represents the "light of inquiry."
- **Secondary (Slate):** Used for supporting UI elements, borders, and secondary text to maintain a low-profile aesthetic.
- **Surface (Charcoal/Navy):** The background hierarchy uses `#020617` (Deepest), `#0F172A` (Surface), and `#1E293B` (Elevated).
- **Functional Colors:** Specific hues are assigned to the provenance lifecycle: 
    - **Proposed:** Amber (Cautionary/Unverified)
    - **Live:** Emerald (Verified/Active)
    - **Rejected:** Rose (Invalidated)
    - **Superseded:** Violet (Historical/Archival)

## Typography
Typography is a dual-system approach balancing institutional authority with technical precision.

- **UI & Navigation:** Uses **Inter** for its clarity and neutral tone. Headlines utilize tight tracking to feel "classified" and urgent.
- **Long-form Research:** Uses **IBM Plex Serif** for all investigative claims, witness testimonies, and academic papers. The serif structure increases reading stamina and lends a "published" feel to raw data.
- **Technical Metadata:** Uses **Geist** (Monospaced) for coordinates, timestamps, and provenance IDs. This font should be used for all "machine-read" data to differentiate it from human narrative.

## Layout & Spacing
The layout follows a **Fixed-Grid** logic for desktop to ensure data visualizations remain consistent. 

- **Grid:** A 12-column grid with 24px gutters. Content is often organized into "Dossier" blocks spanning 4, 6, or 8 columns.
- **Rhythm:** An 8px base unit is used for vertical rhythm, though 4px increments are permitted for tight technical components (e.g., small data tables).
- **Responsive Behavior:** On mobile, the grid collapses to a single column with 16px side margins. Data tables should switch to a "Card-Index" view to maintain legibility of status indicators and provenance links.

## Elevation & Depth
In this design system, depth is communicated through **Tonal Layering** and **Technical Outlines** rather than shadows.

- **Tiers:** The background is the lowest tier. Content cards are one step lighter (`#0F172A`). Hover states or active selections are another step lighter or outlined in a thin 1px Primary Cyan border.
- **Backdrop Blurs:** Used sparingly for modal overlays to maintain focus on the "Dossier" currently being inspected, creating a "Light Table" effect.
- **Ghost Borders:** Elements are separated by low-opacity (`10-20%`) Slate dividers. This reinforces the technical, blueprint-like nature of the UI.

## Shapes
The shape language is primarily **Soft (0.25rem)**. 

- **Hard Angles:** Larger container edges may use 0px roundedness to feel more structural and architectural.
- **Component Radius:** Buttons and input fields use a subtle 4px radius. This prevents the UI from feeling "bubbly" or consumer-grade, maintaining its professional stance.
- **Data Points:** Small circular pips are used for status indicators to stand out against the predominantly rectangular layout.

## Components
- **Status Badges:** Small, rectangular tags with a `label-caps` font. They use a 10% opacity background of the status color with a 100% opacity left-hand "indicator bar" 2px wide.
- **Provenance Links:** Text links using `mono-data` font, underlined with a dotted line. On hover, they reveal a small tooltip with the source's "Reliability Score."
- **Action Buttons:** Primary buttons are solid Slate with Cyan text; secondary buttons are "Ghost" style with thin Slate borders. No heavy gradients or 3D effects.
- **Investigation Cards:** Dark Slate background, 1px border, with a clear header area for the Case ID (Monospaced) and the current Status Badge.
- **Data Tables:** High-density, zebra-striped with 5% Slate. Headers are always `label-caps` and sticky to the top of the viewport.
- **Input Fields:** Underlined or fully boxed with a 1px Slate border. The focus state transitions the border to Primary Cyan with a subtle outer glow.