import os
import time
import tkinter as tk
from tkinter import filedialog
import pygame
from pygame import mixer


class MusicPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Music Player")

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (1200 / 2)
        y = (screen_height / 2) - (600 / 2)

        self.master.geometry(f"1200x600+{int(x)}+{int(y)}")

        pygame.mixer.init()

        self.listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.playback_bar = tk.Canvas(self.master, bg="white", width=500, height=20)
        self.playback_bar.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

        self.controls_frame = tk.Frame(self.master)
        self.controls_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.play_pause_button = tk.Button(self.controls_frame, text="Play", command=self.play_music, state=tk.DISABLED)
        self.play_pause_button.pack(side=tk.LEFT, padx=10, pady=10)

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

        self.music_files = []
        self.music_index = 0
        self.current_music = None
        self.current_duration = 0
        self.paused = False
        self.stime = None
        self.elapsed = 0

    def choose_folder(self):
        music_folder = tk.filedialog.askdirectory()

        self.listbox.delete(0, tk.END)
        self.music_files = []
        for file in os.listdir(music_folder):
            if file.endswith(".mp3"):
                self.listbox.insert(tk.END, file)
                self.music_files.append(os.path.join(music_folder, file))

        if self.music_files:
            self.play_pause_button.config(state=tk.NORMAL)
            self.listbox.selection_set(0)
        else:
            self.play_pause_button.config(state=tk.DISABLED)

    def play_music(self):
        selection = self.listbox.curselection()
        self.music_index = selection[0]
        if not selection:
            return

        self.pause_resume_button.config(state=tk.NORMAL)
        self.previous_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.skip_forward_button.config(state=tk.NORMAL)
        self.skip_backward_button.config(state=tk.NORMAL)

        if self.current_music:
            pygame.mixer.music.stop()

        self.current_music = self.music_files[self.music_index]
        self.current_duration = pygame.mixer.Sound(self.current_music).get_length()
        pygame.mixer.music.load(self.current_music)
        pygame.mixer.music.play()
        stime = time.time()

    def pause_resume_music(self):
        now = time.time()
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.pause_resume_button.config(text="Pause")
            self.elapsed = now - self.stime
        else:
            pygame.mixer.music.pause()
            self.paused = True
            self.pause_resume_button.config(text="Resume")
            self.stime = now - self.elapsed

    def play_previous(self):
        if self.listbox.curselection()[0] > 0:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.music_index - 1)
            self.play_music()
        else:
            self.listbox.selection_set(0)

    def play_next(self):
        if self.listbox.curselection()[0] < len(self.music_files) - 1:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.music_index + 1)
            self.play_music()
        else:
            self.listbox.selection_set(len(self.music_files))

    def skip_forward(self):
        print(pygame.mixer.music.get_pos() / 1000)
        if self.current_pos == 0:
            self.current_pos = pygame.mixer.music.get_pos()
        else:
            self.current_pos += 5000
        if self.current_pos < self.current_duration * 1000:
            mixer.music.pause()
            print("new post nhỏ hơn duration nên sẽ tăng lên 5s")
            pygame.mixer.music.set_pos(self.current_pos / 1000)
            mixer.music.play()
        else:
            print("new post lớn hơn, nên sẽ ..")
            pygame.mixer.music.play(start=self.current_duration / 1000)

    def skip_backward(self):
        if self.stime and not self.paused:
            elapsed = time.time() - self.stime
            delta = min(elapsed, 5)
            pygame.mixer.music.play(start=elapsed - delta)
            self.stime += delta
