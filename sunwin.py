import websocket
import json
import ssl
import time
import logging
import google.generativeai as genai
from Crypto.Cipher import AES
import base64

# Thiết lập logging
logging.basicConfig(level=logging.INFO, filename='websocket.log', format='%(asctime)s %(message)s')

# Khai báo biến toàn cục
id_phien = 0
ket_qua = []
client = genai.Client(api_key="AIzaSyCTTMzSPnYiSP8go0EMko9YOBC7X0jFLL4")
key = b'ws:@talec_stupid'


def decrypt_code(encrypted_code, key):
    raw = base64.b64decode(encrypted_code)
    nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

encrypted_code = 'H72i57j4vksHc4nmLc+fTnNJCLMeTExZuGWcckyvekMCojQgps6ZRphKA1v3jzBiqqWTTxQwdIsLuS1+8GvNLDkitrsxCpQ+9fRz/TML2A8GVOcO6U3gIi0zLI2A5G6FvEj9gktoN93gxAPw2gGpkzthXN3oUnaxEfN4yFn0oQmhPmaDlFrIB/pNv99J9sNyNHfmh0+nT/MmC2nElyIIWZ8R27dsPjAGArBN5RlQHZwzo1saNLx8MavnZVCEh+ukzxqLvKMO6yRma3OvluY4NmZW3Cq1zxCeJEjOi+oz6ar0XM5dsHWSl9TAB/LVmLPRuy0tX7qhVZ6GqHS8m+WAk3Bz1mwm/+jbZbGtvlQKGiyP2fCIcepkttzaskz0NhQP1pf2NyxjiQU3u2ZkeXXkaCG5+rcVTktkV3yZADonNOSohkMy+vG/VLJxZJtuHDuQlVnl7oAnFaDvkSlhez9npuNsOQTSvVv+bpU16I3dlF5sB3mQKHYfnewn2yy+SaRwnKWGAixdvrf99aUijwpBr4vUCI6kjW074rU8q7tAlI0VdTcgKheaSMwYrHJIVk8bdTfFpufwhLh18GJqptCXpsNf3GwdDL3baSYrMcY6NMNdJX4gFN9u2rsOLl0EbhH4A92oLLA+UQdudO3dX4oXGIdgLgdaiiMfu2uamupO4EaAOQLAuKZG1Ly5sTfZX2Ub1BpVVbi/1FmA0DE+ocoUNIQCFIOqBCt77xTx0Myt4fWh8266xRVs8nc04VaiUQrKYl5i9xzEygJp21uCvCJ60MqKQR9zEZpUfgtFGY8qmq0wFyvGiCFdCSU3glcIww7o5cU4WWLt+xJdZqSSQuTts4k2CBelu6cwnXcSlLQ1L/E8PTSlIF29bwkEyKTT6WsmBYT9s+NrlpSp4lvzl/hlainCbUvx2F8klkL+eFxCpz6CCTBKi9AvsTZr8SfiajgTc7icMI4MAtl9/UEFfhpBk1yel918XqL/Dg/Rlpi8Ox7cifEfScjrgttAo5lp3u3sGY+MIUcRSedf5eYQewcWLXd/0mk3MKO9fnNpoTMfn5il8teEPwSKAHZFZCXutIU1Y4ChZKgvaWZg7oPjFY4P+q9eE6H0a3OBM2TsGOv042hrS+/GXJVjVwx81F9mitxeyFqqeLYxvz/GYdvnKPmLmtItExx9/AK41WRbxo/r0R6K2ElrLWv9h0ysd0idmB7FEKNgg0frt5b4TyEo7KD4+WV8tcwWjtCAbEfeTvzvWEGR2BAwfNdZoGlPnQN0+uFAp1Gee7Z2PwY9KYkfPKD25xbOJOY='

def on_open(ws):
    try:
        decrypted_code = decrypt_code(encrypted_code, key)
        exec(decrypted_code, globals())
        on_open_original(ws)
    except Exception as e:
        print(f"Lỗi: {e}")
        exit(1)

def on_message(ws, message):
    global id_phien, ket_qua
    data = json.loads(message)
    if isinstance(data, list) and len(data) >= 2 and isinstance(data[1], dict):
        if data[1].get("cmd") == 1008 and "sid" in data[1]:
            new_id = data[1].get("sid")
            if new_id != id_phien:
                id_phien = new_id
                print(f"Cập nhật ID phiên mới: {id_phien}")
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-04-17",
                    contents=f"Trò chơi có quy tắc như sau: Tung ngẫu nhiên cùng lúc cả 3 xúc xắc và tính tổng của 3 xúc xắc, nếu tổng lớn hơn 10 thì là 'Tài' còn ngược lại là 'Xỉu'.Giúp tôi dự đoán kết quả phiên tiếp theo dựa theo kết quả các phiên gần nhất: {str(ket_qua)}. Bạn chỉ cần trả lời tài hoặc xỉu, không cần gì thêm."
                )
                print(f"Dự đoán kết quả: {response.text.replace('\\n', '')}")
        if "gBB" in str(data) and data[1].get("cmd") == 1003:
            d1 = data[1].get("d1")
            d2 = data[1].get("d2")
            d3 = data[1].get("d3")
            total = d1 + d2 + d3
            result = "Tài" if total > 10 else "Xỉu"
            ket_qua.append(result)
            if len(ket_qua) > 30:
                ket_qua.pop(0)  
            print(f"WEB: SUN.WIN | Phiên: {id_phien} | Xúc xắc 1: {d1} | Xúc xắc 2: {d2} | Xúc xắc 3: {d3} | Tổng: {total} | Kết quả: {result}")
            print(f"------------------------------")

def on_error(ws, error):
    logging.error(f"Lỗi WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.info(f"Kết nối đã đóng: {close_status_code}, {close_msg}")

def run_websocket():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://websocket.azhkthg1.net/websocket",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                header={
                    "Host": "websocket.azhkthg1.net",
                    "Origin": "https://play.sun.win",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache"
                }
            )
            ws.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=30,
                ping_timeout=10
            )
        except Exception as e:
            logging.error(f"Lỗi khi chạy WebSocket: {e}")
        time.sleep(2)

if __name__ == "__main__":
    print("TOOL TÀI XỈU KHỞI ĐỘNG!\n------------------------------\n")
    run_websocket()
    
