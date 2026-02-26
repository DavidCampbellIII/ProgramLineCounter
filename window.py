import tkinter as tk
from tkinter.filedialog import askdirectory
import os
import threading

brackets = set("{}[]()")
STATUS_REFRESH_RATE = 100  # ms between UI refreshes during scan

class Window:
    def __init__(self, root, languages):
        def set_up_main():
            txt_status_box.pack_forget()
            btn_redo.pack_forget()
            etr_ignore_patterns.pack_forget()

            lbl_instructions.pack(pady=(10, 5))
            lbl_folders_label.pack()
            frm_folders.pack(fill=tk.X, padx=10, pady=(0, 2))
            frm_folder_btns.pack()
            opt_languages.pack(pady=4)
            chk_ignore_blank_lines.pack()
            chk_ignore_bracket_lines.pack()
            chk_ignore_patterns.pack()
            btn_start_count.pack(pady=8)

            lbl_instructions["text"] = "Add one or more root directories to scan"

        def hide_main_menu():
            lbl_folders_label.pack_forget()
            frm_folders.pack_forget()
            frm_folder_btns.pack_forget()
            opt_languages.pack_forget()
            btn_start_count.pack_forget()
            chk_ignore_blank_lines.pack_forget()
            chk_ignore_bracket_lines.pack_forget()
            chk_ignore_patterns.pack_forget()
            etr_ignore_patterns.pack_forget()

        def on_browse_click():
            folder = askdirectory()
            if folder:
                lst_folders.insert(tk.END, folder)

        def on_remove_click():
            for i in reversed(lst_folders.curselection()):
                lst_folders.delete(i)

        def on_ignore_patterns_select():
            if ignore_patterns.get():
                etr_ignore_patterns.pack()
            else:
                etr_ignore_patterns.pack_forget()

        def start_count(self):
            folders = list(lst_folders.get(0, tk.END))
            if not folders:
                lbl_instructions["text"] = "Please add at least one folder first."
                return

            lbl_instructions["text"] = "Scanning..."
            hide_main_menu()
            txt_status_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            language = languages[selected_language.get()]
            file_extensions = clean_file_extensions(language.extensions)

            self.status_text = ""
            self.scanning = True
            refresh_status(self)

            def scan_thread():
                total_line_count = 0
                for folder in folders:
                    self.status_text += f"=== {folder} ===\n"
                    for subdir, _, files in os.walk(folder):
                        for file in files:
                            filepath = os.path.join(subdir, file)
                            if has_valid_extension(file_extensions, filepath):
                                try:
                                    with open(filepath, encoding="utf-8", errors="ignore") as f:
                                        length = count_lines(f.readlines())
                                    self.status_text += f"  {filepath}  →  {length} line{'s' if length != 1 else ''}\n"
                                    total_line_count += length
                                except Exception as e:
                                    self.status_text += f"  {filepath}  →  ERROR: {e}\n"

                self.status_text += f"\nDONE!\n\nTotal lines: {total_line_count}"
                self.scanning = False
                root.after(0, lambda: (
                    lbl_instructions.config(text=f"Complete — {total_line_count:,} total lines"),
                    btn_redo.pack(pady=6)
                ))

            threading.Thread(target=scan_thread, daemon=True).start()

        def clean_file_extensions(file_extensions):
            if isinstance(file_extensions, str):
                file_extensions = [file_extensions]
            result = []
            for ext in file_extensions:
                ext = ext.strip()
                if ext[0] != ".":
                    ext = "." + ext
                result.append(ext)
            return result

        def has_valid_extension(file_extensions, filepath):
            for ext in file_extensions:
                if filepath.endswith(ext):
                    return True
            return False

        def count_lines(lines):
            count = 0
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    if not ignore_blank_lines.get():
                        count += 1
                elif len(line) == 1 and any(c in brackets for c in line):
                    if not ignore_bracket_lines.get():
                        count += 1
                else:
                    count += 1
            return count

        def refresh_status(self):
            txt_status_box.delete(1.0, tk.END)
            txt_status_box.insert(tk.END, self.status_text)
            txt_status_box.see(tk.END)
            if self.scanning:
                txt_status_box.after(STATUS_REFRESH_RATE, refresh_status, self)

        # --- State ---
        self.status_text = ""
        self.scanning = False

        # --- Widgets ---
        lbl_instructions = tk.Label(root, wraplength=500)

        lbl_folders_label = tk.Label(root, text="Folders to scan:")

        frm_folders = tk.Frame(root)
        lst_folders = tk.Listbox(frm_folders, width=70, height=6, selectmode=tk.EXTENDED)
        scr_folders_y = tk.Scrollbar(frm_folders, orient=tk.VERTICAL, command=lst_folders.yview)
        scr_folders_x = tk.Scrollbar(frm_folders, orient=tk.HORIZONTAL, command=lst_folders.xview)
        lst_folders.configure(yscrollcommand=scr_folders_y.set, xscrollcommand=scr_folders_x.set)
        scr_folders_y.pack(side=tk.RIGHT, fill=tk.Y)
        scr_folders_x.pack(side=tk.BOTTOM, fill=tk.X)
        lst_folders.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frm_folder_btns = tk.Frame(root)
        btn_browse = tk.Button(frm_folder_btns, text="+ Add Folder", command=on_browse_click)
        btn_remove = tk.Button(frm_folder_btns, text="- Remove Selected", command=on_remove_click)
        btn_browse.pack(side=tk.LEFT, padx=4)
        btn_remove.pack(side=tk.LEFT, padx=4)

        language_names = [name for name, _ in languages.items()]
        selected_language = tk.StringVar()
        selected_language.set(language_names[0])
        opt_languages = tk.OptionMenu(root, selected_language, *language_names)

        ignore_blank_lines = tk.IntVar()
        chk_ignore_blank_lines = tk.Checkbutton(root, text="Ignore Blank Lines", variable=ignore_blank_lines, onvalue=True, offvalue=False)
        ignore_bracket_lines = tk.IntVar()
        chk_ignore_bracket_lines = tk.Checkbutton(root, text="Ignore Bracket Lines", variable=ignore_bracket_lines, onvalue=True, offvalue=False)
        ignore_patterns = tk.IntVar()
        chk_ignore_patterns = tk.Checkbutton(root, text="Ignore pattern", variable=ignore_patterns, onvalue=True, offvalue=False, command=on_ignore_patterns_select)
        etr_ignore_patterns = tk.Entry(root)

        btn_start_count = tk.Button(root, text="Start Count", command=lambda: start_count(self))

        txt_status_box = tk.Text(root)
        txt_status_box.bind("<Key>", lambda e: "break")  # read-only

        btn_redo = tk.Button(root, text="Start Over", command=set_up_main)

        set_up_main()
