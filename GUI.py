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
        self.topFrame = tk.Frame(self.root, height=100)
        self.topFrame.pack(side=tk.TOP)  # pack it in wherever
        self.tree = None
        self.selection = None # Currently selected item in treeview
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
        self.mainFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.mainFrame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.pack(side=tk.TOP, fill=tk.X, expand=1, anchor=tk.N)
        self.playlist_frames = [self.create_playlist_frame(0),
                                self.create_playlist_frame(1)]
        
        # Frame with buttons: refresh, compare, help
        self.buttonFrame = tk.Frame(self.root)
        self.buttonFrame.pack(side=tk.BOTTOM)  # pack it in on bottom
        self.help_window = None; self.compare_viewer = None
        self.init_buttonFrame()
        
        # Bottom frame holds radio button frame and venn diagram
        self.bottomFrame = tk.Frame(self.root)
        self.bottomFrame.pack(side=tk.BOTTOM)
        
        self.radioFrame = None; self.radioVar = None
        self.venn_frame = None; self.venn_canvas = None
        self.init_bottomFrame()
        
        # Infinite loop to keep window up until closed
        self.root.mainloop()
    
    
    def tree_select_event(self, event):
        item_iid = self.tree.selection()[0]
        self.selection = self.tree.item(item_iid)['values'][0]
    
    
    def tree_double_clicked(self, event):
        """ Add playlist if double clicked """
        region = self.tree.identify("region", event.x, event.y)
        if region == 'cell':
            self.add()
            
    
    def add(self):
        """ Passes current selection to processor & updates GUI """
        df, playlist_num = self.processor.add(self.selection)  # record the add
        if df is None:
            return None
        self.update_playlist_frame(playlist_num)
    
    
    def remove(self):
        """ Removes selected playlist from viewer if exists """
        playlist_num, shift = self.processor.remove(self.selection)

        # Ensure valid remove
        if playlist_num == -1:
            return False
        
        # Reset frame removed
        self.playlist_frames[playlist_num].grid_forget()
        
        # Check if need to shift playlist on right to left
        if shift:
            # Right exists, move frame to left
            self.playlist_frames[1].grid_forget()  # delete right
            self.update_playlist_frame(0)  # Add to left (processor has info)
        return True
    
    
    def save(self):
        # Helper function to gather the names to pass to the processor
        output_name = self.new_name.get()
        # TODO: Pass names of playlists 1 and 2
        self.processor.save(output_name)
    
    
    def compare(self):
        selection = config.merge_types.get(self.radioVar.get())
        df = self.processor.compare(selection)
        if df is not None:
            # Get specs about the comparison
            playlist_names = self.processor.playlists
            specs = "Merge Type: {} |  Playlist 1: {} | Playlist 2: {}".format(
                    selection, playlist_names[0], playlist_names[1])
            # Update Comparison Viewer GUI
            self.launch_compare_viewer(df, specs)
            # TODO: If self.compare_viewer is not None, update instead of restarting
            # Update Venn diagram
            self.venn_canvas.pack_forget()
            self.init_venn_diagram(selection)
        
    
    def refresh(self):
        # Reset playlist name fields
#        self.playlist_frames = [self.create_playlist_frame(1),
#                                self.create_playlist_frame(2)]
#        self.init_topFrame()  # Reload topFrame in case folder changed
        self.processor.refresh()
        self.root.destroy()
        self.__init__(self.processor)
    
    
# =============================================================================
#     GUI Updaters
# =============================================================================
    
    def sort_tree(self, tv, col, reverse):
        """ sort the tree view by selected column """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)
    
        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
    
        # Reverse sort next time
        tv.heading(col, command=lambda: self.sort_tree(tv, col, not reverse))
    
    
    def update_playlist_frame(self, playlist_num):
        # Recreate playlist
        self.playlist_frames[playlist_num] = self.create_playlist_frame(playlist_num)
        
        # Add name of playlist to top of playlist frame
        name_frame = tk.Frame(self.playlist_frames[playlist_num])
        name_frame.pack(side=tk.TOP)
        playlist_name = self.processor.playlists[playlist_num]
        label_text = "Playlist {}: {}".format(int(playlist_num + 1), playlist_name)
        label = tk.Label(name_frame, text=label_text)
        label.pack(side=tk.LEFT)
        
        # Add tree to display playlist info to playlist frame & make scrollable
        tree_frame = tk.Frame(self.playlist_frames[playlist_num])
        tree_frame.pack(side=tk.TOP)
        tree = ttk.Treeview(tree_frame, selectmode='browse')
        tree.pack(side='left')
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        # TODO: Fix tree dimensions
        
        # Get dataframe from processor & populate tree
        df = self.processor.get_df(playlist_num)
        col_widths = [100, 80, 80]
        self.populate_tree(tree, df, col_widths)
        
        # Populate bottom section with statistics about playlist
        stats_frame = tk.Frame(self.playlist_frames[playlist_num])
        stats_frame.pack(side=tk.BOTTOM)
        stats = self.processor.get_summary_stats(playlist_num=playlist_num)
        label_2 = tk.Label(stats_frame, text=stats)
        label_2.pack(side=tk.BOTTOM)
    
    
    def launch_compare_viewer(self, df, specs):
        """ df is merged df; specs is merge specifications """
        # Pop-out a new widget
        self.compare_viewer = tk.Toplevel(self.root)
        self.compare_viewer.geometry("560x400")
        
        # Initialize top panel for merge specs & close button
        top_panel = tk.Frame(self.compare_viewer)
        top_panel.pack(side=tk.TOP)
        label_1 = tk.Label(top_panel, text=specs)
        label_1.pack(side=tk.RIGHT)
        close_button = tk.Button(top_panel, text="Close", fg="red", 
                                 command=self.close_compare)
        close_button.pack(side=tk.RIGHT)
        
        # Add tree to display playlist info to playlist frame & make scrollable
        tree_frame = tk.Frame(self.compare_viewer)
        tree_frame.pack(side=tk.TOP) 
        tree = ttk.Treeview(tree_frame, selectmode='browse')
        tree.pack(side='left', fill='y')
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        # TODO: Fix tree dimensions
        
        # Populate tree
        col_widths = [200, 120, 140]
        self.populate_tree(tree, df, col_widths)
        
        # Populate bottom section with statistics about playlist
        stats_frame = tk.Frame(self.compare_viewer)
        stats_frame.pack(side=tk.BOTTOM)
        stats = self.processor.get_summary_stats(df=df)
        label_2 = tk.Label(stats_frame, text=stats)
        label_2.pack(side=tk.BOTTOM)
    
    
    def populate_tree(self, tree, df, col_widths):
        tree["columns"] = ("1", "2", "3")
        tree['show'] = 'headings'
        tree.column("1", width=col_widths[0], anchor='c')
        tree.column("2", width=col_widths[1], anchor='c')
        tree.column("3", width=col_widths[2], anchor='c')
        tree.heading("1", text="Song")
        tree.heading("2", text="Artist")
        tree.heading("3", text="Album")
        
        # loop through rows & add
        for _, row in df.iterrows():
            values = tuple([a if type(a) is not float else "" for a in list(row)])
            tree.insert("", 'end', text="L1", values=values)
    
    
    def update_venn_diagram(self):
        how = config.merge_types.get(self.radioVar.get())
        self.venn_canvas.pack_forget()
        self.init_venn_diagram(how)
        
    
    def display_help(self):
        # Initialize popout window and close button
        self.help_window = tk.Toplevel(self.root)
        self.help_window.geometry("560x400")
        close_button = tk.Button(self.help_window, text="Close", fg="red", 
                                 command=self.close_help)
        close_button.pack(side=tk.BOTTOM)
        
        # Write text
        text = tk.Text(self.help_window)
        text.pack()
        f = open("help.txt", "r")
        help_text = f.read()
        text.insert('end', help_text)
        text.configure(state=tk.DISABLED)
    
    
    def close_help(self):
        self.help_window.destroy()
    
    def close_compare(self):
        self.compare_viewer.destroy()
    
    
# =============================================================================
#     GUI Initializers
# =============================================================================
    
    def create_playlist_frame(self, frame_number):
        """ frame_number is 0 for left, 1 for right """
        frame = tk.Frame(self.mainFrame)
        # Make frame width equal to half of the screen width
        frame.grid(row=0, column=frame_number, sticky="nsew")
        return frame
    
    
    def init_topFrame(self):
        # Display all the playlists in the folder
        names, sizes, dates = config.get_playlist_names()
        
        self.tree = ttk.Treeview(self.topFrame, columns=config.file_cols, 
                                 show="headings", selectmode="browse")
        
        # Define headings
        
        self.tree.heading("#1", text="Playlist Name", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 0, False))
        self.tree.heading("#2", text="Size", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 1, False))
        self.tree.heading("#3", text="Date Modified", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 2, False))
        
        # Insert data
        for name, size, date in zip(names, sizes, dates):
            self.tree.insert("", tk.END, values=(name, size, date))
        
        self.tree.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.tree_select_event)
        self.tree.bind('<Double-1>', self.tree_double_clicked)
        
    
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
    
    
    def init_buttonFrame(self):
        button_1 = tk.Button(self.buttonFrame, text="Refresh", fg="red",
                             command=self.refresh)
        button_2 = tk.Button(self.buttonFrame, text="Compare", fg="red",
                             command=self.compare)
        button_3 = tk.Button(self.buttonFrame, text="Help", fg="red",
                             command=self.display_help)
        button_1.grid(row=0)
        button_2.grid(row=0, column=1)
        button_3.grid(row=0, column=2)
        #self.buttonFrame.focus_set()  # Set focus so that binding will work
        
        
    def init_bottomFrame(self):
        # Radio button frame to specify merge type
        self.radioFrame = tk.Frame(self.bottomFrame)
        self.radioFrame.pack(side=tk.LEFT)
        self.init_radioFrame()
        
        # Venn diagram -- to take place of radio frame
        self.venn_frame = tk.Frame(self.bottomFrame)
        self.venn_frame.pack(side=tk.RIGHT, fill=tk.X)#, expand=1, anchor=tk.N)
        self.init_venn_diagram()
    
    
    def init_radioFrame(self):
        # Radio group for merge type
        self.radioVar = tk.IntVar()
        
        for value in range(4):
            text = config.merge_types.get(value)
            Rb = tk.Radiobutton(self.radioFrame, text=text, variable=self.radioVar, 
                                value=value, command=self.update_venn_diagram)
            Rb.pack(anchor=tk.W)
    
    
    def init_venn_diagram(self, how='inner'):        
        # Create Canvas for Venn Diagram
        self.venn_canvas = tk.Canvas(self.venn_frame, width=175, height=100)
        
        # Specify arc colors from left to right
        colors = ['black', 'black', 'black', 'black']
        if how == 'inner':
            colors[1] = colors[2] = 'red'
        elif how == 'left':
            colors[0] = colors[1] = 'red'
        elif how == 'right':
            colors[2] = colors[3] = 'red'
        elif how == 'outer':
            colors[0] = colors[3] = 'red'
        
        # Left outside arc
        self.venn_canvas.create_arc(10, 5, 100, 95, start=45, extent=270,
                                    outline=colors[0], style='arc', width=2)
        # Left inner arc
        self.venn_canvas.create_arc(75, 5, 165, 95, start=135, extent=90, 
                                    outline=colors[1], style='arc', width=2)
        # Right inner arc
        self.venn_canvas.create_arc(10, 5, 100, 95, start=315, extent=90, 
                                    outline=colors[2], style='arc', width=2)
        # Right outside arc
        self.venn_canvas.create_arc(75, 5, 165, 95, start=225, extent=270, 
                                    outline=colors[3], style='arc', width=2)
        self.venn_canvas.pack(side=tk.TOP)
    