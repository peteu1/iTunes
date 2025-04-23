import config
import tkinter as tk
import tkinter.ttk as ttk
import os


class Main_GUI:
    """ Class handles all of the GUI for the application """
    
    def __init__(self, processor):
        # Processor object used for button call backs
        self.processor = processor
        self.root = tk.Tk()  # make window
        self.root.geometry(config.get_size())
        
        self.init_GUI()
        
        
    def init_GUI(self):
        # Top frame for displaying all playlists in a tree view
        self.topFrame = tk.Frame(self.root, height=100)
        self.topFrame.pack(side=tk.TOP)  # pack it in wherever
        self.tree = None
        self.current_dir = config.playlists_path
        self.cdir_label = None
        self.selection = None # Currently selected item in treeview
        self.init_topFrame()
        
        # Frame with instructions and add button to add playlists to summary
        self.addFrame = tk.Frame(self.root)
        self.addFrame.pack(side=tk.TOP)
        self.init_addFrame()
        
        # Initialize mainFrame GUI
        self.mainFrame = tk.Frame(self.root)
        self.mainFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.mainFrame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.pack(side=tk.TOP, fill=tk.X, expand=1, anchor=tk.N)
        # List of dicts, {'frame': tk.Frame, 'tree': ttk.TreeView}
        self.playlist_frames = [
                {'frame': self.create_playlist_frame(0), 'tree': None},
                {'frame': self.create_playlist_frame(1), 'tree': None}]
        
        # Compare and help window classes
        self.comparator = Comparator(self.root, self.processor)
        self.help_window = Help_Window(self.root)
        
        # Frame with buttons: refresh, compare, help
        self.buttonFrame = tk.Frame(self.root)
        self.buttonFrame.pack(side=tk.BOTTOM)  # pack it in on bottom
        
        self.init_buttonFrame()
        
        # Infinite loop to keep window up until closed
        self.root.mainloop()
    
        
# =============================================================================
#     Callback methods
# =============================================================================
        
    def add(self):
        """ Passes current selection to processor & updates GUI """
        fName = os.path.join(self.current_dir, self.selection)
        
        # Record the add (if valid)
        df, playlist_num = self.processor.add(fName)
        if df is None:
            return None
        self.update_playlist_frame(playlist_num)
    
    
    def remove(self):
        """ Removes selected playlist from viewer if exists """
        fName = os.path.join(self.current_dir, self.selection)
        playlist_num, shift = self.processor.remove(fName)

        # Ensure valid remove
        if playlist_num == -1:
            return False
        
        # Reset frame removed
        self.playlist_frames[playlist_num].get('frame').grid_forget()
        
        # Check if need to shift playlist on right to left
        if shift:
            # Right exists, move frame to left
            self.playlist_frames[1].get('frame').grid_forget()  # delete right
            self.update_playlist_frame(0)  # Add to left (processor has info)
        return True
        
    
    def compare(self):
        if self.processor._verify():
            # Update Comparison Viewer GUI
            self.comparator.launch_compare_viewer()
        
    
    def refresh(self):
        self.processor.refresh()  # Reset playlist name fields
        
        # Remove all frames from the root
        self.topFrame.pack_forget()
        self.addFrame.pack_forget()
        self.mainFrame.pack_forget()
        self.buttonFrame.pack_forget()
        self.comparator.refresh()
        self.help_window.refresh()
        
        # Re-initialize GUI
        self.init_GUI()
    
    
# =============================================================================
#     Tree frame controllers
# =============================================================================
    
    def tree_select_event(self, event):
        item_iid = self.tree.selection()[0]
        self.selection = self.tree.item(item_iid)['values'][0]
    
    
    def tree_double_clicked(self, event):
        """ Navigate file structure/ add playlist """
        region = self.tree.identify("region", event.x, event.y)
        if region == 'cell':
            self.current_dir, action = self.processor.clicked(
                    self.current_dir, self.selection)
            if action == 'updateTree':
                # update tree (remove from top frame and re-create)
                self.cdir_label.pack_forget()
                self.tree.pack_forget()
                self.init_topFrame()
            elif action == 'add':
                self.add()
            elif action == 'remove':
                self.remove()
    
    
# =============================================================================
#     GUI Updaters
# =============================================================================
    
    def sort_tree(self, tv, col, reverse):
        """ sort the tree view by selected column """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)
    
        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
    
        # Reverse sort next time
        tv.heading(col, command=lambda: self.sort_tree(tv, col, not reverse))
    
    
    def update_playlist_frame(self, playlist_num):
        # Recreate playlist
        self.playlist_frames[playlist_num] = {'frame': 
            self.create_playlist_frame(playlist_num)}
        
        # Add name of playlist to top of playlist frame
        name_frame = tk.Frame(self.playlist_frames[playlist_num].get('frame'))
        name_frame.pack(side=tk.TOP)
        
        playlist_name = self.processor.get_playlist_names()[playlist_num]
        label_text = "Playlist {}: {}".format(int(playlist_num + 1), playlist_name)
        label = tk.Label(name_frame, text=label_text)
        label.pack(side=tk.LEFT)
        
        # Add tree to display playlist info to playlist frame & make scrollable
        tree_frame = tk.Frame(self.playlist_frames[playlist_num].get('frame'))
        tree_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        cols = ("Song", "Artist", "Album")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", 
                            selectmode='browse')
        
        tree.pack(side='left', fill=tk.X, expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        # Set initial column widths and allow stretching with window
        col_widths = [100, 80, 80]
        for col, width in zip(list(cols), col_widths):
            tree.column(col, width=width, anchor='c', stretch=tk.YES)
        
        # Add sortable headings
        tree.heading("#1", text="Song", anchor=tk.W,
                     command=lambda: self.sort_tree(tree, 0, False))
        tree.heading("#2", text="Artist", anchor=tk.W,
                     command=lambda: self.sort_tree(tree, 1, False))
        tree.heading("#3", text="Album", anchor=tk.W,
                     command=lambda: self.sort_tree(tree, 2, False))
        
        # Get dataframe from processor & loop through rows to populate tree
        df = self.processor.get_df(playlist_num)
        for _, row in df.iterrows():
            values = tuple([a if type(a) is not float else "" for a in list(row)])
            tree.insert("", 'end', values=values) 
        
        # end config.populate_tree
        # Store tree
        self.playlist_frames[playlist_num]['tree'] = tree
        
        # Populate bottom section with statistics about playlist
        stats_frame = tk.Frame(self.playlist_frames[playlist_num].get('frame'))
        stats_frame.pack(side=tk.BOTTOM)
        stats = self.processor.get_summary_stats(playlist_num=playlist_num)
        label_2 = tk.Label(stats_frame, text=stats)
        label_2.pack(side=tk.BOTTOM)
    
    
# =============================================================================
#     GUI Initializers
# =============================================================================
    
    def init_topFrame(self):
        # Display current directory at top
        self.cdir_label = tk.Label(self.topFrame, text=self.current_dir)
        self.cdir_label.pack(side=tk.TOP)
        
        # Display all the files in current directory
        names, sizes, dates = config.get_file_names(self.current_dir)
        
        self.tree = ttk.Treeview(self.topFrame, columns=config.file_cols, 
                                 show="headings", selectmode="browse")
        # Define headings
        self.tree.heading("#1", text="File", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 0, False))
        self.tree.heading("#2", text="Size", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 1, False))
        self.tree.heading("#3", text="Date Modified", anchor=tk.W, command=
                          lambda: self.sort_tree(self.tree, 2, False))
        
        # Insert data
        self.tree.insert("", tk.END, values=("..", "", "")) # 'go up' directory
        for name, size, date in zip(names, sizes, dates):
            self.tree.insert("", tk.END, values=(name, size, date))
        
        # Pack tree & attach functions
        self.tree.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.tree_select_event)
        self.tree.bind('<Double-1>', self.tree_double_clicked)
        
    
    def create_playlist_frame(self, frame_number):
        """ frame_number is 0 for left, 1 for right """
        frame = tk.Frame(self.mainFrame)
        # Make frame width equal to half of the screen width
        frame.grid(row=0, column=frame_number, sticky="nsew")
        return frame
    
    
    def init_addFrame(self):
        label_1 = tk.Label(self.addFrame, fg="black",
                           text="Select a playlist to add for comparison.", padx=10, pady=5)
        label_1.pack(side=tk.LEFT)
        add_button = tk.Button(self.addFrame, text="Add", fg="#FFFFFF", bg="#27AE60",
                               command=self.add, padx=10)
        add_button.pack(side=tk.LEFT, padx=5)
        remove_button = tk.Button(self.addFrame, text="Remove", fg="red", 
                               command=self.remove)
        remove_button.pack(side=tk.LEFT)
    
    
    def init_buttonFrame(self):
        button_1 = tk.Button(self.buttonFrame, text="Refresh", fg="red",
                             command=self.refresh)
        button_2 = tk.Button(self.buttonFrame, text="Compare", fg="red",
                             command=self.compare)
        button_3 = tk.Button(self.buttonFrame, text="Help", fg="red",
                             command=self.help_window.display)
        button_1.grid(row=0)
        button_2.grid(row=0, column=1)
        button_3.grid(row=0, column=2)
        
        
    
class Help_Window():
    
    def __init__(self, root):
        self.parent = root
        self.visible = False
        
    def refresh(self):
        if self.visible:
            self.close()
    
    def display(self):
        
        # Kill old frame if already visible
        if self.visible:
            self.close()
        
        # Initialize popout window and close button
        self.root = tk.Toplevel(self.parent)
        self.root.geometry("560x400")
        self.visible = True
        close_button = tk.Button(self.root, text="Close", fg="red", 
                                 command=lambda: self.close())
        close_button.pack(side=tk.BOTTOM)
        
        # Write text
        text = tk.Text(self.root)
        text.pack()
        help_text = config.get_help_text()
        text.insert('end', help_text)
        text.configure(state=tk.DISABLED)
    
    
    def close(self):
        self.root.destroy()
        self.visible = False
        
        

class Comparator():
    
    def __init__(self, root, processor):
        self.parent = root
        self.visible = False
        self.processor = processor
        self.root = None
        self.tree = None
        self.topLabel = None; self.statsLabel = None
        self.radioFrame = None; self.radioVar = None
        self.venn_frame = None; self.venn_canvas = None
        self.merge_type = config.merge_types.get(0)
        self.df = None
        self.saveDisplay = None
    
    def refresh(self):
        if self.visible:
            self.close()
        
    def launch_compare_viewer(self):
        """ df is merged df; specs is merge specifications """
        
        # Kill old frame if already visible
        if self.visible:
            self.close()
        
        # Pop-out a new widget
        self.root = tk.Toplevel(self.parent)
        self.root.geometry(config.get_size('comparator'))
        self.visible = True
        
        # Initialize top panel for merge specs & close button
        self.top_panel = tk.Frame(self.root)
        self.top_panel.pack(side=tk.TOP)
        self.init_topFrame()
        
        # Add tree to display playlist info to playlist frame & make scrollable
        self.treeFrame = tk.Frame(self.root)
        self.treeFrame.pack(side=tk.TOP) 
        self.df = self.processor.compare(self.merge_type)
        self.init_treeFrame()
        
        # Populate bottom section with statistics about playlist
        self.detailsFrame = tk.Frame(self.root)
        self.detailsFrame.pack(side=tk.TOP)
        self.init_detailsFrame()
        
        # Save frame for entering new playlist name & saving to file
        self.saveFrame = tk.Frame(self.root)
        self.saveFrame.pack(side=tk.TOP)
        self.saveDisplayFrame = tk.Frame(self.root)
        self.saveDisplayFrame.pack(side=tk.TOP)
        self.init_saveFrame()
        
        # Bottom frame holds radio button frame and venn diagram
        self.bottomFrame = tk.Frame(self.root)
        self.bottomFrame.pack(side=tk.BOTTOM)
        self.init_bottomFrame()
    
    
    def close(self):
        self.root.destroy()
        self.visible = False
    
    
    def merge_type_changed(self):
        # Get new merge type and update venn GUI
        self.merge_type = config.merge_types.get(self.radioVar.get())
        self.venn_canvas.pack_forget()
        self.init_venn_diagram(self.merge_type)
        
        # Update df and related frames
        self.df = self.processor.compare(self.merge_type)
        self.tree.pack_forget(); self.vsb.pack_forget()
        self.init_treeFrame()
        self.topLabel['text'] = self.get_label_text(top=True)
        self.statsLabel['text'] = self.processor.get_summary_stats(df=self.df)
    
    
    def save(self):
        # Helper function to gather the names to pass to the processor
        output_name = self.new_name.get()
        if output_name == "":
            msg = 'Invalid outputname... must enter at least 1 character.'
            # TODO: Ask whether to use default name
            #if cancel:
                #return False
            p_names = self.processor.get_playlist_names()
            output_name = config.get_default_name(p_names[0], p_names[1],
                                                  self.merge_type)
        
        # Attempt to save file
        saved, fpath, error = self.processor.save(output_name, self.df)
        # TODO: Re-structure logic, 
        # TODO: if over-write, re-call this function to handle possible error
        msg = "Abort saving '{}'".format(fpath)
        if error:
            msg = "Error saving '{}'. Aborting...".format(fpath)
        if not saved and not error:
            # File already exists, ask user whether to over-write
            msg = "File '{}' already exists.".format(fpath)
            # TODO: Pop-up window to ask whether to overwrite
            saved, fpath, error = self.processor.save(output_name, self.df, True)
        if saved:
            msg = "File saved to: '{}'".format(fpath)
            
        self.saveDisplay['text'] = msg
    
    
# =============================================================================
#     GUI Initializers
# =============================================================================
    
    def init_saveFrame(self):
        label_2 = tk.Label(self.saveFrame, text="New playlist name: ")
        label_2.pack(side=tk.LEFT)
        
        self.new_name = tk.Entry(self.saveFrame)
        self.new_name.pack(side=tk.LEFT)
        
        save_button = tk.Button(self.saveFrame, text="Save", fg="red",
                                command=self.save)
        save_button.pack(side=tk.LEFT)
        
        self.saveDisplay = tk.Label(self.saveDisplayFrame, text="")
        self.saveDisplay.pack(side=tk.LEFT)
        
    
    def init_detailsFrame(self):
        stats = self.processor.get_summary_stats(df=self.df)
        self.statsLabel = tk.Label(self.detailsFrame, text=stats)
        self.statsLabel.pack(side=tk.BOTTOM)
        
    
    def init_topFrame(self):
        # Get specs about the comparison
        specs = self.get_label_text(top=True)
        self.topLabel = tk.Label(self.top_panel, text=specs)
        self.topLabel.pack(side=tk.RIGHT)
        close_button = tk.Button(self.top_panel, text="Close", fg="red", 
                                 command=self.close)
        close_button.pack(side=tk.RIGHT)
    
    
    def init_treeFrame(self):
        self.tree = ttk.Treeview(self.treeFrame, selectmode='browse')
        self.tree.pack(side='left', fill='y')
        self.vsb = ttk.Scrollbar(self.treeFrame, orient="vertical", 
                            command=self.tree.yview)
        self.vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=self.vsb.set)
        # TODO: Fix tree dimensions
        
        # Populate tree
        col_widths = [200, 120, 140]
        config.populate_tree(self.tree, self.df, col_widths)
        
    
    def init_bottomFrame(self):
        # Radio button frame to specify merge type
        self.radioFrame = tk.Frame(self.bottomFrame)
        self.radioFrame.pack(side=tk.LEFT)
        self.init_radioFrame()
        
        # Venn diagram -- to take place of radio frame
        self.venn_frame = tk.Frame(self.bottomFrame)
        self.venn_frame.pack(side=tk.RIGHT, fill=tk.X)#, expand=1, anchor=tk.N)
        self.init_venn_diagram()
    
    
    def get_label_text(self, top):
        if top:
            playlist_names = self.processor.get_playlist_names()
            specs = "Merge Type: {} |  Playlist 1: {} | Playlist 2: {}".format(
                    self.merge_type, playlist_names[0], playlist_names[1])
            return specs
        
    
    def init_radioFrame(self):
        # Radio group for merge type
        self.radioVar = tk.IntVar()
        
        for value in range(4):
            text = config.merge_types.get(value)
            Rb = tk.Radiobutton(self.radioFrame, text=text, variable=self.radioVar, 
                                value=value, command=self.merge_type_changed)
            Rb.pack(anchor=tk.W)
    
    
    def init_venn_diagram(self, how='inner'):        
        # Create Canvas for Venn Diagram
        self.venn_canvas = tk.Canvas(self.venn_frame, width=175, height=100)
        
        # Specify arc colors from left to right
        colors = ['black', 'black', 'black', 'black']
        if how == 'inner':
            colors[1] = colors[2] = 'red'
        elif how == 'left':
            colors[0] = colors[1] = 'red'
        elif how == 'right':
            colors[2] = colors[3] = 'red'
        elif how == 'outer':
            colors[0] = colors[3] = 'red'
        
        # Left outside arc
        self.venn_canvas.create_arc(10, 5, 100, 95, start=45, extent=270,
                                    outline=colors[0], style='arc', width=2)
        # Left inner arc
        self.venn_canvas.create_arc(75, 5, 165, 95, start=135, extent=90, 
                                    outline=colors[1], style='arc', width=2)
        # Right inner arc
        self.venn_canvas.create_arc(10, 5, 100, 95, start=315, extent=90, 
                                    outline=colors[2], style='arc', width=2)
        # Right outside arc
        self.venn_canvas.create_arc(75, 5, 165, 95, start=225, extent=270, 
                                    outline=colors[3], style='arc', width=2)
        self.venn_canvas.pack(side=tk.TOP)
    
    