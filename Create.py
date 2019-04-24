# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 20:07:39 2018

@author: Peter
"""

import pandas as pd

p1 = pd.read_csv('p1.csv', encoding='latin1')
p21 = pd.read_csv('p21.csv', encoding='latin1')

# Sort
p1 = p1.sort_values(['Artist', 'Album', 'Name'])
p21 = p21.sort_values(['Artist', 'Album', 'Name'])

#m = p21.merge(p1, on=['Artist', 'Album', 'Name'], how='left')
print(len(p21))
print(len(p1))
m = p1[~p1['Name'].isin(p21['Name'])]
print(len(m))

print(p21['Name'][0:10])
print(p1['Name'][0:10])
#m.to_csv("iPhoneRap.txt", sep='\t', index=False, header=True)



