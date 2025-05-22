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

# PERTANYAAN KUIS
questions = [
    {"pertanyaan": "Apa jenis makanan yang kamu konsumsi?", "jawaban": ["Halal", "Non-Halal"]},
    {"pertanyaan": "Apakah kamu seorang vegetarian?", "jawaban": ["Iya", "Tidak"]},
    {"pertanyaan": "Apa kamu memiliki alergi makanan tertentu?", "jawaban": ["Iya", "Tidak"]},
    {"pertanyaan": "Apa kamu sedang diet?", "jawaban": ["Iya", "Tidak"]}
]

# TAMPILKAN KUIS
def tampilkan_kuis(index=0, jawaban_user=[]):
    for widget in main_frame.winfo_children():
        widget.destroy()
    if index >= len(questions):
        with open("kuis.json", "w") as f:
            json.dump(jawaban_user, f, indent=4)
        selesai = ctk.CTkLabel(main_frame, text="Terima kasih telah mengisi kuis!", font=("Kanit", 20))
        selesai.place(relx=0.5, rely=0.5, anchor="center")
        return

    q = questions[index]
    label_q = ctk.CTkLabel(main_frame, text=q["pertanyaan"], font=("Kanit", 20), text_color="#1f1f1f")
    label_q.place(relx=0.5, rely=0.3, anchor="center")

    def jawab(val):
        jawaban_user.append({"pertanyaan": q["pertanyaan"], "jawaban": val})
        tampilkan_kuis(index + 1, jawaban_user)

    btn1 = ctk.CTkButton(main_frame, text=q["jawaban"][0], command=lambda: jawab(q["jawaban"][0]),
                         width=200, height=40, fg_color="#FF7070", hover_color="#FF5050")
    btn1.place(relx=0.5, rely=0.45, anchor="center")

    btn2 = ctk.CTkButton(main_frame, text=q["jawaban"][1], command=lambda: jawab(q["jawaban"][1]),
                         width=200, height=40, fg_color="#FF7070", hover_color="#FF5050")
    btn2.place(relx=0.5, rely=0.55, anchor="center")

# HALAMAN LOGIN
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
    image_path = "smile.png.png"
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

def mulai_kuis(username):
    pertanyaan_kuis = [
        {"pertanyaan": "Apakah kamu ingin makan pedas?", "opsi": ["Iya", "Tidak"], "kolom": "rasa_makanan", "nilai": "pedas"},
        {"pertanyaan": "Apakah kamu sedang ingin makanan manis?", "opsi": ["Iya", "Tidak"], "kolom": "rasa_makanan", "nilai": "manis"},
        {"pertanyaan": "Apakah kamu suka makanan berkuah?", "opsi": ["Iya", "Tidak"], "kolom": "tekstur_makanan", "nilai": "berkuah"},
        {"pertanyaan": "Apakah cuaca di tempatmu panas?", "opsi": ["Iya", "Tidak"], "kolom": "cocok_untuk_cuaca", "nilai": "panas"}
    ]

    jawaban_user = {"username": username, "jawaban": []}
    current_index = [0]

    def tampilkan_pertanyaan():
        for widget in main_frame.winfo_children():
            widget.destroy()

        if current_index[0] < len(pertanyaan_kuis):
            item = pertanyaan_kuis[current_index[0]]

            label = ctk.CTkLabel(main_frame, text=item["pertanyaan"], font=("Kanit", 20))
            label.pack(pady=50)

            def jawab(val):
                jawaban_user["jawaban"].append({
                    "pertanyaan": item["pertanyaan"],
                    "jawaban": val,
                    "kolom_filter": item["kolom"],
                    "nilai": item["nilai"] if val == "Iya" else None
                })
                current_index[0] += 1
                tampilkan_pertanyaan()

            for opsi in item["opsi"]:
                btn = ctk.CTkButton(main_frame, text=opsi, width=200, height=40, command=lambda val=opsi: jawab(val))
                btn.pack(pady=10)
        else:
            # Simpan hasil ke kuis.json
            try:
                with open("kuis.json", "r") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []

            data.append(jawaban_user)
            with open("kuis.json", "w") as f:
                json.dump(data, f, indent=4)

            # Setelah kuis selesai, tampilkan ucapan
            for widget in main_frame.winfo_children():
                widget.destroy()
            label = ctk.CTkLabel(main_frame, text="Terima kasih telah mengisi kuis!", font=("Kanit", 20))
            label.pack(pady=100)

    tampilkan_pertanyaan()

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
