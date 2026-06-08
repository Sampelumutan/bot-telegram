import requests
import json
import os
from datetime import datetime
import threading

TOKEN = "8824022136:AAEJt74GwCIh6_x09UmYbkflXAlDG_z8Rg4"
URL = f"https://api.telegram.org/bot{TOKEN}/"
DATA_FILE = "user_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass

def send_message(chat_id, text):
    def _send():
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
        try:
            requests.post(URL + "sendMessage", json=payload, timeout=2)
        except:
            pass
    threading.Thread(target=_send).start()

def handle_command(chat_id, text, username):
    all_users = load_data()
    uid = str(chat_id)
    
    if uid not in all_users:
        all_users[uid] = {
            "username": username,
            "wallet": 0,
            "maxpos": None,
            "maxtop": None,
            "journal": []
        }
    
    user = all_users[uid]
    
    # START
    if text == "/start":
        msg = """🤖 *Selamat Datang di Bot @sijago_tembak!*

Berikut perintah yang tersedia:

💰 *Wallet & Posisi*
/botwallet - Cek saldo wallet
/setmaxpos <angka> - Atur maksimum posisi
/setmaxtop <angka> - Atur maksimum top

📝 *Journal*
/journal <catatan> - Catat transaksi
/viewjournal - Lihat catatan

ℹ️ *Informasi*
/status - Cek status bot
/help - Bantuan

Contoh:
/setmaxpos 10000000
/journal Beli SOL 100 biji"""
        send_message(chat_id, msg)
        save_data(all_users)
        return
    
    # HELP
    if text == "/help":
        msg = """📖 *PANDUAN BOT @sijago_tembak*

/botwallet - Cek saldo wallet
/setmaxpos 10000 - Set max position
/setmaxtop 5000 - Set max top
/setwallet 1000000 - Isi saldo
/journal Beli SOL - Catat transaksi
/viewjournal - Lihat catatan
/status - Cek status bot"""
        send_message(chat_id, msg)
        return
    
    # BOTWALLET
    if text == "/botwallet":
        send_message(chat_id, f"💰 *Saldo Wallet @sijago_tembak*\n\nRp {user['wallet']:,.0f}")
        return
    
    # SETWALLET
    if text.startswith("/setwallet"):
        parts = text.split()
        if len(parts) == 2:
            try:
                user["wallet"] = float(parts[1])
                save_data(all_users)
                send_message(chat_id, f"✅ *Wallet berhasil diupdate!*\n\n💰 Saldo: Rp {user['wallet']:,.0f}")
            except:
                send_message(chat_id, "❌ Masukkan angka yang benar!\nContoh: /setwallet 1000000")
        else:
            send_message(chat_id, "⚠️ *Format salah!*\n\nGunakan: /setwallet <angka>\nContoh: /setwallet 1000000")
        return
    
    # SETMAXPOS
    if text.startswith("/setmaxpos"):
        parts = text.split()
        if len(parts) == 2:
            try:
                user["maxpos"] = float(parts[1])
                save_data(all_users)
                send_message(chat_id, f"✅ *Max Position berhasil diatur!*\n\n📊 Nilai: Rp {user['maxpos']:,.0f}")
            except:
                send_message(chat_id, "❌ Masukkan angka yang benar!\nContoh: /setmaxpos 10000000")
        else:
            send_message(chat_id, "⚠️ *Format salah!*\n\nGunakan: /setmaxpos <angka>\nContoh: /setmaxpos 10000000")
        return
    
    # SETMAXTOP
    if text.startswith("/setmaxtop"):
        parts = text.split()
        if len(parts) == 2:
            try:
                user["maxtop"] = float(parts[1])
                save_data(all_users)
                send_message(chat_id, f"✅ *Max Top berhasil diatur!*\n\n📈 Nilai: Rp {user['maxtop']:,.0f}")
            except:
                send_message(chat_id, "❌ Masukkan angka yang benar!\nContoh: /setmaxtop 5000000")
        else:
            send_message(chat_id, "⚠️ *Format salah!*\n\nGunakan: /setmaxtop <angka>\nContoh: /setmaxtop 5000000")
        return
    
    # JOURNAL
    if text.startswith("/journal"):
        note = text.replace("/journal", "").strip()
        if note:
            if "journal" not in user:
                user["journal"] = []
            user["journal"].append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": note
            })
            save_data(all_users)
            send_message(chat_id, f"✅ *Journal berhasil dicatat!*\n\n📝 {note}\n🕐 {datetime.now().strftime('%H:%M:%S')}")
        else:
            send_message(chat_id, "⚠️ *Format salah!*\n\nGunakan: /journal <catatan Anda>\nContoh: /journal Beli SOL 100 biji")
        return
    
    # VIEWJOURNAL
    if text == "/viewjournal":
        journals = user.get("journal", [])
        if not journals:
            send_message(chat_id, "📭 *Belum ada journal entries*\n\nGunakan /journal <catatan> untuk membuat catatan pertama!")
        else:
            msg = "*📔 Journal Entries (5 terakhir)*\n\n"
            for entry in journals[-5:][::-1]:
                msg += f"🕐 {entry['time']}\n📝 {entry['note']}\n\n---\n\n"
            send_message(chat_id, msg)
        return
    
    # STATUS
    if text == "/status":
        maxpos_str = f"Rp {user['maxpos']:,.0f}" if user.get('maxpos') else "Not set"
        maxtop_str = f"Rp {user['maxtop']:,.0f}" if user.get('maxtop') else "Not set"
        msg = f"""*🤖 STATUS BOT - @sijago_tembak*

💰 Wallet: Rp {user['wallet']:,.0f}
📈 Max Position: {maxpos_str}
🏆 Max Top: {maxtop_str}
📝 Journal: {len(user.get('journal', []))} entries

👤 User: @{username}
✅ Bot siap membantu!"""
        send_message(chat_id, msg)
        return
    
    # UNKNOWN COMMAND
    send_message(chat_id, "❓ *Command tidak dikenal*\n\nGunakan /help untuk melihat daftar perintah yang tersedia.")

# Variabel untuk menyimpan last_update_id
last_id = 0

def main():
    global last_id
    print("=" * 55)
    print("⚡ BOT SUPER CEPAT - @sijago_tembak")
    print("=" * 55)
    print("Bot berjalan dengan mode super cepat!")
    print("Respon akan muncul dalam 1-2 detik")
    print("-" * 55)
    print("Tekan Ctrl+C untuk menghentikan bot\n")
    
    while True:
        try:
            # Long polling dengan timeout 1 detik (super cepat)
            response = requests.get(
                URL + "getUpdates", 
                params={'timeout': 1, 'offset': last_id + 1}, 
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    for update in data.get('result', []):
                        if 'message' in update:
                            msg = update['message']
                            text = msg.get('text', '')
                            
                            if text and text.startswith('/'):
                                chat_id = msg['chat']['id']
                                username = msg['chat'].get('username', 'user')
                                print(f"📨 [{datetime.now().strftime('%H:%M:%S')}] @{username}: {text}")
                                handle_command(chat_id, text, username)
                            
                            # Update last_id
                            if update['update_id'] > last_id:
                                last_id = update['update_id']
        
        except KeyboardInterrupt:
            print("\n" + "=" * 55)
            print("👋 Bot berhenti. Sampai jumpa!")
            print("=" * 55)
            break
        except requests.exceptions.Timeout:
            # Timeout normal, lanjutkan
            continue
        except Exception as e:
            # Error lain, tetap lanjutkan
            continue

if __name__ == "__main__":
    main()