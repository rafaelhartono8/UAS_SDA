import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import json
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Aplikasi Rekomendasi Makanan")

# Ukuran layar
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
window_width = int(screen_width * 0.9)
window_height = int(screen_height * 0.9)
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
app.geometry(f"{window_width}x{window_height}+{x}+{y}")

canvas = tk.Canvas(app, width=window_width, height=window_height, highlightthickness=0)
canvas.place(x=0, y=0)

# Gradasi kuning ke putih
for i in range(window_height):
    r, g, b = 255, int(235 + (255 - 235) * i / window_height), int(59 + (255 - 59) * i / window_height)
    hex_color = f'#{r:02x}{g:02x}{b:02x}'
    canvas.create_line(0, i, window_width, i, fill=hex_color)

main_frame = ctk.CTkFrame(app, fg_color="transparent", width=window_width, height=window_height)
main_frame.place(x=0, y=0)

# SIMPAN DATA REGISTRASI
def simpan_data(nama, username, password):
    user_data = {"nama": nama, "username": username, "password": password}
    filename = "users.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    data.append(user_data)
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# AUTENTIKASI LOGIN
def autentikasi(username, password):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False, None
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True, user["nama"]
    return False, None

# TAMPILAN BERANDA
def tampilkan_beranda(nama):
    for widget in main_frame.winfo_children():
        widget.destroy()

    greeting = ctk.CTkLabel(main_frame, text=f"Hai, {nama}!", font=("Kanit", 18, "bold"), text_color="white")
    greeting.place(relx=0.1, rely=0.05, anchor="w")

    image_path = "makanan.png"
    if os.path.exists(image_path):
        img = Image.open(image_path).resize((300, 150))
        photo = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(main_frame, text="", image=photo, fg_color="transparent")
        img_label.image = photo
        img_label.place(relx=0.5, rely=0.2, anchor="center")

    prompt = ctk.CTkLabel(main_frame, text="Mau makan apa hari ini?", font=("Kanit", 20), text_color="white")
    prompt.place(relx=0.5, rely=0.4, anchor="center")

    def buka_form_preferensi():
        for widget in main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(main_frame, text="Kategori:").place(x=100, y=100)
        kategori_cb = ctk.CTkComboBox(main_frame, values=["Vegan", "Vegetarian", "Semua"])
        kategori_cb.place(x=200, y=100)

        ctk.CTkLabel(main_frame, text="Suhu:").place(x=100, y=150)
        suhu_cb = ctk.CTkComboBox(main_frame, values=["Panas", "Dingin"])
        suhu_cb.place(x=200, y=150)

        ctk.CTkLabel(main_frame, text="Tekstur:").place(x=100, y=200)
        tekstur_cb = ctk.CTkComboBox(main_frame, values=["Kering", "Berkuah"])
        tekstur_cb.place(x=200, y=200)

        ctk.CTkLabel(main_frame, text="Rasa:").place(x=100, y=250)
        rasa_cb = ctk.CTkComboBox(main_frame, values=["Manis", "Asin", "Pedas"])
        rasa_cb.place(x=200, y=250)

        def cari():
            hasil = f"Kategori: {kategori_cb.get()}, Suhu: {suhu_cb.get()}, Tekstur: {tekstur_cb.get()}, Rasa: {rasa_cb.get()}"
            hasil_label = ctk.CTkLabel(main_frame, text=f"Rekomendasi: {hasil}", font=("Kanit", 14))
            hasil_label.place(x=100, y=320)

        cari_btn = ctk.CTkButton(main_frame, text="Cari Makanan", command=cari)
        cari_btn.place(x=100, y=300)

    mood_btn = ctk.CTkButton(main_frame, text="SESUAIKAN MOOD KAMU", fg_color="#C16C6C", hover_color="#B04C4C", command=buka_form_preferensi)
    mood_btn.place(relx=0.5, rely=0.5, anchor="center")

# TAMPILKAN KUIS

def mulai_kuis(username):
    for widget in main_frame.winfo_children():
        widget.destroy()

    pertanyaan_list = [
        {
            "pertanyaan": "Apa jenis makanan yang kamu konsumsi?",
            "opsi": ["Halal", "Non-Halal"]
        },
        {
            "pertanyaan": "Apakah kamu memiliki alergi?",
            "opsi": ["Iya", "Tidak"]
        },
        {
            "pertanyaan": "Apakah kamu seorang vegetarian?",
            "opsi": ["Iya", "Tidak"]
        }
    ]

    jawaban_user = {
        "username": username,
        "jawaban": []
    }

    def tampilkan_pertanyaan(index):
        for widget in main_frame.winfo_children():
            widget.destroy()

        if index < len(pertanyaan_list):
            q_data = pertanyaan_list[index]
            pertanyaan = q_data["pertanyaan"]
            opsi = q_data["opsi"]

            label_q = ctk.CTkLabel(main_frame, text=pertanyaan, font=("Kanit", 20), text_color="#1f1f1f")
            label_q.place(relx=0.5, rely=0.3, anchor="center")

            for i, o in enumerate(opsi):
                btn = ctk.CTkButton(main_frame, text=o, width=200, height=40, fg_color="#FF7070",
                                    hover_color="#FF5050",
                                    command=lambda val=o: proses_jawaban(index, pertanyaan, val))
                btn.place(relx=0.5, rely=0.45 + i * 0.1, anchor="center")
        else:
            try:
                with open("kuis.json", "r") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []

            data.append(jawaban_user)
            with open("kuis.json", "w") as f:
                json.dump(data, f, indent=4)

            tampilkan_beranda(jawaban_user["username"])

    def proses_jawaban(index, pertanyaan, jawaban):
        jawaban_user["jawaban"].append({
            "pertanyaan": pertanyaan,
            "jawaban": jawaban
        })
        tampilkan_pertanyaan(index + 1)

    tampilkan_pertanyaan(0)

def show_login():
    for widget in main_frame.winfo_children():
        widget.destroy()
    label_welcome = ctk.CTkLabel(
        main_frame,
        text="SELAMAT DATANG\nMAU MAKAN APA HARI INI?",
        font=("Kanit", 20, "bold"),
        text_color="#424242"
    )
    label_welcome.place(relx=0.5, rely=0.1, anchor="center")
    image_path = "smile.png"
    img = Image.open(image_path).resize((200, 200))
    photo = ImageTk.PhotoImage(img)
    img_label = ctk.CTkLabel(main_frame, text="", image=photo, fg_color="transparent")
    img_label.image = photo
    img_label.place(relx=0.5, rely=0.4, anchor="center")

    def tampilkan_form_login():
        login_frame = ctk.CTkFrame(main_frame, fg_color="#C16C6C", corner_radius=20)
        login_frame.place(relx=0.5, rely=0.7, anchor="center")

        label_login = ctk.CTkLabel(login_frame, text="LOGIN", font=("Kanit", 14, "bold"), text_color="#1f1f1f")
        label_login.pack(pady=(10, 5))

        entry_username = ctk.CTkEntry(login_frame, placeholder_text="Username", width=250)
        entry_username.pack(pady=5)

        entry_password = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=250)
        entry_password.pack(pady=5)

        error_label = ctk.CTkLabel(login_frame, text="", text_color="red", font=("Kanit", 12))
        error_label.pack()

        def proses_login():
            username = entry_username.get().strip()
            password = entry_password.get().strip()
            berhasil, nama = autentikasi(username, password)
            if berhasil:
                error_label.configure(text="")
                print(f"Login berhasil untuk {nama}")
                mulai_kuis(username)
            else:
                error_label.configure(text="Username atau password salah")

        masuk_btn = ctk.CTkButton(
            login_frame, text="MASUK", fg_color="yellow", text_color="black",
            hover_color="#FFD700", width=200, height=35, font=("Kanit", 14, "bold"),
            command=proses_login
        )
        masuk_btn.pack(pady=(10, 0))

        daftar_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        daftar_frame.pack(pady=(5, 10))

        label_text = ctk.CTkLabel(daftar_frame, text="Belum punya akun?", font=("Kanit", 12), text_color="#424242")
        label_text.pack(side="left")

        label_daftar = ctk.CTkLabel(daftar_frame, text=" Daftar", font=("Kanit", 12, "bold"), text_color="yellow", cursor="hand2")
        label_daftar.pack(side="left")

        label_daftar.bind("<Enter>", lambda e: label_daftar.configure(text_color="red"))
        label_daftar.bind("<Leave>", lambda e: label_daftar.configure(text_color="yellow"))
        label_daftar.bind("<Button-1>", lambda e: show_register())

    login_btn = ctk.CTkButton(
        main_frame,
        text="LOGIN",
        fg_color="#FF7070", hover_color="#FF5050",
        text_color="#424242", corner_radius=10,
        width=200, height=40,
        command=tampilkan_form_login
    )
    login_btn.place(relx=0.5, rely=0.75, anchor="center")

    frame_daftar = ctk.CTkFrame(master=main_frame, fg_color="transparent")
    frame_daftar.place(relx=0.5, rely=0.83, anchor="center")

    label_text = ctk.CTkLabel(master=frame_daftar, text="Belum punya akun?", text_color="#424242", font=("Kanit", 20))
    label_text.pack(side="left")

    label_daftar = ctk.CTkLabel(master=frame_daftar, text=" Daftar", text_color="#0044cc", font=("Kanit", 20, "bold"), cursor="hand2")
    label_daftar.pack(side="left")

    label_daftar.bind("<Enter>", lambda e: label_daftar.configure(text_color="red"))
    label_daftar.bind("<Leave>", lambda e: label_daftar.configure(text_color="#0044cc"))
    label_daftar.bind("<Button-1>", lambda e: show_register())

# HALAMAN REGISTER
def show_register():
    for widget in main_frame.winfo_children():
        widget.destroy()
    back_btn = ctk.CTkLabel(main_frame, text="← REGISTRASI", font=("Kanit", 18, "bold"), text_color="#424242", cursor="hand2")
    back_btn.place(x=20, y=20)
    back_btn.bind("<Button-1>", lambda e: show_login())

    title = ctk.CTkLabel(main_frame, text="Selamat Datang!", font=("Kanit", 18, "bold"), text_color="#1f1f1f")
    title.place(relx=0.1, rely=0.15, anchor="w")

    desc = ctk.CTkLabel(main_frame, text="Registrasi akun kamu untuk memulai mencari rekomendasi makanan.", font=("Kanit", 14), text_color="#1f1f1f")
    desc.place(relx=0.1, rely=0.2, anchor="w")

    entry_nama = ctk.CTkEntry(main_frame, placeholder_text="Nama", width=300)
    entry_nama.place(relx=0.1, rely=0.27, anchor="w")

    entry_username = ctk.CTkEntry(main_frame, placeholder_text="Username", width=300)
    entry_username.place(relx=0.1, rely=0.34, anchor="w")

    entry_password = ctk.CTkEntry(main_frame, placeholder_text="Password", show="*", width=300)
    entry_password.place(relx=0.1, rely=0.41, anchor="w")

    def on_submit():
        nama = entry_nama.get().strip()
        username = entry_username.get().strip()
        password = entry_password.get().strip()
        if not nama or not username or not password:
            print("Semua field harus diisi.")
            return
        simpan_data(nama, username, password)
        show_login()

    lanjut_btn = ctk.CTkButton(
        main_frame,
        text="SELANJUTNYA",
        fg_color="#C16C6C", hover_color="#B04C4C",
        text_color="white", corner_radius=10,
        width=200, height=40,
        command=on_submit
    )
    lanjut_btn.place(relx=0.1, rely=0.55, anchor="w")

# Tampilkan halaman awal
show_login()
app.mainloop()
