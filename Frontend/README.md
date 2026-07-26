# ResolveAI — Banking AI Customer Service Frontend

A clean, professional fintech-style React frontend demoing an AI banking support flow: a chat
resolution, a receipt-style confirmation, a full audit trail, and a human-escalation handoff.

## Tech stack

- React 18
- React Router v6
- Tailwind CSS
- React Icons (`react-icons/hi2`)
- Vite

## Getting started

```bash
npm install
npm run dev
```

Then open the URL Vite prints (usually `http://localhost:5173`).

To build for production:

```bash
npm run build
npm run preview
```

## Project structure

```
resolveai/
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
├── public/
│   └── favicon.svg
└── src/
    ├── main.jsx              # App entry, wraps App in ThemeProvider + BrowserRouter
    ├── App.jsx                # Route table + gradient backdrop + page transition wrapper
    ├── index.css               # Tailwind directives + shared glass/pill component classes
    ├── context/
    │   └── ThemeContext.jsx    # Day/night theme state, persisted to localStorage
    ├── components/
    │   ├── Header.jsx          # Top nav — logo, step progress rail, day/night toggle
    │   ├── GradientBackdrop.jsx# Blurred colour blobs behind the app (light + dark sets)
    │   ├── PageContainer.jsx   # Shared max-width/padding wrapper
    │   ├── ChatBubble.jsx      # Customer / AI message bubble
    │   ├── TypingIndicator.jsx # Animated "AI is typing" dots (available for reuse)
    │   ├── StatusBadge.jsx     # Pill badge (success / pending / progress)
    │   ├── InfoRow.jsx         # Label/value row used on receipt-style pages
    │   ├── TimelineStep.jsx    # Single step in the audit trail timeline
    │   └── SuccessSeal.jsx     # Animated checkmark seal (signature element)
    └── pages/
        ├── ChatPage.jsx         # "/"             Chat interface
        ├── ConfirmationPage.jsx # "/confirmation"  Transaction receipt
        ├── AuditPage.jsx        # "/audit"         Vertical audit timeline
        └── EscalationPage.jsx   # "/escalation"    Human handoff screen
```

## Design system

The UI uses a soft-gradient glassmorphism style: translucent, blurred "glass" cards float over
blurred colour blobs in the background, with pill-shaped buttons and gentle shadows — inspired by
modern wellness/lifestyle app UIs, adapted with a blue-led palette to stay trustworthy for banking.

| Token | Light | Dark | Use |
|---|---|---|---|
| `primary-600` | `#2563EB` | `#2563EB` | Primary actions, links, brand mark |
| `accent-500` | `#8B5CF6` | `#8B5CF6` | Gradient partner for primary (buttons, avatars, icons) |
| `success-600` | `#16A34A` | `#16A34A` | Success states, reversed-amount emphasis |
| `ink-*` | slate scale | — | Light-mode text/borders/backgrounds |
| `night-*` | — | deep navy/indigo scale | Dark-mode text/borders/backgrounds |

All colors, shadows, and animation keyframes are defined in `tailwind.config.js` — edit them
there to re-theme the whole app.

### Day / night mode

- Toggle button (sun/moon icon) lives in the header, top right.
- Theme state is managed by `src/context/ThemeContext.jsx`, persisted to `localStorage`
  (`resolveai-theme`), and falls back to the OS-level `prefers-color-scheme` on first visit.
- Tailwind's `class` dark mode strategy is used — dark styles are written as `dark:` variants
  throughout components, and the `dark` class is toggled on `<html>`.
- A tiny inline script in `index.html` applies the saved theme before React loads, so there's no
  flash of the wrong theme on refresh.

### Background blobs

`src/components/GradientBackdrop.jsx` renders four blurred, absolutely-positioned colour blobs
(primary blue, violet, blush pink, and success green) behind the whole app, with separate colour
sets for light and dark mode that cross-fade on toggle. Edit that file to change blob colours,
size, or position.

## Notes

- All data is static/mocked (no backend calls). Swap the hard-coded values in `pages/*.jsx`
  and `components/*.jsx` for real API data when wiring up a backend.
- "Download Confirmation" on the chat page generates a small `.txt` receipt client-side as a
  stand-in for a real PDF/receipt download.
- Fully responsive: the step progress rail collapses on mobile, and every page uses a
  constrained `max-w-*` column that reflows on small screens.
- Reduced-motion is respected (`prefers-reduced-motion`) — animations are disabled automatically
  for users who request it.
