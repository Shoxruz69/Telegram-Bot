import sys
import time
import subprocess
import os
import signal

NGROK_TOKEN = "3HGX0zRphzrLZ7EkOFDZQJkjVgp_5QCbb5gnUCEKhHGLr7Kh"
NGROK_DOMAIN = "quickly-sessions-creamer.ngrok-free.dev"
FLASK_PORT = 5000

NGROK_PATH = r"C:\Users\avt\AppData\Local\ngrok\ngrok.exe"

def start_ngrok():
    # Token ni sozlash
    subprocess.run([NGROK_PATH, "config", "add-authtoken", NGROK_TOKEN], 
                   capture_output=True)
    
    url = f"https://{NGROK_DOMAIN}"
    print(f"[ngrok] Ulandi: {url}")
    
    with open("ngrok_url.txt", "w") as f:
        f.write(url)

    while True:
        print(f"[ngrok] Tunnel ishga tushirilmoqda: {NGROK_DOMAIN}:{FLASK_PORT}")
        try:
            # Ngrok ni to'g'ridan subprocess sifatida ishga tushirish
            proc = subprocess.Popen([
                NGROK_PATH, "http", str(FLASK_PORT),
                "--domain", NGROK_DOMAIN,
                "--log", "stdout",
                "--log-level", "warn"
            ])
            
            proc.wait()  # Jarayon tugaguncha kutish
            
            print(f"[ngrok] Jarayon to'xtadi (exit={proc.returncode}). 5s kutilmoqda...")
        except KeyboardInterrupt:
            print("[ngrok] To'xtatilmoqda...")
            try:
                proc.terminate()
            except:
                pass
            sys.exit(0)
        except Exception as e:
            print(f"[ngrok] Xato: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    start_ngrok()
