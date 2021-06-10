import tkinter as tk
from tkinter.filedialog import askdirectory
import os

brackets = set("{}[]()")
STATUS_REFRESH_RATE = 10

class Window:
    def __init__(self, root, languages):
        def set_up_main():
            txt_status_box.pack_forget()
            btn_redo.pack_forget()

            lbl_instructions.pack()
            btn_browse.pack()
            etr_file_extension.pack()
            chk_ignore_blank_lines.pack()
            chk_ignore_bracket_lines.pack()
            chk_ignore_patterns.pack()
            lbl_current_path.pack()

            lbl_current_path["text"] = "None"
            txt_status_box.delete(1.0, tk.END)

        def hide_main_menu():
            btn_browse.pack_forget()
            etr_file_extension.pack_forget()
            btn_start_count.pack_forget()
            lbl_current_path.pack_forget()
            chk_ignore_blank_lines.pack_forget()
            chk_ignore_bracket_lines.pack_forget()
            chk_ignore_patterns.pack_forget()

        def on_browse_click():  
            root_dir = askdirectory()
            if root_dir:
                lbl_current_path["text"] = root_dir
                btn_start_count.pack()

        def on_ignore_patterns_select():
            if ignore_patterns.get():
                etr_ignore_patterns.pack()
            else:
                etr_ignore_patterns.pack_forget()

        def start_count(self):
            root_dir = lbl_current_path["text"]
            lbl_instructions["text"] = "Starting search from root file '" + root_dir + "'"
            hide_main_menu()
            
            txt_status_box.pack()
            file_extension = etr_file_extension.get().strip()
            if file_extension[0] != ".": #add the '.' if it is not already there
                file_extension = "." + file_extension

            refresh_status(self)

            total_line_count = 0
            for subdir, _, files in os.walk(root_dir):
                for file in files:
                    filepath = subdir + os.sep + file
                    self.status_text += "Analyzing " + filepath + "..."
                    if filepath.endswith(file_extension):
                        with open(filepath) as f:
                            length = count_lines(f.readlines())
                            self.status_text += "Found " + str(length) + (" lines!\n", " line!\n")[length == 1]
                            txt_status_box.update()
                            total_line_count += length
            
            self.status_text += "\nDONE!\n\nTotal lines: " + str(total_line_count)
            btn_redo.pack()

        def count_lines(lines):
            count = 0
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    if not ignore_bracket_lines.get():
                        count += 1
                elif len(line) == 1:
                    if any((c in brackets) for c in line):
                        if not ignore_bracket_lines.get():
                            count += 1
                    else:
                        count += 1 
                else:
                    count += 1
            return count

        def refresh_status(self):
            txt_status_box.delete(1.0, tk.END)
            txt_status_box.insert(tk.END, self.status_text)
            txt_status_box.see(tk.END)
            txt_status_box.after(STATUS_REFRESH_RATE, refresh_status, self)

        self.status_text = ""
        lbl_instructions = tk.Label(root, text="Please select the root directory of all the code you'd like to process")
        lbl_current_path = tk.Label(text="None", fg='#03bafc')

        etr_file_extension = tk.Entry()
        etr_file_extension.insert(0, ".cs")

        btn_browse = tk.Button(root, text="Browse", command=on_browse_click)
        btn_start_count = tk.Button(root, text="Start Count", command=lambda: start_count(self))
        ignore_blank_lines = tk.IntVar()
        chk_ignore_blank_lines = tk.Checkbutton(root, text="Ignore Blank Lines", variable=ignore_blank_lines, onvalue=True, offvalue=False)
        ignore_bracket_lines = tk.IntVar()
        chk_ignore_bracket_lines = tk.Checkbutton(root, text="Ignore Bracket Lines", variable=ignore_bracket_lines, onvalue=True, offvalue=False)

        ignore_patterns = tk.IntVar()
        chk_ignore_patterns = tk.Checkbutton(root, text="Ignore pattern", variable=ignore_patterns, onvalue=True, offvalue=False, command=on_ignore_patterns_select)
        etr_ignore_patterns = tk.Entry()

        txt_status_box = tk.Text(root)
        txt_status_box.bind("<Key>", lambda e: "break") #makes the status box readonly
        btn_redo = tk.Button(root, text="Redo", command=set_up_main)

        set_up_main()