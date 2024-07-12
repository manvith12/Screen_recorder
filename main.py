from tkinter import *
from tkinter import messagebox, ttk
import cv2
import pyautogui
import numpy as np
from PIL import Image, ImageTk
import json
import time
from plyer import notification

class ScreenRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Manchan's Screen Recorder")
        self.master.configure(bg='#ffffff')

        self.screen_size = pyautogui.size()
        self.filename = ""
        self.video = None
        self.paused = False
        self.frame_rate = 30
        self.codec = 'MJPG'
        self.start_time = None

        self.start_icon = ImageTk.PhotoImage(Image.open('start_icon.png').resize((32, 32)))
        self.pause_icon = ImageTk.PhotoImage(Image.open('pause_icon.png').resize((32, 32)))
        self.stop_icon = ImageTk.PhotoImage(Image.open('stop_icon.png').resize((32, 32)))

        self.background_image = ImageTk.PhotoImage(Image.open('background_image.png'))

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        background_label = Label(self.master, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.header_label = Label(self.master, text="Manchan's Screen Recorder", font=('Helvetica', 20), bg='#ffffff', fg='#333333')
        self.header_label.pack(pady=20)

        filename_frame = Frame(self.master, bg='#ffffff')
        filename_frame.pack(pady=(0, 20))

        filename_label = Label(filename_frame, text="Filename:", font=('Helvetica', 12), bg='#ffffff', fg='#333333')
        filename_label.grid(row=0, column=0, padx=(10, 5))

        self.entry_filename = Entry(filename_frame, font=('Helvetica', 12), width=30, bg='white', fg='#333333')
        self.entry_filename.grid(row=0, column=1, padx=(0, 10))

        self.settings_frame = Frame(self.master, bg='#ffffff')
        self.settings_frame.pack(pady=10)

        frame_rate_label = Label(self.settings_frame, text="Frame Rate:", font=('Helvetica', 12), bg='#ffffff', fg='#333333')
        frame_rate_label.grid(row=0, column=0, padx=(10, 5))

        self.entry_frame_rate = Entry(self.settings_frame, font=('Helvetica', 12), width=10, bg='white', fg='#333333')
        self.entry_frame_rate.insert(END, str(self.frame_rate))
        self.entry_frame_rate.grid(row=0, column=1, padx=(0, 20))

        codec_label = Label(self.settings_frame, text="Codec:", font=('Helvetica', 12), bg='#ffffff', fg='#333333')
        codec_label.grid(row=0, column=2, padx=(20, 5))

        self.entry_codec = Entry(self.settings_frame, font=('Helvetica', 12), width=10, bg='white', fg='#333333')
        self.entry_codec.insert(END, self.codec)
        self.entry_codec.grid(row=0, column=3, padx=(0, 10))

        button_frame = Frame(self.master, bg='#ffffff')
        button_frame.pack(pady=20)

        self.start_button = ttk.Button(button_frame, text="Start Recording", image=self.start_icon, compound='left', command=self.start_recording)
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = ttk.Button(button_frame, text="Pause/Resume", image=self.pause_icon, compound='left', command=self.toggle_pause, state=DISABLED)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.stop_button = ttk.Button(button_frame, text="Stop Recording", image=self.stop_icon, compound='left', command=self.confirm_stop_recording, state=DISABLED)
        self.stop_button.grid(row=0, column=2, padx=10)

        self.start_button.image = self.start_icon
        self.pause_button.image = self.pause_icon
        self.stop_button.image = self.stop_icon

        self.label_status = Label(self.master, text="Status: Ready to record", font=('Helvetica', 12), bg='#ffffff', fg='#333333')
        self.label_status.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='indeterminate')
        self.progress_bar.pack(pady=10)

        self.master.bind('<Control-s>', lambda event: self.start_recording())
        self.master.bind('<Control-p>', lambda event: self.toggle_pause())
        self.master.bind('<Control-q>', lambda event: self.confirm_stop_recording())

    def start_recording(self):
        self.filename = self.entry_filename.get().strip()
        if not self.filename:
            messagebox.showerror("Error", "Filename cannot be empty.")
            return

        try:
            self.frame_rate = int(self.entry_frame_rate.get())
            self.codec = self.entry_codec.get().strip()

            self.video = cv2.VideoWriter(self.filename + '.avi', cv2.VideoWriter_fourcc(*self.codec), self.frame_rate, self.screen_size)
            notification.notify(
                title='SCREEN RECORDING!',
                message="Your screen is being recorded...",
                app_name="Screen Recorder"
            )
            self.label_status.config(text="Status: Recording... (Press 'Ctrl + p' to pause/resume, 'Ctrl + q' to stop)")
            self.progress_bar.start()
            self.start_time = time.time()

            self.start_button.config(state=DISABLED)
            self.pause_button.config(state=NORMAL)
            self.stop_button.config(state=NORMAL)

            self.recording_loop()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.label_status.config(text="Status: Error occurred during recording")
            self.cleanup_after_error()

    def recording_loop(self):
        while True:
            if not self.paused:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if self.video is not None:
                    self.video.write(frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                self.confirm_stop_recording()
                break
            elif key == ord('p'):
                self.toggle_pause()

            self.master.update_idletasks()
            self.master.update()

            if self.video is None:
                break

    def toggle_pause(self):
        if self.video is None:
            return
        
        self.paused = not self.paused
        if self.paused:
            notification.notify(
                title='PAUSED',
                message="Recording paused. Press 'Ctrl + p' to resume.",
                app_name="Screen Recorder"
            )
            self.label_status.config(text="Status: Paused. Press 'Ctrl + p' to resume.")
        else:
            notification.notify(
                title='RESUMED',
                message="Recording resumed.",
                app_name="Screen Recorder"
            )
            self.label_status.config(text="Status: Recording... (Press 'Ctrl + p' to pause/resume, 'Ctrl + q' to stop)")

    def confirm_stop_recording(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to stop recording?"):
            self.stop_recording()

    def stop_recording(self):
        if self.video:
            self.video.release()
            self.video = None
            cv2.destroyAllWindows()
            notification.notify(
                title='RECORDING ENDED!',
                message="Recording stopped. Your file has been saved successfully.",
                app_name="Screen Recorder"
            )
            self.label_status.config(text="Status: Ready to record")
            self.progress_bar.stop()
            self.progress_bar['value'] = 0
            self.start_time = None

            self.start_button.config(state=NORMAL)
            self.pause_button.config(state=DISABLED)
            self.stop_button.config(state=DISABLED)

            self.save_settings()

    def cleanup_after_error(self):
        if self.video:
            self.video.release()
            self.video = None
            cv2.destroyAllWindows()

            self.start_button.config(state=NORMAL)
            self.pause_button.config(state=DISABLED)
            self.stop_button.config(state=DISABLED)

    def save_settings(self):
        settings = {
            'frame_rate': self.frame_rate,
            'codec': self.codec
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.frame_rate = settings.get('frame_rate', 30)
                self.codec = settings.get('codec', 'MJPG')
                self.entry_frame_rate.delete(0, END)
                self.entry_frame_rate.insert(END, str(self.frame_rate))
                self.entry_codec.delete(0, END)
                self.entry_codec.insert(END, self.codec)
        except FileNotFoundError:
            pass

def main():
    root = Tk()
    root.geometry("500x500")
    app = ScreenRecorder(root)
    root.resizable(True, True)
    root.mainloop()

if __name__ == "__main__":
    main()
