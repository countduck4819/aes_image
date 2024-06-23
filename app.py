#!/usr/bin/env python3
import os
import cv2
import tkinter as tk
import numpy as np
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from PIL import Image, ImageTk
from lsb import LSB
from aes import AESCipher
from Crypto.Cipher import AES
import secrets
import docx2txt

# Activity handle all user interaction like:
# 1. preview image
# 2. handle button click interaction
# 3. program lifecycle from start and exit
# 4. how User Interface looks like
class EncodeTag:
  # store image on cv2 object to be able to image manipulation
  image = None
  # store image on Imagetk object to be able to preview on window
  imgPanel = None

  keyInput = None
  messageInput = None
  path = "./dst.png"

  def __init__(self ,master):
    self.master = master
    self.master.title('AES + Steganography')
    # use blank image when program started
    self.image = np.zeros(shape=[40, 40, 3], dtype=np.uint8)
    self.updateImage()

    titleName = tk.Label(self.master, text='Giấu tin')
    titleName.place(x=170, y=10)
    
    openBtn = tk.Button(self.master, text='Mở file ảnh', command=self.openImage)
    openBtn.place(x=20, y=30)

    btnFrame = tk.Frame(self.master)
    btnFrame.place(x=170, y=410, width=200, height=100)

    encodeBtn = tk.Button(btnFrame, text='Mã hóa', command=self.encode)
    encodeBtn.place(x=0, y=0)

    # decodeBtn = tk.Button(btnFrame, text='Decode', command=self.decode)
    # decodeBtn.place(x=100, y=0)

    savebtnFrame = tk.Frame(self.master)
    savebtnFrame.place(x=167, y=460, width=200, height=100)

    saveBtn = tk.Button(savebtnFrame, text='Lưu ảnh đã mã hóa', command=self.saveImage)
    saveBtn.place(x=0, y=0)

    keyLabel = tk.Label(self.master, text='Mật khẩu')
    keyLabel.place(x=10, y=520)
    self.keyInput = tk.Entry(self.master)
    self.keyInput.place(x=100, y=520, width=200)
    
    createKeyBtn = tk.Button(self.master, text='Sinh mật khẩu', command=self.generate_aes_16bit_key)
    createKeyBtn.place(x=320, y=520)

    messageLabel = tk.Label(self.master, text='Tin cần giấu')
    messageLabel.place(x=10, y=550)
    selectFileBtn = tk.Button(self.master, text='Mở file text/doc', command=self.open_file)
    selectFileBtn.place(x=420, y=550)
    self.messageInput = tk.Text(self.master, height=10, width=60)
    self.messageInput.place(x=10, y=580)

  def getKeyValue(self):
    return self.keyInput.get();
  
  def generate_aes_16bit_key(self):
    key = secrets.token_hex(16)
    key = ''.join(secrets.choice(key) for i in range(16))
    self.keyInput.delete(0,tk.END)
    self.keyInput.insert(0,key)
    messagebox.showinfo("Thông báo", "Sinh khóa thành công")
    return 
  
  def open_file(self):
    file_name = tk.filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text,Word Files", "*.txt;*.docx")])
    if file_name:
        try:
            if os.path.isfile(file_name) and os.access(file_name, os.R_OK):
                with open(file_name, "r") as file:
                    if file_name.endswith(".txt"):
                        content = file.read()
                    elif file_name.endswith(".docx"):
                        content = docx2txt.process(os.path.abspath(file_name))
                    self.messageInput.delete("1.0", "end")
                    self.messageInput.insert("end", content)
            else:
                messagebox.showerror("Error!", "Không tìm thấy tệp hoặc quyền truy cập bị từ chối")
        except Exception as e:
            messagebox.showerror("Error!", str(e))
  
  # updateImage read image from cv2 object and preview on image window
  def updateImage(self):
     # Thiết lập kích thước mới, giữ tỷ lệ khung hình
    max_width = 400
    max_height = 300
    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    
    
    # Lấy kích thước ban đầu của ảnh
    if self.imgPanel == None:
        image = image.convert("RGB")
        image = Image.eval(image, lambda x: 255)
        image = image.resize((max_width, max_height), resample=Image.BILINEAR)
    else: 
        original_width, original_height = image.size
        if original_width > max_width or original_height > max_height:
          ratio = min(max_width / original_width, max_height / original_height)
          new_width = int(original_width * ratio)
          new_height = int(original_height * ratio)
          image = image.resize((new_width, new_height), resample=Image.BILINEAR)
    image = ImageTk.PhotoImage(image)
    
    if self.imgPanel == None:
      self.imgPanel = tk.Label(image=image)
      self.imgPanel.image = image
      self.imgPanel.place(x=30, y=85)
    else:
      self.imgPanel.configure(image = image)
      self.imgPanel.image = image

  # cipher create AESCipher object to encode message with inputed key as secret key
  def cipher(self):
    key = self.keyInput.get()
    # key length must 16 character
    if len(key) != 16:
      messagebox.showwarning("Warning","Key must be 16 character")
      return

    return AESCipher(self.keyInput.get())

  # encode encode message using AESCipher and embed cipher text to image
  def encode(self):
    message = self.messageInput.get("1.0",'end-1c')
    # message length will forced to be multiple of 16 by adding extra white space
    # at the end
    if len(message)%16 != 0:
      message += (" " * (16-len(message)%16))

    cipher = self.cipher()
    if cipher == None:
      return
    cipherText = cipher.encrypt(message)

    obj = LSB(self.image)
    obj.embed(cipherText)
    self.messageInput.delete(1.0, tk.END)
    self.image = obj.image

    # preview image after cipher text is embedded
    self.updateImage()
    messagebox.showinfo("Thông báo", "Mã hóa thành công")

  # # decode extract cipher text from image and try decode it using provided secret key
  # def decode(self):
  #   cipher = self.cipher()
  #   if cipher == None:
  #     return

  #   obj = LSB(self.image)

  #   cipherText = obj.extract()
  #   msg = cipher.decrypt(cipherText)
    
  #   # show decoded secret message to message input box
  #   self.messageInput.delete(1.0, tk.END)
  #   self.messageInput.insert(tk.INSERT, msg)

  # openImage ask user to select image
  def openImage(self):
    path = askopenfilename()
    if not isinstance(path, str):
      return

    self.image = cv2.imread(path)
    self.updateImage()

  # saveValue export int value for every color channel (RGB)
  # on csv format
  def saveValue(self):
    path = asksaveasfilename(title = "Select file")
    if path == '':
      return

    np.savetxt(path+'_blue.csv', self.image[:, :, 0], delimiter=',', fmt='%d')
    np.savetxt(path+'_green.csv', self.image[:, :, 1], delimiter=',', fmt='%d')
    np.savetxt(path+'_red.csv', self.image[:, :, 2], delimiter=',', fmt='%d')

    messagebox.showinfo("Info", "Saved")

  # saveImage save image on png format
  def saveImage(self):
    path = asksaveasfilename(title = "Select file",filetypes=[("png files", "*.png")])
    if path == '':
      return

    # if ".png" not in path:
    path = path + ".bmp"

    obj = LSB(self.image)
    obj.save(path)

    messagebox.showinfo("Thông báo", "Ảnh đã được lưu")


class DecodeTag:
  # store image on cv2 object to be able to image manipulation
  image = None
  # store image on Imagetk object to be able to preview on window
  imgPanel = None

  keyInput = None
  messageInput = None
  path = "./dst.png"

  def __init__(self,master):
    self.master = master

    # use blank image when program started
    self.image = np.zeros(shape=[40, 40, 3], dtype=np.uint8)
    self.updateImage()

      

  # updateImage read image from cv2 object and preview on image window
  def updateImage(self):
     # Thiết lập kích thước mới, giữ tỷ lệ khung hình
    max_width = 400
    max_height = 300
    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    
    titleName = tk.Label(self.master, text='Tách tin')
    titleName.place(x=780, y=10)
    
    openBtn = tk.Button(self.master, text='Mở file ảnh', command=self.openImage)
    openBtn.place(x=620, y=30)

    btnFrame = tk.Frame(self.master)
    btnFrame.place(x=770, y=410, width=200, height=100)

    # encodeBtn = tk.Button(btnFrame, text='Encode', command=self.encode)
    # encodeBtn.place(x=0, y=0)

    decodeBtn = tk.Button(btnFrame, text='Giải mã', command=self.decode)
    decodeBtn.place(x=0, y=0)

    savebtnFrame = tk.Frame(self.master)
    savebtnFrame.place(x=760, y=460, width=200, height=100)

    # saveBtn = tk.Button(savebtnFrame, text='Save Image', command=self.saveImage)
    # saveBtn.place(x=0, y=0)

    # saveValueBtn = tk.Button(savebtnFrame, text='Save Value', command=self.saveValue)
    # saveValueBtn.place(x=100, y=0)

    keyLabel = tk.Label(self.master, text='Khóa')
    keyLabel.place(x=610, y=520)
    self.keyInput = tk.Entry(self.master)
    self.keyInput.place(x=700, y=520, width=200)

    messageLabel = tk.Label(self.master, text='Tin nhắn đã tách')
    messageLabel.place(x=610, y=550)
    self.messageInput = tk.Text(self.master, height=10, width=60)
    self.messageInput.place(x=610, y=580)
    
    # Lấy kích thước ban đầu của ảnh
    if self.imgPanel == None:
        image = image.convert("RGB")
        image = Image.eval(image, lambda x: 255)
        image = image.resize((max_width, max_height), resample=Image.BILINEAR)
    else: 
        original_width, original_height = image.size
        if original_width > max_width or original_height > max_height:
          ratio = min(max_width / original_width, max_height / original_height)
          new_width = int(original_width * ratio)
          new_height = int(original_height * ratio)
          image = image.resize((new_width, new_height), resample=Image.BILINEAR)
    image = ImageTk.PhotoImage(image)
    
    if self.imgPanel == None:
      self.imgPanel = tk.Label(image=image)
      self.imgPanel.image = image
      self.imgPanel.place(x=630, y=85)
    else:
      self.imgPanel.configure(image = image)
      self.imgPanel.image = image

  # cipher create AESCipher object to encode message with inputed key as secret key
  def cipher(self):
    key = self.keyInput.get()
    # key length must 16 character
    if len(key) != 16:
      messagebox.showwarning("Cảnh báo","Mật khẩu phải 16 kí tự")
      return

    return AESCipher(self.keyInput.get())

  # encode encode message using AESCipher and embed cipher text to image
  # def encode(self):
  #   message = self.messageInput.get("1.0",'end-1c')
  #   # message length will forced to be multiple of 16 by adding extra white space
  #   # at the end
  #   if len(message)%16 != 0:
  #     message += (" " * (16-len(message)%16))

  #   cipher = self.cipher()
  #   if cipher == None:
  #     return
  #   cipherText = cipher.encrypt(message)

  #   obj = LSB(self.image)
  #   obj.embed(cipherText)
  #   self.messageInput.delete(1.0, tk.END)
  #   self.image = obj.image

  #   # preview image after cipher text is embedded
  #   self.updateImage()
  #   messagebox.showinfo("Thông báo", "Mã hóa thành công")

  # decode extract cipher text from image and try decode it using provided secret key
  def decode(self):
    cipher = self.cipher()
    if cipher == None:
      return

    obj = LSB(self.image)

    cipherText = obj.extract()
    msg = cipher.decrypt(cipherText)
    if (msg == "Không thể giải mã ciphertext."):
      self.messageInput.config(fg="red", state="disabled")
      self.messageInput.delete(1.0, tk.END)
      self.messageInput.insert(tk.INSERT, msg)
      messagebox.showerror("Lỗi", "Tách tin không thành công")
    else:
      self.messageInput.config(fg="black")
      self.messageInput.delete(1.0, tk.END)
      self.messageInput.insert(tk.INSERT, msg)
      messagebox.showinfo("Thông báo", "Tách tin thành công")
    # show decoded secret message to message input box
    

  # openImage ask user to select image
  def openImage(self):
    path = askopenfilename()
    if not isinstance(path, str):
      return

    self.image = cv2.imread(path)
    self.updateImage()

  # saveValue export int value for every color channel (RGB)
  # on csv format
  def saveValue(self):
    path = asksaveasfilename(title = "Select file")
    if path == '':
      return

    np.savetxt(path+'_blue.csv', self.image[:, :, 0], delimiter=',', fmt='%d')
    np.savetxt(path+'_green.csv', self.image[:, :, 1], delimiter=',', fmt='%d')
    np.savetxt(path+'_red.csv', self.image[:, :, 2], delimiter=',', fmt='%d')

    messagebox.showinfo("Info", "Saved")

  # saveImage save image on png format
  def saveImage(self):
    path = asksaveasfilename(title = "Select file",filetypes=[("png files", "*.png")])
    if path == '':
      return

    if ".png" not in path:
      path = path + ".png"

    obj = LSB(self.image)
    obj.save(path)

    messagebox.showinfo("Info", "Saved")

  def startLoop(self):
    self.master.mainloop()

if __name__ == "__main__":
  root = tk.Tk()
  # tag1 = tk.Label(root, text="tag1", width=10, height=5)
  # tag1.config(text="helo1")
  # tag1.pack(side=tk.LEFT)

  # tag2 = tk.Label(root , text="tag2", width=10, height=5)
  # tag2.config(text="helo2")
  # tag2.pack(side=tk.LEFT)
  EncodeTag(root)
  DecodeTag(root)
  root.mainloop()
