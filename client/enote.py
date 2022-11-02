from tkinter import *
from communicate import *

from io import BytesIO
from datetime import date
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import filedialog

import os
import time
import uuid
import pickle
import requests
import webbrowser


# Path run script
PATH = os.path.dirname(os.path.realpath(__file__))

# Global variable
USERNAME = "ptan21"
NOTE_DATA = []
URL = ""
client = ""

#---------------------------------HANDLE FUNCTION----------------------------------------#


# Update note list
def update_note():
    textScroll.configure(state=NORMAL)
    textScroll.delete("1.0", END)

    for x in NOTE_DATA:
        # print(x)

        if x["type"] == "text":
            button = Button(textScroll, text=x["title"],
                            command=lambda x=x, frame=frame5: show_note_frame(frame, x), width=78, height=2)
        elif x["type"] == "image":
            button = Button(textScroll, text=x["title"],
                            command=lambda x=x, frame=frame6: show_note_frame(frame, x), width=78, height=2)
        else:
            button = Button(textScroll, text=x["title"],
                            command=lambda x=x, frame=frame7: show_note_frame(frame, x), width=78, height=2)

        textScroll.window_create(END, window=button)
        textScroll.insert(END, "\n")

    textScroll.configure(state="disabled")


# Login handle
def login():
    global USERNAME, NOTE_DATA
    _username = str(user_login.get())
    _password = str(password_login.get())

    cmd = "login"
    send_command(client, cmd)
    send_pickle(client, [_username, _password])

    msg = receive_message(client)
    if msg == "Login successfully!":
        USERNAME = _username

        lst = client.recv(2048)
        NOTE_DATA = pickle.loads(lst)
        show_frame(frame1)
        update_note()
    else:
        messagebox.showinfo("Login fail", msg)


# Signup handle
def signup():
    _fullname = str(full_name.get())
    _username = str(user_signup.get())
    _password = str(password_signup.get())

    print(_fullname, _username, _password)
    cmd = "signup"
    send_command(client, cmd)
    send_pickle(client, [_fullname, _username, _password])
    messagebox.showinfo("Sign up", receive_message(client))


# Send note to server
def send_note(client):
    global NOTE_DATA
    _title = str(titleNote1.get())
    _type = get_note_type()
    _today = str(date.today())
    client.send(_type.encode(FORMAT))

    if _type == "text":
        _text = str(textInput.get("1.0", END)).rstrip("\n")
        _author = USERNAME
        lst = [_author, _title, _text, _today]
        data = pickle.dumps(lst)
        client.sendall(data)
    elif _type == "image":
        _path = link_path1.get()
        _file = open(_path, "rb")
        _ext = get_file_type()

        file_size = os.path.getsize(_path)
        file_data = _file.read(file_size)

        # print(file_size)
        client.sendall(str(file_size).encode(FORMAT))
        client.sendall(file_data)

        _author = USERNAME
        lst = [_author, _title, _ext, _today]
        data = pickle.dumps(lst)
        client.sendall(data)
    else:
        _path = link_path1.get()
        _file = open(_path, "rb")
        # _ext = get_file_type()
        _filename = get_file_name()

        file_size = os.path.getsize(_path)
        file_data = _file.read(file_size)

        # print(file_size)
        client.sendall(str(file_size).encode(FORMAT))
        client.sendall(file_data)

        _author = USERNAME
        lst = [_author, _title, _filename, _today]
        data = pickle.dumps(lst)
        client.sendall(data)

    lst = client.recv(2048)
    NOTE_DATA = pickle.loads(lst)
    update_note()


# Get note type
def get_note_type():
    selected = int(radio.get())

    if selected == 1:
        return "text"
    elif selected == 2:
        return "image"
    else:
        return "file"


# Get file type extention
def get_file_type():
    file_name = link_path1.get()
    ext = ""
    for i in range(len(file_name) - 1, 0, -1):
        if file_name[i] != '.':
            ext = file_name[i] + ext
        else:
            break

    return ext


# Get file name
def get_file_name():
    file_name = link_path1.get()
    _name = ""
    for i in range(len(file_name) - 1, 0, -1):
        if file_name[i] != '\\':
            _name = file_name[i] + _name
        else:
            break

    return _name


# UI
def show_frame(frame):
    global text, text1
    text.config(state=NORMAL)
    text.delete('1.0', END)

    text1.config(state=NORMAL)
    text1.delete('1.0', END)

    text.config(state=DISABLED)
    text1.config(state=DISABLED)

    frame.tkraise()


def show_note_frame(frame, x):
    global _title, titleNote, text, URL
    _title.set(x["title"])
    _type.set(x["type"])
    _time.set(x["time"])

    if x["type"] == "text":
        text.config(state=NORMAL)
        text.insert(END, x["content"])
        text.config(state=DISABLED)

    elif x["type"] == "image":
        global img_note
        cmd = "request image"
        send_command(client, cmd)
        send_message(client, x["file"])

        imgURL = client.recv(2048).decode(FORMAT)
        URL = imgURL

        response = requests.get(imgURL)
        img = Image.open(BytesIO(response.content))
        img_note = ImageTk.PhotoImage(img)

        img_frame = Frame(frame6, bd=2, height=920,
                          width=440)  # relief=SUNKEN)

        img_frame.grid_rowconfigure(0, weight=1)
        img_frame.grid_columnconfigure(0, weight=1)

        xscrollbar = Scrollbar(img_frame, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=E+W)

        yscrollbar = Scrollbar(img_frame)
        yscrollbar.grid(row=0, column=1, sticky=N+S)

        canvas = Canvas(
            img_frame, bd=0, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, width=620, height=400)
        canvas.grid(row=0, column=0, sticky=N +
                    S+E+W)
        canvas.config(scrollregion=canvas.bbox(ALL))

        canvas.create_image(0, 0, image=img_note, anchor=NW)
        canvas.config(scrollregion=canvas.bbox(ALL))

        xscrollbar.config(command=canvas.xview)
        yscrollbar.config(command=canvas.yview)

        img_frame.place(x=25, y=190)

    else:
        cmd = "request file"
        send_command(client, cmd)
        send_message(client, x["file"])

        _url = client.recv(2048).decode(FORMAT)
        URL = _url
        # print(url)
        text1.config(state=NORMAL)
        file_name = x["file"].replace("/", "://")
        text1.insert(END, file_name)
        text1.config(state=DISABLED)

    frame.tkraise()

# Select type


def select_type():
    selected = int(radio.get())
    if selected > 1:
        link_path1.config(state=NORMAL)
        file_button1.config(state=NORMAL)

        textInput.config(state=NORMAL)
        textInput.delete('1.0', END)
        textInput.config(state=DISABLED)
    else:
        link_path1.delete(0, END)
        link_path1.config(state=DISABLED)
        file_button1.config(state=DISABLED)
        textInput.config(state=NORMAL)


root = Tk()
root.title('E-Note')
root.geometry('680x700')
root.configure(bg="white")
root.resizable(False, False)

url = "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
response = requests.get(url)
imgByte = Image.open(BytesIO(response.content))
img_note = ImageTk.PhotoImage(imgByte)

frame1 = Frame(root)
frame2 = Frame(root)
frame3 = Frame(root)

for frame in (frame1, frame2, frame3):
    frame.grid(row=0, column=0, sticky='nsew')


#####################################################################################################################################

frame1 = Frame(root, width=680, height=700, bg=('white'), padx=5, pady=5)
frame1.place(x=0, y=0)

heading = Label(frame1, text="E-NOTE", fg="#154f3c", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 18, 'bold'))
heading.place(x=300, y=10)


signout_button = Button(frame1,
                        width=10, pady=2, text='Log out', fg='white', bg="#12756a", border=0, cursor='hand2',
                        font=('Bahnschrift SemiLight SemiConde', 14), command=lambda: show_frame(frame2)).place(x=555, y=0)
####################################################################

frame_menu = Frame(frame1, width=620, height=500, bg=('#c9f5e8'))
frame_menu.place(x=30, y=130)

menu_heading = Label(frame_menu, text="Your notes", fg="#154f3c", bg="#c9f5e8",
                     font=('Bahnschrift SemiLight SemiConde', 18, 'bold'))
menu_heading.place(x=250, y=5)

####################################################################
# button

textScroll = Text(frame_menu,  bg="#12756a", width=72, height=30)
textScroll.place(x=20, y=50)

sb = Scrollbar(frame_menu, command=textScroll.yview)
sb.place(x=582, y=50, height=450)

textScroll.configure(yscrollcommand=sb.set)

# for i in range(6):
#     button = Button(textScroll, text="Hello",
#                     command=lambda: show_frame(frame5), width=78, height=2)
#     textScroll.window_create(END, window=button)
#     textScroll.insert(END, "\n")

# textScroll.configure(state="disabled")


####################################################################
# submit button_object
newnote_button = Button(frame1,
                        width=20, pady=3, text='Add new note', fg='white', bg="#12756a", border=0, cursor='hand2',
                        font=('Bahnschrift SemiLight SemiConde', 14), command=lambda: show_frame(frame4))
newnote_button.place(x=30, y=60)

#####################################################################################################################################
# login form

frame2 = Frame(root, width=680, height=700, bg=('white'))
frame2.place(x=0, y=0)

####################################################################################
frame_slogan = Frame(frame2, width=680, height=320, bg="#98ebdc")
frame_slogan.place(x=00, y=000)

appname = Label(frame_slogan, text="E-NOTE", fg="white", bg="#98ebdc",
                font=('Bahnschrift SemiLight SemiConde', 40, 'bold'))
appname.place(x=60, y=30)

slogan = Label(frame_slogan, text="creating your own Emotional Note", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 30, "italic"))
slogan.place(x=60, y=100)

intro1 = Label(frame_slogan, text="A product from Group ...", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 20))
intro1.place(x=375, y=200)

intro2 = Label(frame_slogan, text="Computer Network-21CLC07", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 20))
intro2.place(x=350, y=250)
####################################################################################
frame_login = Frame(frame2, width=630, height=300, bg="white")
frame_login.place(x=10, y=330)

sign_up_img = PhotoImage(file=PATH + '/img/photo_note_2.png')
Label(frame_login, image=sign_up_img, bg="white").place(x=10, y=15)


heading = Label(frame_login, text="Log in", fg="#86d9cf", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 23,  'bold'))
heading.place(x=320, y=40)


####################################################################
# username_part

def on_enter1(e):
    user_login.delete(0, 'end')


def on_leave1(e):
    name = user_signup.get()
    if name == '':
        user_login.insert(0, 'Username')


user_login = Entry(frame_login, width=25, fg='black', border=0, bg="white",
                   font=('Bahnschrift SemiLight SemiConde', 11))
user_login.place(x=320, y=110)
user_login.insert(0, 'Username')
user_login.bind('<FocusIn>', on_enter1)
user_login.bind('<FocusOut>', on_leave1)

Frame(frame_login, width=290, height=2, bg='black').place(x=320, y=140)


####################################################################
# password_part

def on_enter2(e):
    password_login.delete(0, 'end')


def on_leave2(e):
    name = password_login.get()
    if name == '':
        password_login.insert(0, 'Password')


password_login = Entry(frame_login, width=25, fg='black', border=0, bg="white",
                       font=('Bahnschrift SemiLight SemiConde', 11))
password_login.place(x=320, y=160)
password_login.insert(0, 'Password')
password_login.bind('<FocusIn>', on_enter2)
password_login.bind('<FocusOut>', on_leave2)

Frame(frame_login, width=290, height=2, bg='black').place(x=320, y=190)
####################################################################

Button(frame_login,
       width=35, pady=7, text='Log in', fg='white', bg="#12756a", border=0,
       font=('Bahnschrift SemiLight SemiConde', 12), command=login).place(x=320, y=220)
label = Label(frame_login, text="Don't have an account?", fg='black',
              bg='white', font=('Bahnschrift SemiLight SemiConde', 12))
label.place(x=370, y=270)

sign_up = Button(frame_login, width=6, text='Sign up', bg="white", fg='#12756a', border=0, cursor='hand2',
                 font=('Bahnschrift SemiLight SemiConde', 12), command=lambda: show_frame(frame3))
sign_up.place(x=520, y=268)

#####################################################################################################################################
# sign up form

frame3 = Frame(root, width=680, height=700, bg=('white'))
frame3.place(x=0, y=0)


frame_slogan = Frame(frame3, width=680, height=320, bg="#98ebdc")
frame_slogan.place(x=00, y=000)

appname = Label(frame_slogan, text="E-NOTE", fg="white", bg="#98ebdc",
                font=('Bahnschrift SemiLight SemiConde', 40, 'bold'))
appname.place(x=60, y=30)

slogan = Label(frame_slogan, text="creating your own Emotional Note", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 30, "italic"))
slogan.place(x=60, y=100)

intro1 = Label(frame_slogan, text="A product from Group ...", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 20))
intro1.place(x=375, y=200)

intro2 = Label(frame_slogan, text="Computer Network-21CLC07", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 20))
intro2.place(x=350, y=250)


####################################################################################
frame_signup1 = Frame(frame3, width=630, height=300, bg="white")
frame_signup1.place(x=10, y=330)

img = PhotoImage(file=PATH + '/img/photo_note_2.png')
Label(frame_signup1, image=img, bg="white").place(x=10, y=20)

frame_signup = Frame(frame_signup1, width=300, height=390, bg="white")
frame_signup.place(x=350, y=10)

heading = Label(frame_signup, text="Sign up", fg="#86d9cf", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 23, 'bold'))
heading.place(x=0, y=0)

####################################################################
# name_part


def on_enter3(e):
    full_name.delete(0, 'end')


def on_leave3(e):
    name = full_name.get()
    if name == '':
        full_name.insert(0, 'Fullname')


full_name = Entry(frame_signup, width=25, fg='black', border=0, bg="white",
                  font=('Bahnschrift SemiLight SemiConde', 11))
full_name.place(x=0, y=60)
full_name.insert(0, 'Fullname')
full_name.bind('<FocusIn>', on_enter3)
full_name.bind('<FocusOut>', on_leave3)


Frame(frame_signup, width=290, height=2, bg='black').place(x=0, y=90)

####################################################################
# username_part


def on_enter4(e):
    user_signup.delete(0, 'end')


def on_leave4(e):
    name = user_signup.get()
    if name == '':
        user_signup.insert(0, 'Username')


user_signup = Entry(frame_signup, width=25, fg='black', border=0, bg="white",
                    font=('Bahnschrift SemiLight SemiConde', 11))
user_signup.place(x=0, y=110)
user_signup.insert(0, 'Username')
user_signup.bind('<FocusIn>', on_enter4)
user_signup.bind('<FocusOut>', on_leave4)

Frame(frame_signup, width=290, height=2, bg='black').place(x=0, y=140)


####################################################################
# password_part

def on_enter5(e):
    password_signup.delete(0, 'end')


def on_leave5(e):
    name = password_signup.get()
    if name == '':
        password_signup.insert(0, 'Password')


password_signup = Entry(frame_signup, width=25, fg='black', border=0, bg="white",
                        font=('Bahnschrift SemiLight SemiConde', 11))
password_signup.place(x=0, y=160)
password_signup.insert(0, 'Password')
password_signup.bind('<FocusIn>', on_enter5)
password_signup.bind('<FocusOut>', on_leave5)

Frame(frame_signup, width=290, height=2, bg='black').place(x=0, y=190)
####################################################################

Button(frame_signup,
       width=35, pady=7, text='Sign up', fg='white', bg="#12756a", border=0,
       font=('Bahnschrift SemiLight SemiConde', 12), command=signup).place(x=2, y=210)
label = Label(frame_signup, text="Already have an account?", fg='black',
              bg='white', font=('Bahnschrift SemiLight SemiConde', 12))
label.place(x=40, y=260)

sign_up = Button(frame_signup, width=6, text='Log in', bg="white", fg='#12756a', border=0, cursor='hand2',
                 font=('Bahnschrift SemiLight SemiConde', 12), command=lambda: show_frame(frame2))
sign_up.place(x=205, y=258)

#####################################################################################################################################
# new note form

frame4 = Frame(root, width=680, height=700, bg=('white'), padx=5, pady=5)
frame4.place(x=0, y=0)

####################################################################
# page name

heading = Label(frame4, text="A NEW NOTE", fg="#154f3c", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 18, 'bold'))
heading.place(x=270, y=10)

back_button = Button(frame4,
                     width=5, pady=2, text='Back', fg='white', bg="#12756a", border=0, cursor='hand2',
                     font=('Bahnschrift SemiLight SemiConde', 14), command=lambda: show_frame(frame1)).place(x=600, y=0)
####################################################################
# title Note name


heading1 = Label(frame4, text="Note title : ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'))
heading1.place(x=30, y=40)


def enter_type(e):
    pass
    # titleNote1.delete(0, 'end')


def leave_type(e):
    # name = titleNote1.get()
    # if name == '':
    #     titleNote1.insert(0, 'type here')
    pass


titleNote1 = Entry(frame4, width=30, fg='#048a49', border=0, bg="white",
                   font=('Bahnschrift SemiLight SemiConde', 14))
titleNote1.place(x=140, y=42)
# titleNote1.insert(0, 'type here')
titleNote1.bind('<FocusIn>', enter_type)
titleNote1.bind('<FocusOut>', leave_type)

Frame(frame4, width=290, height=2, bg='black').place(x=140, y=72)


heading2 = Label(frame4, text="Type of note : ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'),)
heading2.place(x=30, y=115)


radio = IntVar()
check1 = Radiobutton(frame4, text="Text", cursor='hand2', fg="#048a49",
                     font=('Bahnschrift SemiLight SemiConde', 14), variable=radio,
                     value=1, command=select_type)
check1.select()
check1.place(x=180, y=114)

check2 = Radiobutton(frame4, text="Image", cursor='hand2', fg="#048a49",
                     font=('Bahnschrift SemiLight SemiConde', 14),  variable=radio,
                     value=2, command=select_type)
check2.place(x=290, y=114)

check3 = Radiobutton(frame4, text="File", cursor='hand2', fg="#048a49",
                     font=('Bahnschrift SemiLight SemiConde', 14),  variable=radio,
                     value=3, command=select_type)
check3.place(x=400, y=114)

####################################################################
# txt area

textInput = Text(frame4, height=15, width=67,
                 bg=('#b3f2dd'), font=('Bahnschrift SemiLight SemiConde', 14),
                 padx=10, pady=10)
textInput.place(x=30, y=170)


####################################################################
# file area

def open_file():
    file = filedialog.askopenfile(mode='r', filetypes=[('All Files', '*.*')])
    if file:
        filepath = os.path.abspath(file.name)
        link_path1.delete(0, END)  # Remove current text in entry
        link_path1.insert(0, filepath)  # Insert the 'path'


heading3 = Label(frame4, text="File link : ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'))
heading3.place(x=30, y=570)

link_path1 = Entry(frame4, width=47, fg='white', bg="#12756a", border=0, cursor='hand2',
                   font=('Bahnschrift SemiLight SemiConde', 14))
link_path1.place(x=128, y=571, width=428, height=35.5)

file_button1 = Button(frame4, text='Choose file', fg='white', bg="#12756a", border=0, cursor='hand2',
                      font=('Bahnschrift SemiLight SemiConde', 14),
                      command=open_file
                      )
file_button1.place(x=561, y=571)


####################################################################
# submit button_object
link_path1.config(state=DISABLED)
file_button1.config(state=DISABLED)


def submit_button():
    # inputTXT = text.get("1.0",END)
    # titleName = titleNote.get()

    send_command(client, "send_note")
    send_note(client)

    titleNote1.config(state=DISABLED)
    textInput.config(state=DISABLED)
    link_path1.config(state=DISABLED)
    file_button1.config(state=DISABLED)

    time.sleep(2)
    titleNote1.config(state=NORMAL)
    textInput.config(state=NORMAL)
    link_path1.config(state=NORMAL)
    file_button1.config(state=NORMAL)

    titleNote1.delete(0, END)
    textInput.delete('1.0', END)
    link_path1.delete(0, END)

    check1.select()
    link_path1.config(state=DISABLED)
    file_button1.config(state=DISABLED)

    messagebox.showinfo("Create note", "Note was saved")


submit_button = Button(frame4,
                       width=20, pady=3, text='Submit', fg='white', bg="#12756a", border=0, cursor='hand2',
                       font=('Bahnschrift SemiLight SemiConde', 14),
                       command=submit_button)
submit_button.place(x=250, y=640)

#####################################################################################################################################
# old note form

frame5 = Frame(root, width=680, height=700, bg=('white'), padx=5, pady=5)
frame5.place(x=0, y=0)


####################################################################
# page name

heading = Label(frame5, text="E-NOTE", fg="#154f3c", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 18, 'bold'))
heading.place(x=300, y=10)

back_button = Button(frame5,
                     width=5, pady=2, text='Back', fg='white', bg="#12756a", border=0, cursor='hand2',
                     font=('Bahnschrift SemiLight SemiConde', 14), command=lambda: show_frame(frame1)).place(x=600, y=0)

####################################################################
# title Note name

heading1 = Label(frame5, text="Note title: ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'))
heading1.place(x=30, y=40)

_title = StringVar()
_type = StringVar()
_time = StringVar()

titleNote2 = Entry(frame5, width=29, fg='#048a49', border=0, bg="white",
                   font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_title)

titleNote2.place(x=140, y=42)
titleNote2.config(state=DISABLED)


Frame(frame5, width=290, height=2, bg='black').place(x=140, y=72)

####################################################################
# type of note
services = []

heading2 = Label(frame5, text="Type : ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'),)
heading2.place(x=30, y=115)

typeNote = Entry(frame5, width=15, fg='#048a49', border=0, bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_type)
typeNote.place(x=90, y=112)
typeNote.configure(state="disabled")

Frame(frame5, width=150, height=2, bg='black').place(x=90, y=142)

headingTime = Label(frame5, text="Time: ", fg="#048a49", bg="white",
                    font=('Bahnschrift SemiLight SemiConde', 14, 'bold'),)
headingTime.place(x=300, y=115)

timeNote = Entry(frame5, width=15, fg='#048a49', border=0, bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_time)
timeNote.place(x=360, y=112)
timeNote.configure(state="disabled")

Frame(frame5, width=150, height=2, bg='black').place(x=360, y=142)

####################################################################
# txt area

text = Text(frame5, height=15, width=67,
            bg=('#b3f2dd'), font=('Bahnschrift SemiLight SemiConde', 14),
            padx=10, pady=10)
text.place(x=30, y=190)
####################################################################
# download button_object


def open_url():
    webbrowser.open_new_tab(URL)


def save_text():
    file_name = str(uuid.uuid4()) + ".txt"
    file = open(PATH + "/download/" + file_name, "wt")
    txt = str(text.get("1.0", END))
    file.write(txt)
    messagebox.showinfo("Download text", "Your file is in download folder")


download_button1 = Button(frame5,
                          width=20, pady=3, text='Download file', fg='white', bg="#12756a", border=0, cursor='hand2',
                          font=('Bahnschrift SemiLight SemiConde', 14), command=save_text)
download_button1.place(x=250, y=600)

#####################################################################################################################################
# old note form : img

frame6 = Frame(root, width=680, height=700, bg=('white'), padx=5, pady=5)
frame6.place(x=0, y=0)


####################################################################
# page name

heading = Label(frame6, text="E-NOTE", fg="#154f3c", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 18, 'bold'))
heading.place(x=300, y=10)

back_button = Button(frame6,
                     width=5, pady=2, text='Back', fg='white', bg="#12756a", border=0, cursor='hand2',
                     font=('Bahnschrift SemiLight SemiConde', 14), command=lambda: show_frame(frame1)).place(x=600, y=0)

####################################################################
# title Note name
heading1 = Label(frame6, text="Note title: ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'))
heading1.place(x=30, y=40)

titleNote3 = Entry(frame6, width=29, fg='#048a49', border=0, bg="white",
                   font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_title)

titleNote3.place(x=140, y=42)
titleNote3.config(state=DISABLED)


Frame(frame6, width=290, height=2, bg='black').place(x=140, y=72)

####################################################################
# type of note
services = []

heading2 = Label(frame6, text="Type : ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'),)
heading2.place(x=30, y=115)

typeNote = Entry(frame6, width=15, fg='#048a49', border=0, bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_type)
typeNote.place(x=90, y=112)
typeNote.configure(state="disabled")

Frame(frame6, width=150, height=2, bg='black').place(x=90, y=142)

headingTime = Label(frame6, text="Time: ", fg="#048a49", bg="white",
                    font=('Bahnschrift SemiLight SemiConde', 14, 'bold'),)
headingTime.place(x=300, y=115)

timeNote = Entry(frame6, width=15, fg='#048a49', border=0, bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_time)
timeNote.place(x=360, y=112)
timeNote.configure(state="disabled")

Frame(frame6, width=150, height=2, bg='black').place(x=360, y=142)

####################################################################
# download button_object


download_button2 = Button(frame6,
                          width=20, pady=3, text='Download file', fg='white', bg="#12756a", border=0, cursor='hand2',
                          font=('Bahnschrift SemiLight SemiConde', 14), command=open_url)
download_button2.place(x=250, y=640)

#####################################################################################################################################
# old note form : file

frame7 = Frame(root, width=680, height=700, bg=('white'), padx=5, pady=5)
frame7.place(x=0, y=0)

####################################################################
# page name

heading = Label(frame7, text="E-NOTE", fg="#154f3c", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 18, 'bold'))
heading.place(x=300, y=10)

back_button = Button(frame7,
                     width=5, pady=2, text='Back', fg='white', bg="#12756a", border=0, cursor='hand2',
                     font=('Bahnschrift SemiLight SemiConde', 14), command=lambda: show_frame(frame1)).place(x=600, y=0)

####################################################################
# title Note name
heading1 = Label(frame7, text="Note title: ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'))
heading1.place(x=30, y=40)

titleNote4 = Entry(frame7, width=29, fg='#048a49', border=0, bg="white",
                   font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_title)

titleNote4.place(x=140, y=42)
titleNote4.config(state=DISABLED)


Frame(frame7, width=290, height=2, bg='black').place(x=140, y=72)

####################################################################
# type of note
services = []

heading2 = Label(frame7, text="Type : ", fg="#048a49", bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'),)
heading2.place(x=30, y=115)

typeNote = Entry(frame7, width=15, fg='#048a49', border=0, bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_type)
typeNote.place(x=90, y=112)
typeNote.configure(state="disabled")

Frame(frame7, width=150, height=2, bg='black').place(x=90, y=142)

headingTime = Label(frame7, text="Time: ", fg="#048a49", bg="white",
                    font=('Bahnschrift SemiLight SemiConde', 14, 'bold'),)
headingTime.place(x=300, y=115)

timeNote = Entry(frame7, width=15, fg='#048a49', border=0, bg="white",
                 font=('Bahnschrift SemiLight SemiConde', 14, 'bold'), textvariable=_time)
timeNote.place(x=360, y=112)
timeNote.configure(state="disabled")

Frame(frame7, width=150, height=2, bg='black').place(x=360, y=142)

####################################################################
# txt area

text1 = Text(frame7, height=3, width=67,
             bg=('#b3f2dd'), font=('Bahnschrift SemiLight SemiConde', 14),
             padx=10, pady=10)
text1.place(x=30, y=190)
text1.configure(state="disabled")

####################################################################
# download button_object


download_button3 = Button(frame7,
                          width=20, pady=3, text='Download file', fg='white', bg="#12756a", border=0, cursor='hand2',
                          font=('Bahnschrift SemiLight SemiConde', 14), command=open_url)
download_button3.place(x=250, y=600)


#####################################################################################################################################
# ip/port form

frame8 = Frame(root, width=680, height=700, bg=('white'))
frame8.place(x=0, y=0)

####################################################################################

frame_slogan = Frame(frame8, width=680, height=320, bg="#98ebdc")
frame_slogan.place(x=00, y=000)

appname = Label(frame_slogan, text="E-NOTE", fg="white", bg="#98ebdc",
                font=('Bahnschrift SemiLight SemiConde', 40, 'bold'))
appname.place(x=60, y=30)

slogan = Label(frame_slogan, text="creating your own Emotional Note", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 30, "italic"))
slogan.place(x=60, y=100)

intro1 = Label(frame_slogan, text="A product from Group ...", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 20))
intro1.place(x=375, y=200)

intro2 = Label(frame_slogan, text="Computer Network-21CLC07", fg="#145243", bg="#98ebdc",
               font=('Bahnschrift SemiLight SemiConde', 20))
intro2.place(x=350, y=250)
####################################################################################

frame_port = Frame(frame8, width=630, height=300, bg="white")
frame_port.place(x=10, y=330)

img1 = PhotoImage(file=PATH + '/img/photo_note_2.png')
Label(frame_port, image=img1, bg="white").place(x=10, y=15)


heading = Label(frame_port, text="Connecting to Server", fg="#86d9cf", bg="white",
                font=('Bahnschrift SemiLight SemiConde', 23,  'bold'))
heading.place(x=320, y=40)


####################################################################
# username_part

def on_enter1(e):
    ipAdd.delete(0, 'end')


def on_leave1(e):
    name = ipAdd.get()
    if name == '':
        ipAdd.insert(0, 'IP Address')


ipAdd = Entry(frame_port, width=25, fg='black', border=0, bg="white",
              font=('Bahnschrift SemiLight SemiConde', 11))
ipAdd.place(x=320, y=110)
ipAdd.insert(0, 'IP Address')
ipAdd.bind('<FocusIn>', on_enter1)
ipAdd.bind('<FocusOut>', on_leave1)

Frame(frame_port, width=290, height=2, bg='black').place(x=320, y=140)


####################################################################
# password_part

def on_enter2(e):
    portnumber.delete(0, 'end')


def on_leave2(e):
    name = portnumber.get()
    if name == '':
        portnumber.insert(0, 'Port number')


portnumber = Entry(frame_port, width=25, fg='black', border=0, bg="white",
                   font=('Bahnschrift SemiLight SemiConde', 11))
portnumber.place(x=320, y=160)
portnumber.insert(0, 'Port number')
portnumber.bind('<FocusIn>', on_enter2)
portnumber.bind('<FocusOut>', on_leave2)

Frame(frame_port, width=290, height=2, bg='black').place(x=320, y=190)
####################################################################


def get_connection():
    global client

    PORT = int(portnumber.get())
    SERVER = str(ipAdd.get())
    ADDR = (SERVER, PORT)

    client = connect_server(ADDR)

    if client:
        show_frame(frame2)
    else:
        messagebox.showinfo("Try again", "Server not found!")


Button(frame_port,
       width=35, pady=7, text='Connect', fg='white', bg="#12756a", border=0,
       font=('Bahnschrift SemiLight SemiConde', 12), command=get_connection).place(x=320, y=220)


if __name__ == '__main__':
    show_frame(frame8)

    root.mainloop()
