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

