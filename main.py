import tkinter as tk
from window import Window
from language import Language

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Program Line Counter v0.00.002")
    languages = Language.loadLanguages("config/languages.json")
    window = Window(root, languages)
    root.mainloop()