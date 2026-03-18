# PRD: Weather App — Glassmorphism Dark Theme Redesign

## Overview

The current Weather App UI is built with flat, image-dependent widgets (PNG files for search bar, logo, and bottom stats box) and a basic light/blue color scheme. This PRD defines the redesign of the frontend into a **premium glassmorphism dark-theme** using pure Tkinter — no external image files.

The backend logic (API calls, geocoding, timezone resolution) remains **unchanged**.

---

## Goals

- Replace all PNG image assets with pure Tkinter-drawn widgets
- Apply a glassmorphism dark theme throughout the UI
- Improve visual hierarchy, typography, and layout spacing
- Keep the app fully self-contained (no image file dependencies)

---

## Design System

### Color Palette

| Token | Value | Usage |
|---|---|---|
| `bg-deep` | `#0a0f1e` | Root window background (deep navy) |
| `bg-gradient-start` | `#0d1b2a` | Gradient top |
| `bg-gradient-end` | `#1a1a2e` | Gradient bottom |
| `glass-fill` | `#ffffff14` | Glass panel background (white 8% opacity) |
| `glass-border` | `#ffffff22` | Glass panel border (white 13% opacity) |
| `accent-blue` | `#4fc3f7` | Primary accent (sky blue) |
| `accent-purple` | `#b388ff` | Secondary accent (lavender) |
| `text-primary` | `#e8eaf6` | Main readable text |
| `text-muted` | `#90a4ae` | Subtitles, labels |
| `temp-color` | `#80deea` | Temperature display |
| `error-color` | `#ef9a9a` | Error messages |

### Typography

- **Titles / Temp**: `"Helvetica"`, bold, large (40–70pt)
- **Labels**: `"Helvetica"`, bold, 11–13pt, letter-spaced uppercase
- **Values**: `"Helvetica"`, bold, 16–20pt
- **Clock/City**: `"Helvetica"`, 14–18pt, muted color

### Window

- **Size**: `950x580` (wider to accommodate new layout)
- **Resizable**: `False`
- **Background**: Deep navy (`#0a0f1e`) simulated with Canvas gradient

---

## Layout Specification

### Section 1 — Header / Search Bar (top strip)

Replace `search.png` and `search_icon.png` with:
- A **rounded dark glass Frame** spanning the top of the window
- An **Entry widget** with no border, dark fill, white text, placeholder hint "Enter city name..."
- A **styled Button** labelled `🔍` (Unicode search emoji) with accent color hover effect
- App name label **"WeatherGlass"** on the left of the bar with gradient-effect text

### Section 2 — Left Panel (current time & city)

Replace bare Labels placed at fixed coords with a **glass card Frame**:
- City name (large, bold, accent blue)
- "CURRENT WEATHER" subtitle (muted)
- Local time (large clock, white)
- Day + date line (muted)

### Section 3 — Right Panel (temperature display)

Replace bare Label at fixed position with a **glass card Frame**:
- Giant temperature number with `°C` suffix (teal accent)
- Condition text (e.g. "Cloudy") prominent
- Feels-like row (muted, smaller)
- Unicode weather emoji determined by condition string (e.g. ☀️ 🌧️ ❄️ 🌩️)

### Section 4 — Stats Bar (bottom)

Replace `box.png` bottom image with a **glass info bar** containing 4 stat cards, each with:
- Unicode icon (💨 Wind, 💧 Humidity, 📋 Description, 🌡️ Pressure)
- Label (uppercase, muted, small)
- Value (bold, white, larger)
- Glass divider lines between cards

---

## Glassmorphism Implementation Strategy (Tkinter)

Since Tkinter does not support `rgba` transparency or CSS `backdrop-filter: blur`, the glassmorphism effect will be **simulated** as follows:

| Effect | Technique |
|---|---|
| Dark background gradient | `tk.Canvas` with two-tone vertical fill using `create_rectangle` strips |
| Glass panels | `tk.Frame` with background color `#1e2a3a` (semi-translucent dark blue) + `highlightbackground=#4fc3f7` 1px border |
| Rounded corners | `tk.Canvas` with `create_rounded_rect()` helper using `arc` + `line` primitives |
| Glow / shimmer border | `highlightthickness=1`, `highlightcolor` set to accent |
| Hover effects | `<Enter>` / `<Leave>` bindings to change button bg/fg |
| Subtle inner shadow | Layered canvas rectangles with slightly offset colors |

---

## File Changes

| File | Action | Notes |
|---|---|---|
| `Weather.py` | **Modify** | Full UI rewrite; backend logic preserved |
| `PRD.md` | **New** | This document |
| `search.png`, `search_icon.png`, `logo.png`, `box.png` | **Keep, unused** | Not deleted; just not loaded or referenced |

---

## Detailed Component Specs

### `create_glass_card(parent, x, y, w, h, radius=18)`
A reusable canvas-based helper that draws a rounded-rectangle "glass" panel at the specified position.

### `create_gradient_bg(canvas, w, h)`
Draws a vertical gradient from `#0d1b2a` → `#1a1a2e` across the canvas serving as root background.

### `SearchBar`
- Width: spans full window width minus 40px padding each side
- Entry width: ~30 chars
- Button: Unicode `🔍`, flat cursor `hand2`, hover turns accent blue
- Bind `<Return>` key to trigger `getWeather()`

### `WeatherEmoji(condition)`
A function mapping OpenWeatherMap condition strings to Unicode emoji:
```
Clear       → ☀️
Clouds      → ⛅
Rain        → 🌧️
Drizzle     → 🌦️
Thunderstorm→ ⛈️
Snow        → ❄️
Mist/Fog    → 🌫️
default     → 🌡️
```

### `StatsBar`
Four equal-width glass cards packed horizontally at the bottom.
Each card: icon label (top), value label (middle, large), unit label (bottom, muted).

---

## Behaviour Requirements

| Requirement | Detail |
|---|---|
| Search trigger | Button click OR `<Return>` key press |
| Error display | Inline label inside main area (red text), not a popup `messagebox` |
| Loading state | Button text changes to `⏳` while API is fetching |
| Default state | Stats show `--` placeholders until a search is made |
| API error | Show `"City not found"` in the error label |

---

## Out of Scope

- Animated backgrounds or particle effects
- Multi-day forecast
- Unit switching (°C ↔ °F toggle) — future feature
- System tray integration

---

## Verification Plan

### Manual Testing

1. **Run the app**:
   ```
   cd "c:\Users\Dumindu\Documents\Python Projects\Weather-App-Python"
   python Weather.py
   ```
2. **Visual check**: Confirm window opens with dark navy background and glass-style panels (no images loaded).
3. **Search test**: Type `London` and press Enter or click 🔍 — verify temperature, condition, time, wind, humidity, description, and pressure all populate.
4. **Invalid city test**: Type `xyzxyzxyz` and confirm inline error label appears (not a popup).
5. **Keyboard test**: Focus the search field, type a city, press `Enter` — verify it triggers the weather fetch.
6. **Hover test**: Hover over the search button — verify colour changes to accent blue.
7. **No image dependency**: Rename/remove `search.png` temporarily and confirm app still launches without error.
