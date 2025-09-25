#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 19:19:10 2025

@author: seretur
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
import os
import time
from edge_tts import Communicate

# Inicializar pygame de forma segura
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()

TEMP_AUDIO_FILE = "temp_output.mp3"

# Voces permitidas
VOICES = {
    "Argentina (Femenina)": "es-AR-ElenaNeural",
    "Argentina (Masculina)": "es-AR-TomasNeural",
    "Bolivia (femenina)": "es-BO-SofiaNeural",
    "Uruguay (Femenina)": "es-UY-ValentinaNeural",
    "EE.UU. (Femenina)": "es-US-PalomaNeural",
    "EE.UU. (Masculina)": "es-US-AlonsoNeural",
}

# Estilos predefinidos (solo como referencia; los sliders tienen prioridad si se usan)
STYLES = {
    "Normal": ("+0%", "+0Hz"),
    "Alegre": ("+15%", "+3Hz"),
    "Seria": ("-10%", "-2Hz"),
    "Sorprendida": ("+20%", "+5Hz"),
    "Susurro": ("-20%", "-4Hz"),
    "Enojada": ("+5%", "-3Hz"),
    "Nerviosa": ("+25%", "+1Hz"),
}

def format_rate(value):
    """Convierte valor numérico a formato de rate para edge-tts."""
    return f"{int(value):+d}%"

def format_pitch(value):
    """Convierte valor numérico a formato de pitch para edge-tts."""
    return f"{int(value):+d}Hz"

async def generate_audio(text, voice_id, rate_str, pitch_str, output_file):
    """Genera el archivo de audio (sin reproducir)."""
    communicate = Communicate(text, voice_id, rate=rate_str, pitch=pitch_str)
    await communicate.save(output_file)

def run_async(coro):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def play_audio():
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Advertencia", "Ingresa un texto.")
        return

    selected_voice = voice_var.get()
    if selected_voice not in VOICES:
        messagebox.showwarning("Advertencia", "Selecciona una voz válida.")
        return

    # Obtener valores de sliders
    rate_val = rate_slider.get()
    pitch_val = pitch_slider.get()

    # Si ambos sliders están en 0, usar el estilo seleccionado
    if rate_val == 0 and pitch_val == 0:
        style = style_var.get()
        rate_str, pitch_str = STYLES.get(style, ("+0%", "+0Hz"))
    else:
        rate_str = format_rate(rate_val)
        pitch_str = format_pitch(pitch_val)

    voice_id = VOICES[selected_voice]

    def play_task():
        try:
            asyncio.run(generate_audio(text, voice_id, rate_str, pitch_str, TEMP_AUDIO_FILE))
            time.sleep(0.2)
            if os.path.exists(TEMP_AUDIO_FILE):
                pygame.mixer.music.load(TEMP_AUDIO_FILE)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                messagebox.showerror("Error", "No se generó el archivo temporal.")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al reproducir:\n{str(e)}")

    threading.Thread(target=play_task, daemon=True).start()

def save_audio():
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Advertencia", "Ingresa un texto.")
        return

    selected_voice = voice_var.get()
    if selected_voice not in VOICES:
        messagebox.showwarning("Advertencia", "Selecciona una voz válida.")
        return

    # Obtener valores
    rate_val = rate_slider.get()
    pitch_val = pitch_slider.get()

    if rate_val == 0 and pitch_val == 0:
        style = style_var.get()
        rate_str, pitch_str = STYLES.get(style, ("+0%", "+0Hz"))
    else:
        rate_str = format_rate(rate_val)
        pitch_str = format_pitch(pitch_val)

    voice_id = VOICES[selected_voice]

    # Diálogo para guardar archivo
    filepath = filedialog.asksaveasfilename(
        title="Guardar audio como",
        defaultextension=".mp3",
        filetypes=[("Archivos MP3", "*.mp3")],
        initialfile="voz_latina.mp3"
    )
    if not filepath:
        return  # Cancelado

    def save_task():
        try:
            asyncio.run(generate_audio(text, voice_id, rate_str, pitch_str, filepath))
            messagebox.showinfo("Éxito", f"Audio guardado en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el audio:\n{str(e)}")

    threading.Thread(target=save_task, daemon=True).start()

def on_clear():
    text_box.delete("1.0", tk.END)

def on_closing():
    if os.path.exists(TEMP_AUDIO_FILE):
        try:
            pygame.mixer.music.stop()
            time.sleep(0.1)
            os.remove(TEMP_AUDIO_FILE)
        except:
            pass
    root.destroy()

# === GUI ===
root = tk.Tk()
root.title("Lector de Texto Avanzado - Voces Latinos")
root.geometry("650x650")
root.resizable(True, True)
root.protocol("WM_DELETE_WINDOW", on_closing)

# Título
tk.Label(root, text="Lector de Texto con Voces Latinos", font=("Arial", 16, "bold")).pack(pady=10)

# Texto
tk.Label(root, text="Texto a leer:", font=("Arial", 10)).pack(anchor="w", padx=20)
text_box = tk.Text(root, height=5, width=75, font=("Arial", 11))
text_box.pack(padx=20, pady=5)
text_box.insert("1.0", "muy buenas tardes")

# Voz
tk.Label(root, text="Voz:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=(10, 0))
voice_var = tk.StringVar(value="Argentina (Femenina)")
ttk.Combobox(root, textvariable=voice_var, values=list(VOICES.keys()), state="readonly", width=35).pack(padx=20, pady=5)

# Estilo
tk.Label(root, text="Estilo (solo si sliders en 0):", font=("Arial", 10)).pack(anchor="w", padx=20, pady=(10, 0))
style_var = tk.StringVar(value="Normal")
ttk.Combobox(root, textvariable=style_var, values=list(STYLES.keys()), state="readonly", width=35).pack(padx=20, pady=5)

# Sliders
frame_sliders = tk.Frame(root)
frame_sliders.pack(pady=15)

# Velocidad (rate)
tk.Label(frame_sliders, text="Velocidad (%):", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10)
rate_slider = tk.Scale(frame_sliders, from_=-50, to=100, orient=tk.HORIZONTAL, length=300, resolution=5)
rate_slider.set(0)
rate_slider.grid(row=0, column=1, padx=10)

# Tono (pitch)
tk.Label(frame_sliders, text="Tono (Hz):", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10)
pitch_slider = tk.Scale(frame_sliders, from_=-10, to=10, orient=tk.HORIZONTAL, length=300, resolution=1)
pitch_slider.set(0)
pitch_slider.grid(row=1, column=1, padx=10)

# Botones
btn_frame = tk.Frame(root)
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Reproducir", command=play_audio, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=12).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Guardar como MP3", command=save_audio, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Limpiar", command=on_clear, bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=12).pack(side=tk.LEFT, padx=10)

# Nota
tk.Label(
    root,
    text="Nota: Si los sliders están en 0, se usa el estilo seleccionado. De lo contrario, se usan los valores manuales.",
    font=("Arial", 8),
    fg="gray",
    wraplength=600,
    justify="center"
).pack(side=tk.BOTTOM, pady=10)

root.mainloop()