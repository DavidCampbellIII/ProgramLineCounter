import tkinter as tk
from tkinter.filedialog import askdirectory
import os
import time

MILLISECOND = 1.0 / 1000.0
brackets = set("{}[]()")

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

def start_count():
    root_dir = lbl_current_path["text"]
    lbl_instructions["text"] = "Starting search from root file '" + root_dir + "'"
    btn_browse.pack_forget()
    etr_file_extension.pack_forget()
    btn_start_count.pack_forget()
    lbl_current_path.pack_forget()
    chk_ignore_blank_lines.pack_forget()
    chk_ignore_bracket_lines.pack_forget()
    chk_ignore_patterns.pack_forget()

    txt_status_box.pack()
    file_extension = etr_file_extension.get().strip()
    if file_extension[0] != ".": #add the '.' if it is not already there
        file_extension = "." + file_extension

    total_line_count = 0
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            filepath = subdir + os.sep + file
            update_status("Analyzing " + filepath + "...")
            #time.sleep(MILLISECOND * 500) #TODO how do you properly wait so the status box is updated as the program processes the data?
            if filepath.endswith(file_extension):
                with open(filepath) as f:
                    length = count_lines(f.readlines())
                    update_status("Found " + str(length) + (" lines!\n", " line!\n")[length == 1])
                    total_line_count += length
    
    update_status("\nDONE!\n\nTotal lines: " + str(total_line_count))
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


def update_status(msg):
    txt_status_box.insert(tk.END, msg + "\n")
    txt_status_box.see("end")

def set_up_main():
    txt_status_box.pack_forget()
    btn_redo.pack_forget()

    frm_header.pack()
    lbl_instructions.pack()
    btn_browse.pack()
    etr_file_extension.pack()
    chk_ignore_blank_lines.pack()
    chk_ignore_bracket_lines.pack()
    chk_ignore_patterns.pack()
    lbl_current_path.pack()

    lbl_current_path["text"] = "None"
    txt_status_box.delete(1.0, tk.END)
    

#=======================Window Setup=========================
window = tk.Tk()
window.title("Program Line Counter v0.00.002")

frm_header = tk.Frame() #TODO use this thing

lbl_instructions = tk.Label(frm_header, text="Please select the root directory of all the code you'd like to process")

btn_browse = tk.Button(text="Browse", command=on_browse_click)
btn_start_count = tk.Button(text="Start Count", command=start_count)
ignore_blank_lines = tk.IntVar()
chk_ignore_blank_lines = tk.Checkbutton(text="Ignore Blank Lines", variable=ignore_blank_lines, onvalue=True, offvalue=False)
ignore_bracket_lines = tk.IntVar()
chk_ignore_bracket_lines = tk.Checkbutton(text="Ignore Bracket Lines", variable=ignore_bracket_lines, onvalue=True, offvalue=False)

etr_file_extension = tk.Entry()
etr_file_extension.insert(0, ".cs")

ignore_patterns = tk.IntVar()
chk_ignore_patterns = tk.Checkbutton(text="Ignore pattern", variable=ignore_patterns, onvalue=True, offvalue=False, command=on_ignore_patterns_select)
etr_ignore_patterns = tk.Entry()

lbl_current_path = tk.Label(text="None", fg='#03bafc')

txt_status_box = tk.Text()
txt_status_box.bind("<Key>", lambda e: "break") #makes the status box readonly
btn_redo = tk.Button(text="Redo", command=set_up_main)

set_up_main()

window.mainloop()