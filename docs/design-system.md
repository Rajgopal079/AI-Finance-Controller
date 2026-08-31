# FINCTRL AI — Enterprise Design System & UI Specification

## 1. Design Philosophy
FINCTRL AI's interface is built as a high-density, mission-critical finance operations control system. It draws visual hierarchy and design discipline from modern financial interfaces (Stripe, Ramp, Linear) while prioritizing calm data presentation, high legibility, and rapid decision-making.

---

## 2. Color Palette & Dark Theme Tokens

```css
/* Color System Tokens */
--bg-app: #0B0F19;           /* Primary Obsidian Dark Background */
--bg-surface: #111827;       /* Card / Panel Background */
--bg-surface-hover: #1F2937; /* Interactive Hover State */
--bg-card-muted: #1E293B;    /* Muted Container */

--border-subtle: #1E293B;    /* Subtle Hairline Dividers */
--border-strong: #334155;    /* Focused Element Borders */

--text-primary: #F8FAFC;     /* Headings, KPI values, Primary text */
--text-secondary: #94A3B8;   /* Labels, Metadata, Subtitles */
--text-muted: #64748B;       /* Captions, Timestamp, Table headers */

/* Semantic Status Colors */
--status-success: #10B981;   /* Matched, Valid, Approved (Green) */
--status-warning: #F59E0B;   /* Partial Match, High Risk, Medium Severity (Amber) */
--status-error: #EF4444;     /* Discrepancy, Critical Severity, Rejected (Red) */
--status-info: #3B82F6;      /* Open, Information, Escalated (Blue) */
--status-purple: #8B5CF6;    /* AI Agent Execution Accent (Indigo/Violet) */
```

---

## 3. Typography & Numerical Hierarchy
- **Font Stack**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`.
- **Financial Monospace**: `JetBrains Mono`, `Fira Code`, `ui-monospace`, `monospace` for Currency Amounts (e.g. `₹850,000.00`), Hashes (`SHA-256`), and Record IDs (`INV-1002`).
- **Hierarchy Rules**:
  - `h1`: 24px / 1.2 line-height, Bold (`#F8FAFC`)
  - `h2`: 18px / 1.3 line-height, SemiBold (`#F8FAFC`)
  - `h3` / Section Header: 14px, Medium, Tracking Wide, Uppercase (`#94A3B8`)
  - Body: 14px / 1.5 line-height (`#CBD5E1`)
  - Captions / Metadata: 12px (`#64748B`)

---

## 4. Layout Architecture & Component Rules
- **Grid Layout**: 12-column responsive layout with fixed sidebar (240px width) on desktop.
- **Card Containers**: 1px subtle border (`#334155`), rounded corners (8px radius), flat obsidian background (`#111827`).
- **Data Tables**: High density rows (40px height), sticky headers, explicit column alignments (Left for IDs/text, Right for Currency/Amounts, Center for Badges/Scores).
- **Status Badges**: Semi-transparent background with solid border and uppercase bold text (e.g. `bg-emerald-500/10 text-emerald-400 border border-emerald-500/20`).

---

## 5. Animation Guidelines (Framer Motion)
- **Restrained Motion**: Motion is strictly used for structural clarity, drawer slide-ins, modal overlays, and status transitions.
- **Page Transition**: `initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.15 }}`.
- **Drawer / Slide-over**: `initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }} transition={{ type: "spring", damping: 25, stiffness: 250 }}`.
- **Reduced Motion Support**: Fully respects `prefers-reduced-motion: reduce`.
