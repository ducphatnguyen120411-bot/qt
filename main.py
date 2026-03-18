import os, time, json, threading
import customtkinter as ctk
from pypresence import Presence
from datetime import datetime, timedelta

class DiscordQuestProV3(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Discord Quest Pro v3.0")
        self.geometry("480x550")
        ctk.set_appearance_mode("dark")
        
        self.running = False
        self.rpc = None
        self.config = self.load_config()
        self.setup_ui()

    def load_config(self):
        if not os.path.exists("config.json"):
            return {"client_id": "", "games": ["Arknights: Endfield", "Call of Duty: Warzone"]}
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def setup_ui(self):
        # Tiêu đề xịn
        self.header = ctk.CTkLabel(self, text="⚡ DISCORD QUEST AUTOMATION", font=("Orbitron", 20, "bold"), text_color="#5865F2")
        self.header.pack(pady=20)

        # Container
        self.frame = ctk.CTkFrame(self, fg_color="#2B2D31")
        self.frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Chọn Game
        ctk.CTkLabel(self.frame, text="🎮 CHỌN NHIỆM VỤ GAME:", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        self.game_select = ctk.CTkComboBox(self.frame, values=self.config["games"], width=300, height=35)
        self.game_select.pack(pady=10)

        # Thời gian (mặc định 900s = 15p)
        ctk.CTkLabel(self.frame, text="⏳ THỜI GIAN TREO (GIÂY):", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.time_input = ctk.CTkEntry(self.frame, width=300, height=35)
        self.time_input.insert(0, "900")
        self.time_input.pack(pady=10)

        # Progress
        self.status_text = ctk.CTkLabel(self.frame, text="Trạng thái: Sẵn sàng", text_color="#B5BAC1")
        self.status_text.pack(pady=5)
        self.progress_bar = ctk.CTkProgressBar(self.frame, width=350, height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        # Nút bấm
        self.btn_action = ctk.CTkButton(self, text="BẮT ĐẦU LÀM QUEST", font=("Arial", 14, "bold"), 
                                        fg_color="#5865F2", hover_color="#4752C4", height=45, command=self.toggle_process)
        self.btn_action.pack(pady=20)

        # Log
        self.log_box = ctk.CTkTextbox(self, height=80, font=("Consolas", 11), fg_color="#1E1F22")
        self.log_box.pack(padx=20, pady=(0, 20), fill="x")

    def log(self, msg):
        self.log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see("end")

    def toggle_process(self):
        if not self.running:
            cid = self.config.get("client_id")
            if not cid or cid == "YOUR_CLIENT_ID_HERE":
                self.log("Lỗi: Bạn chưa nhập Client ID vào config.json!")
                return
            
            self.running = True
            self.btn_action.configure(text="DỪNG LẠI", fg_color="#ED4245", hover_color="#C03537")
            threading.Thread(target=self.run_quest, daemon=True).start()
        else:
            self.running = False

    def run_quest(self):
        try:
            self.rpc = Presence(self.config["client_id"])
            self.rpc.connect()
            
            game = self.game_select.get()
            target_sec = int(self.time_input.get())
            start_time = int(time.time())

            self.log(f"Đang giả lập chơi: {game}")

            while self.running:
                current_time = int(time.time())
                elapsed = current_time - start_time
                
                if elapsed >= target_sec:
                    self.log("Đã đủ thời gian! Hãy vào Discord nhận thưởng.")
                    break

                # Cập nhật Discord
                self.rpc.update(
                    state=f"Nhiệm vụ: {game}",
                    details="Đang tự động làm Quest...",
                    start=start_time,
                    large_image="default"
                )

                # Cập nhật UI
                percent = elapsed / target_sec
                self.after(0, lambda p=percent, e=elapsed, t=target_sec: self.update_ui(p, e, t))
                time.sleep(1)

        except Exception as e:
            self.log(f"Lỗi: {e}")
        finally:
            self.stop_rpc()

    def update_ui(self, p, e, t):
        self.progress_bar.set(p)
        self.status_text.configure(text=f"Tiến độ: {e}/{t} giây", text_color="#3BA55C")

    def stop_rpc(self):
        self.running = False
        if self.rpc:
            self.rpc.close()
            self.rpc = None
        self.btn_action.configure(text="BẮT ĐẦU LÀM QUEST", fg_color="#5865F2")
        self.status_text.configure(text="Trạng thái: Đã dừng", text_color="#ED4245")
        self.log("Đã dừng tool.")

if __name__ == "__main__":
    app = DiscordQuestProV3()
    app.mainloop()
