# --- Nút hiện đại ---
class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            font=("Segoe UI", 14, "bold"),  # font
            fg="white",                     # màu chữ
            bg="#6a5acd",                  # background
            activebackground="#483d8b", # màu backgound khi nhấn
            activeforeground="#6a5acd", # màu chữ khi nhấn
            relief="flat", # kiểu viền
            bd=0, # độ dày viền
            padx=15,           # khoảng cách ngang            
            pady=10,           # khoảng cách dọc
            cursor="hand2"  # con trỏ chuột khi đặt lên nút
        )
        self.bind("<Enter>", self.on_enter) # Hiệu ứng hover
        self.bind("<Leave>", self.on_leave) # Hiệu ứng hover

    def on_enter(self, e):
        self.config(bg="#7b68ee", fg="white")  # Màu sáng hơn khi hover

    def on_leave(self, e):
        self.config(bg="#6a5acd", fg="white")  # Trở về màu gốc
class RPSClientApp: 
    def __init__(self, root): # Khởi tạo giao diện
        self.root = root
        self.root.title("✊✂🖐 Kéo Búa Bao Online") # Tiêu đề cửa sổ
        self.root.geometry("500x420") # Kích thước cửa sổ
        self.sock = None
        self.reader_thread = None
        self.connected = False
        self.opponent = None

        # --- Gradient nền ---
        self.bg = tk.Canvas(root, width=500, height=420) # Canvas để vẽ gradient
        self.bg.pack(fill="both", expand=True)
        self.draw_gradient(self.bg, "#6a11cb", "#2575fc")  # tím -> xanh

        # --- Container chính ---
        self.card = tk.Frame(self.bg, bg="white", bd=0, relief="flat")
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=360)

        # --- Thanh trạng thái ---
        self.lbl_status = tk.Label(self.card, text="Chưa kết nối.", font=("Segoe UI", 12, "bold"), bg="white", fg="#333")
        self.lbl_status.pack(pady=10)
 # --- Nút chơi ---
        frm_btn = tk.Frame(self.card, bg="white")
        frm_btn.pack(pady=15)

        # Tăng khoảng cách giữa các nút để dễ nhìn hơn
        self.btn_keo = ModernButton(frm_btn, text="✂ Kéo", command=lambda: self.send_move("Kéo"))
        self.btn_bua = ModernButton(frm_btn, text="✊ Búa", command=lambda: self.send_move("Búa"))
        self.btn_bao = ModernButton(frm_btn, text="🖐 Bao", command=lambda: self.send_move("Bao"))
        
        self.btn_keo.grid(row=0, column=0, padx=12)  # Tăng khoảng cách
        self.btn_bua.grid(row=0, column=1, padx=12)
        self.btn_bao.grid(row=0, column=2, padx=12)

        # --- Label kết quả ---
        self.lbl_you = tk.Label(self.card, text="Bạn: ...", font=("Segoe UI", 11), bg="white", fg="#333")
        self.lbl_opp = tk.Label(self.card, text="Đối thủ: ...", font=("Segoe UI", 11), bg="white", fg="#333")
