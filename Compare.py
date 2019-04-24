# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 19:02:43 2018

@author: Peter
"""
import pandas as pd

p = pd.read_csv('p.csv', encoding='latin1')
p1 = pd.read_csv('p1.csv', encoding='latin1')
p21 = pd.read_csv('p21.csv', encoding='latin1')
meta = pd.DataFrame([("p", len(p)), ("p1", len(p1)), ("p21", len(p21))])
print(meta)

# Retain artist, album, song (should be unique within playlist)
p = p[['Artist', 'Album', 'Name']]
p1 = p1[['Artist', 'Album', 'Name']]
p21 = p21[['Artist', 'Album', 'Name']]

# Concatanate columns into one
p = p.apply(lambda x: '_'.join(map(str,x)), axis=1)
p1 = p1.apply(lambda x: '_'.join(map(str,x)), axis=1)
p21 = p21.apply(lambda x: '_'.join(map(str,x)), axis=1)

# Sort
p = p.sort_values().reset_index(drop=True)
p1 = p1.sort_values()
p21 = p21.sort_values()

# Find differences b/w p and p1
#s = set(p)
s1 = set(p1)
s21 = set(p21)
print(len(s1), len(s21))

#idx = pd.Series(list(s21.intersection(s1)))
#print(len(idx))

#m = pd.Series(list(s21.difference(s1)))
#m = pd.Series(list(s21 - s1))
rap = pd.Series(list(s21 - s1))
print(rap)
