import os
import time
import threading
import subprocess
import requests
from flask import Flask, jsonify, request
from FireBase.firebase_controller import FirebaseController

# ========== CONFIG ==========
NGROK_PATH = r"D:\Python\RemoteController\Server\Ngrok\ngrok.exe"
PORT = 8080
DELAY = 3600  # thời gian cập nhật Firebase (s) = 1 giờ
FIREBASE_CRED = r"../Firebase/service-account-key.json"

# ========== FIREBASE + NGROK CLASS ==========
class NgrokFirebaseUpdater:
    def __init__(self, ngrok_path, port, delay, firebase_cred_path):
        self.ngrok_path = ngrok_path
        self.port = port
        self.delay = delay
        self.firebase_controller = FirebaseController(cred_path=firebase_cred_path)
        self.disable_proxies()

    def disable_proxies(self):
        for var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
            os.environ.pop(var, None)

    def start_ngrok(self) -> str:
        subprocess.run("taskkill /F /IM ngrok.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen([self.ngrok_path, "http", str(self.port)], shell=True)
        print("🔄 Đang khởi động Ngrok...")

        for i in range(30):
            try:
                res = requests.get("http://localhost:4040/api/tunnels")
                if res.status_code == 200:
                    data = res.json()
                    for tunnel in data.get("tunnels", []):
                        public_url = tunnel.get("public_url")
                        if public_url:
                            print(f"✅ Ngrok URL nhận được sau {i + 1}s: {public_url}")
                            return public_url
            except requests.RequestException:
                pass
            time.sleep(1)

        print("❌ Không thể lấy URL từ Ngrok sau 30 giây.")
        return None

    def update_firebase_host(self, url: str):
        try:
            if url:
                self.firebase_controller.set_url(url)
                print("📡 Đã cập nhật URL lên Firebase:", url)
            else:
                print("⚠️ URL rỗng, không cập nhật Firebase.")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật Firebase: {e}")

    def run(self):
        while True:
            try:
                print("⏳ Đang tạo Ngrok tunnel và cập nhật...")
                url = self.start_ngrok()
                self.update_firebase_host(url)
                print(f"🕒 Chờ {self.delay // 60} phút...\n")
                time.sleep(self.delay)
            except KeyboardInterrupt:
                print("🛑 Đã dừng chương trình bởi người dùng.")
                break
            except Exception as e:
                print(f"❌ Lỗi không xác định: {e}")
                time.sleep(10)

# ========== FLASK API ==========
app = Flask(__name__)

@app.route("/check-connection", methods=["GET"])
def check_connection():
    print("✅ Flask đã nhận request check_connection")
    return jsonify({
        "status": "ok",
        "message": "Connection successful"
    }), 200

@app.route("/controller-input", methods=["POST"])
def controller_input():
    if request.is_json:
        data = request.get_json()
        print(f"🎮 Nhận dữ liệu điều khiển: {data}")
        # TODO: Xử lý dữ liệu điều khiển tại đây (ví dụ: gửi lệnh tới game/ứng dụng đích)
        return jsonify({"status": "success", "message": "Dữ liệu điều khiển đã nhận."}), 200
    else:
        return jsonify({"status": "error", "message": "Yêu cầu phải là JSON."}), 400

def run_flask_server(host="0.0.0.0", port=PORT):
    app.run(host=host, port=port, debug=False, use_reloader=False)

# ========== MAIN ==========
if __name__ == "__main__":
    updater = NgrokFirebaseUpdater(
        ngrok_path=NGROK_PATH,
        port=PORT,
        delay=DELAY,
        firebase_cred_path=FIREBASE_CRED,
    )

    # Chạy Flask ở luồng riêng
    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.daemon = True
    flask_thread.start()

    # Chạy cập nhật Firebase mỗi giờ
    updater.run()
