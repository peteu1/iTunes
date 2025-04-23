import os
from datetime import datetime


def get_size(frame='GUI'):
    width = 600; height = 600
    if frame == "comparator":
        width = 550; height = 450
    return "{}x{}".format(str(width), str(height))
    

# path to where all the playlist .txt's are stored (relative)
wdir = os.getcwd()
playlists_rel_path = 'playlists'
playlists_path = os.path.join(wdir, playlists_rel_path)


def _dir_size(fPath):
    """ recursive function to get size of entire directory """
    size = os.path.getsize(fPath)
    if not os.path.isdir(fPath):
        return size
    return size + sum([_dir_size(os.path.join(fPath, file)) for 
                       file in os.listdir(fPath)])


def get_file_names(path):
    """ Gets names of all playlists in playlists_path """
    files = os.listdir(path)
    paths = [os.path.join(path, file) for file in files]
    dts = [datetime.utcfromtimestamp(os.path.getctime(path)) for path in paths]
    dates = [datetime.strftime(dt, '%m-%d-%Y') for dt in dts]
    kbs = []
    # TODO: If path is too close to root, don't compute directory sizes (too slow!)
    for path in paths:
        try:
            kbs.append(str(int(round(_dir_size(path)/1024, 0))) + " KB")
        except:
            kbs.append("")
    return files, kbs, dates


def get_default_name(p1, p2, merge_type):
    if merge_type == 'inner':
        return p1 + '_' + p2
    if merge_type == 'left':
        return p1 + '-' + p2
    elif merge_type == 'right':
        return p2 + '-' + p1
    return p1 + '+' + p2  # outer

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
