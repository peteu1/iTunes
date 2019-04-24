# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 21:55:18 2019

@author: peter
"""

import config

import tkinter as tk
import tkinter.ttk as ttk
#import pandas as pd


class GUI:
    """ Class handles all of the GUI for the application """
    
    def __init__(self, processor):
        # Processor object used for button call backs
        self.processor = processor
        self.new_name = ""
        self.root = tk.Tk()  # make window
        self.root.geometry(config.size)
        
        # Top frame for displaying all playlists in a tree view
        self.topFrame = tk.Frame(self.root)  # invisible container
        self.topFrame.pack(side=tk.TOP)  # pack it in wherever
        self.tree = None
        self.selection = None  # Currently selected item in treeview
        self.init_topFrame()
        
        # Frame with instructions and add button to add playlists to summary
        self.addFrame = tk.Frame(self.root)
        self.addFrame.pack(side=tk.TOP)
        self.init_addFrame()
        
        # Save frame for entering new playlist name & saving to file
        self.saveFrame = tk.Frame(self.root)
        self.saveFrame.pack(side=tk.TOP)
        self.init_saveFrame()
        
        
        # Initialize mainFrame GUI
        self.mainFrame = tk.Frame(self.root)
        self.mainFrame.pack(side=tk.TOP, fill=tk.X)
        # TODO: Re-work the playlist frames
        self.playlist_frames = [self.create_playlist_frame(1),
                                self.create_playlist_frame(2)]
        
        # TODO: ALso make a viewer frame to populate when compare is called
        
        # Initialize bottomFrame GUI
        self.bottomFrame = tk.Frame(self.root)
        self.bottomFrame.pack(side=tk.BOTTOM)  # pack it in on bottom
        self.init_bottomFrame()
        
        # Infinite loop to keep window up until closed
        self.root.mainloop()
    
    
    def init_topFrame(self):
        # Display all the playlists in the folder
        names, sizes, dates = config.get_playlist_names()
        
        self.tree = ttk.Treeview(self.topFrame, columns=("name", "size", "date"), 
                            show="headings", selectmode="browse")
        
        # Define headings
        self.tree.heading("#1", text="Playlist Name", anchor=tk.W)
        self.tree.heading("#2", text="Size", anchor=tk.W)
        self.tree.heading("#3", text="Date modified", anchor=tk.W)
        
        # Insert data
        for name, size, date in zip(names, sizes, dates):
            self.tree.insert("", tk.END, values=(name, size, date))
        
        self.tree.pack(side=tk.TOP, fill=tk.X)
        self.tree.bind('<<TreeviewSelect>>', self.tree_select_event)
        
    
    def tree_select_event(self, event):
        item_iid = self.tree.selection()[0]
        self.selection = self.tree.item(item_iid)['values'][0]
        print(self.selection)
        
    
    def init_addFrame(self):
        label_1 = tk.Label(self.addFrame, fg="green", bg="black",
                           text="Highlight a playlist and press add --->")
        label_1.pack(side=tk.LEFT)
        add_button = tk.Button(self.addFrame, text="Add", fg="red", 
                               command=self.add)
        add_button.pack(side=tk.LEFT)
        remove_button = tk.Button(self.addFrame, text="Remove", fg="red", 
                               command=self.remove)
        remove_button.pack(side=tk.LEFT)
        
    
    def add(self):
        """ Passes current selection to processor & updates GUI """
        df, playlist_num = self.processor.add(self.selection)
        if df is None:
            return None
        
        print(df.head())
        # TODO: Get frame corresponding to playlist_num
        #frame = self.playlist_frames[playlist_num]
        # TODO: Add name of playlist (self.selection) to top of playlist frame
        # TODO: Add playlist info to main frame GUI by updating text frames
        # TODO: Make scrollable
        
    
    def remove(self):
        """ Removes selected playlist from viewer if exists """
        playlist_num = self.processor.remove(self.selection)
        if playlist_num != -1:
            print("playlist", playlist_num, "removed")
            # Reset playlist frame
            self.playlist_frames[playlist_num] = self.create_playlist_frame(playlist_num)
        
            
    
    def create_playlist_frame(self, frame_number):
        # TODO MAYBE: Don't return frame, return empty tk.Text()
        
        frame = tk.Frame(self.mainFrame)
        #frame = TkinterDnD.Tk()
        orient_frame = tk.LEFT if frame_number == 1 else tk.RIGHT
        frame.pack(side=orient_frame)  #grid(row=0, column=(frame_number-1))
        label_text = "Playlist {}".format(int(frame_number))
        label = tk.Label(frame, text=label_text)
        # TODO: Make frame width equal to half of the screen width
        label.pack(side=tk.LEFT)
        return frame
    
    
    def init_saveFrame(self):
        label_2 = tk.Label(self.saveFrame, text="New playlist name: ")
        label_2.pack(side=tk.LEFT)
        
        self.new_name = tk.Entry(self.saveFrame)
        self.new_name.pack(side=tk.LEFT)
        
        save_button = tk.Button(self.saveFrame, text="Save", fg="red",
                                command=self.save)
        save_button.pack(side=tk.LEFT)
    
    
    def save(self):
        # Helper function to gather the names to pass to the processor
        output_name = self.new_name.get()
        # TODO: Pass names of playlists 1 and 2
        self.processor.save(output_name)
    
    
    def init_bottomFrame(self):
        button_1 = tk.Button(self.bottomFrame, text="Refresh", fg="red",
                             command=self.refresh)
        button_2 = tk.Button(self.bottomFrame, text="Compare", fg="red",
                             command=self.processor.compare)
        button_3 = tk.Button(self.bottomFrame, text="Help", fg="red",
                             command=self.display_help)
        button_1.grid(row=0)
        button_2.grid(row=0, column=1)
        button_3.grid(row=0, column=2)
        #self.buttonFrame.focus_set()  # Set focus so that binding will work
    
    
    def display_help(self):
        print("display_help not implemented")
    
    
    def refresh(self):
        # Reset playlist name fields
        self.playlist_frames = [self.create_playlist_frame(1),
                                self.create_playlist_frame(2)]
        self.init_topFrame()  # Reload topFrame in case folder changed
        self.processor.refresh()
        
        
        
#    def init_settingsPanel(self):
#        label_3 = tk.Label(self.settingsPanel, text="Merge how?")
#        # TODO: Need radio group
#        radio_button_1 = tk.Radiobutton(self.settingsPanel, text="Inner")
#        radio_button_2 = tk.Radiobutton(self.settingsPanel, text="Outer")
#        check_box_1 = tk.Checkbutton(self.settingsPanel, text="Save to file?",
#                                     command=self.processor.toggle_checked)
#        label_3.grid(row=0, columnspan=2)
#        radio_button_1.grid(row=1)
#        radio_button_2.grid(row=1, column=1)
#        check_box_1.grid(row=2, columnspan=2)