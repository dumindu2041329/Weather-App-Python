import tkinter as tk
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import threading

# ─────────────────────── Design Tokens ───────────────────────
BG_DEEP = "#0a0f1e"
BG_GRAD_TOP = "#0d1b2a"
BG_GRAD_BOT = "#1a1a2e"
GLASS_FILL = "#1e2a3a"
GLASS_BORDER = "#2a4a5e"
ACCENT_BLUE = "#4fc3f7"
ACCENT_PURPLE = "#b388ff"
TEXT_PRIMARY = "#e8eaf6"
TEXT_MUTED = "#90a4ae"
TEMP_COLOR = "#80deea"
ERROR_COLOR = "#ef9a9a"
SEARCH_BG = "#162030"
HOVER_BG = "#253545"

MIN_W = 760
MIN_H = 500
INIT_W = 950
INIT_H = 580

# ─────────────────────── Helpers ─────────────────────────────

def draw_gradient(canvas, w, h, color1, color2, steps=120):
    """Draw a vertical gradient on a Canvas."""
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    for i in range(steps):
        t = i / steps
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        color = f"#{r:02x}{g:02x}{b:02x}"
        y0 = int(h * i / steps)
        y1 = int(h * (i + 1) / steps) + 1
        canvas.create_rectangle(0, y0, w, y1, fill=color, outline="")


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=18, **kwargs):
    """Draw a rounded rectangle on a Canvas."""
    r = radius
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def create_glass_card(canvas, x, y, w, h, radius=18):
    """Draw a glassmorphism-style card on the canvas."""
    # Outer glow / border
    create_rounded_rect(canvas, x - 1, y - 1, x + w + 1, y + h + 1,
                        radius=radius + 1, fill="#2a3f55", outline="")
    # Main glass fill
    create_rounded_rect(canvas, x, y, x + w, y + h,
                        radius=radius, fill=GLASS_FILL, outline="")
    # Top highlight line (simulate light refraction)
    canvas.create_line(x + radius, y + 1, x + w - radius, y + 1,
                       fill="#2a3a4a", width=1)


def weather_emoji(condition):
    """Map OpenWeatherMap main condition to a Unicode emoji."""
    mapping = {
        "Clear": "☀️",
        "Clouds": "⛅",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Haze": "🌫️",
        "Smoke": "🌫️",
    }
    return mapping.get(condition, "🌡️")


# ─────────────────────── Main Window ─────────────────────────

root = tk.Tk()
root.title("WeatherGlass")
root.geometry(f"{INIT_W}x{INIT_H}+280+160")
root.minsize(MIN_W, MIN_H)
root.resizable(True, True)
root.configure(bg=BG_DEEP)

# ── Full-window background canvas ──
bg_canvas = tk.Canvas(root, bd=0, highlightthickness=0)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

# ═════════════════ SECTION 1 — Search Bar ═════════════════════

textfield = tk.Entry(root, justify="left", width=24,
                     font=("Helvetica", 16), bg=SEARCH_BG, fg=TEXT_PRIMARY,
                     insertbackground=ACCENT_BLUE, border=0, relief="flat")
textfield.focus()

def _on_focus_in(e):
    if textfield.get() == "Enter city name...":
        textfield.delete(0, tk.END)
        textfield.config(fg=TEXT_PRIMARY)

def _on_focus_out(e):
    if textfield.get() == "":
        textfield.insert(0, "Enter city name...")
        textfield.config(fg=TEXT_MUTED)

textfield.insert(0, "Enter city name...")
textfield.config(fg=TEXT_MUTED)
textfield.bind("<FocusIn>", _on_focus_in)
textfield.bind("<FocusOut>", _on_focus_out)

search_btn = tk.Button(root, text="🔍", font=("Helvetica", 16),
                       bg=GLASS_FILL, fg=ACCENT_BLUE,
                       activebackground=ACCENT_BLUE,
                       activeforeground=BG_DEEP,
                       border=0, cursor="hand2",
                       command=lambda: getWeather())
search_btn.bind("<Enter>", lambda e: search_btn.config(bg=ACCENT_BLUE, fg=BG_DEEP))
search_btn.bind("<Leave>", lambda e: search_btn.config(bg=GLASS_FILL, fg=ACCENT_BLUE))

# ═════════════════ SECTION 2 — Left Panel ═════════════════════

city_label = tk.Label(root, text="—", font=("Helvetica", 26, "bold"),
                      fg=ACCENT_BLUE, bg=GLASS_FILL, anchor="w")
subtitle_label = tk.Label(root, text="Search a city to get started",
                          font=("Helvetica", 11), fg=TEXT_MUTED,
                          bg=GLASS_FILL, anchor="w")
clock_label = tk.Label(root, text="--:-- --", font=("Helvetica", 38, "bold"),
                       fg=TEXT_PRIMARY, bg=GLASS_FILL, anchor="w")
date_label = tk.Label(root, text="", font=("Helvetica", 12),
                      fg=TEXT_MUTED, bg=GLASS_FILL, anchor="w")
error_label = tk.Label(root, text="", font=("Helvetica", 11, "bold"),
                       fg=ERROR_COLOR, bg=GLASS_FILL, anchor="w")

# ═════════════════ SECTION 3 — Right Panel ════════════════════

emoji_label = tk.Label(root, text="🌡️", font=("Helvetica", 44),
                       bg=GLASS_FILL, fg=TEXT_PRIMARY)
temp_label = tk.Label(root, text="--°C", font=("Helvetica", 60, "bold"),
                      fg=TEMP_COLOR, bg=GLASS_FILL, anchor="w")
condition_label = tk.Label(root, text="", font=("Helvetica", 18, "bold"),
                           fg=TEXT_PRIMARY, bg=GLASS_FILL, anchor="w")
feels_label = tk.Label(root, text="", font=("Helvetica", 12),
                       fg=TEXT_MUTED, bg=GLASS_FILL, anchor="w")

# ═════════════════ SECTION 4 — Stats Bar ══════════════════════

STAT_ICONS  = ["💨", "💧", "📋", "🌡️"]
STAT_TITLES = ["WIND", "HUMIDITY", "DESCRIPTION", "PRESSURE"]
STAT_UNITS  = ["m/s", "%", "", "hPa"]

stat_value_labels = []
for _ in range(4):
    val = tk.Label(root, text="--", font=("Helvetica", 20, "bold"),
                   fg=TEXT_PRIMARY, bg=GLASS_FILL, anchor="center")
    stat_value_labels.append(val)


# ─────────────────────── Responsive Layout ───────────────────

_resize_job = None

def layout(w=None, h=None):
    """Redraw the entire UI for the given window dimensions."""
    if w is None:
        w = root.winfo_width()
    if h is None:
        h = root.winfo_height()
    if w < 10 or h < 10:
        return  # Window not yet realized

    PAD     = 30           # Outer padding
    GAP     = 18           # Gap between left/right main panels
    STATS_H = 160          # Fixed stats bar height
    SEARCH_H = 52
    SEARCH_Y = 22
    MAIN_Y  = SEARCH_Y + SEARCH_H + 18
    STATS_Y = h - STATS_H - PAD
    MAIN_H  = max(STATS_Y - MAIN_Y - 12, 80)

    INNER_W = w - PAD * 2
    LEFT_W  = max(int(INNER_W * 0.42), 260)
    RIGHT_X = PAD + LEFT_W + GAP
    RIGHT_W = max(INNER_W - LEFT_W - GAP, 200)

    CARD_PAD = 12
    CARD_W   = max((INNER_W - CARD_PAD * 3) // 4, 120)

    # ── Redraw canvas ──────────────────────────────────────────
    bg_canvas.config(width=w, height=h)
    bg_canvas.delete("all")

    draw_gradient(bg_canvas, w, h, BG_GRAD_TOP, BG_GRAD_BOT)

    # Search bar card
    create_glass_card(bg_canvas, PAD, SEARCH_Y, INNER_W, SEARCH_H, radius=26)
    bg_canvas.create_text(PAD + 30, SEARCH_Y + SEARCH_H // 2,
                          text="WeatherGlass", anchor="w",
                          font=("Helvetica", 14, "bold"), fill=ACCENT_BLUE)

    # Left panel card
    create_glass_card(bg_canvas, PAD, MAIN_Y, LEFT_W, MAIN_H, radius=20)

    # Right panel card
    create_glass_card(bg_canvas, RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H, radius=20)

    # Stats bar cards
    for i in range(4):
        cx = PAD + i * (CARD_W + CARD_PAD)
        create_glass_card(bg_canvas, cx, STATS_Y, CARD_W, STATS_H, radius=16)
        bg_canvas.create_text(cx + CARD_W // 2, STATS_Y + 26,
                              text=STAT_ICONS[i], font=("Helvetica", 20), fill=TEXT_PRIMARY)
        bg_canvas.create_text(cx + CARD_W // 2, STATS_Y + 55,
                              text=STAT_TITLES[i], font=("Helvetica", 9, "bold"), fill=TEXT_MUTED)
        if STAT_UNITS[i]:
            bg_canvas.create_text(cx + CARD_W // 2, STATS_Y + STATS_H - 18,
                                  text=STAT_UNITS[i], font=("Helvetica", 8), fill=TEXT_MUTED)

    # ── Reposition widgets ─────────────────────────────────────

    # Search bar
    entry_x = PAD + 180
    entry_w = INNER_W - 180 - 60
    textfield.place(x=entry_x, y=SEARCH_Y + 9, width=entry_w, height=34)
    search_btn.place(x=w - PAD - 55, y=SEARCH_Y + 7, width=44, height=38)

    # Left panel
    ix = PAD + 20
    iw = LEFT_W - 40
    city_label.place(x=ix, y=MAIN_Y + 20, width=iw)
    subtitle_label.place(x=ix, y=MAIN_Y + 58)
    clock_label.place(x=ix, y=MAIN_Y + 82, width=iw)
    date_label.place(x=ix, y=MAIN_Y + 148)
    error_label.place(x=ix, y=MAIN_Y + MAIN_H - 38)

    # Right panel
    rx = RIGHT_X + 18
    rw = RIGHT_W - 36
    emoji_label.place(x=rx, y=MAIN_Y + 16)
    temp_label.place(x=rx + 68, y=MAIN_Y + 10, width=rw - 68)
    condition_label.place(x=rx, y=MAIN_Y + 110, width=rw)
    feels_label.place(x=rx, y=MAIN_Y + 148, width=rw)

    # Stat value labels
    for i, val in enumerate(stat_value_labels):
        cx = PAD + i * (CARD_W + CARD_PAD)
        val.place(x=cx + 8, y=STATS_Y + 68, width=CARD_W - 16, height=30)


def _on_resize(event):
    """Debounce resize so layout() fires once per resize gesture."""
    global _resize_job
    if event.widget is not root:
        return
    if _resize_job:
        root.after_cancel(_resize_job)
    _resize_job = root.after(30, lambda: layout(event.width, event.height))


root.bind("<Configure>", _on_resize)

# Initial layout
root.update_idletasks()
layout(INIT_W, INIT_H)


# ─────────────────────── Weather Logic ───────────────────────

def getWeather():
    city = textfield.get().strip()
    if not city or city == "Enter city name...":
        error_label.config(text="⚠ Please enter a city name")
        return

    # Clear previous error
    error_label.config(text="")

    # Loading state
    search_btn.config(text="⏳", state="disabled")
    root.update_idletasks()

    # Run fetch in a thread to keep UI responsive
    threading.Thread(target=_fetch_weather, args=(city,), daemon=True).start()


def _fetch_weather(city):
    try:
        # ── Geocode & timezone ──
        geolocator = Nominatim(user_agent="my_unique_weather_app")
        location = geolocator.geocode(city, timeout=10)

        if location is None:
            root.after(0, _show_error, "City not found. Try again.")
            return

        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
        home = pytz.timezone(result)
        local_time = datetime.now(home)
        current_time = local_time.strftime("%I:%M %p")
        current_date = local_time.strftime("%A, %d %B %Y")

        # ── Weather API ──
        api = (
            "https://api.openweathermap.org/data/2.5/weather?q="
            + city
            + "&appid=0939196fa24fdb0a34470cc229abf7a4"
        )

        json_data = requests.get(api, timeout=10).json()

        if json_data.get("cod") != 200:
            root.after(0, _show_error, "City not found. Try again.")
            return

        condition = json_data["weather"][0]["main"]
        description = json_data["weather"][0]["description"].title()
        temp = int(json_data["main"]["temp"] - 273.15)
        feels_like = int(json_data["main"]["feels_like"] - 273.15)
        pressure = json_data["main"]["pressure"]
        humidity = json_data["main"]["humidity"]
        wind = json_data["wind"]["speed"]

        # ── Update UI on main thread ──
        root.after(0, _update_ui, city.title(), current_time, current_date,
                   condition, description, temp, feels_like,
                   wind, humidity, pressure)

    except Exception:
        root.after(0, _show_error, "Something went wrong. Check your connection.")


def _update_ui(city, time_str, date_str, condition, description,
               temp, feels_like, wind, humidity, pressure):
    # Left panel
    city_label.config(text=city)
    subtitle_label.config(text="CURRENT WEATHER")
    clock_label.config(text=time_str)
    date_label.config(text=date_str)
    error_label.config(text="")

    # Right panel
    emoji_label.config(text=weather_emoji(condition))
    temp_label.config(text=f"{temp}°C")
    condition_label.config(text=condition)
    feels_label.config(text=f"Feels like {feels_like}°C  •  {description}")

    # Stats bar
    stat_value_labels[0].config(text=f"{wind}")
    stat_value_labels[1].config(text=f"{humidity}")
    stat_value_labels[2].config(text=description)
    stat_value_labels[3].config(text=f"{pressure}")

    # Reset search button
    search_btn.config(text="🔍", state="normal")


def _show_error(msg):
    error_label.config(text=f"⚠ {msg}")
    search_btn.config(text="🔍", state="normal")


# ─────────────────────── Bindings ────────────────────────────

def _on_return(event):
    getWeather()

textfield.bind("<Return>", _on_return)

# ─────────────────────── Run ─────────────────────────────────

root.mainloop()
