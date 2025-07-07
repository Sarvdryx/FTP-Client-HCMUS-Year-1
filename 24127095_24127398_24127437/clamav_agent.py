import socket
import subprocess
import os
import msvcrt

HOST = '0.0.0.0'
PORT = 5001
BUFFER_SIZE = 8192
SAVE_FOLDER = "C:\\ScanFile"
ClamAV_PATH = "C:\\Users\\duynh/Downloads\\clamav-1.4.3.win.x64\\clamav-1.4.3.win.x64\\clamscan.exe"

os.makedirs(SAVE_FOLDER, exist_ok=True)

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
server_socket.settimeout(5.0)

try:
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b' ':
                print("Đã nhận lệnh dừng server.")
                break

        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue

        print("========================================================")
        print(f"Client kết nối từ: {addr}")

        # Nhận tên file (dòng đầu tiên, kết thúc bằng \n)
        filename_bytes = b""
        while not filename_bytes.endswith(b"\n"):
            byte = conn.recv(1)
            if not byte:
                break
            filename_bytes += byte

        filename = filename_bytes.strip().decode(errors="ignore")
        save_path = os.path.join(SAVE_FOLDER, filename)

        print(f"Đang lưu vào: {save_path}")

        # Nhận file
        with open(save_path, 'wb') as f:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)

        print("Đã nhận file. Bắt đầu quét...")

        result = subprocess.run(
            [ClamAV_PATH, save_path],
            capture_output=True,
            text=True,
            timeout=300
        )

        print("Kết quả quét:", result.stdout)
        conn.send(result.stdout.encode())
        conn.close()
        os.remove(save_path)
        print("========================================================")

finally:
    server_socket.close()
    print("Server đã đóng socket.")