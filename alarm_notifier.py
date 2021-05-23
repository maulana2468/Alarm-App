from locale import resetlocale
from tkinter import *
from tkinter import ttk, messagebox
from infi.systray import SysTrayIcon
from tkinter import filedialog
from plyer import notification
from playsound import playsound
import time, threading, datetime, os, sys

class App:
    def __init__(self, alarm_app):
        self.alarm_app = alarm_app
        self.alarm_app.title("Alarm App")
        self.alarm_app.geometry("350x350")
        self.alarm_app.resizable(False, False)
        
        def open(systray):
            self.alarm_app.after(0, self.alarm_app.deiconify)
        
        def minimize():
            pil = messagebox.askyesnocancel(title="Keluar", 
                                            message="Aplikasi Keluar?\n\nPilih \"No\" untuk minimize tray")
            if pil == True:
                alarm_end_thread()
                systray.shutdown()
                self.alarm_app.destroy()
            elif pil == False:
                self.alarm_app.withdraw()
            
        self.alarm_app.protocol("WM_DELETE_WINDOW", minimize)
        
        menu = (("Open Alarm", None, open), )
        systray = SysTrayIcon("alarm-clock.ico", "Alarm App", menu_options=menu)
        systray.start()
        
        # COMBOBOX
        times = []
        for x in range(0, 60):
            if len(str(x)) != 2: 
                x = "0" + str(x)
            times.append(x)
        self.hours_cb = ttk.Combobox(self.alarm_app, state="readonly", value=times[:25], width=3)
        self.min_cb = ttk.Combobox(self.alarm_app, state="readonly", value=times, width=3)
        self.sec_cb = ttk.Combobox(self.alarm_app, state="readonly", value=times, width=3)
        self.hours_cb.place(x=100, y=29)
        self.min_cb.place(x=190, y=29)
        self.sec_cb.place(x=280, y=29)
        
        # ENTRY INFO
        self.info = Entry(self.alarm_app, width=36)
        self.info.place(x=100, y=60)
        
        # SOUND PATH
        self.sound_path = Entry(self.alarm_app, width=30)
        self.sound_path.place(x=100, y=265)
        
        # BUTTON SOUND FILE
        sound_button = Button(self.alarm_app, text="Find", width=3, height=1, 
                              command=lambda:App.button_listener(self))
        sound_button.place(x=290,y=262)        
                
        # LABEL DIVIDE
        label_divide_1 = Label(self.alarm_app, text=":")
        label_divide_2 = Label(self.alarm_app, text=":")
        label_divide_1.place(x=160, y=29)
        label_divide_2.place(x=250, y=29)
        
        # LABEL TEXT
        time_label = Label(self.alarm_app, text="Waktu:")
        info_label = Label(self.alarm_app, text="Keterangan:")
        time_label.place(x=24, y=29)
        info_label.place(x=24, y=60)
        
        # LABEL SOUND
        sound_label = Label(self.alarm_app, text="Suara:")
        sound_label.place(x=24,y=265)
        
        # BUTTON ADD
        save_button = Button(self.alarm_app, text="Simpan", width=20, 
                             command=lambda:App.save(self))
        save_button.place(x=24,y=300)
        
        # BUTTON RESET
        reset_button = Button(self.alarm_app, text="Reset", width=19,
                              command=lambda:App.reset_listener(self))
        reset_button.place(x=180,y=300)
        
        # TABLE
        self.table = ttk.Treeview(self.alarm_app)
        self.table["columns"] = ("Jam", "Kegiatan")
        
        self.table.column("#0", width=0, stretch=NO)
        self.table.column("Jam", anchor=W, width=90)
        self.table.column("Kegiatan", anchor=W, width=200)
        
        self.table.heading("#0", text="")
        self.table.heading("Jam", text="Jam", anchor=W)
        self.table.heading("Kegiatan", text="Kegiatan", anchor=W)
    
        self.table.pack(pady=100)
        
        vsb = ttk.Scrollbar(self.alarm_app, orient="vertical", command=self.table.yview)
        vsb.place(x=305, y=100, height=150)
        
        App.update_table(self)
        
    def button_listener(self):
        sound_file = filedialog.askopenfilename(
            filetypes = (("File MP3", "*.mp3"), 
                         ("File WAV", "*.wav"), 
                         ("All Files", "*"))
            )
        self.sound_path.insert(0, sound_file)
        
    def save(self):
        hours_time = self.hours_cb.get()
        min_time = self.min_cb.get()
        sec_time = self.sec_cb.get()
        info = self.info.get()
        
        if len(hours_time) == 0 or len(min_time) == 0 or len(sec_time) == 0:
            messagebox.showwarning(title="Error", message="Waktu tidak boleh kosong!")
        else:
            time = f"{hours_time}:{min_time}:{sec_time}"
            f = open("data.cfg", "a")
            f.write(f"{time};{info}\n")
            f.close()
            
        App.update_table(self)
        global sound
        sound = self.sound_path.get()
     
    def update_table(self):
        for i in self.table.get_children():
            self.table.delete(i)
        if os.stat('data.cfg').st_size != 0:
            f = open("data.cfg", "r")
            for data in f:
                times, info = data.split(";")
                self.table.insert(parent='', index='end', values=(times, info))
            f.close()   
            
    def reset_listener(self):  
        self.sound_path.delete(0, "end")
        sound = self.sound_path.get()
        for i in self.table.get_children():
            self.table.delete(i)
        open("data.cfg", "w").close()
    
def alarm(stop):
    while True:
        time.sleep(1)
        current_time = datetime.datetime.now()
        now = current_time.strftime("%H:%M:%S")
        print(now)
        if os.stat('data.cfg').st_size != 0:
            f = open("data.cfg", "r")
            for data in f:
                times, info = data.split(";")
                if now == times:
                    playsound(f"{sound}", block=False)
                    notification.notify(title="Alarm Notifications",
                                        message=info,
                                        app_name="Alarm App",
                                        app_icon="bell.ico",
                                        timeout=100,
                                        ticker="Alarm App",
                                        toast=False)
            f.close()
        if exit_flag:
            break
    
def main():
    alarm = Tk()
    alarm.iconbitmap("alarm-clock.ico")
    App(alarm)
    alarm.mainloop()
    
def alarm_end_thread():
    global exit_flag
    exit_flag = True
    time_thread.join()
           
if __name__ == '__main__':
    app_gui_thread = threading.Thread(target=main)
    app_gui_thread.start()
    exit_flag = False
    time_thread = threading.Thread(target=alarm, args=(lambda:exit_flag, ))
    time_thread.start()
    