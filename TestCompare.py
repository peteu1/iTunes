# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 20:31:06 2019

@author: peter
"""

from PlaylistComparer import Processor
import config
import pandas as pd


def main():
    processor = Processor()
    names, kbs, dates = config.get_playlist_names()
    processor._add(names[0])
    processor._add(names[1])
    
    df = processor.compare()
    df.to_csv(r'output\\test.txt', index=None, sep='\t')
    
    

if __name__ == "__main__":
    main()