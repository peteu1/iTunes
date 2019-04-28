# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 19:39:12 2019

@author: peter
"""

# Import classes
from GUI import Main_GUI
import config

# Import modules
import pandas as pd


class Processor:
    
    def __init__(self):
        self.running = True
        self.playlists = []
        self.dfs = []
    
# =============================================================================
#     Getter methods
# =============================================================================
    
    def get_df(self, idx):
        """ Gets the abbreviated version of the df at idx """
        if idx < len(self.dfs):
            return self.dfs[idx][['Name', 'Artist', 'Album']]
        print("df out of range!")
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
            return -1, False
        
        if playlist_name not in self.playlists:
            print(playlist_name, "not in viewer")
            return -1, False
        
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
            # TODO: Use default name; Need how joined, then can use in name
#            fpath = "output\\{}"  # TODO: Move to config
#            p1_name = p1.split('.')[0]
#            p2_name = p2.split('.')[0]
#            out_name = 'output\\{}{}{}.csv'
#            df.to_csv(out_name.format(p1_name, '+', p2_name), index=False)
#            df1_unique.to_csv(out_name.format(p1_name, '-', p2_name), index=False)
#            df2_unique.to_csv(out_name.format(p2_name, '-', p1_name), index=False)
            print("Save as name not valid")
            return False
        
        # TODO: Must also have output to save, i.e. compare has been called
        
        print("!!save not fully implemented")
        #print('Saving playlist to:', output_name)
        return output_name
    
    
    def compare(self, how='inner'):
        # Ensure valid compare
        valid = self._verify()
        if not valid:
            print("Need 2 playlists to compare")
            return None
        
        print("Compare type:", how)
        p1 = self.playlists[0]
        p2 = self.playlists[1]
        df1 = self.dfs[0]
        df2 = self.dfs[1]
                
        # TODO: Give another button to show stats about duplicates (popout?)
        
        if how == 'left':
            # Get what is unique in playlist_1
            df1_unique = self.get_unique(df1, df2)
            print("\nnum unique in {}: {}, total length: {}"
                  .format(p1, len(df1_unique), len(df1)))
            # TODO: Try not dropping index and use it to index df1_full
            return df1_unique
        
        if how == 'right':
            # Get what is unique in playlist_2
            df2_unique = self.get_unique(df2, df1)
            print("\nnum unique in {}: {}, total length: {}"
                  .format(p2, len(df2_unique), len(df2)))
            return df2_unique
        
        if how == 'outer':
            # Outer join
            df = df1.append(df2).reset_index(drop=True)
            df.drop_duplicates(inplace=True)
            print("Total unique:", len(df))
        
        else:  # if how == 'inner'
            df = df1.merge(df2, how='inner')
            df.drop_duplicates(inplace=True)
        
        return df
        
    
    def refresh(self):
        self.__init__()
        
    
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
        #df.drop_duplicates(inplace=True)
        
        self.dfs.append(df)  # Store df
        playlist_num = len(self.playlists) - 1
        print("playlists:", self.playlists)
        return df, playlist_num
    
    
    def get_summary_stats(self, playlist_num=-1, df=None):
        """ 
        Gets the summary statistics about a playlist
        @param playlist_num (int) to index the dataframe by frame number
        @param df (df) to get stats about a df (for compare viewer)
        @return stats (str) nicely formatted summary statistics
        """
        if df is None:
            df = self.dfs[playlist_num]
        num_songs = len(df)
        num_unique = len(df.drop_duplicates())
        
        num_dupes = num_songs - num_unique
        unique_artists = len(df.groupby('Artist').count())
        unique_albums = len(df.groupby('Album').count())
        
        stats = "Songs: {} | Artists: {} | Albums: {} | Duplicates: {}".format(
                num_songs, unique_artists, unique_albums, num_dupes)
        print(stats)
        return stats
    
    
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
    