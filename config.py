# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 21:59:30 2019

@author: peter
"""

import os
from datetime import datetime

width = 600
height = 700
size = "{}x{}".format(str(width), str(height))

# path to where all the playlist .txt's are stored (relative)
playlists_path = 'playlists'  # TODO: Get this dynamically (settings panel?)

def get_playlist_names():
    """ Gets names of all playlists in playlists_path """
    names = os.listdir(playlists_path)
    ctimes = [os.path.getctime(playlists_path + '\\' + path) for path in names]
    dates = [datetime.strftime(datetime.utcfromtimestamp(ctime), '%m-%d-%Y') for
             ctime in ctimes]
    sizes = [os.path.getsize(playlists_path + '\\' + path) for path in names]
    kbs = [str(int(round(size/1024, 0))) + " KB" for size in sizes]
    return names, kbs, dates


# Converts radio button value to merge type str
merge_types = {0: 'inner', 1: 'outer', 2: 'left', 3: 'right'}

# Columns for top treeview file viewer
file_cols = ("name", "size", "date")
file_col_names = {0: "Playlist Name", 1: "Size", 2: "Date Modified"}