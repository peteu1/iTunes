# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 19:22:16 2019

@author: peter

Goal: Allow the user to navigate to the desired directory and playlist files

**Stand-alone application at the moment**
"""

import config
from PlaylistComparer import Processor
import tkinter as tk
import tkinter.ttk as ttk
import os


class Main_GUI:
    
    def __init__(self, processor):
        self.processor = processor
        self.root = tk.Tk()  # make window
        self.root.geometry(config.get_size())
        self.tree = None
        self.selection = None
        self.current_dir = config.playlists_path
        self.init_tree()
        self.root.mainloop()
        

    def init_tree(self):
        self.tree = ttk.Treeview(self.root, columns=config.file_cols, 
                                 show="headings", selectmode="browse")
        
        self.tree.heading("#1", text="File Name", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 0, False))
        self.tree.heading("#2", text="Size", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 1, False))
        self.tree.heading("#3", text="File Type", anchor=tk.W, command=
                           lambda: self.sort_tree(self.tree, 2, False))
#        self.tree.heading("#3", text="Date Modified", anchor=tk.W, command=
#                           lambda: self.sort_tree(self.tree, 2, False))
        
        # Get data for current directory
        names, sizes, dates = config.get_file_names(self.current_dir)
        
        # Add 'go up' directory
        self.tree.insert("", tk.END, values=("..", "", ""))
        
        # Insert data
        for name, size, date in zip(names, sizes, dates):
            self.tree.insert("", tk.END, values=(name, size, date))
        
        # Pack tree & attach functions
        self.tree.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.tree_select_event)
        self.tree.bind('<Double-1>', self.tree_double_clicked)
    
    
    def tree_select_event(self, event):
        item_iid = self.tree.selection()[0]
        self.selection = self.tree.item(item_iid)['values'][0]
    
    
    def tree_double_clicked(self, event):
        """ Add playlist if double clicked """
        region = self.tree.identify("region", event.x, event.y)
        if region == 'cell':
            print('self.selection', self.selection)
            print('self.current_dir', self.current_dir)
            if os.path.isfile(self.selection):
                filename, file_extension = os.path.splitext(self.selection)
                if file_extension == '.txt':
                    self.add()
            else:
                if self.selection == "..":
                    # Go up a directory
                    self.current_dir = os.path.dirname(self.current_dir)
                elif os.path.isdir(self.selection):
                    self.current_dir = os.path.join(self.current_dir, self.selection)
                print('self.current_dir', self.current_dir)
                self.update_tree()
            
    
    def update_tree(self):
        self.tree.pack_forget()
        self.init_tree()
    
    def add(self):
        print("add not implemented")
    
    
    def sort_tree(self, tv, col, reverse):
            """ sort the tree view by selected column """
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)
        
            # Rearrange items in sorted positions
            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)
        
            # Reverse sort next time
            tv.heading(col, command=lambda: self.sort_tree(tv, col, not reverse))


def main():
    processor = Processor()
    Main_GUI(processor)
    
    
    

if __name__ == "__main__":
    main()

