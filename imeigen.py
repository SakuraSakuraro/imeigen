import random
import tkinter as tk
import os
import sys
from PIL import Image, ImageTk
import tkinter.constants as tkconstants
from tkinter import ttk
import configparser
import pygame

# Getting language strings from config.ini
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8-sig')
lang = config.get('Settings', 'Lang')

imei_num = config.get(lang, 'IMEINUM')
gen_num = config.get(lang, 'GENNUM')
clipbrd = config.get(lang, 'CLIPBRD')
gen_imei = config.get(lang, 'GENIMEI')
error1_msg = config.get(lang, 'ERROR1')
error2_msg = config.get(lang, 'ERROR2')
success_msg = config.get(lang, 'SUCCGEN')
prog_name = config.get(lang, 'NAMEPROG')

def play_music():
    sound_enabled = config.getboolean('Settings', 'Sound')
    if sound_enabled:
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "music.mp3"))
        pygame.mixer.music.play(-1)

# Start background music
play_music()

# Getting the list of phones from phone_models.txt and their corresponding IMEI
with open('./phone_models.txt') as f:
    phone_models_imei = dict(line.strip().split(':') for line in f.readlines())

root = tk.Tk()
root.title(string=prog_name)

canvas = tk.Canvas(root, width=353, height=196, highlightthickness=0)
canvas.pack()

# Setting a background image
bg_image = ImageTk.PhotoImage(Image.open(sys._MEIPASS + "\\background.png"))
canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)

# File patch to icon
icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon.ico'))

# Setting a icon
root.iconbitmap(icon_path)

# Disabling window resizing
root.resizable(tkconstants.FALSE, tkconstants.FALSE)

# Disabling expand to full screen
root.attributes('-fullscreen', False)

# Calculation of IMEI check digit by "Luhn" algorithm
def calculate_imei(imei):
    odd_sum = 0
    even_sum = 0
    for i, digit in enumerate(imei):
        if i % 2 == 0: # i is even
            even_sum += int(digit)
        else: # i is odd
            even_digit = int(digit) * 2
            if even_digit > 9:
                even_digit = even_digit // 10 + even_digit % 10
            even_sum += even_digit
    total = odd_sum + even_sum
    if total % 10 == 0:
        check_digit = 0
    else:
        check_digit = 10 - total % 10
    return imei + str(check_digit)

# Generate the IMEI
def generate_imei():
    imei_prefix = imei_prefix_entry.get()
    amount_to_generate = amount_to_generate_entry.get()
    if not amount_to_generate.isdigit() or len(amount_to_generate) > 3:
        generate_button.config(text=error2_msg, state=tk.DISABLED)
        root.after(2000, lambda: generate_button.config(text=gen_imei, state=tk.NORMAL))
        return
    amount_to_generate = int(amount_to_generate)
    if len(imei_prefix) != 8 or not imei_prefix.isdigit():
        generate_button.config(text=error1_msg, state=tk.DISABLED)
        root.after(2000, lambda: generate_button.config(text=gen_imei, state=tk.NORMAL))
        return
    imei_list = []
    for i in range(amount_to_generate):
        imei = imei_prefix + str(random.randint(0, 999999)).zfill(6)
        imei_with_check_digit = calculate_imei(imei)
        imei_list.append(imei_with_check_digit)
    with open('imei.txt', 'a') as f:
        f.write('\n'.join(imei_list) + '\n')
    generate_button.config(text=success_msg, state=tk.DISABLED)
    root.after(2000, lambda: generate_button.config(text=gen_imei, state=tk.NORMAL))

# Paste from clipboard
def paste_imei_prefix():
    imei_prefix_entry.delete(0, tk.END)
    imei_prefix_entry.insert(0, root.clipboard_get())
    
# Getting user selected IMEI from phone_models.txt
def set_imei_prefix(*args):
    selected_phone_model = phone_model_var.get()
    selected_imei = phone_models_imei.get(selected_phone_model, "")
    imei_prefix_entry.delete(0, tk.END)
    imei_prefix_entry.insert(0, selected_imei)

def paste_amount_to_generate():
    amount_to_generate_entry.delete(0, tk.END)
    amount_to_generate_entry.insert(0, root.clipboard_get())

# # Add a drop-down list with phone models
phone_models = list(phone_models_imei.keys())
phone_model_var = tk.StringVar(root)
phone_model_var.set(phone_models[0])
phone_model_dropdown = tk.OptionMenu(root, phone_model_var, *phone_models, command=set_imei_prefix)
phone_model_dropdown.config(width=23)
phone_model_dropdown.pack(pady=8)
phone_model_var.set("")
canvas.create_window(100, 26, anchor=tk.CENTER, window=phone_model_dropdown)

imei_prefix_label = canvas.create_text(97, 52, text=imei_num, font="calibri 11 bold")

imei_prefix_entry = tk.Entry(root)
canvas.create_window(97, 72, anchor=tk.CENTER, width=148, height=20, window=imei_prefix_entry)
imei_prefix_button = tk.Button(root, text=clipbrd, command=paste_imei_prefix)
canvas.create_window(99, 99, anchor=tk.CENTER, width=177, height=25, window=imei_prefix_button)

amount_to_generate_label = canvas.create_text(97, 125, text=gen_num, font="calibri 11 bold")

amount_to_generate_entry = tk.Entry(root)
canvas.create_window(97, 146, anchor=tk.CENTER, width=148, height=20, window=amount_to_generate_entry)

generate_button = tk.Button(root, text=gen_imei, command=generate_imei)
canvas.create_window(97, 173, anchor=tk.CENTER, width=170, height=24, window=generate_button)

#Start program
root.mainloop()