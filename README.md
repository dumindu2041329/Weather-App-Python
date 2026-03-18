# Weather App - Python GUI 🌤️🌡️

A desktop weather application built using Python 🐍 and the Tkinter library 🖼️. This app fetches real-time weather data 📡 from an API and displays it with a clean, user-friendly interface ✨.

---

## 🚀 Features
* **Real-time Weather ☁️:** Get current temperature 🌡️, wind speed 💨, humidity 💧, and pressure 📉.
* **City Search 🔍:** Search for weather details of any city worldwide 🌍.
* **Modern UI 🎨:** Designed with custom icons and a clean, glassmorphism layout 🪟.
* **Precise Information ⏱️:** Displays "Feels Like" conditions 🥶🥵 and current local time 🕰️.
* **Standalone Installer 📦:** Comes with a ready-to-use `.exe` installer so you don't even need Python! 💽

## 🛠️ Tech Stack & Libraries
This project is built using:
* **Python 🐍**: Core logic and backend.
* **Tkinter 🪟**: For creating the Graphical User Interface (GUI).
* **Requests 🌐**: To handle API calls and fetch live data.
* **Geopy 📍 & Timezonefinder 🕒**: To get exact coordinates and local time.
* **PyInstaller 🛠️ & Inno Setup 🧙‍♂️**: Used to bundle the app into a Windows installer.

## 📊 How it Works
The app uses the **OpenWeatherMap API 🌤️** to retrieve live weather data. When a user enters a city 🏙️, the app sends a request, parses the JSON response 📄, and updates the labels on the screen in real-time ⚡.

## ⚙️ How to Setup and Run
1. **Clone the repository 📥:**
   ```bash
   git clone https://github.com/dumindu2041329/Weather-App-Python.git
   ```
2. **Run without installing (Windows) 🪟:**
   Download and run the pre-built installer located at:
   `installer/WeatherGlass_Setup.exe` 🚀

3. **Or run from source 🧑‍💻:**
   ```bash
   pip install -r requirements.txt
   python Weather.py
   ```