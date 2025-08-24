import threading
import json
import tkinter as tk
from tkinter import messagebox

# --- Tiện ích JSON dòng ---
def send_msg(sock: socket.socket, obj: dict):
    data = (json.dumps(obj) + "\n").encode("utf-8")
    sock.sendall(data)

def recv_line(sock: socket.socket):
    buf = []
    while True:
        ch = sock.recv(1)
        if not ch:
            return None
        if ch == b"\n":
            return b"".join(buf).decode("utf-8")
        buf.append(ch)
        
# --- Giao diện đẳng cấp ---
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
self.lbl_result = tk.Label(self.card, text="Kết quả: ...", font=("Segoe UI", 16, "bold"), bg="white", fg="#444")

        self.lbl_you.pack(pady=6)
        self.lbl_opp.pack(pady=6)
        self.lbl_result.pack(pady=8)

        # Nút connect chỉ cần tên
        frm_name = tk.Frame(self.card, bg="white")
        frm_name.pack(pady=10)
        tk.Label(frm_name, text="Tên:", bg="white", fg="#444", font=("Segoe UI", 11)).pack(side="left")
        self.ent_name = tk.Entry(frm_name, font=("Segoe UI", 11), width=18)
        self.ent_name.insert(0, "Player")
        self.ent_name.pack(side="left", padx=8)
        self.btn_connect = ModernButton(frm_name, text="Kết nối", command=self.connect)
        self.btn_connect.pack(side="left")

        self.enable_move_buttons(False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
 # Gradient background
    def draw_gradient(self, canvas, color1, color2):
        width, height = 500, 420
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height
        for i in range(height):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr>>8:02x}{ng>>8:02x}{nb>>8:02x}"
            canvas.create_line(0, i, width, i, fill=color)
            import socket
        # --- Connect ---
    def connect(self):
        if self.connected:
            return
        host = "127.0.0.1"
        port = 5000
        name = self.ent_name.get().strip() or "Player"
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            send_msg(self.sock, {"type": "join", "name": name})
            self.connected = True
            self.btn_connect.config(state="disabled", text="Đã kết nối")
            self.set_status("Đã kết nối. Đang chờ ghép cặp...")
            # Thread nhận dữ liệu
            self.reader_thread = threading.Thread(target=self.reader_loop, daemon=True)
            self.reader_thread.start()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không kết nối được: {e}")

    def reader_loop(self):
        try:
            while True:
                line = recv_line(self.sock)
                if line is None:
                    self.on_server_disconnected()
                    return
                msg = json.loads(line)
                self.handle_msg(msg)
        except Exception:
            self.on_server_disconnected()

    # --- Xử lý message ---
    def handle_msg(self, msg: dict):
        t = msg.get("type")
        if t == "start":
            self.opponent = msg.get("opponent", "Đối thủ")
            self.set_status(f"Đã ghép cặp với: {self.opponent}. Chọn nước đi!")
            self.enable_move_buttons(True)
            self.reset_round_labels()
        elif t == "round_result":
            you = msg.get("you", "...")
            opp = msg.get("opponent", "...")
            outcome = msg.get("outcome", "draw")
            self.lbl_you.config(text=f"Bạn: {you}")
            self.lbl_opp.config(text=f"Đối thủ: {opp}")
            colors = {"win": "green", "lose": "red", "draw": "orange"}
            text = {"win": "🎉 Bạn THẮNG!", "lose": "😢 Bạn THUA", "draw": "🤝 HOÀ"}
            self.lbl_result.config(text=text.get(outcome, outcome), fg=colors.get(outcome, "#444"))
            self.enable_move_buttons(True)
        elif t == "opponent_left":
            self.set_status("Đối thủ đã thoát. Đang chờ ghép cặp...")
            self.enable_move_buttons(False)
            self.reset_round_labels()

    # --- Gửi ---
    def send_move(self, choice: str):
        if not self.connected:
            return
        send_msg(self.sock, {"type": "move", "choice": choice})
        self.enable_move_buttons(False)
        self.lbl_you.config(text=f"Bạn: {choice}")
        self.lbl_opp.config(text="Đối thủ: (đang chờ...)")
        self.lbl_result.config(text="Kết quả: (đang xử lý...)", fg="#666")

    # --- UI tiện ích ---
    def set_status(self, text):
        self.lbl_status.config(text=text)

    def enable_move_buttons(self, enable: bool):
        state = "normal" if enable else "disabled"
        self.btn_keo.config(state=state)
        self.btn_bua.config(state=state)
        self.btn_bao.config(state=state)

    def reset_round_labels(self):
        self.lbl_you.config(text="Bạn: ...", fg="#333")
        self.lbl_opp.config(text="Đối thủ: ...", fg="#333")
        self.lbl_result.config(text="Kết quả: ...", fg="#444")

    def on_server_disconnected(self):
        self.connected = False
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.sock = None
        self.enable_move_buttons(False)
        self.set_status("⚠ Mất kết nối server!")

    def on_close(self):
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RPSClientApp(root)
    root.mainloop()
    
