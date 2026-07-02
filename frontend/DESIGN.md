---
name: Aura Fintech Interface
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
  on-surface-variant: '#c6c6cb'
  inverse-surface: '#d4e4fa'
  inverse-on-surface: '#233143'
  outline: '#8f9095'
  outline-variant: '#45474b'
  surface-tint: '#c3c6cf'
  primary: '#c3c6cf'
  on-primary: '#2d3137'
  primary-container: '#0d1117'
  on-primary-container: '#797d85'
  inverse-primary: '#5b5e66'
  secondary: '#4fdbc8'
  on-secondary: '#003731'
  secondary-container: '#04b4a2'
  on-secondary-container: '#003f38'
  tertiary: '#d0bcff'
  on-tertiary: '#3c0091'
  tertiary-container: '#160040'
  on-tertiary-container: '#8c5ef8'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dfe2eb'
  primary-fixed-dim: '#c3c6cf'
  on-primary-fixed: '#181c22'
  on-primary-fixed-variant: '#43474e'
  secondary-fixed: '#71f8e4'
  secondary-fixed-dim: '#4fdbc8'
  on-secondary-fixed: '#00201c'
  on-secondary-fixed-variant: '#005048'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#051424'
  on-background: '#d4e4fa'
  surface-variant: '#273647'
typography:
  headline-xl:
    fontFamily: Outfit
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 24px
  message-gap: 16px
  section-gap: 32px
  glass-padding: 20px
---

## Brand & Style
The design system is engineered for a high-stakes financial environment, blending the security of traditional banking with the cutting-edge feel of a modern AI assistant. The aesthetic utilizes **Glassmorphism** to create a sense of depth and transparency, symbolizing clarity in complex mutual fund data. 

The interface leverages deep, layered surfaces and vibrant accent gradients to guide the user's eye toward critical insights. It evokes a feeling of being "ahead of the curve"—sophisticated enough for seasoned investors while remaining intuitive for newcomers.

## Colors
The palette is built on a foundation of **Deep Slate and Obsidian**, providing a high-contrast environment where accents can shine without causing eye strain. 

- **Primary Base:** A rich, dark slate (#020617) serves as the canvas.
- **Accent Gradients:** A "Fintech Aurora" gradient (Violet to Teal) is used for primary actions, progress indicators, and AI-driven insights.
- **Glass Layers:** Surfaces use varying opacities of a mid-slate blue with a subtle white-tinted border to simulate light catching the edge of a glass pane.
- **Functional Colors:** Teal is used for "Success" and growth-related metrics, while a muted Violet handles secondary interactive elements.

## Typography
This design system utilizes **Outfit**, a geometric sans-serif that balances modern tech aesthetics with high readability. 

Headlines use tighter letter spacing and heavier weights to feel "locked-in" and authoritative. Body text maintains a generous line height for long-form financial explanations. Labels and data points are often set in Medium or SemiBold weights to ensure they remain legible when placed over translucent glass backgrounds.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a focus on a centered chat container for the desktop experience.

- **Chat Flux:** On desktop, the chat interface occupies a 720px central column. On mobile, it expands to 100% width with 16px horizontal margins.
- **Rhythm:** An 8px linear scale is used. Components such as chat bubbles and data cards use 20px internal padding to maintain a spacious, premium feel.
- **Safe Areas:** Deep bottom padding is reserved for the fixed input area to ensure the "Glass" input field feels floating and unconstrained.

## Elevation & Depth
Depth is not achieved through shadows, but through **Backdrop Blurs and Tonal Stacking**.

1.  **Level 0 (Base):** Solid `#020617` Slate.
2.  **Level 1 (Panels):** `background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(12px);` with a 1px border `rgba(255, 255, 255, 0.05)`.
3.  **Level 2 (Popovers/Messages):** `background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(20px);` with a 1px border `rgba(255, 255, 255, 0.15)`.
4.  **Level 3 (Accents):** Linear gradients with a soft outer glow (0px 0px 20px rgba(139, 92, 246, 0.3)) to simulate light emission.

## Shapes
The design system adopts a **Rounded** philosophy. Standard cards and chat containers use a 1rem (16px) radius to feel approachable yet modern. 

Input fields and small buttons use a slightly smaller radius (12px) to maintain a crisp look. Interactive "Chips" (suggested questions) use a fully pill-shaped radius to distinguish them from static content containers.

## Components
- **Glass Buttons:** Primary buttons use the Violet-to-Teal gradient with white text. Secondary buttons use a glass surface with a white text and a high-opacity border.
- **Chat Bubbles:** AI responses utilize the Level 1 glass surface. User messages are distinguished by a subtle deep-purple tint `rgba(139, 92, 246, 0.2)` and right-alignment.
- **Mutual Fund Cards:** High-fidelity cards featuring mini-sparklines in Teal (positive) or Rose (negative). The card background should be slightly more opaque than the chat bubble to signify importance.
- **Interactive Input:** A floating glass bar at the bottom. The text caret and focus ring should use the Teal accent color.
- **Feedback Chips:** Small, pill-shaped glass elements for quick-replies (e.g., "Show me more funds," "Risk analysis") that glow subtly on hover.