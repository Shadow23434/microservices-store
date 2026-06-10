---
name: BookStore
colors:
  surface: "#f9fafb"
  surface-dim: "#f3f4f6"
  surface-bright: "#ffffff"
  surface-container-lowest: "#ffffff"
  surface-container-low: "#f9fafb"
  surface-container: "#f3f4f6"
  surface-container-high: "#e5e7eb"
  surface-container-highest: "#d1d5db"
  on-surface: "#111827"
  on-surface-variant: "#6b7280"
  inverse-surface: "#030712"
  inverse-on-surface: "#f9fafb"
  outline: "#9ca3af"
  outline-variant: "#e5e7eb"
  surface-tint: "#d36d24"
  primary: "#d36d24"
  on-primary: "#ffffff"
  primary-container: "#d67a3a"
  on-primary-container: "#3d1c08"
  inverse-primary: "#d88d5b"
  secondary: "#6b7280"
  on-secondary: "#ffffff"
  secondary-container: "#f3f4f6"
  on-secondary-container: "#374151"
  tertiary: "#8f4818"
  on-tertiary: "#ffffff"
  tertiary-container: "#ecd0ba"
  on-tertiary-container: "#3d1c08"
  error: "#dc2626"
  on-error: "#ffffff"
  error-container: "#fee2e2"
  on-error-container: "#991b1b"
  primary-fixed: "#fbf5f0"
  primary-fixed-dim: "#ecd0ba"
  on-primary-fixed: "#3d1c08"
  on-primary-fixed-variant: "#8f4818"
  secondary-fixed: "#f9fafb"
  secondary-fixed-dim: "#e5e7eb"
  on-secondary-fixed: "#111827"
  on-secondary-fixed-variant: "#374151"
  tertiary-fixed: "#f6eadf"
  tertiary-fixed-dim: "#e0b08d"
  on-tertiary-fixed: "#3d1c08"
  on-tertiary-fixed-variant: "#733c16"
  background: "#f9fafb"
  on-background: "#111827"
  surface-variant: "#f3f4f6"
typography:
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 36px
    fontWeight: "700"
    lineHeight: 44px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: "700"
    lineHeight: 36px
    letterSpacing: -0.005em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: "600"
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: "400"
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: "400"
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: "400"
    lineHeight: 16px
  price-display:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: "700"
    lineHeight: 32px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: "700"
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 24px
  panel-padding: 20px
---

## Brand & Style

BookStore is a modern e-commerce bookstore application targeting book lovers, casual readers, and literary enthusiasts who shop online for physical and digital books. The interface must support browsing a catalog, viewing book details, managing a cart and wishlist, and completing checkout — all while conveying trust, warmth, and intellectual credibility.

The visual style is **Editorial Warm-Commerce**: a hybrid of a well-curated independent bookshop and a polished e-commerce storefront. The palette leans into warm amber-orange tones derived from aged leather, worn spines, and candlelight — a deliberate departure from cold tech blues — while Inter's clean geometry keeps the UI crisp and scannable. Playfair Display appears selectively for editorial headings, adding literary gravitas without overplaying the metaphor.

The emotional response is one of discovery, warmth, and reliability. Users should feel they are browsing a beautifully curated collection, not a generic marketplace.

## Colors

The palette is built around a **warm amber-orange primary** (derived from the logo's #D96B27), replacing default Tailwind indigo with a custom scale redefined in the CSS `@theme` block. This single tonal axis anchors all interactive elements — active navigation indicators, primary buttons, focus rings, badges — giving the product a cohesive brand identity distinct from typical blue-primary storefronts.

- **Primary (Amber-Orange):** #d36d24 is the accent for active states, primary buttons, focus outlines, and badge fills. Its lighter step #d88d5b serves as the dark-mode counterpart for accessible contrast.
- **Tertiary (Warm Sepia):** #8f4818 and its container #ecd0ba are used for secondary call-to-action states and hover states on editorial content — reinforcing the bookshop warmth without competing with the primary.
- **Neutrals:** Tailwind Gray-50 (#f9fafb) is the page canvas; Gray-900 (#111827) provides the dark-mode canvas. Gray-500 (#6b7280) renders secondary metadata (author names, category labels, units). Pure white (#ffffff) forms cards and panel surfaces.
- **Semantic Colors:** Red-600 (#dc2626) is reserved strictly for error messages and out-of-stock indicators. No other semantic color currently appears in the system.
- **Dark Mode:** Every color token has a dark-mode variant controlled via Tailwind's `dark:` variant. Dark surfaces shift to Gray-950 (#030712) for the header/footer and Gray-900 for the page background, while amber primary tones shift one step lighter for contrast.

## Typography

The typographic system pairs two fonts for distinct roles. **Inter** (sans-serif) handles all interface text — labels, navigation, input fields, buttons, metadata, body copy — for its exceptional legibility at small sizes and neutral authority. **Playfair Display** (serif) provides editorial character for large book titles, hero headlines, and featured section headings, lending the platform a literary identity without cluttering the functional UI layer.

A third typeface, **Material Symbols Outlined**, is loaded for icon glyphs alongside Lucide React components, though Lucide is the primary icon library in use.

Typography creates a clear three-tier hierarchy:

- **Headline-lg / Headline-md** (Playfair Display, 36–28px, 700): Used for hero section titles and featured book headings. Applied sparingly — only where editorial weight is intended.
- **Headline-sm** (Inter, 20px, 600): Section headings within the catalog, cart totals, and modal titles.
- **Price Display** (Inter, 24px, 700): Book prices and summary totals — bold enough to anchor a purchase decision without typographic decorators.
- **Body-lg / Body-md** (Inter, 16–14px, 400): Product descriptions, review content, and footer copy.
- **Label-caps** (Inter, 11px, 700, 0.05em tracking): Uppercase category labels, section headers in the footer and sidebar. Provides structural anchoring while occupying minimal vertical space.

## Layout & Spacing

The layout uses a **Fluid Max-Width Container** approach. A `max-w-7xl` container (1280px) with responsive horizontal padding (`px-4 sm:px-6 lg:px-8`) adapts to all screen sizes without a fixed-column grid. Content areas are organized contextually: catalog pages use an implicit sidebar + grid arrangement for filters and book cards; book detail pages use a two-column split (cover image + purchase panel).

- **Header:** Sticky at `z-50`, height `h-16` (64px). Contains: logo + brand name (left), desktop navigation (center), search bar (center-right, hidden on mobile), icon actions (right: theme toggle, search, account, wishlist, cart, hamburger).
- **Mobile Search:** A collapsible bar appended below the header on mobile, triggered by the Search icon. Auto-focused on open.
- **Navigation:** Horizontal links in the header on desktop (`md:flex`), hidden on mobile in favor of a hamburger menu. Active links use a bottom border in the primary amber color.
- **Footer:** Full-width, white (dark: Gray-950) background with a 4-column grid (`md:grid-cols-4`): brand blurb, Shop links, Support links, and a newsletter subscription form. Responsive to single-column on mobile.
- **Rhythm:** An 8px linear scale governs layout spacing (padding, margins, gaps). A 4px scale is used for internal component spacing (icon-label gaps, badge padding).
- **Responsive Behavior:** At mobile breakpoints, the navigation collapses to a hamburger, the search bar drops below the header, and multi-column page layouts reflow to single-column. The header remains sticky at all breakpoints.

## Elevation & Depth

The system uses **Tonal Surface Layers** with thin, low-contrast borders rather than pronounced shadows.

- **Level 0 (Canvas):** Gray-50 (#f9fafb) for the page background in light mode; Gray-900 (#111827) in dark mode. This slightly off-white tone reduces eye strain during extended browsing sessions.
- **Level 1 (Cards & Panels):** Pure white (#ffffff) with a 1px Gray-200 (`#e5e7eb`) border. Book cards, cart panels, and the account section use this treatment. A very soft ambient box-shadow (`0 1px 3px rgba(0,0,0,0.07)`) suggests the card is raised above the canvas.
- **Level 2 (Header & Footer):** White (dark: Gray-950) with a 1px Gray-200 border on the bottom (header) or top (footer). The sticky header uses a slightly stronger drop shadow on scroll to reinforce its overlay position over main content.
- **Level 3 (Modals & Dropdowns):** White background with a 1px Gray-200 border and a medium shadow (`0 10px 15px -3px rgba(0,0,0,0.1)`). Used for the theme picker dropdown, which appears on hover above the header.
- **Interactive States:** Buttons and icon buttons use `hover:bg-gray-100` / `dark:hover:bg-gray-800` to signal interactivity via surface tinting rather than borders. Focus states use a 1px amber ring (`focus:ring-indigo-500` remapped to the custom amber).

## Shapes

The shape language is **Rounded-Warm**: radiused corners throughout, consistent with the approachable editorial aesthetic. Hard edges are avoided to prevent the storefront from feeling sterile or warehouse-like.

- **Search Input:** Full pill shape (`rounded-full`) — the most prominent interactive element on every page, emphasizing discovery and exploration.
- **Buttons:** `rounded-md` (6px) for primary and secondary actions (Subscribe, Add to Cart). `rounded-r-md` + `rounded-l-md` used on split button-input pairs (newsletter form).
- **Cards (Book Tiles):** `rounded-lg` (8px) for book cover containers and product cards. Consistent with the Level 1 elevation treatment.
- **Badges (Cart, Wishlist counts):** Full pill shape (`rounded-full`), small 16×16px — ensures they never obscure the icon they annotate.
- **Modals/Dropdowns:** `rounded-md` (6px), consistent with buttons, to signal they are interactive overlays.

## Components

- **Primary Button:** bg-indigo-600 (amber #d36d24) fill with white text, `rounded-md`. Hover: bg-indigo-700 (#b3581a, 10% darker). Used for Add to Cart, Subscribe, Checkout.
- **Icon Buttons (Header):** Transparent background, Gray-500 (or Gray-400 dark) icon color. Hover: text-indigo-600 (amber) + bg-gray-100 (dark: bg-gray-800), `rounded-full` containment for 40px hit target.
- **Navigation Links:** `text-sm font-medium`, Gray-500 default, amber (indigo-600) + bottom border `border-b-2` on active route. Smooth transition via `transition-colors duration-200`.
- **Search Bar:** `rounded-full`, 1px Gray-300 border turning amber (`focus:border-indigo-500`) on focus with a 1px outer ring in amber. Left-aligned Search icon, right-aligned clear (X) icon when query is present.
- **Book Cards:** White background, 1px Gray-200 border, `rounded-lg`, ambient shadow. Contains: cover image (aspect-ratio constrained), title (Headline-sm), author (body-md, Gray-500), price (Price-display), star rating, and Add to Cart/Wishlist controls.
- **Badge Chips (Cart & Wishlist count):** 16×16px circle, bg-indigo-600 (amber), white text, `text-xs font-bold`, `rounded-full`. Positioned `absolute -top-1 -right-1` on the parent icon.
- **Theme Picker Dropdown:** Appears on hover (`group-hover:opacity-100 group-hover:visible`) above the theme icon. White bg, `rounded-md`, 1px Gray-200 border, shadow-lg. Three items: Light / Dark / System, each with a matching Lucide icon and amber active highlight.
- **Input Fields:** 1px Gray-300 (dark: Gray-700) border, bg-gray-50 (dark: Gray-900), `rounded-md`, placeholder in Gray-500 (dark: Gray-400). `focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500` for amber focus ring.
- **Footer Newsletter Form:** Split control — rounded-l `<input>` for email + rounded-r amber `<button>` for Subscribe. Inline `flex` layout at all breakpoints.
- **Icons:** Lucide React icons, default stroke width. 20px (`h-5 w-5`) for header action icons; 24px (`h-6 w-6`) for navigation icons (User, Heart, ShoppingCart, Menu). Color inherits from parent text color for consistency with hover transitions.
- **Logo:** Custom SVG book mark composed of three amber (#D96B27) paths suggesting open pages. Rendered at 32×32px in the header and footer. Accompanied by the wordmark "BookStore" in `text-xl font-bold` Inter, hidden on small mobile screens (`hidden sm:block`).
