# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 21:59:30 2019

@author: peter
"""

import os
from datetime import datetime


size = "500x500"

# path to where all the playlist .txt's are stored (relative)
playlists_path = 'playlists'

def get_playlist_names():
    """ Gets names of all playlists in playlists_path """
    names = os.listdir(playlists_path)
    ctimes = [os.path.getctime(playlists_path + '\\' + path) for path in names]
    dates = [datetime.strftime(datetime.utcfromtimestamp(ctime), '%m-%d-%Y') for
             ctime in ctimes]
    sizes = [os.path.getsize(playlists_path + '\\' + path) for path in names]
    kbs = [str(int(round(size/1024, 0))) + " KB" for size in sizes]
    return names, kbs, dates


