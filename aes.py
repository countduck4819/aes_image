#!/usr/bin/env python3

from Crypto.Cipher import AES

# AESCipher used to do text manipulation/cryptography
# key length : 16 character
# message length : multiple of 16
class AESCipher:
  def __init__(self, key):
    self.key = str.encode(key)

  # encrypt encript message in msg using key
  # and return ciphertext result
  def encrypt(self, msg):
    cipher = AES.new(self.key, AES.MODE_ECB)
    cipherText = cipher.encrypt(str.encode(msg))
    return cipherText.hex()

  # decrypt try decrypt cipher text in cipherText using key
  # and return secret message as result
  def decrypt(self, cipherText):
    try:
        # Kiểm tra xem cipherText có phải là một chuỗi hex hợp lệ không
        bytes.fromhex(cipherText)
    except ValueError:
        return "Ciphertext không hợp lệ."

    decipher = AES.new(self.key, AES.MODE_ECB)
    try:
        # Tiến hành giải mã
        msg = decipher.decrypt(bytes.fromhex(cipherText))
        # Loại bỏ padding (nếu có)
        msg = msg.rstrip(b'\0')
        return msg.decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        return "Không thể giải mã ciphertext."
