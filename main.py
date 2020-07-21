import tkinter as tk
from tkinter.filedialog import askdirectory
import os

def on_browse_click():
    root_dir = askdirectory()
    if root_dir:
        lbl_current_path["text"] = root_dir
        btn_start_count.pack()

def start_count():
    root_dir = lbl_current_path["text"]
    lbl_instructions["text"] = "Starting search from root file '" + root_dir + "'"
    btn_browse.pack_forget()
    etr_file_extension.pack_forget()
    btn_start_count.pack_forget()
    lbl_current_path.pack_forget()

    txt_status_box.pack()
    file_extension = etr_file_extension.get()
    total_line_count = 0
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            filepath = subdir + os.sep + file
            update_status("Analyzing " + filepath + "...")

            if filepath.endswith(file_extension):
                with open(filepath) as f:
                    length = len(f.readlines())
                    update_status("Found " + str(length) + (" lines!", " line!")[length == 1])
                    total_line_count += length
    
    update_status("Total lines: " + str(total_line_count))

    

def update_status(msg):
    txt_status_box.insert(tk.END, msg + "\n")
    txt_status_box.see("end")
    

#=======================Window Setup=========================
window = tk.Tk()
window.title("Program Line Counter v0.00.001")

lbl_instructions = tk.Label(text="Please select the root directory of all the code you'd like to process")

btn_browse = tk.Button(text="Browse", command=on_browse_click)
btn_start_count = tk.Button(text="Start Count", command=start_count)

etr_file_extension = tk.Entry()
etr_file_extension.insert(0, ".cs")

lbl_current_path = tk.Label(text="None", fg='#03bafc')

txt_status_box = tk.Text()
txt_status_box.bind("<Key>", lambda e: "break") #makes the status box readonly

lbl_instructions.pack()
btn_browse.pack()
etr_file_extension.pack()
lbl_current_path.pack()

window.mainloop()