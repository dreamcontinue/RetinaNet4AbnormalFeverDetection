from tkinter import *
import tkinter as tk
import tkinter.messagebox as mb
import tkinter.filedialog as fd
from PIL import Image, ImageTk
import os, sys
from detect_img import detect as detect_img

top = Tk()
top.title('电缆终端异常发热检测')
top.geometry('1000x600')
# top.resizable(width=False, height=False)

img_path = None
use_gpu=tk.BooleanVar()


def set_btn(state='normal'):
    btn_open_img.config(state=state)
    btn_rot.config(state=state)
    btn_det.config(state=state)
    btn_dir.config(state=state)

def ck_gpu():
    print(use_gpu.get())


def open_img():
    global img_path
    img_path = fd.askopenfilename()
    img = Image.open(img_path)
    img.thumbnail((480, 560))
    img = ImageTk.PhotoImage(img)
    label_open_img.config(image=img)
    top.mainloop()


def rotate():
    img = Image.open(img_path)
    img = img.rotate(90, expand=True)
    img.save(img_path)

    img = Image.open(img_path)
    img.thumbnail((480, 560))
    img = ImageTk.PhotoImage(img)
    label_open_img.config(image=img)
    top.mainloop()


def detect():
    label_detect.delete(tk.ALL)
    label_detect.update()
    if img_path is None: return
    if not (img_path.endswith('.jpg') or img_path.endswith('.png')): return
    set_btn('disable')
    label_detect.create_text((100, 100), anchor=NW, text='正在检测中...(1/1)')
    label_detect.update()

    save_path = os.path.join(os.path.split(img_path)[0], 'detection results')
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_path = os.path.join(save_path, os.path.split(img_path)[1])
    flag, p = detect_img(img_path, save_path)
    img = Image.open(save_path)
    img.thumbnail((480, 560))
    img = ImageTk.PhotoImage(image=img)
    label_detect.create_image((100, 20), anchor=NW, image=img)
    label_detect.update()

    title = '检测到发热异常,概率 {}%'.format(int(100 * p)) if flag and p > 0 else '检测无异常'
    msg = '检测结果图像已存储到文件：\n \"' + save_path + '\" 中'
    label_detect.create_text((100, 420), anchor=NW, text=title)
    label_detect.update()

    label_detect.create_text((100, 460), anchor=NW, text=msg, width=300)
    label_detect.update()
    set_btn('normal')
    top.mainloop()


def open_dir_detect():
    global img_path
    img_dir = fd.askdirectory()
    if img_dir is None: return
    summ = 0
    for filename in os.listdir(img_dir):
        if not (filename.endswith('.jpg') or filename.endswith('.png')): continue
        summ += 1
    if summ == 0: return
    cnt = 0
    cnt_hot = 0
    label_detect.delete(tk.ALL)
    label_detect.update()
    set_btn('disable')
    for filename in os.listdir(img_dir):
        if not (filename.endswith('.jpg') or filename.endswith('.png')): continue

        label_detect.create_text((100, 20), anchor=NW, text='检测进度 {}/{}'.format(cnt, summ))
        label_detect.update()
        cnt += 1

        img_path = os.path.join(img_dir, filename)

        img = Image.open(img_path)
        img.thumbnail((480, 560))
        img = ImageTk.PhotoImage(img)
        label_open_img.config(image=img)
        label_open_img.update()

        save_path = os.path.join(os.path.split(img_path)[0], 'detection results')
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        save_img_path = os.path.join(save_path, os.path.split(img_path)[1])
        f, p = detect_img(img_path, save_img_path)

        label_detect.delete(tk.ALL)
        label_detect.update()

        dimg = Image.open(save_img_path)
        dimg.thumbnail((480, 560))
        dimg = ImageTk.PhotoImage(image=dimg)
        label_detect.create_image((100, 50), anchor=NW, image=dimg)
        label_detect.update()

        label_detect.create_text((100, 450), anchor=NW,
                                 text='检测到发热异常,概率 {}%'.format(int(100 * p)) if f and p > 0 else '检测无异常')
        if f and p > 0: cnt_hot += 1
        label_detect.update()

    label_detect.delete(tk.ALL)
    label_detect.update()
    title = '发热异常/总检测图像:({}/{})'.format(cnt_hot, cnt)
    msg = '检测结果图像已存储到文件夹：\n \"' + save_path + '\" 中'

    label_detect.create_text((100, 200), anchor=NW, text=title)
    label_detect.create_text((100, 260), anchor=NW, text=msg, width=300)
    label_detect.update()
    if sys.platform == 'win32':
        if mb.askyesno(message='是否打开文件夹'):
            os.startfile(save_path)

    set_btn('normal')
    top.mainloop()


btn_open_img = Button(top, text="打开图像", command=open_img)
btn_open_img.place(relx=0.02, rely=0.)
label_open_img = Label(top, width=480, height=560, image=None)
label_open_img.place(relx=0., rely=0.05)

btn_rot = Button(top, text="旋转", command=rotate)
btn_rot.place(relx=0.1, rely=0.)
btn_det = Button(top, text="检测", command=detect)
btn_det.place(relx=0.15, rely=0.)

btn_dir = Button(top, text="选择文件夹并检测", command=open_dir_detect)
btn_dir.place(relx=0.4, rely=0.)

# label_detect = Label(top, width=420, height=490, image=None)
# label_detect.place(relx=0.5, rely=0.05)

label_result = Label(top, text="")
label_result.place(relx=0.55, rely=0.8)
label_count = Label(top, text="")
label_count.place(relx=0.55, rely=0.08)

label_detect = Canvas(top, width=480, height=600)
label_detect.place(relx=0.5, rely=0.05)

# btn_gpu=Checkbutton(top,text='使用gpu加速',variable=use_gpu,command=ck_gpu)
# btn_gpu.place(relx=0.85,rely=0.)

top.mainloop()
