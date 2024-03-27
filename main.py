import os.path
import datetime
import subprocess
import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import util

import mysql.connector

import random
import smtplib
from email.message import EmailMessage
from tkinter import ttk
import re


class LivenessDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def detect_liveness(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) < 2:
                return False
        return True

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.title('face recognition')
        self.main_window.geometry("1200x520")
        self.main_window.configure(bg='green')

        self.text_label_register_new_user = util.get_text_label(self.main_window, '          Student Portal for Meru \n University of Science & Technology')
        self.text_label_register_new_user.place(x=700, y=20)


        self.text_label_register_new_user = util.get_text_label(self.main_window, 'Login As Administrator')
        self.text_label_register_new_user.place(x=795, y=140)
        self.login_button_main_window = util.get_button(self.main_window, 'ADMIN', 'green', self.login_admin)
        self.login_button_main_window.place(x=800, y=180)


        self.text_label_register_new_user = util.get_text_label(self.main_window, 'Login As Student?')
        self.text_label_register_new_user.place(x=795, y=320)
        self.login_button_main_window = util.get_button(self.main_window, 'LOGIN', 'green', self.login_new)
        self.login_button_main_window.place(x=800, y=360)

        self.text_label_register_new_user = util.get_text_label(self.main_window, "You don't have an account?")
        self.text_label_register_new_user.place(x=795, y=410)
        self.register_new_user_button_main_window = util.get_button(self.main_window, 'REGISTER', 'red',self.register_new_user, fg='white')
        self.register_new_user_button_main_window.place(x=795, y=450)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def login(self):
        liveness_detector = LivenessDetector()
        while True:
            unknown_img_path = './.tmp.jpg'
            cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

            if not liveness_detector.detect_liveness(self.most_recent_capture_arr):
                util.msg_box('Error', 'This is fake face. Please use a real face.')
                continue

            output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
            name = output.split(',')[1][:-5]
            if name in ['unknown_person', 'no_persons_found']:
                util.msg_box('Error', 'Unknown user Please register or try again')
                continue
            else:
                util.msg_box('Welcome back !', 'Welcome, {}.'.format(name))
                self.face_window.destroy()
                self.home_page(name)
            break  
        
        os.remove(unknown_img_path)
    
    def show_face_window(self):
        self.main_window.withdraw()
        self.face_window = tk.Toplevel(self.main_window)
        self.face_window.geometry("500x500")
        self.face_window.configure(bg='green')
        self.face_window.title("Face Phase 3")

        self.webcam_label = util.get_img_label(self.face_window)
        self.webcam_label.place(x=10, y=0, width=450, height=400)

        self.add_webcam(self.webcam_label)
        self.login()
    

    def home_page(self, name):
        self.home_page_window = tk.Toplevel(self.main_window)
        self.home_page_window.geometry("1200x520")
        self.home_page_window.configure(bg='yellow')
        self.home_page_window.title("Home Page")

        name_label = tk.Label(self.home_page_window, text="Welcome: {}".format(name), font=("Arial", 30), fg='green',bg='yellow')
        name_label.pack(pady=20)
        logout_button = tk.Button(self.home_page_window, text="Logout", bg='red', command=self.logout)
        logout_button.pack(pady=10)

    def logout(self):
        self.keep_processing = True
        self.home_page_window.destroy()
        self.login_new_window.destroy()
        self.main_window.deiconify()


    def login_admin(self):
        self.admin_window = tk.Toplevel(self.main_window)
        self.admin_window.geometry("500x350+300+100")
        self.admin_window.configure(bg='yellow')
        self.admin_window.title("Admin Login")

        self.show_password_button = util.get_button(self.admin_window, 'Show Password', 'red',self.show_password1)
        self.show_password_button.place(x=140, y=190)

        self.accept_button_admin_window = util.get_button(self.admin_window, 'ADMINISTRATOR', 'green', self.see_users)
        self.accept_button_admin_window.place(x=140, y=250)

        self.text_label_admin = util.get_text_label1(self.admin_window, 'Username:')
        self.text_label_admin.place(x=30, y=100)
        self.entry_text_admin_name = util.get_entry_text(self.admin_window)
        self.entry_text_admin_name.place(x=170, y=110)

        self.text_label_admin = util.get_text_label1(self.admin_window, 'Password:')
        self.text_label_admin.place(x=30, y=150)
        self.entry_text_admin_password = util.get_entry_text1(self.admin_window, show='*')
        self.entry_text_admin_password.place(x=170, y=160)

        self.text_label_admin = util.get_text_label1(self.admin_window, 'ADMIN LOGIN PAGE')
        self.text_label_admin.place(x=130, y=50)
    
    def see_users(self):
        if self.entry_text_admin_name.get()=='' or self.entry_text_admin_password.get()=='':
            util.msg_box("Error","Admin Username or Password Can't be Empty")
        else:
            connecton = mysql.connector.connect(host='localhost', user='root', password='', database='administrator')
            c = connecton.cursor()

            username = self.entry_text_admin_name.get()
            password = self.entry_text_admin_password.get()

            query="SELECT * FROM admin WHERE username = %s AND password = %s"
            c.execute(query, (username, password))
            result = c.fetchone()

            if result:
                util.msg_box("Success","                    Welcome Again \n Click Ok to see the Registered Students ")
                self.users()
                self.fetch_data()
            else:
                util.msg_box("Error","You Have Entered Wrong Username Or Password")
    def show_password1(self):
        password = self.entry_text_admin_password.get()
        self.entry_text_admin_password.configure(show='')
        self.entry_text_admin_password.delete(0, tk.END)
        self.entry_text_admin_password.insert(0, password)
        self.admin_window.after(2000, lambda: self.entry_text_admin_password.configure(show='*'))
    
    def users(self):
        self.users_window = tk.Toplevel(self.main_window)
        self.users_window.geometry("1020x520")
        self.users_window.configure(bg='yellow')
        self.users_window.title("Admin Login")

        label = tk.Label(self.users_window, text="All REGISTERED STUDENTS", font=("Arial", 16), bg="yellow", fg="green")
        label.pack(pady=5)
        style = ttk.Style()
        style.configure("Treeview", background="green", foreground="white")

        self.data_treeview = ttk.Treeview(self.users_window, columns=("DeRegister","ID", "Full Name", "Phone Number", "Student Email"))
        self.data_treeview.heading("#0", text="Row")
        self.data_treeview.heading("DeRegister", text="DeRegister")
        self.data_treeview.heading("ID", text="ID")
        self.data_treeview.heading("Full Name", text="Full Name")
        self.data_treeview.heading("Phone Number", text="Phone Number")
        self.data_treeview.heading("Student Email", text="Student Email")

        self.data_treeview.column("#0", width=0, stretch=tk.NO)
        self.data_treeview.tag_bind("DeRegister", "<ButtonRelease-1>", self.delete_row)
        self.data_treeview.pack(pady=10)
    def fetch_data(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="face"
            )
            cursor = connection.cursor()
            query = "SELECT * FROM faces"
            cursor.execute(query)
            rows = cursor.fetchall()
            for i, row in enumerate(rows, start=1):
                self.data_treeview.insert("", i, values=(f"DeRegister ",) + row, tags=("DeRegister",))

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            cursor.close()
            connection.close()
    def delete_row(self, event):
        selected_item = self.data_treeview.selection()
        if selected_item:
            item = selected_item[0]
            row_values = self.data_treeview.item(item, "values")
            delete = row_values[1]  
            self.data_treeview.delete(item)
        if self.delete_from_database(delete):
            util.msg_box("Success", "Successfully De-Registered One Student!")

    def delete_from_database(self, delete):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="face"
            )
            cursor = connection.cursor()
            delete_query = f"DELETE FROM faces WHERE id = {delete}"
            cursor.execute(delete_query)
            connection.commit()

            return True 

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False 

        finally:
            cursor.close()
            connection.close()


    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520")
        self.register_new_user_window.configure(bg='green')
        self.register_new_user_window.title("User Registration Phase")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green',self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=850, y=320)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again','red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=850, y=370)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'FullName:')
        self.text_label_register_new_user.place(x=750, y=70)
        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=890, y=80)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Telephone:')
        self.text_label_register_new_user.place(x=750, y=120)
        self.entry_text_register_new_telephone = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_telephone.place(x=890, y=130)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Email:')
        self.text_label_register_new_user.place(x=750, y=170)
        self.entry_text_register_new_email = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_email.place(x=890, y=180)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Password:')
        self.text_label_register_new_user.place(x=750, y=220)
        self.entry_text_register_new_password = util.get_entry_text1(self.register_new_user_window, show='*')
        self.entry_text_register_new_password.place(x=890, y=230)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Confirm:')
        self.text_label_register_new_user.place(x=750, y=270)
        self.entry_text_register_new_confirm = util.get_entry_text1(self.register_new_user_window, show='*')
        self.entry_text_register_new_confirm.place(x=890, y=280)


        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'CREATE AN ACCOUNT')
        self.text_label_register_new_user.place(x=800, y=10)


    def login_new(self):
        self.login_new_window = tk.Toplevel(self.main_window)
        self.login_new_window.geometry("500x350+300+100")
        self.login_new_window.configure(bg='green')
        self.login_new_window.title("Login Phase 1")

        self.show_password_button = util.get_button(self.login_new_window, 'Show Password', 'red',self.show_password)
        self.show_password_button.place(x=140, y=190)

        self.accept_button_login_new_window = util.get_button(self.login_new_window, 'Accept', 'green', self.send_otp)
        self.accept_button_login_new_window.place(x=140, y=250)

        self.text_label_login_new = util.get_text_label(self.login_new_window, 'Email:')
        self.text_label_login_new.place(x=30, y=100)
        self.entry_text_register_new_email = util.get_entry_text(self.login_new_window)
        self.entry_text_register_new_email.place(x=170, y=110)

        self.text_label_login_new = util.get_text_label(self.login_new_window, 'Password:')
        self.text_label_login_new.place(x=30, y=150)
        self.entry_text_register_new_password = util.get_entry_text1(self.login_new_window, show='*')
        self.entry_text_register_new_password.place(x=170, y=160)

        self.text_label_login_new = util.get_text_label(self.login_new_window, 'LOGIN PAGE')
        self.text_label_login_new.place(x=130, y=50)
    
    def show_password(self):
        password = self.entry_text_register_new_password.get()
        self.entry_text_register_new_password.configure(show='')
        self.entry_text_register_new_password.delete(0, tk.END)
        self.entry_text_register_new_password.insert(0, password)
        self.login_new_window.after(2000, lambda: self.entry_text_register_new_password.configure(show='*'))


    def send_otp(self):
        email = self.entry_text_register_new_email.get()
        password = self.entry_text_register_new_password.get()

        if not email or not password:
            util.msg_box('Error','Email And Password Cannot be Empty')
            return
        if self.check_credentials(email, password):
            otp = self.generate_otp()
            self.send_otp_email(email, otp)
            self.show_otp_window(otp)
        else:
            util.msg_box("Error","Incorrect Email or Password,\n Please try again!")
    def generate_otp(self):
        return ''.join(random.choice('0123456789') for _ in range(6))

    def check_credentials(self, email, password):
        try:
            db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="face"
            )
            cursor = db_connection.cursor()
            query = "SELECT * FROM faces WHERE email = %s AND password = %s"
            cursor.execute(query, (email,password))
            result = cursor.fetchone()

            cursor.close()
            db_connection.close()

            return result is not None
        except Exception as e:
            util.msg_box("Error",f"Error checking credentials: {e}")
            return False
    def send_otp_email(self, email, otp):
        sender_email = "joelzablon31@gmail.com"
        sender_password = "tmhbqbnzqwrfqiog"

        message = EmailMessage()
        message.set_content(f"Verification OTP is: {otp}")
        message["Subject"] = "Your Verification OTP for Login"
        message["From"] = sender_email
        message["To"] = email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
                util.msg_box("Success", "OTP sent successfully")
        except Exception as e:
            util.msg_box("Error",f"Error sending OTP: {e}")
            util.msg_box("Error", "Failed to send OTP. Please try again.")


    def show_otp_window(self, otp):
        otp_new_window = tk.Toplevel(self.main_window)
        otp_new_window.geometry("350x300")
        otp_new_window.configure(bg='green')
        otp_new_window.title("OTP Phase 2")

        accept_button_otp_new_window = util.get_button(otp_new_window, text="Verify OTP", command=lambda: self.verify_otp(entry_otp_new_email, otp_new_window, otp), color='red')
        accept_button_otp_new_window.place(x=50, y=150)

        label_otp_new = util.get_text_label(otp_new_window, 'Enter OTP:')
        label_otp_new.place(x=30, y=80)
        entry_otp_new_email = tk.Entry(otp_new_window)
        entry_otp_new_email.place(x=180, y=90)

        label_login_new = util.get_text_label(otp_new_window, 'OTP PHASE')
        label_login_new.place(x=100, y=10)

    def verify_otp(self, entry_otp_new_email, otp_new_window, otp):
        entered_otp = entry_otp_new_email.get()

        if entered_otp == otp:
            otp_new_window.destroy()
            self.login_new_window.destroy()
            self.show_face_window()
        else:
            util.msg_box("Error","Incorrect OTP, \n Please try again!")


    def login1(self):
        util.msg_box("Success","Login successfully!")

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        if self.entry_text_register_new_user.get() == '' or self.entry_text_register_new_telephone.get() == '' or self.entry_text_register_new_email.get() == '' or self.entry_text_register_new_password.get() == '' or self.entry_text_register_new_confirm.get() == '':
            util.msg_box('Error', 'All Fields Are Required')
            return
        if not re.match("^[a-zA-Z]+( [a-zA-Z]+)+$", self.entry_text_register_new_user.get()):
            util.msg_box('Error', 'Username Must Contain Only Letters and At Least Two Words')
            return
        if self.entry_text_register_new_password.get() != self.entry_text_register_new_confirm.get():
            util.msg_box('Error', 'Password Must Match')
            return
        if len(self.entry_text_register_new_password.get()) <= 5:
            util.msg_box('Error', 'Password Must be Atleast 6 Characters')
        if not self.entry_text_register_new_email.get().endswith('@gmail.com'):
            util.msg_box('Error', 'Email Must Be of the Form example@gmail.com')
            return
        if not (re.search("[@_!#$%^&*()<>?/\|}{~:]", self.entry_text_register_new_password.get()) and
                any(char.isdigit() for char in self.entry_text_register_new_password.get()) and
                re.search("[a-z]", self.entry_text_register_new_password.get()) and
                re.search("[A-Z]", self.entry_text_register_new_password.get())):
            util.msg_box('Error', 'Password Must Contain Special Characters, Numbers, Small and Capital Letters')
            return
        else:
            connecton = mysql.connector.connect(host='localhost', user='root', password='', database='face')
            c = connecton.cursor()

            name = self.entry_text_register_new_user.get()
            phone = self.entry_text_register_new_telephone.get()
            email = self.entry_text_register_new_email.get()
            password = self.entry_text_register_new_password.get()

            c.execute("SELECT * FROM faces WHERE email = %s", (email,))
            existing_email = c.fetchone()
            if existing_email:
                util.msg_box('Error','Email already exists in the database')
                return

            c.execute("SELECT * FROM faces WHERE name = %s", (name,))
            existing_name = c.fetchone()
            if existing_name:
                util.msg_box('Error', 'Name already exists in the database')
                return

            insert_query = "INSERT INTO `faces`(`name`, `phone`, `email`, `password`) VALUES (%s,%s,%s,%s)"
            vals = (name, phone, email, password)
            c.execute(insert_query, vals)
            connecton.commit()

            util.msg_box('Success!', 'User was registered successfully !')

            name = self.entry_text_register_new_user.get()
            cv2.imwrite(os.path.join(self.db_dir, '{}.jpg'.format(name)), self.register_new_user_capture)
        self.register_new_user_window.destroy()


if __name__ == "__main__":
    app = App()
    app.start()
