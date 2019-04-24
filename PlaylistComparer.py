# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 19:39:12 2019

@author: peter
"""

# Import classes
from GUI import GUI
import config

# Import modules
import tkinter as tk
import os
import pandas as pd


class Processor:
    
    def __init__(self):
        self.running = True
        self.checked = False
        
        # TODO: Make these into 1 dict
        self.playlists = []
        self.dfs = []
        
    
    def _verify(self):
        """ @return True if two playlists have been added; False otherwise """
        return len(self.playlists) >= 2
        
         
    def add(self, playlist_name):
        print("playlist added:", playlist_name)
        
        if playlist_name in self.playlists:
            print("Can't compare to itself")
            return None, 1
        
        if self._verify():
            print("Can only compare two playlists")
            return None, 2
        
        # Add playlist name to playlists to track how many are added
        self.playlists.append(playlist_name)
        
        fName = config.playlists_path + "\\" + playlist_name
        df = pd.read_csv(fName, sep = '\t', encoding='utf-16')
        df = df[['Artist', 'Album', 'Name']]
        df.drop_duplicates(inplace=True)
        
        self.dfs.append(df)  # Store df
        
        return df, len(self.playlists)
    
    
    def remove(self, playlist_name):
        if len(self.playlists) == 0:
            print("Nothing to remove")
            return -1
        
        if playlist_name not in self.playlists:
            print(playlist_name, "not in viewer")
            return -1
        
        idx = 0 if self.playlists[0] == playlist_name else 1
        self.playlists.remove(playlist_name)
        if len(self.playlists):
            self.dfs = [self.dfs[(idx+1)%2]]  # Retain only the other df
        return idx
    
    
    def save(self, output_name):
        valid = self._verify()
        if not valid:
            print("Must add at least 2 playlists")
            return False
        
        if output_name == "":
            print("Save as name not valid")
            return False
        
        # TODO: Must also have output to save, i.e. compare has been called
        
        print('Saving playlist to:', output_name)
        print("save not implemented")
        return True
    
    
    def refresh(self):
        print("refresh not implemented")
        
    def compare(self):
        print("compare not implemented")
        
    def toggle_checked(self):
        print("toggle_checked called")
        self.checked = not self.checked
    
    
        

class Controller:
    
    def __init__(self):
        self.processor = Processor()
        self.gui = GUI(self.processor)
        #self.playlist_1 = self.playlist_2 = None
    
    
    def choose_playlists(self):
        paths = []
        for _, f in enumerate(os.listdir(config.playlists_path)):
            paths.append(f)
            print("{}: {}".format(_, f))
            
        # TODO: ensure input is number and in range
        p1 = paths[int(input("Choose a path by number: "))]
        p2 = paths[int(input("Choose a path by number: "))]
#        p1 = paths[0]; p2 = paths[1]
        return p1, p2
    
    
    def get_unique(self, df1, df2):
        """ returns the songs in df1 (left) that are not in df2 """
        left = df1[~((df1.Artist.isin(df2.Artist)) & 
                      (df1.Album.isin(df2.Album)) & 
                      (df1.Name.isin(df2.Name)))]
        left.reset_index(drop=True, inplace=True)
        
        return left
    
    
    def compare(self, playlist_1, playlist_2):
        fpath = "playlists\\{}"
        p1_name = playlist_1.split('.')[0]
        p2_name = playlist_2.split('.')[0]
        out_name = 'output\\{}{}{}.csv'
        
        df1_full = pd.read_csv(fpath.format(playlist_1), sep = '\t', encoding='utf-16')
        df1 = df1_full[['Artist', 'Album', 'Name']]
        df1.drop_duplicates(inplace=True)
        
        df2_full = pd.read_csv(fpath.format(playlist_2), sep = '\t', encoding='utf-16')
        df2 = df2_full[['Artist', 'Album', 'Name']]
        df2.drop_duplicates(inplace=True)
        
        # Get what is unique in playlist_1
        df1_unique = self.get_unique(df1, df2)
        print("\nnum unique in {}: {}, total length: {}"
              .format(playlist_1, len(df1_unique), len(df1)))
        # TODO: Try not dropping index and use it to index df1_full
        df1_unique.to_csv(out_name.format(p1_name, '-', p2_name), index=False)
        
        # Get what is unique in playlist_2
        df2_unique = self.get_unique(df2, df1)
        print("\nnum unique in {}: {}, total length: {}"
              .format(playlist_2, len(df2_unique), len(df2)))
        df2_unique.to_csv(out_name.format(p2_name, '-', p1_name), index=False)
        
        # Outer join
        df = df1.append(df2).reset_index(drop=True)
        df.drop_duplicates(inplace=True)
        df.to_csv(out_name.format(p1_name, '+', p2_name), index=False)
        print("Total unique:", len(df))

# end Controller        
        

def main():
    controller = Controller()
    #playlist_1, playlist_2 = controller.choose_playlists()
    #controller.compare(playlist_1, playlist_2)
    
    
if __name__ == "__main__":
    main()
    