import os
import time
import json
import threading
from datetime import datetime
import customtkinter as ctk
from pypresence import Presence

# ===== THIẾT LẬP GIAO DIỆN CƠ BẢN =====
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DiscordQuestPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Discord Quest Tool Pro")
        self.geometry("450x520")
        self.resizable(False, False)

        # Quản lý trạng thái
        self.running = False
        self.rpc = None
        self.client_id = self.load_config()

        self.setup_ui()

    def load_config(self):
        """Đọc config.json, tự tạo file mẫu nếu chưa có."""
        try:
            if not os.path.exists("config.json"):
                default_config = {"client_id": "YOUR_CLIENT_ID_HERE"}
                with open("config.json", "w") as f:
                    json.dump(default_config, f, indent=4)
                return ""
            with open("config.json", "r") as f:
                config = json.load(f)
                return config.get("client_id", "")
        except Exception as e:
            return ""

    def setup_ui(self):
        # --- Tiêu đề ---
        self.title_label = ctk.CTkLabel(self, text="DISCORD QUEST PRO", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        # --- Khu vực cài đặt (Main Frame) ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Chọn Game
        self.game_label = ctk.CTkLabel(self.main_frame, text="🎮 Chọn Game:", font=ctk.CTkFont(weight="bold"))
        self.game_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.game_select = ctk.CTkComboBox(self.main_frame, width=180, values=[
            "Cyberpunk 2077", "GTA V", "Fortnite", "Minecraft", "Genshin Impact"
        ])
        self.game_select.grid(row=0, column=1, padx=15, pady=(15, 10), sticky="e")

        # Thời gian
        self.time_label = ctk.CTkLabel(self.main_frame, text="⏳ Thời gian (s):", font=ctk.CTkFont(weight="bold"))
        self.time_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")

        self.time_input = ctk.CTkEntry(self.main_frame, width=180, placeholder_text="Ví dụ: 900")
        self.time_input.insert(0, "900")
        self.time_input.grid(row=1, column=1, padx=15, pady=10, sticky="e")

        # --- Trạng thái & Thanh tiến trình ---
        self.status_label = ctk.CTkLabel(self.main_frame, text="Trạng thái: Đang nghỉ...", text_color="gray")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(15, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=320)
        self.progress_bar.grid(row=3, column=0, columnspan=2, pady=5)
        self.progress_bar.set(0)

        # --- Nút điều khiển ---
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.grid(row=4, column=0, columnspan=2, pady=(15, 15))

        self.start_btn = ctk.CTkButton(self.btn_frame, text="🚀 Bắt đầu", fg_color="green", hover_color="darkgreen", command=self.start_quest)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(self.btn_frame, text="🛑 Dừng lại", fg_color="red", hover_color="darkred", state="disabled", command=self.stop_quest)
        self.stop_btn.pack(side="left", padx=10)

        # --- Hộp thoại Log ---
        self.log_box = ctk.CTkTextbox(self, height=120, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(pady=(0, 20), padx=20, fill="x")
        
        self.log("Hệ thống sẵn sàng!")
        if not self.client_id or self.client_id == "YOUR_CLIENT_ID_HERE":
            self.log("CẢNH BÁO: Vui lòng nhập client_id vào file config.json!")

    def log(self, msg):
        """In log kèm thời gian thực."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end")

    def start_quest(self):
        if not self.client_id or self.client_id == "YOUR_CLIENT_ID_HERE":
            self.log("Lỗi: Không tìm thấy client_id hợp lệ!")
            return
        try:
            duration = int(self.time_input.get())
            if duration <= 0: raise ValueError
        except ValueError:
            self.log("Lỗi: Thời gian phải là số nguyên dương!")
            return

        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Đang kết nối Discord...", text_color="yellow")

        # Khởi chạy luồng nền
        threading.Thread(target=self.quest_worker, args=(self.game_select.get(), duration), daemon=True).start()

    def quest_worker(self, game, duration):
        """Luồng xử lý chính, tách biệt khỏi UI."""
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.after(0, self.log, "Đã kết nối Discord RPC!")
        except Exception as e:
            self.after(0, self.log, "Lỗi: Không thể kết nối. Discord đã mở chưa?")
            self.after(0, self.reset_ui)
            return

        start_time = int(time.time())
        self.after(0, lambda: self.status_label.configure(text=f"Đang cày: {game}...", text_color="lightgreen"))

        while self.running:
            elapsed = int(time.time()) - start_time
            if elapsed >= duration:
                self.after(0, self.log, "Hoàn thành nhiệm vụ! Hãy vào Discord nhận quà.")
                break

            try:
                # Chỉ gửi update RPC mỗi 15s để tránh Rate Limit của Discord
                if elapsed % 15 == 0 or elapsed == 0:
                    self.rpc.update(
                        details="Playing for quest...",
                        state="Auto Quest Tool Pro",
                        start=start_time,
                        large_image="default",
                        large_text=game
                    )
            except Exception:
                self.after(0, self.log, "Lỗi khi cập nhật RPC (Mất kết nối).")
                break

            # Cập nhật thanh tiến trình (Dùng self.after để an toàn)
            progress_val = min(elapsed / duration, 1.0)
            self.after(0, self.progress_bar.set, progress_val)
            self.after(0, lambda e=elapsed, d=duration: self.status_label.configure(text=f"Tiến trình: {e}/{d}s"))

            # Chờ 1s mỗi vòng lặp giúp nút Stop phản hồi nhanh
            time.sleep(1)

        self.after(0, self.reset_ui)

    def stop_quest(self):
        self.log("Đang dừng...")
        self.running = False

    def reset_ui(self):
        """Khôi phục UI sau khi chạy xong hoặc bấm Stop."""
        self.running = False
        if self.rpc:
            try:
                self.rpc.close()
            except: pass
            self.rpc = None
            
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Trạng thái: Đã dừng", text_color="gray")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = DiscordQuestPro()
    app.mainloop()
