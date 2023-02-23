import os
import tkinter as tk
from tkinter import filedialog
import pygame
import time
import tkinter.ttk as ttk
from tinytag import TinyTag


class MusicPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Music Player")

        # Center the window.
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (1200 / 2)
        y = (screen_height / 2) - (650 / 2)
        self.master.geometry(f"1200x650+{int(x)}+{int(y)}")

        # Initialize window components.
        self.listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.progress_bar = ttk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL, value=0, command=self.slide,
                                      state=tk.DISABLED)
        self.progress_bar.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

        self.status_frame = tk.Frame(self.master)
        self.status_frame.pack(side=tk.TOP, fill=tk.X, ipady=2)

        self.duration_label = tk.Label(self.status_frame, text="00:00", borderwidth=0, anchor=tk.E)
        self.duration_label.pack(side=tk.RIGHT, padx=13)

        self.current_time_label = tk.Label(self.status_frame, text="00:00", borderwidth=0, anchor=tk.E)
        self.current_time_label.pack(side=tk.LEFT, padx=13)

        self.controls_frame = tk.Frame(self.master)
        self.controls_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.play = tk.Button(self.controls_frame, text="Play", command=self.play_music, state=tk.DISABLED)
        self.play.pack(side=tk.LEFT, padx=10, pady=10)

        self.pause_resume_button = tk.Button(self.controls_frame, text="Pause", command=self.pause_resume_music,
                                             state=tk.DISABLED)
        self.pause_resume_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(self.controls_frame, text="Next >>", command=self.play_next, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.skip_forward_button = tk.Button(self.controls_frame, text=">> 5s", command=self.skip_forward,
                                             state=tk.DISABLED)
        self.skip_forward_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.skip_backward_button = tk.Button(self.controls_frame, text="<< 5s", command=self.skip_backward,
                                              state=tk.DISABLED)
        self.skip_backward_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.previous_button = tk.Button(self.controls_frame, text="<< Previous", command=self.play_previous,
                                         state=tk.DISABLED)
        self.previous_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.choose_folder_button = tk.Button(self.master, text="Choose Folder", command=self.choose_folder)
        self.choose_folder_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Initialize some variables that will we will need later.
        self.music_files = []
        self.current_song = None
        self.paused = False
        self.loop_is_running = False

        # Initialize Mixer to control the music stream.
        pygame.mixer.init()

    def choose_folder(self):
        """
        Let user choose their music containing directory.
        """

        # Empty the music list.
        self.listbox.delete(0, tk.END)
        self.music_files = []

        # Choose the folder, filter music files only, put the file names to listbox and put the files
        # to music_files.
        music_folder = tk.filedialog.askdirectory()
        # music_folder = r"/home/vu/Music"
        for file in os.listdir(music_folder):
            if file.endswith((".mp3", ".mp4", ".m4a", ".m4b", ".m4r", ".m4v", ".alac", ".aax", ".aaxc", ".wav", ".ogg",
                              ".opus", ".flac", ".wma")):
                self.listbox.insert(tk.END, file)
                self.music_files.append(os.path.join(music_folder, file))

        # If there is at least one music file, enable the buttons, and set the selection of
        # the list box to index 0, else disable all buttons.
        if self.music_files:
            self.play.config(state=tk.NORMAL)
            self.pause_resume_button.config(state=tk.NORMAL)
            self.previous_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.skip_forward_button.config(state=tk.NORMAL)
            self.skip_backward_button.config(state=tk.NORMAL)
            self.progress_bar.config(state=tk.NORMAL)
            self.listbox.selection_set(0)
        else:
            self.play.config(state=tk.DISABLED)
            self.pause_resume_button.config(state=tk.DISABLED)
            self.previous_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.skip_forward_button.config(state=tk.DISABLED)
            self.skip_backward_button.config(state=tk.DISABLED)
            self.progress_bar.config(state=tk.DISABLED)

    def play_music(self):
        """
        Start/rewind the music stream.
        """

        # If the streaming is paused then call the pause_resume_music function to resume.
        if self.paused:
            self.pause_resume_music()

        # Get the current selection index of the listbox, set the new current_song.
        self.current_song = self.music_files[self.listbox.curselection()[0]]

        # Set the progress bar value to 0 and set its maximum to the duration of the current_song.
        self.progress_bar.config(value=0)
        self.progress_bar.config(to=TinyTag.get(self.current_song).duration)

        # Set the text of duration_label to current song's duration.
        self.duration_label.config(text=f"{time.strftime('%M:%S', time.gmtime(TinyTag.get(self.current_song).duration))}")

        # Check if the loop function is running, there should be only one loop running at a time.
        if not self.loop_is_running:
            self.loop()

        # Play the song.
        pygame.mixer.music.load(self.current_song)
        pygame.mixer.music.play()

    def pause_resume_music(self):
        """
        Pause/resume the music stream.
        """

        # Pause the music, and set the button text to "Resume" if the stream is currently unpause, otherwise resume
        # the stream, set the button text to "Pause".
        if self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))
            self.paused = False
            self.pause_resume_button.config(text="Pause")
        else:
            pygame.mixer.music.pause()
            self.paused = True
            self.pause_resume_button.config(text="Resume")

    def play_previous(self):
        """
        Play the previous song in the list box.
        """

        # Play the previous song according to the order in listbox.
        if self.listbox.curselection()[0] > 0:
            current_index = self.listbox.curselection()[0]
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(current_index - 1)
            self.play_music()

        # If the streaming currently at the first song then replay the first song, which is also the current song.
        else:
            self.listbox.selection_set(self.listbox.curselection()[0])
            self.play_music()

    def play_next(self):
        """
        Play the next song in the list box.
        """

        # Play the next song according to the order in listbox.
        if self.listbox.curselection()[0] < len(self.music_files) - 1:
            current_index = self.listbox.curselection()[0]
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(current_index + 1)
            self.play_music()

        # If the streaming currently at the last song then replay the last song, which is also the current song.
        else:
            self.listbox.selection_set(self.listbox.curselection()[0])
            self.play_music()

    def skip_forward(self):
        """
        Skip 5 seconds forward.
        """

        # Increase the value of progress bar by 5 seconds.
        self.progress_bar.config(value=self.progress_bar.get() + 5)

        # If the progress bar value higher than the song duration then jump to the next song.
        if self.progress_bar.get() > TinyTag.get(self.current_song).duration:
            self.play_next()
            self.pause_resume_music()

        # Reload and play the music according to the updated progress bar.
        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        # If the stream is paused then update the current time label value as the slider sliding, this is supposed
        # to be the function loop's job but while the stream being paused the loop won't update the label value.
        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def skip_backward(self):
        """
        Skip 5 seconds backward.
        """

        # Decrease the value of progress bar by 5 seconds, then reload and play the music accordingly.
        self.progress_bar.config(value=self.progress_bar.get() - 5)
        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        # If the stream is paused then update the current time label value as the slider sliding, this is supposed
        # to be the function loop's job but while the stream being paused the loop won't update the label value.
        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def loop(self):
        """
        Determine what happen every 1 second.
        """

        self.loop_is_running = True
        # If the stream is not paused then increase the value of current_time_label, slider both by 1 second.
        if not self.paused:
            song_duration = int(TinyTag.get(self.current_song).duration)

            self.progress_bar.config(value=self.progress_bar.get() + 1)

            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

            # Once the progress_bar reach its end then jump to the next song.
            if self.progress_bar.get() > song_duration:
                self.play_next()

        self.status_frame.after(1000, self.loop)

    def slide(self, _):
        """
        Determine what happen as the slider's value change.
        """

        # Convert the slider value to integer.
        self.progress_bar.config(value=int(self.progress_bar.get()))

        # If the stream is not paused then also update the song accordingly.
        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        # If the stream is paused then update the current time label value as the slider sliding, this is supposed
        # to be the function loop's job but while the stream being paused the loop won't update the label value.
        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

