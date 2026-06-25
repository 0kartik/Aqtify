# Aqtify frontend

React 19 + Vite. Standard project, standard tooling — no CDN hacks.

```
src/
├── main.jsx              entry point
├── App.jsx                header, API key bar, tabs, panel routing
├── index.css               design tokens (CSS variables) + base styles
├── styles.js               shared inline-style constants
├── api/
│   └── client.js          all fetch calls to the Aqtify backend, in one place
├── components/            generic, reusable UI pieces
│   ├── Icon.jsx
│   ├── Button.jsx
│   ├── Field.jsx
│   ├── Dropzone.jsx
│   ├── Pipeline.jsx
│   ├── ErrorBox.jsx
│   ├── DataRow.jsx
│   ├── VerdictBanner.jsx
│   ├── CheckGrid.jsx
│   ├── MethodBars.jsx
│   ├── Panel.jsx
│   └── KeyBar.jsx
└── panels/                 the three feature screens
    ├── RegisterPanel.jsx
    ├── VerifyPanel.jsx
    └── DetectPanel.jsx
```

## Setup

```bash
npm install
npm run dev       # http://localhost:5173, hot reload
npm run build     # production build -> dist/
npm run preview   # serve the production build locally
npm run lint      # oxlint
```

By default the app talks to `http://127.0.0.1:8000`. To point it elsewhere,
copy `.env.example` to `.env` and set `VITE_AQTIFY_API_BASE`.

## Design

Flat, neutral palette — off-white surfaces, near-black for primary actions,
no blue, no violet, no gradients anywhere. Green/amber/red are reserved
strictly for verification status (authentic / suspicious / tampered), never
used decoratively. All tokens live in `src/index.css` as CSS variables if
you want to retheme.
