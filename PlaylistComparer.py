# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 19:39:12 2019

@author: peter
"""

# Import classes
from GUI import Main_GUI
import config

# Import modules
import tkinter as tk
import os
import pandas as pd


class Processor:
    
    def __init__(self):
        self.running = True
        self.checked = False
        
        self.playlists = []
        self.dfs = []
    
    
# =============================================================================
#     Getter methods
# =============================================================================
    
    def get_df(self, idx):
        """ Gets the abbreviated version of the df at idx """
        if idx < len(self.dfs):
            return self.dfs[idx][['Artist', 'Album', 'Name']]
        return None
    
    
# =============================================================================
#     Callback methods    
# =============================================================================
    
    def add(self, playlist_name):
        # Validate integrity
        if playlist_name in self.playlists:
            print("Can't compare playlist to itself")
            return None, 1
        if self._verify():
            print("Can only compare two playlists")
            return None, 2
        
        return self._add(playlist_name)
    
    
    def remove(self, playlist_name):
        if len(self.playlists) == 0:
            print("Nothing to remove")
            return -1
        
        if playlist_name not in self.playlists:
            print(playlist_name, "not in viewer")
            return -1
        
        # Get original index (0 or 1) of playlist removed
        idx = 0 if self.playlists[0] == playlist_name else 1
        self.playlists.remove(playlist_name)
        shift = False  # Becomes true if playlist 0 removed and 1 still exists
        if len(self.playlists):
            self.dfs = [self.dfs[(idx+1)%2]]  # Retain only the other df
            if idx == 0:
                shift = True
        print("playlists:", self.playlists)
        return idx, shift
    
    
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
        print("!!save not fully implemented")
        return True
    
    
    def compare(self, how='inner'):
        
        # Ensure valid compare
        valid = self._verify()
        if not valid:
            print("Need 2 playlists to compare")
            return False
        
        p1 = self.playlists[0]
        p2 = self.playlists[1]
        
        df1 = self.dfs[0]
        df2 = self.dfs[1]
        
        # TODO: Use how to determine how to compare (how to slice df)
        
        # TODO: Give another button to show stats about duplicates (popout?)
        # TODO: Or do this automatically upon self.add()
        # Get what is unique in playlist_1
        df1_unique = self.get_unique(df1, df2)
        print("\nnum unique in {}: {}, total length: {}"
              .format(p1, len(df1_unique), len(df1)))
        # TODO: Try not dropping index and use it to index df1_full
        
        # Get what is unique in playlist_2
        df2_unique = self.get_unique(df2, df1)
        print("\nnum unique in {}: {}, total length: {}"
              .format(p2, len(df2_unique), len(df2)))
        
        # Outer join
        df = df1.append(df2).reset_index(drop=True)
        df.drop_duplicates(inplace=True)
        print("Total unique:", len(df))
        
        
        # TODO: Move to save
#        fpath = "playlists\\{}"
#        p1_name = p1.split('.')[0]
#        p2_name = p2.split('.')[0]
#        out_name = 'output\\{}{}{}.csv'
#        df.to_csv(out_name.format(p1_name, '+', p2_name), index=False)
#        df1_unique.to_csv(out_name.format(p1_name, '-', p2_name), index=False)
#        df2_unique.to_csv(out_name.format(p2_name, '-', p1_name), index=False)
        
        return df
        
    
    def refresh(self):
        self.__init__()
        
    
#    def toggle_checked(self):
#        print("toggle_checked called")
#        self.checked = not self.checked
    
    
# =============================================================================
#     Logic methods
# =============================================================================
    
    def _verify(self):
        """ @return True if two playlists have been added; False otherwise """
        return len(self.playlists) >= 2
    
    
    def _add(self, playlist_name):
        # Add playlist name to playlists to track how many are added
        self.playlists.append(playlist_name)
        
        fName = config.playlists_path + "\\" + playlist_name
        df = pd.read_csv(fName, sep = '\t', encoding='utf-16')
        df = df[['Artist', 'Album', 'Name']]
        df.drop_duplicates(inplace=True)
        
        self.dfs.append(df)  # Store df
        playlist_num = len(self.playlists) - 1
        print("playlists:", self.playlists)
        return df, playlist_num
    
    
    def get_unique(self, df1, df2):
        """ returns the songs in df1 (left) that are not in df2 """
        left = df1[~((df1.Artist.isin(df2.Artist)) & 
                      (df1.Album.isin(df2.Album)) & 
                      (df1.Name.isin(df2.Name)))]
        left.reset_index(drop=True, inplace=True)
        
        return left
        

def main():
    processor = Processor()
    Main_GUI(processor)
    
    
if __name__ == "__main__":
    main()
    