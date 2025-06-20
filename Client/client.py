import requests
from FireBase.firebase_controller import FirebaseController

class RemoteClient:
    def __init__(self,
                 firebase_cred_path="../Firebase/service-account-key.json",
                 timeout=10):
        self.firebase = FirebaseController(
            cred_path=firebase_cred_path
        )
        self.timeout = timeout
        self.server_url = self.get_server_url()

    def get_server_url(self):
        url = self.firebase.get_url()
        if not url:
            raise ValueError("❌ Không tìm thấy server_url trong Firebase.")
        print(f"🌐 Lấy server_url từ Firebase: {url}")
        return url

    def check_connection(self):
        """Gửi request GET để kiểm tra kết nối đến server."""
        try:
            print(f"🔍 Gửi request đến: {self.server_url}/check-connection")
            response = requests.get(f"{self.server_url}/check-connection", timeout=self.timeout)
            if response.status_code == 200:
                print("✅ Kết nối thành công:", response.json())
                return True
            else:
                print(f"⚠️ Phản hồi lỗi từ server: {response.status_code}")
                return False
        except requests.RequestException as e:
            print("❌ Lỗi khi kết nối đến server:", e)
            return False

    def send_controller_data(self, button_states, axis_values, hat_values):
        """Gửi dữ liệu trạng thái bộ điều khiển đến server."""
        if not self.server_url:
            print("❌ Không có URL server để gửi dữ liệu.")
            return False

        data = {
            "button_states": button_states,
            "axis_values": axis_values,
            "hat_values": hat_values
        }
        try:
            # print(f"🎮 Gửi dữ liệu điều khiển đến: {self.server_url}/controller-input")
            response = requests.post(f"{self.server_url}/controller-input", json=data, timeout=self.timeout)
            if response.status_code == 200:
                # print("✅ Dữ liệu điều khiển đã gửi thành công.", response.json())
                return True
            else:
                print(f"⚠️ Lỗi gửi dữ liệu điều khiển: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Lỗi khi gửi dữ liệu điều khiển: {e}")
            return False


if __name__ == "__main__":
    client = RemoteClient()
    client.check_connection()
