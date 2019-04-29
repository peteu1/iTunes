# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 21:59:30 2019

@author: peter
"""

import os
from datetime import datetime


def get_size(frame='GUI'):
    width = 600; height = 600
    if frame == "comparator":
        width = 550; height = 450
    return "{}x{}".format(str(width), str(height))
    

# path to where all the playlist .txt's are stored (relative)
wdir = os.getcwd()
playlists_rel_path = 'playlists'  # TODO: Get this dynamically (settings panel?)
playlists_path = os.path.join(wdir, playlists_rel_path)


def get_file_names(path):
    """ Gets names of all playlists in playlists_path """
    files = os.listdir(path)
    ctimes = [os.path.getctime(path + '\\' + file) for file in files]
    dates = [datetime.strftime(datetime.utcfromtimestamp(ctime), '%m-%d-%Y') for
             ctime in ctimes]
    sizes = [os.path.getsize(path + '\\' + file) for file in files]
    kbs = [str(int(round(size/1024, 0))) + " KB" for size in sizes]
    return files, kbs, dates


# Converts radio button value to merge type str
merge_types = {0: 'inner', 1: 'outer', 2: 'left', 3: 'right'}

# Columns for top treeview file viewer
file_cols = ("name", "size", "date")
file_col_names = {0: "Playlist Name", 1: "Size", 2: "Date Modified"}


def populate_tree(tree, df, col_widths):
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
    

help_path = 'strings/help.txt'

def get_help_text():
    f = open(help_path, "r")
    help_text = f.read()
    return help_text
