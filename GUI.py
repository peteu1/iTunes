# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 21:55:18 2019

@author: peter
"""

import config

import tkinter as tk
import tkinter.ttk as ttk
#import pandas as pd


class Main_GUI:
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
        self.playlist_frames = [self.create_playlist_frame(0),
                                self.create_playlist_frame(1)]
        
        # Comparison viewer frame, gets populated when compare is called
        # TODO: Maybe make this a popout; new class for this?
        
        # Radio button frame to specify merge type
        self.radioFrame = tk.Frame(self.root)
        self.radioFrame.pack(side=tk.BOTTOM)
        self.merge_type = 'inner'
        self.radioVar = None
        self.init_radioFrame()
        
        # Bottom frame contains the buttons: refresh, compare, help
        self.bottomFrame = tk.Frame(self.root)
        self.bottomFrame.pack(side=tk.BOTTOM)  # pack it in on bottom
        self.init_bottomFrame()
        
        # Infinite loop to keep window up until closed
        self.root.mainloop()
    
    
    def add(self):
        """ Passes current selection to processor & updates GUI """
        selection = self.tree.item(self.tree.selection()[0])['values'][0]
        df, playlist_num = self.processor.add(selection)  # record the add
        if df is None:
            return None
        #print(df.head())
        print("num:", playlist_num)
        
        self.update_playlist_frame(playlist_num)
        
    
    def remove(self):
        """ Removes selected playlist from viewer if exists """
        selection = self.tree.item(self.tree.selection()[0])['values'][0]
        playlist_num, shift = self.processor.remove(selection)
        
        # Ensure valid remove
        if playlist_num == -1:
            return False
        
        # Reset frame removed
        self.playlist_frames[playlist_num].pack_forget()
        
        # Check if need to shift playlist on right to left
        if shift:
            # Right exists, move frame to left
            self.playlist_frames[1].pack_forget()  # delete right
            self.update_playlist_frame(0)  # Add to left (processor has info)
        return True
    
    
    def save(self):
        # Helper function to gather the names to pass to the processor
        output_name = self.new_name.get()
        # TODO: Pass names of playlists 1 and 2
        self.processor.save(output_name)
    
    
    def compare(self):
        # TODO: Use self.radioVar.get() and don't need merge_type
        selection = config.merge_types.get(self.radioVar.get())
        df = self.processor.compare(selection)
        if df is not None:
            print('comapre GUI not implement')
            # TODO: Update Comparison Viewer GUI
        
    
    def refresh(self):
        # Reset playlist name fields
        self.playlist_frames = [self.create_playlist_frame(1),
                                self.create_playlist_frame(2)]
        self.init_topFrame()  # Reload topFrame in case folder changed
        self.processor.refresh()
    
    
# =============================================================================
#     GUI Updaters
# =============================================================================
    
    def update_playlist_frame(self, playlist_num):
        # Recreate playlist
        self.playlist_frames[playlist_num] = self.create_playlist_frame(playlist_num)
        
        # Add name of playlist to top of playlist frame
        playlist_name = self.processor.playlists[playlist_num]
        label_text = "Playlist {}: {}".format(int(playlist_num + 1), playlist_name)
        label = tk.Label(self.playlist_frames[playlist_num], text=label_text)
        label.pack(side=tk.LEFT)
        
        # TODO: Add playlist info to main frame GUI by updating text frames
        
        # TODO: Make scrollable
    
    
    def display_help(self):
        print("display_help not implemented")
        # TODO: Popout?
    
    
# =============================================================================
#     GUI Initializers
# =============================================================================
    
    
    def create_playlist_frame(self, frame_number):
        """ frame_number is 0 for left, 1 for right """
        # TODO MAYBE: Don't return frame, return empty tk.Text()
        
        frame = tk.Frame(self.mainFrame)
        orient_frame = tk.LEFT if frame_number == 0 else tk.RIGHT
        frame.pack(side=orient_frame)  #grid(row=0, column=(frame_number-1))
        
        # TODO: Make frame width equal to half of the screen width
        return frame
    
    
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
        self.tree.bind('<<TreeviewSelect>>')
        
    
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
    
    
    def init_saveFrame(self):
        label_2 = tk.Label(self.saveFrame, text="New playlist name: ")
        label_2.pack(side=tk.LEFT)
        
        self.new_name = tk.Entry(self.saveFrame)
        self.new_name.pack(side=tk.LEFT)
        
        save_button = tk.Button(self.saveFrame, text="Save", fg="red",
                                command=self.save)
        save_button.pack(side=tk.LEFT)
    
    
    def init_radioFrame(self):
        # Radio group for merge_type
        self.radioVar = tk.IntVar()
        R1 = tk.Radiobutton(self.radioFrame, text="Inner", variable=self.radioVar, 
                            value=0, command=self.compare)
        R2 = tk.Radiobutton(self.radioFrame, text="Outer", variable=self.radioVar, 
                            value=1, command=self.compare)
        R3 = tk.Radiobutton(self.radioFrame, text="Left", variable=self.radioVar, 
                            value=2, command=self.compare)
        R1.pack(anchor=tk.W)
        R2.pack(anchor=tk.W)
        R3.pack(anchor=tk.W)
    
    
    def init_bottomFrame(self):
        button_1 = tk.Button(self.bottomFrame, text="Refresh", fg="red",
                             command=self.refresh)
        button_2 = tk.Button(self.bottomFrame, text="Compare", fg="red",
                             command=self.compare)
        button_3 = tk.Button(self.bottomFrame, text="Help", fg="red",
                             command=self.display_help)
        button_1.grid(row=0)
        button_2.grid(row=0, column=1)
        button_3.grid(row=0, column=2)
        #self.buttonFrame.focus_set()  # Set focus so that binding will work
    