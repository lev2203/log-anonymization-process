import customtkinter
from tkinter import filedialog
from tkinter import messagebox
import threading
import re
import os
import tkinter as tk
from tkinter import ttk

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()
app.geometry("400x240")
app.title("Обезличивание логов")
app.resizable(False, False)

def anonymize_logs():
    input_file = filedialog.askopenfilename(title="Выберите файл с логами")
    if input_file:
        output_file = filedialog.asksaveasfilename(title="Сохранить обезличенные логи как", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if output_file:
            t = threading.Thread(target=process_logs, args=(input_file, output_file))
            t.start()

def process_chunk(chunk):
    #chunk = re.sub(rb'\b(?:\d{1,3}\.){3}\d{1,3}\b', b'xxx.xxx.xxx.xxx', chunk)
    #chunk = re.sub(rb'\b\w+_user\b', b'xxx_user', chunk)
    #chunk = re.sub(rb'\b(?:\d{4}-){3}\d{4}\b', b'xxxx-xxxx-xxxx-xxxx', chunk)
    #chunk = re.sub(rb'\b\d{9}\b', b'*********', chunk)
    chunk = re.sub(rb'\d{16}', b'****************', chunk)
    chunk = re.sub(rb'\xd0\xa3\xd0\x9d\xd0\x9f: \d+', b'\xd0\xa3\xd0\x9d\xd0\x9f: *********', chunk)
    #chunk = re.sub(rb'(?<=\xd0\x9d\xd0\x9e\xd0\x9c\xd0\x95\xd0\xa0 \xd0\xa1\xd0\xa7\xd0\x95\xd0\xa2\xd0\x90 - )\w+',b'xxxxxxxxxxxxxxxxxxxxxxxxxx', chunk)
    chunk = re.sub(rb'(?<=\bBY\d{2}\w{3})\w+(?=\w{4}\b)', b'****************', chunk)
    #chunk = re.sub(rb';\d{13}=\d{20}\?', b';xxxxxxxxxxxxx', chunk)
    #chunk = re.sub(rb'\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}\.\d{3}', b'xxxx:xx:xx xx:xx:xx.xxx', chunk)
    #chunk = re.sub(rb'(?<="PAN":")\d{16}(?=")', b'****************', chunk)
    #chunk = re.sub(rb'\d{16}', b'****************', chunk)
    #chunk = re.sub(rb';\d{7}(.*?)\d{12}\?', b';xxxxxxx\\1xxxxxxxxxxxxx?', chunk)
    chunk = re.sub(rb'\d{12}', b'************', chunk)
    chunk = re.sub(rb'\d{7}', b'*******', chunk)
    chunk = re.sub(rb'\d{8}', b'********', chunk)

    return chunk

def process_logs(input_file, output_file):
    CHUNK_SIZE = 1024 * 1024  # 1 МБ

    total_size = os.path.getsize(input_file)
    processed_size = 0

    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
        while True:
            chunk = infile.read(CHUNK_SIZE)
            if not chunk:
                break
            processed_chunk = process_chunk(chunk)
            outfile.write(processed_chunk)

            processed_size += len(chunk)
            percent = int(processed_size / total_size * 100)
            app.after(100, lambda p=percent: update_progress(p))

    app.after(100, lambda: status_label.configure(text="Обезличивание завершено"))

def update_progress(percent):
    progress_bar["value"] = percent
    progress_label.configure(text=f"Процент обезличивания: {percent}%")

def on_exit():
    if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
        app.destroy()

button = customtkinter.CTkButton(master=app, text="Выбрать и обезличить логи", command=anonymize_logs)
button.place(relx=0.5, rely=0.4, anchor=customtkinter.CENTER)

style = ttk.Style()
style.theme_use("default")  # Используйте стандартную тему Tkinter

style.configure("custom.Horizontal.TProgressbar", troughcolor="gray", background="blue")  # Используйте цвета из палитры Tkinter
progress_bar = ttk.Progressbar(app, mode="determinate", length=200, style="custom.Horizontal.TProgressbar")
progress_bar.place(relx=0.5, rely=0.6, anchor=customtkinter.CENTER)

progress_label = customtkinter.CTkLabel(master=app, text="", anchor="center")
progress_label.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)

status_label = customtkinter.CTkLabel(master=app, text="", anchor="center")
status_label.place(relx=0.5, rely=0.8, anchor=customtkinter.CENTER)

app.protocol("WM_DELETE_WINDOW", on_exit)
app.mainloop()
