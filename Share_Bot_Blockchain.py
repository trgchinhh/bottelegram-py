# -----------------------------------------------------------
#  ! Python
#  (*) Chương trình mô phỏng blockchain bằng telegram bot
#  (*) Mỗi tin nhắn tương ứng 1 block
# -----------------------------------------------------------

import telebot, hashlib
from telebot import types
from datetime import datetime

API_BOT = "THAY API BOT"
bot = telebot.TeleBot(API_BOT)

class Block:
    def __init__(self, data):
        self.data = data
        self.prev_hash = ""
        self.hash = ""
        self.nonce = 0
        self.time = ""

def proof_of_work(dokho):
    return dokho * "0"

def hash(block):
    block_data = block.data + block.prev_hash + str(block.nonce)
    block_data = block_data.encode("utf-8")
    return hashlib.sha256(block_data).hexdigest()

class BlockChain:
    def __init__(self):
        self.chain = []
        self.g_countforprintblock = 0
        block = Block("Genesis Block")
        block.hash = hash(block)
        self.chain.append(block)

    def add_block(self, data, dokho):
        block = Block(data)
        block.prev_hash = self.chain[-1].hash
        block.hash = hash(block)
        start = datetime.now()
        while block.hash.startswith(dokho) == False:
            block.nonce += 1
            block.hash = hash(block)
        end = datetime.now()
        block.time = str(end - start)
        self.chain.append(block)

    def print_block(self, msg):
        content = ""
        if self.g_countforprintblock != 0:
            block = self.chain[-1]
            content = (
                f"Data: {block.data}\n"
                f"Prev hash: {block.prev_hash}\n"
                f"Hash: {block.hash}\n"
                f"Nonce: {block.nonce}\n"
                f"Time: {block.time}s"
            )
            bot.send_message(msg.chat.id, f"<pre>{content}</pre>", parse_mode="HTML")
        else :    
            for block in self.chain:
                content = (
                    f"Data: {block.data}\n"
                    f"Prev hash: {block.prev_hash}\n"
                    f"Hash: {block.hash}\n"
                    f"Nonce: {block.nonce}\n"
                    f"Time: {block.time}s"
                )
                bot.send_message(msg.chat.id, f"<pre>{content}</pre>", parse_mode="HTML")
        self.g_countforprintblock += 1

blockchain = BlockChain()

@bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=['sticker','photo','video','document'])  
def main(message):
    msg = message
    dokho = proof_of_work(5) # độ khó bằng 5 (5 số 0 trước mã hash)
    if msg.text: data = msg.text
    elif msg.content_type == "sticker": data = f"STICKER {msg.sticker.emoji} from {msg.from_user.id}"
    elif msg.content_type == "photo": data = f"PHOTO from {msg.from_user.id}"
    else: data = f"{msg.content_type.upper()} from {msg.from_user.id}"
    blockchain.add_block(data, dokho)
    blockchain.print_block(msg)
   
if __name__ == "__main__":
    bot.infinity_polling()



