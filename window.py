import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
import os
import threading

brackets = set("{}[]()")
STATUS_REFRESH_RATE = 100

# ── Colour palette (VS-Code dark) ─────────────────────────────────
BG      = "#1e1e1e"
BG2     = "#252526"
BG3     = "#2d2d30"
FG      = "#d4d4d4"
FG_DIM  = "#858585"
ACCENT  = "#4ec9b0"   # teal
ACCENT2 = "#569cd6"   # blue
SEL_BG  = "#264f78"


class Window:
    def __init__(self, root, languages):
        root.configure(bg=BG)
        root.geometry("980x700")
        root.minsize(720, 500)
        root.title("Program Line Counter")

        # ── ttk styles ────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".",
            background=BG, foreground=FG,
            fieldbackground=BG3, borderwidth=0, relief="flat")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TButton",
            background=BG3, foreground=FG,
            relief="flat", padding=(10, 5), font=("Segoe UI", 9))
        style.map("TButton",
            background=[("active", "#3e3e42"), ("pressed", SEL_BG)])
        style.configure("Accent.TButton",
            background=ACCENT2, foreground="#ffffff",
            relief="flat", padding=(10, 5), font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton",
            background=[("active", "#6baed6"), ("pressed", SEL_BG)])
        style.configure("TScrollbar",
            background=BG3, troughcolor=BG2, borderwidth=0,
            arrowcolor=FG_DIM, relief="flat")
        style.configure("Treeview",
            background=BG2, foreground=FG, fieldbackground=BG2,
            rowheight=22, font=("Consolas", 9), borderwidth=0, relief="flat")
        style.configure("Treeview.Heading",
            background=BG3, foreground=ACCENT, relief="flat",
            font=("Segoe UI", 9, "bold"))
        style.map("Treeview",
            background=[("selected", SEL_BG)],
            foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading",
            background=[("active", BG3)])

        # ── Helper used during widget construction ─────────────────
        def make_check(parent, text, var, command=None):
            return tk.Checkbutton(parent, text=text, variable=var,
                onvalue=True, offvalue=False, command=command,
                bg=BG, fg=FG, activebackground=BG, activeforeground=ACCENT,
                selectcolor=BG3, font=("Segoe UI", 10))

        # ── Shared state ──────────────────────────────────────────
        self.status_text  = ""
        self.scanning     = False
        self.scan_results = []      # list of (filepath, line_count)
        self.dir_data     = {}      # norm_key -> (display_name, total, self_count)
        self.dir_children = {}      # norm_key -> [child_norm_keys]
        self.dir_roots    = []      # top-level norm_keys
        self.total_lines  = 0

        # ── Root layout ───────────────────────────────────────────
        # Pack the log strip at the bottom FIRST so it always owns
        # the bottom edge; frm_content then fills the remaining space.
        frm_log_outer = tk.Frame(root, bg=BG2)
        frm_log_outer.pack(side=tk.BOTTOM, fill=tk.X)   # ← bottom first

        frm_content = ttk.Frame(root)
        frm_content.pack(fill=tk.BOTH, expand=True)      # ← fills the rest

        # ── Log panel (children not packed yet → 0 height) ────────
        log_expanded = [True]   # list so nested functions can mutate it

        frm_log_header = tk.Frame(frm_log_outer, bg=BG3, height=28)
        frm_log_header.pack_propagate(False)
        tk.Label(frm_log_header, text="Scan Log",
            bg=BG3, fg=FG_DIM, font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=10, pady=4)

        # btn_log_toggle defined after toggle_log()
        txt_log_frame = tk.Frame(frm_log_outer, bg=BG2, height=190)
        txt_log_frame.pack_propagate(False)

        txt_status_box = tk.Text(txt_log_frame,
            bg=BG2, fg="#9cdcfe",
            insertbackground=FG, selectbackground=SEL_BG,
            font=("Consolas", 9), relief="flat", bd=4,
            wrap=tk.NONE, state=tk.DISABLED)
        scr_log_y = ttk.Scrollbar(txt_log_frame, command=txt_status_box.yview)
        scr_log_x = ttk.Scrollbar(txt_log_frame,
            orient=tk.HORIZONTAL, command=txt_status_box.xview)
        txt_status_box.configure(
            yscrollcommand=scr_log_y.set, xscrollcommand=scr_log_x.set)
        scr_log_y.pack(side=tk.RIGHT,  fill=tk.Y)
        scr_log_x.pack(side=tk.BOTTOM, fill=tk.X)
        txt_status_box.pack(fill=tk.BOTH, expand=True)

        # ═════════════════════════════════════════════════════════
        # VIEW 1 – Main Menu
        # ═════════════════════════════════════════════════════════
        frm_menu = ttk.Frame(frm_content)

        tk.Label(frm_menu, text="Program Line Counter",
            bg=BG, fg=ACCENT, font=("Segoe UI", 18, "bold")
        ).pack(pady=(24, 4))

        lbl_instructions = tk.Label(frm_menu,
            text="Add one or more root directories to scan",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 10))
        lbl_instructions.pack(pady=(0, 20))

        tk.Label(frm_menu, text="Folders to scan",
            bg=BG, fg=FG, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=24)

        frm_folders = tk.Frame(frm_menu, bg=BG3, highlightbackground=BG3,
            highlightthickness=1)
        lst_folders = tk.Listbox(frm_folders,
            bg=BG2, fg=FG,
            selectbackground=SEL_BG, selectforeground="#ffffff",
            font=("Consolas", 9), relief="flat", borderwidth=0,
            highlightthickness=0, activestyle="none",
            width=80, height=7)
        scr_fld_y = ttk.Scrollbar(frm_folders, command=lst_folders.yview)
        scr_fld_x = ttk.Scrollbar(frm_folders,
            orient=tk.HORIZONTAL, command=lst_folders.xview)
        lst_folders.configure(
            yscrollcommand=scr_fld_y.set, xscrollcommand=scr_fld_x.set)
        scr_fld_y.pack(side=tk.RIGHT,  fill=tk.Y)
        scr_fld_x.pack(side=tk.BOTTOM, fill=tk.X)
        lst_folders.pack(fill=tk.BOTH, expand=True)
        frm_folders.pack(fill=tk.X, padx=24, pady=(4, 0))

        frm_fld_btns = ttk.Frame(frm_menu)
        ttk.Button(frm_fld_btns, text="+ Add Folder",
            command=lambda: on_browse_click(),
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(frm_fld_btns, text="− Remove Selected",
            command=lambda: on_remove_click()
        ).pack(side=tk.LEFT)
        frm_fld_btns.pack(anchor="w", padx=24, pady=6)

        # Language selector
        frm_options = ttk.Frame(frm_menu)
        tk.Label(frm_options, text="Language:",
            bg=BG, fg=FG, font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 6))
        language_names   = list(languages.keys())
        selected_language = tk.StringVar(value=language_names[0])
        opt_menu = tk.OptionMenu(frm_options, selected_language, *language_names)
        opt_menu.configure(bg=BG3, fg=FG,
            activebackground=SEL_BG, activeforeground=FG,
            highlightthickness=0, relief="flat", font=("Segoe UI", 10), bd=0)
        opt_menu["menu"].configure(bg=BG3, fg=FG,
            activebackground=SEL_BG, activeforeground=FG, relief="flat")
        opt_menu.pack(side=tk.LEFT)
        frm_options.pack(anchor="w", padx=24, pady=(4, 0))

        # Checkboxes
        ignore_blank_lines   = tk.IntVar()
        ignore_bracket_lines = tk.IntVar()
        ignore_patterns      = tk.IntVar()

        frm_checks = ttk.Frame(frm_menu)
        make_check(frm_checks, "Ignore Blank Lines",
            ignore_blank_lines
        ).pack(side=tk.LEFT, padx=(0, 16))
        make_check(frm_checks, "Ignore Bracket Lines",
            ignore_bracket_lines
        ).pack(side=tk.LEFT, padx=(0, 16))
        make_check(frm_checks, "Ignore pattern",
            ignore_patterns, command=lambda: on_ignore_patterns_select()
        ).pack(side=tk.LEFT)
        frm_checks.pack(anchor="w", padx=24, pady=6)

        etr_ignore_patterns = tk.Entry(frm_menu,
            bg=BG3, fg=FG, insertbackground=FG,
            font=("Consolas", 10), relief="flat")

        ttk.Button(frm_menu, text="▶   Start Count",
            command=lambda: start_count(self),
            style="Accent.TButton"
        ).pack(pady=16)

        # ═════════════════════════════════════════════════════════
        # VIEW 2 – Scanning indicator
        # ═════════════════════════════════════════════════════════
        frm_scanning = ttk.Frame(frm_content)
        tk.Label(frm_scanning, text="Scanning…",
            bg=BG, fg=ACCENT, font=("Segoe UI", 20, "bold")
        ).pack(pady=(80, 8))
        tk.Label(frm_scanning,
            text="Progress is shown in the log panel below.",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 11)
        ).pack()

        # ═════════════════════════════════════════════════════════
        # VIEW 3 – Results
        # ═════════════════════════════════════════════════════════
        frm_results = ttk.Frame(frm_content)

        # Top bar: summary labels (centred) + Start Over (right)
        frm_res_topbar = ttk.Frame(frm_results)
        ttk.Button(frm_res_topbar, text="↩  Start Over",
            command=lambda: set_up_main()
        ).pack(side=tk.RIGHT)
        frm_res_topbar.pack(fill=tk.X, padx=16, pady=(12, 0))

        lbl_res_title = tk.Label(frm_results, text="",
            bg=BG, fg=ACCENT, font=("Segoe UI", 16, "bold"))
        lbl_res_title.pack(pady=(6, 2))
        lbl_res_sub = tk.Label(frm_results, text="",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 10))
        lbl_res_sub.pack(pady=(0, 10))

        # ── Directory breakdown ────────────────────────────────
        def _section_header(parent, label_text, sort_asc_cmd, sort_desc_cmd):
            """Reusable row: section label on left, sort buttons on right."""
            frm = ttk.Frame(parent)
            tk.Label(frm, text=label_text,
                bg=BG, fg=FG, font=("Segoe UI", 9, "bold")
            ).pack(side=tk.LEFT)
            ttk.Button(frm, text="Most Lines ↓",
                command=sort_asc_cmd
            ).pack(side=tk.RIGHT, padx=(4, 0))
            ttk.Button(frm, text="Least Lines ↑",
                command=sort_desc_cmd
            ).pack(side=tk.RIGHT, padx=(0, 4))
            frm.pack(fill=tk.X, padx=16, pady=(0, 2))

        _section_header(frm_results, "BY DIRECTORY",
            lambda: sort_dir_results(descending=True),
            lambda: sort_dir_results(descending=False))

        frm_dir_wrap = ttk.Frame(frm_results)
        dir_tree = ttk.Treeview(frm_dir_wrap,
            columns=("lines", "pct", "self_lines", "self_pct"),
            show="tree headings", selectmode="browse", height=10)
        dir_tree.heading("#0",         text="Directory",  anchor="w")
        dir_tree.heading("lines",      text="Total",      anchor="e")
        dir_tree.heading("pct",        text="Total %",    anchor="e")
        dir_tree.heading("self_lines", text="Self",       anchor="e")
        dir_tree.heading("self_pct",   text="Self %",     anchor="e")
        dir_tree.column("#0",         anchor="w", width=350, minwidth=200, stretch=True)
        dir_tree.column("lines",      anchor="e", width=90,  minwidth=70,  stretch=False)
        dir_tree.column("pct",        anchor="e", width=70,  minwidth=55,  stretch=False)
        dir_tree.column("self_lines", anchor="e", width=90,  minwidth=70,  stretch=False)
        dir_tree.column("self_pct",   anchor="e", width=70,  minwidth=55,  stretch=False)
        scr_dir_y = ttk.Scrollbar(frm_dir_wrap, command=dir_tree.yview)
        scr_dir_x = ttk.Scrollbar(frm_dir_wrap,
            orient=tk.HORIZONTAL, command=dir_tree.xview)
        dir_tree.configure(
            yscrollcommand=scr_dir_y.set, xscrollcommand=scr_dir_x.set)
        scr_dir_y.pack(side=tk.RIGHT,  fill=tk.Y)
        scr_dir_x.pack(side=tk.BOTTOM, fill=tk.X)
        dir_tree.tag_configure("child", foreground=FG_DIM)
        dir_tree.pack(fill=tk.BOTH, expand=True)
        frm_dir_wrap.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        # ── File breakdown ─────────────────────────────────────
        _section_header(frm_results, "BY FILE",
            lambda: sort_results(descending=True),
            lambda: sort_results(descending=False))

        frm_tree = ttk.Frame(frm_results)
        tree = ttk.Treeview(frm_tree,
            columns=("filepath", "lines", "pct"), show="headings",
            selectmode="browse")
        tree.heading("filepath", text="File Path", anchor="w")
        tree.heading("lines",    text="Lines",     anchor="e")
        tree.heading("pct",      text="%",         anchor="e")
        tree.column("filepath", anchor="w", stretch=True)
        tree.column("lines",    anchor="e", width=90, minwidth=70, stretch=False)
        tree.column("pct",      anchor="e", width=70, minwidth=55, stretch=False)
        scr_tree_y = ttk.Scrollbar(frm_tree, command=tree.yview)
        scr_tree_x = ttk.Scrollbar(frm_tree,
            orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(
            yscrollcommand=scr_tree_y.set, xscrollcommand=scr_tree_x.set)
        scr_tree_y.pack(side=tk.RIGHT,  fill=tk.Y)
        scr_tree_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True)
        frm_tree.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        # ═════════════════════════════════════════════════════════
        # ALL CALLBACKS & HELPERS
        # (defined after widgets so closures resolve names correctly)
        # ═════════════════════════════════════════════════════════

        def show_view(view):
            for f in (frm_menu, frm_scanning, frm_results):
                f.pack_forget()
            view.pack(fill=tk.BOTH, expand=True)

        def toggle_log():
            if log_expanded[0]:
                txt_log_frame.pack_forget()
                btn_log_toggle.configure(text="▶  Show Log")
                log_expanded[0] = False
            else:
                txt_log_frame.pack(fill=tk.BOTH)
                btn_log_toggle.configure(text="▼  Hide Log")
                log_expanded[0] = True

        # Now we can create the toggle button (it references toggle_log)
        btn_log_toggle = tk.Button(frm_log_header,
            text="▼  Hide Log", command=toggle_log,
            bg=BG3, fg=ACCENT2,
            activebackground=BG3, activeforeground=ACCENT,
            relief="flat", cursor="hand2", font=("Segoe UI", 9), bd=0)
        btn_log_toggle.pack(side=tk.RIGHT, padx=8)

        def set_up_main():
            frm_log_header.pack_forget()
            txt_log_frame.pack_forget()
            log_expanded[0] = True
            btn_log_toggle.configure(text="▼  Hide Log")
            txt_status_box.configure(state=tk.NORMAL)
            txt_status_box.delete("1.0", tk.END)
            txt_status_box.configure(state=tk.DISABLED)
            self.status_text = ""
            lbl_instructions["text"] = "Add one or more root directories to scan"
            etr_ignore_patterns.pack_forget()
            show_view(frm_menu)

        def show_scanning_view():
            frm_log_header.pack(fill=tk.X)
            txt_log_frame.pack(fill=tk.BOTH)
            log_expanded[0] = True
            btn_log_toggle.configure(text="▼  Hide Log")
            show_view(frm_scanning)

        def show_results_view(total, results, root_folders):
            from collections import defaultdict
            self.total_lines  = total

            abs_roots = [os.path.abspath(f) for f in root_folders]
            norm_roots = {os.path.normcase(r) for r in abs_roots}

            def to_relative(abs_path):
                for r in abs_roots:
                    if abs_path.startswith(r):
                        rel = os.path.relpath(abs_path, r)
                        if rel == ".":
                            return os.path.basename(r)
                        return os.path.join(os.path.basename(r), rel)
                return abs_path

            self.scan_results = [
                (to_relative(os.path.abspath(fp)), n) for fp, n in results
            ]

            dir_totals = defaultdict(int)
            dir_self   = defaultdict(int)
            display_name = {}
            parent_of    = {}
            all_keys     = set()
            for fpath, n in results:
                abs_dir = os.path.abspath(os.path.dirname(fpath))
                key = os.path.normcase(abs_dir)
                dir_self[key] += n
                d_display = abs_dir
                d = key
                while True:
                    dir_totals[d] += n
                    all_keys.add(d)
                    if d not in display_name:
                        display_name[d] = to_relative(d_display)
                    if d in norm_roots:
                        break
                    d_display = os.path.dirname(d_display)
                    parent = os.path.normcase(d_display)
                    if parent == d:
                        break
                    parent_of[d] = parent
                    d = parent

            self.dir_data = {
                k: (display_name.get(k, k), dir_totals[k], dir_self.get(k, 0))
                for k in all_keys
            }
            children = defaultdict(list)
            roots = []
            for k in all_keys:
                if k in parent_of:
                    children[parent_of[k]].append(k)
                else:
                    roots.append(k)
            self.dir_children = dict(children)
            self.dir_roots = roots

            num_dirs = len(self.dir_data)
            lbl_res_title["text"] = f"Complete — {total:,} total lines"
            lbl_res_sub["text"] = (
                f"{len(results)} file{'s' if len(results) != 1 else ''} across "
                f"{num_dirs} director{'ies' if num_dirs != 1 else 'y'}")
            sort_dir_results(descending=True)
            sort_results(descending=True)
            show_view(frm_results)

        def _pct(n):
            if self.total_lines == 0:
                return "—"
            return f"{n / self.total_lines * 100:.2f}%"

        def sort_dir_results(descending=True):
            dir_tree.delete(*dir_tree.get_children())

            def insert_subtree(parent_iid, keys):
                keys = sorted(keys,
                    key=lambda k: self.dir_data[k][1], reverse=True)
                for k in keys:
                    display, total, self_n = self.dir_data[k]
                    label = os.path.basename(display) or display
                    iid = dir_tree.insert(parent_iid, tk.END, text=label,
                        values=(f"{total:,}", _pct(total),
                                f"{self_n:,}", _pct(self_n)),
                        open=True, tags=("child",))
                    children = self.dir_children.get(k, [])
                    if children:
                        insert_subtree(iid, children)

            all_keys = sorted(
                self.dir_data.keys(),
                key=lambda k: self.dir_data[k][1],
                reverse=descending)
            for k in all_keys:
                display, total, self_n = self.dir_data[k]
                iid = dir_tree.insert("", tk.END, text=display,
                    values=(f"{total:,}", _pct(total),
                            f"{self_n:,}", _pct(self_n)),
                    open=False)
                children = self.dir_children.get(k, [])
                if children:
                    insert_subtree(iid, children)

        def sort_results(descending=True):
            tree.delete(*tree.get_children())
            for fpath, n in sorted(
                    self.scan_results, key=lambda x: x[1], reverse=descending):
                tree.insert("", tk.END, values=(fpath, f"{n:,}", _pct(n)))

        def on_browse_click():
            folder = askdirectory()
            if folder:
                lst_folders.insert(tk.END, folder)

        def on_remove_click():
            for i in reversed(lst_folders.curselection()):
                lst_folders.delete(i)

        def on_ignore_patterns_select():
            if ignore_patterns.get():
                etr_ignore_patterns.pack(padx=24, pady=(0, 4), fill=tk.X)
            else:
                etr_ignore_patterns.pack_forget()

        def start_count(self):
            folders = list(lst_folders.get(0, tk.END))
            if not folders:
                lbl_instructions["text"] = "Please add at least one folder first."
                return

            language      = languages[selected_language.get()]
            file_exts     = clean_file_extensions(language.extensions)
            self.status_text  = ""
            self.scanning     = True
            self.scan_results = []

            show_scanning_view()
            refresh_status(self)

            def scan_thread():
                total   = 0
                results = []
                for folder in folders:
                    _log(f"=== {folder} ===\n")
                    for subdir, _, files in os.walk(folder):
                        for file in files:
                            fpath = os.path.join(subdir, file)
                            if has_valid_extension(file_exts, fpath):
                                try:
                                    with open(fpath, encoding="utf-8",
                                              errors="ignore") as f:
                                        n = count_lines(f.readlines())
                                    results.append((fpath, n))
                                    total += n
                                    _log(f"  {fpath}  →  "
                                         f"{n:,} line{'s' if n != 1 else ''}\n")
                                except Exception as e:
                                    _log(f"  {fpath}  →  ERROR: {e}\n")
                _log(f"\nDONE!   Total: {total:,} lines\n")
                self.scanning = False
                root.after(0, lambda: show_results_view(total, results, folders))

            threading.Thread(target=scan_thread, daemon=True).start()

        def _log(text):
            self.status_text += text

        def refresh_status(self):
            txt_status_box.configure(state=tk.NORMAL)
            txt_status_box.delete(1.0, tk.END)
            txt_status_box.insert(tk.END, self.status_text)
            txt_status_box.see(tk.END)
            txt_status_box.configure(state=tk.DISABLED)
            if self.scanning:
                txt_status_box.after(STATUS_REFRESH_RATE, refresh_status, self)

        def clean_file_extensions(exts):
            if isinstance(exts, str):
                exts = [exts]
            result = []
            for ext in exts:
                ext = ext.strip()
                if ext[0] != ".":
                    ext = "." + ext
                result.append(ext)
            return result

        def has_valid_extension(file_exts, filepath):
            return any(filepath.endswith(ext) for ext in file_exts)

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

        # ── Initial state ─────────────────────────────────────────
        frm_menu.pack(fill=tk.BOTH, expand=True)
