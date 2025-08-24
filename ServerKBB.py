import socket
import threading
import json
from typing import Dict, Optional, Tuple, List

HOST = "0.0.0.0"   
PORT = 5000        

# --- Tiện ích JSON dòng ---
def send_msg(sock: socket.socket, obj: dict):
    data = (json.dumps(obj) + "\n").encode("utf-8")
    sock.sendall(data)

def recv_line(sock: socket.socket) -> Optional[str]:
    buf = []
    while True:
        ch = sock.recv(1)
        if not ch:
            return None
        if ch == b"\n":
            return b"".join(buf).decode("utf-8")
        buf.append(ch)

# --- Luật chơi ---
BEATS = {"Kéo": "Bao", "Búa": "Kéo", "Bao": "Búa"}  # A beats B

def judge(a_move: str, b_move: str) -> Tuple[str, str]:
    if a_move == b_move:
        return "draw", "draw"
    if BEATS.get(a_move) == b_move:
        return "win", "lose"
    return "lose", "win"

# --- Quản lý phòng 2 người ---
class Room:
    def __init__(self, a_sock: socket.socket, a_name: str, b_sock: socket.socket, b_name: str):
        self.a = (a_sock, a_name)
        self.b = (b_sock, b_name)
        self.lock = threading.Lock()
        self.choices: Dict[str, Optional[str]] = {a_name: None, b_name: None}
        # thông báo bắt đầu
        send_msg(a_sock, {"type": "start", "opponent": b_name})
        send_msg(b_sock, {"type": "start", "opponent": a_name})
        print(f"[ROOM] {a_name} vs {b_name} đã ghép cặp")

    def submit_move(self, player_name: str, move: str):
        with self.lock:
            if player_name not in self.choices:
                return
            self.choices[player_name] = move
            # nếu đủ 2 lượt thì chấm
            names = list(self.choices.keys())
            if all(self.choices[n] is not None for n in names):
                a_name, b_name = names
                a_move, b_move = self.choices[a_name], self.choices[b_name]
                a_result, b_result = judge(a_move, b_move)
                # gửi kết quả
                a_sock = self.a[0] if self.a[1] == a_name else self.b[0]
                b_sock = self.b[0] if self.b[1] == b_name else self.a[0]
                try:
                    send_msg(a_sock, {"type": "round_result",
                                      "you": a_move, "opponent": b_move, "outcome": a_result})
                except Exception:
                    pass
                try:
                    send_msg(b_sock, {"type": "round_result",
                                      "you": b_move, "opponent": a_move, "outcome": b_result})
                except Exception:
                    pass
                # reset cho ván mới
                self.choices = {a_name: None, b_name: None}

    def other_player(self, name: str) -> Tuple[Optional[socket.socket], Optional[str]]:
        if name == self.a[1]:
            return self.b
        if name == self.b[1]:
            return self.a
        return None, None

# --- Server state ---
rooms_by_player: Dict[str, Room] = {}
waiting_queue: List[Tuple[socket.socket, str]] = []
state_lock = threading.Lock()

def handle_client(sock: socket.socket, addr):
    name = None
    try:
        # B1: nhận gói join
        line = recv_line(sock)
        if not line:
            raise ConnectionError("no data")
        msg = json.loads(line)
        if msg.get("type") != "join" or not msg.get("name"):
            send_msg(sock, {"type": "error", "message": "Invalid join"})
            return
        name = msg["name"]
        send_msg(sock, {"type": "joined", "message": f"Xin chào {name}. Chờ ghép cặp..."})
        print(f"[JOIN] {name} từ {addr}")

        # B2: xếp hàng ghép cặp
        with state_lock:
            waiting_queue.append((sock, name))
            # nếu có >=2 người thì lấy 2 đầu hàng đợi
            if len(waiting_queue) >= 2:
                (a_sock, a_name) = waiting_queue.pop(0)
                (b_sock, b_name) = waiting_queue.pop(0)
                room = Room(a_sock, a_name, b_sock, b_name)
                rooms_by_player[a_name] = room
                rooms_by_player[b_name] = room

        # B3: vòng lặp nhận dữ liệu
        while True:
            line = recv_line(sock)
            if line is None:
                raise ConnectionError("client disconnected")
            msg = json.loads(line)
            t = msg.get("type")
            if t == "move":
                mv = msg.get("choice")
                if mv not in ("Kéo", "Búa", "Bao"):
                    send_msg(sock, {"type": "error", "message": "Lựa chọn không hợp lệ"})
                    continue
                with state_lock:
                    room = rooms_by_player.get(name)
                if room:
                    room.submit_move(name, mv)
                else:
                    send_msg(sock, {"type": "info", "message": "Đang chờ đối thủ..."})
            else:
                send_msg(sock, {"type": "error", "message": "Gói tin không hỗ trợ"})
    except Exception as e:
        print(f"[DISCONNECT] {name or addr} - {e}")
    finally:
        # dọn dẹp
        try:
            sock.close()
        except Exception:
            pass
        with state_lock:
            # loại khỏi hàng đợi nếu còn
            for i, (s, n) in list(enumerate(waiting_queue)):
                if s is sock:
                    waiting_queue.pop(i)
                    break
            # thông báo đối thủ nếu ở trong phòng
            if name and name in rooms_by_player:
                room = rooms_by_player.pop(name)
                other_sock, other_name = room.other_player(name)
                if other_name and other_name in rooms_by_player:
                    rooms_by_player.pop(other_name, None)
                if other_sock:
                    try:
                        send_msg(other_sock, {"type": "opponent_left"})
                    except Exception:
                        pass

def main():
    print(f"Server listening on {HOST}:{PORT} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
