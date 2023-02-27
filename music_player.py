import os
import tkinter as tk
from tkinter import filedialog
import pygame
import time
import tkinter.ttk as ttk
from tinytag import TinyTag
from random import randint


class MusicPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Music Player")

        # Center the window.
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (1250 / 2)
        y = (screen_height / 2) - (800 / 2)
        self.master.geometry(f"1250x800+{int(x)}+{int(y)}")

        # Initialize window components.
        self.listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.progress_bar = ttk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL, value=0,
                                      command=self.progress_bar_slide, state=tk.DISABLED)
        self.progress_bar.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

        self.status_frame = tk.Frame(self.master)
        self.status_frame.pack(side=tk.TOP, fill=tk.X, ipady=2)

        self.duration_label = tk.Label(self.status_frame, text="00:00", borderwidth=0)
        self.duration_label.pack(side=tk.RIGHT, padx=13)

        self.current_time_label = tk.Label(self.status_frame, text="00:00", borderwidth=0)
        self.current_time_label.pack(side=tk.LEFT, padx=13)

        self.song_title_label = tk.Label(self.status_frame)
        self.song_title_label.pack()

        self.controls_frame = tk.Frame(self.master)
        self.controls_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(20, 0))

        self.play = tk.Button(self.controls_frame, text="Play", command=self.play_music, state=tk.DISABLED)
        self.play.pack(side=tk.LEFT, padx=10, pady=10)

        self.pause_resume_button = tk.Button(self.controls_frame, text="Pause", command=self.pause_resume_music,
                                             state=tk.DISABLED)
        self.pause_resume_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(self.controls_frame, text="Next >>", command=self.next_song, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.skip_forward_button = tk.Button(self.controls_frame, text=">> 5s", command=self.skip_forward,
                                             state=tk.DISABLED)
        self.skip_forward_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.skip_backward_button = tk.Button(self.controls_frame, text="<< 5s", command=self.skip_backward,
                                              state=tk.DISABLED)
        self.skip_backward_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.previous_button = tk.Button(self.controls_frame, text="<< Previous", command=self.previous_song,
                                         state=tk.DISABLED)
        self.previous_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.play_mode_frame = tk.Frame(self.master)
        self.play_mode_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        self.play_mode_label = tk.Label(self.play_mode_frame, text="Play mode: ", borderwidth=0)
        self.play_mode_label.pack(side=tk.LEFT, padx=(13, 0))

        self.play_mode_button = tk.Button(self.play_mode_frame, text="Sequence", command=self.change_play_mode,
                                          state=tk.DISABLED)
        self.play_mode_button.pack(side=tk.LEFT)

        self.volume_frame = tk.Frame(self.master)
        self.volume_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.volume_label = tk.Label(self.volume_frame, text="Volume: ", borderwidth=0)
        self.volume_label.pack(side=tk.LEFT, padx=13)

        self.volume_bar = ttk.Scale(self.volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, value=1,
                                    command=self.volume_bar_slide, state=tk.DISABLED, length=250)
        self.volume_bar.pack(side=tk.LEFT)

        self.volume_value_label = tk.Label(self.volume_frame, text="100%", borderwidth=0)
        self.volume_value_label.pack(side=tk.LEFT, padx=15)

        self.choose_folder_button = tk.Button(self.master, text="Choose Folder", command=self.choose_folder)
        self.choose_folder_button.pack(side=tk.BOTTOM, padx=10, pady=(40, 20))

        # Initialize some variables that will we will need later.
        self.music_files = []
        self.current_song = None
        self.paused = False
        self.loop_is_running = False
        self.play_mode = "Sequence"

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

        # If there is at least one music file, enable the elements, and set the selection of
        # the list box to index 0, else disable all elements.
        if self.music_files:
            self.play.config(state=tk.NORMAL)
            self.pause_resume_button.config(state=tk.NORMAL)
            self.previous_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.skip_forward_button.config(state=tk.NORMAL)
            self.skip_backward_button.config(state=tk.NORMAL)
            self.play_mode_button.config(state=tk.NORMAL)
            self.listbox.selection_set(0)
        else:
            self.play.config(state=tk.DISABLED)
            self.pause_resume_button.config(state=tk.DISABLED)
            self.previous_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.skip_forward_button.config(state=tk.DISABLED)
            self.skip_backward_button.config(state=tk.DISABLED)
            self.progress_bar.config(state=tk.DISABLED)
            self.progress_bar.config(state=tk.DISABLED)
            self.play_mode_button.config(state=tk.DISABLED)

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

        # Set the text of current time label to 0 and duration_label's to current song's duration.
        self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(0))}")
        self.duration_label.config(
            text=f"{time.strftime('%M:%S', time.gmtime(TinyTag.get(self.current_song).duration))}")

        # Set the text of song title label to the song's title.
        self.song_title_label.config(text=f"{self.listbox.get(self.listbox.curselection()[0])}")

        # Check if the loop function is running, to make sure there is only one loop running at a time.
        if not self.loop_is_running:
            self.loop()

        # Enable the progress bar and volume bar.
        self.progress_bar.config(state=tk.NORMAL)
        self.volume_bar.config(state=tk.NORMAL)

        # Play the song.
        pygame.mixer.music.load(self.current_song)
        pygame.mixer.music.play()

    def pause_resume_music(self):
        """
        Pause/resume the music stream.
        """

        if self.paused:
            # The stream is pausing so resume it, start playing at the position according to progress bar.
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

            # Set self.paused and its text to "False".
            self.paused = False
            self.pause_resume_button.config(text="Pause")
        else:
            # Pause the stream.
            pygame.mixer.music.pause()

            # Set self.paused to True and its text to "Resume".
            self.paused = True
            self.pause_resume_button.config(text="Resume")

    def previous_song(self):
        """
        Jump to the previous song in the list box.
        """

        # If the current mode is "Random" then call the play_random_song function then return.
        if self.play_mode == "Random":
            self.play_random_song()
            return

        # Get the current index of the song in list box.
        current_index = self.listbox.curselection()[0]

        # Clear the selections in list box.
        self.listbox.selection_clear(0, tk.END)

        # If current index greater than 0 then play set the selection to the previous song in list box.
        if current_index > 0:
            self.listbox.selection_set(current_index - 1)

        # If the streaming currently at the first song then jump to the last song.
        else:
            self.listbox.selection_set(len(self.music_files) - 1)

        # If the stream is pausing then remain that status.
        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def next_song(self):
        """
        Jump to the next song in the list box.
        """

        # If the current mode is "Random" then call the play_random_song function then return.
        if self.play_mode == "Random":
            self.play_random_song()
            return

        # Get the current index of the song in list box.
        current_index = self.listbox.curselection()[0]

        # Clear the selections in list box.
        self.listbox.selection_clear(0, tk.END)

        # If current index is not the latest index of the list box (which is also the same as music_files) then set
        # the selection to the next song in list box.
        if current_index < len(self.music_files) - 1:
            self.listbox.selection_set(current_index + 1)

        # If the streaming currently at the last song then jump to the first song.
        else:
            self.listbox.selection_set(0)

        # If the stream is pausing then remain that status.
        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def skip_forward(self):
        """
        Skip 5 seconds forward.
        """

        # Increase the value of progress bar by 5 seconds.
        self.progress_bar.config(value=self.progress_bar.get() + 5)

        # If the progress bar value higher than the song duration then jump to the next song.
        if self.progress_bar.get() > TinyTag.get(self.current_song).duration:
            self.next_song()

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

        # Decrease the value of progress bar by 5 seconds.
        self.progress_bar.config(value=self.progress_bar.get() - 5)

        # If the progress bar value lower than 0 then jump to the previous song.
        if self.progress_bar.get() < 0:
            self.previous_song()

        # Reload and play the music according to the updated progress bar.
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

            # Once the progress_bar reach its end then consider the current mode for the next action, whether call the
            # next_song function or repeat the current song.
            if self.progress_bar.get() > song_duration:
                if self.play_mode == "Repeat":
                    self.play_music()
                else:
                    self.next_song()

        self.status_frame.after(1000, self.loop)

    def progress_bar_slide(self, _):
        """
        Determine what happen as the progress bar slider's value change.
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

    def volume_bar_slide(self, _):
        """
        Determine what happen as the volume bar slider's value change.
        """

        # Set new volume base on the value of the slider.
        pygame.mixer.music.set_volume(self.volume_bar.get())

        # Set the value for label base on the current volume.
        self.volume_value_label.config(text=f"{int(pygame.mixer.music.get_volume() * 100)}%")

    def change_play_mode(self):
        """
        Change playing mode, sequence, repeat, or random.
        """
        if self.play_mode == "Sequence":
            self.play_mode = "Repeat"
        elif self.play_mode == "Repeat":
            self.play_mode = "Random"
        else:
            self.play_mode = "Sequence"

        # Change the button text.
        self.play_mode_button.config(text=f"{self.play_mode}")

    def play_random_song(self):
        """
        Play a random song.
        """

        # Clear the list box.
        self.listbox.selection_clear(0, tk.END)

        # Set the list box selection to a random position.
        self.listbox.selection_set(randint(0, len(self.music_files) - 1))

        # If the stream is pausing then remain that status.
        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()
