import tkinter as tk
from tkinter import ttk, colorchooser, font, messagebox, filedialog
import json
import os

SETTINGS_FILE = "teleprompta_settings.json"
DEFAULT_TEXT = "Welcome to Teleprompta!\n\nHighlight text and apply a style preset from the toolbar above."

DEFAULT_STYLE_PRESETS = [
    {"name": "Body", "font": "Arial", "size": 24, "color": "#AAAAAA"},
    {"name": "Title", "font": "Arial Black", "size": 28, "color": "#000000"},
    {"name": "Tips", "font": "Arial", "size": 20, "color": "#2196F3"},
]

DEFAULT_BG_COLOR = "#222222"
DEFAULT_BG_ALPHA = 0.85
DEFAULT_MENUBAR_COLOR = "#111111"

DEFAULT_SWATCHES = [
    ["#AAAAAA", "#FFFFFF", "#000000", "#FF4444", "#2196F3", "#00E5FF"],
    ["#000000", "#4CAF50", "#FFEB3B", "#FF9800", "#9C27B0", "#F44336"],
    ["#2196F3", "#4CAF50", "#FFEB3B", "#FF4444", "#9C27B0", "#00E5FF"]
]
DEFAULT_BG_SWATCHES = ["#222222", "#111111", "#444444", "#2196F3", "#4CAF50", "#FFEB3B"]
DEFAULT_MENUBAR_SWATCHES = ["#111111", "#222222", "#333333", "#444444", "#FFFFFF", "#000000"]

def load_settings():
    defaults = {
        "text": DEFAULT_TEXT,
        "styles": DEFAULT_STYLE_PRESETS,
        "bg_color": DEFAULT_BG_COLOR,
        "bg_alpha": DEFAULT_BG_ALPHA,
        "menubar_color": DEFAULT_MENUBAR_COLOR,
        "swatches": DEFAULT_SWATCHES,
        "bg_swatches": DEFAULT_BG_SWATCHES,
        "menubar_swatches": DEFAULT_MENUBAR_SWATCHES,
        "last_script": None
    }
    if not os.path.exists(SETTINGS_FILE):
        return defaults
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        while len(data["styles"]) < 3:
            data["styles"].append(DEFAULT_STYLE_PRESETS[len(data["styles"])])
        while len(data["swatches"]) < 3:
            data["swatches"].append(DEFAULT_SWATCHES[len(data["swatches"])])
        while len(data["bg_swatches"]) < 6:
            data["bg_swatches"].append(DEFAULT_BG_SWATCHES[len(data["bg_swatches"])])
        while len(data["menubar_swatches"]) < 6:
            data["menubar_swatches"].append(DEFAULT_MENUBAR_SWATCHES[len(data["menubar_swatches"])])
        return data
    except Exception:
        return defaults

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save settings.\n{e}")

def export_script(filename, text, tags):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"text": text, "tags": tags}, f, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save script.\n{e}")

def import_script(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("text", ""), data.get("tags", {})
    except Exception as e:
        messagebox.showerror("Open Error", f"Could not open script.\n{e}")
        return "", {}

class StylePreview(tk.Label):
    def __init__(self, master, style, bg="#f0f0f0", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.style = style
        self.bg = bg
        self.config(text="Preview", anchor="w", width=16, bg=self.bg)
        self.refresh()
    def refresh(self):
        f = (self.style["font"], self.style["size"], "bold")
        self.config(font=f, fg=self.style["color"], bg=self.bg)

class StyleEditorPanel(tk.Frame):
    def __init__(self, master, styles, font_families, on_update, swatches, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#f0f0f0")
        self.styles = styles
        self.font_families = font_families
        self.on_update = on_update
        self.previews = []
        self.entries = []
        self.swatches = swatches
        self.swatch_buttons = []
        self.build()
    def build(self):
        for idx, style in enumerate(self.styles):
            row = idx * 2
            name_var = tk.StringVar(value=style["name"])
            name_entry = tk.Entry(self, textvariable=name_var, width=10)
            name_entry.grid(row=row, column=0, padx=4, pady=4, sticky="ew")
            name_entry.bind("<FocusOut>", lambda e, i=idx: self.update_name(i))
            name_entry.bind("<Return>", lambda e, i=idx: self.update_name(i))
            font_var = tk.StringVar(value=style["font"])
            font_cb = ttk.Combobox(self, values=self.font_families, textvariable=font_var, width=16, state="readonly")
            font_cb.grid(row=row, column=1, padx=2)
            size_var = tk.IntVar(value=style["size"])
            size_cb = ttk.Combobox(self, values=list(range(10,73)), textvariable=size_var, width=3, state="readonly")
            size_cb.grid(row=row, column=2, padx=2)
            color_btn = tk.Button(self, text="Color", bg=style["color"], fg="black", width=6,
                                  command=lambda i=idx: self.choose_color(i))
            color_btn.grid(row=row, column=3, padx=2)
            swatch_frame = tk.Frame(self, bg="#f0f0f0")
            swatch_frame.grid(row=row, column=4, padx=2)
            btns = []
            for cidx, color in enumerate(self.swatches[idx]):
                b = tk.Button(swatch_frame, bg=color, width=2, height=1, relief="flat",
                              highlightbackground="#fff" if MainMenuBar._is_dark(color) else "#000",
                              highlightcolor="#fff" if MainMenuBar._is_dark(color) else "#000",
                              highlightthickness=2, bd=0)
                b.grid(row=0, column=cidx, padx=1)
                b.bind("<Button-1>", lambda e, i=idx, col=color: self.set_quick_color(i, col))
                b.bind("<Button-3>", lambda e, i=idx, c=cidx: self.customize_swatch(i, c))
                btns.append(b)
            self.swatch_buttons.append(btns)
            preview = StylePreview(self, style)
            preview.grid(row=row, column=5, padx=8)
            self.previews.append(preview)
            self.entries.append((name_var, font_var, size_var, color_btn))
            font_cb.bind("<<ComboboxSelected>>", lambda e, i=idx: self.update_style(i))
            size_cb.bind("<<ComboboxSelected>>", lambda e, i=idx: self.update_style(i))
            if idx < len(self.styles) - 1:
                tk.Frame(self, height=2, bd=1, relief="sunken", bg="#cccccc").grid(row=row+1, column=0, columnspan=6, sticky="ew", pady=3)
    def update_name(self, idx):
        name_var = self.entries[idx][0]
        self.styles[idx]["name"] = name_var.get()
        self.on_update()
    def choose_color(self, idx):
        color = colorchooser.askcolor(title="Choose Text Color", initialcolor=self.styles[idx]["color"])
        if color and color[1]:
            self.styles[idx]["color"] = color[1]
            self.entries[idx][3].config(bg=color[1])
            self.previews[idx].refresh()
            self.on_update()
    def set_quick_color(self, idx, color):
        self.styles[idx]["color"] = color
        self.entries[idx][3].config(bg=color)
        self.previews[idx].refresh()
        self.on_update()
    def customize_swatch(self, idx, cidx):
        color = colorchooser.askcolor(title="Customize Swatch", initialcolor=self.swatches[idx][cidx])
        if color and color[1]:
            self.swatches[idx][cidx] = color[1]
            self.swatch_buttons[idx][cidx].config(bg=color[1])
            self.on_update()
    def update_style(self, idx):
        _, font_var, size_var, _ = self.entries[idx]
        self.styles[idx]["font"] = font_var.get()
        self.styles[idx]["size"] = int(size_var.get())
        self.previews[idx].refresh()
        self.on_update()

class BgSwatchPanel(tk.Frame):
    def __init__(self, master, bg_color, on_set, swatches, on_update, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.bg_color = bg_color
        self.on_set = on_set
        self.swatches = swatches
        self.swatch_buttons = []
        self.on_update = on_update
        self.build()
    def build(self):
        for cidx, color in enumerate(self.swatches):
            b = tk.Button(self, bg=color, width=2, height=1, relief="flat",
                          highlightbackground="#fff" if MainMenuBar._is_dark(color) else "#000",
                          highlightcolor="#fff" if MainMenuBar._is_dark(color) else "#000",
                          highlightthickness=2, bd=0)
            b.pack(side="left", padx=1)
            b.bind("<Button-1>", lambda e, col=color: self.set_bg_quick_color(col))
            b.bind("<Button-3>", lambda e, c=cidx: self.customize_swatch(c))
            self.swatch_buttons.append(b)
    def set_bg_quick_color(self, color):
        self.bg_color = color
        self.on_set(self.bg_color)
    def customize_swatch(self, cidx):
        color = colorchooser.askcolor(title="Customize Swatch", initialcolor=self.swatches[cidx])
        if color and color[1]:
            self.swatches[cidx] = color[1]
            self.swatch_buttons[cidx].config(bg=color[1])
            self.on_update()

class MenuBarSwatchPanel(tk.Frame):
    def __init__(self, master, menubar_color, on_set, swatches, on_update, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.menubar_color = menubar_color
        self.on_set = on_set
        self.swatches = swatches
        self.swatch_buttons = []
        self.on_update = on_update
        self.build()
    def build(self):
        for cidx, color in enumerate(self.swatches):
            b = tk.Button(self, bg=color, width=2, height=1, relief="flat",
                          highlightbackground="#fff" if MainMenuBar._is_dark(color) else "#000",
                          highlightcolor="#fff" if MainMenuBar._is_dark(color) else "#000",
                          highlightthickness=2, bd=0)
            b.pack(side="left", padx=1)
            b.bind("<Button-1>", lambda e, col=color: self.set_menubar_quick_color(col))
            b.bind("<Button-3>", lambda e, c=cidx: self.customize_swatch(c))
            self.swatch_buttons.append(b)
    def set_menubar_quick_color(self, color):
        self.menubar_color = color
        self.on_set(self.menubar_color)
    def customize_swatch(self, cidx):
        color = colorchooser.askcolor(title="Customize Menu Bar Swatch", initialcolor=self.swatches[cidx])
        if color and color[1]:
            self.swatches[cidx] = color[1]
            self.swatch_buttons[cidx].config(bg=color[1])
            self.on_update()

class SettingsPanel(tk.Toplevel):
    def __init__(self, master, styles, bg_color, bg_alpha, menubar_color, font_families, on_styles_update, on_bg_update, on_menubar_update, swatches, bg_swatches, menubar_swatches):
        super().__init__(master)
        self.title("Settings")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        self.styles = styles
        self.bg_color = bg_color
        self.bg_alpha = bg_alpha
        self.menubar_color = menubar_color
        self.on_styles_update = on_styles_update
        self.on_bg_update = on_bg_update
        self.on_menubar_update = on_menubar_update
        self.font_families = font_families
        self.swatches = swatches
        self.bg_swatches = bg_swatches
        self.menubar_swatches = menubar_swatches
        self.build()
        self.transient(master)
        self.grab_set()
        self.center_window()
    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')
    def build(self):
        style_frame = tk.LabelFrame(self, text="Styles", bg="#f0f0f0")
        style_frame.pack(fill="x", padx=10, pady=8)
        self.editor = StyleEditorPanel(style_frame, self.styles, self.font_families, self.on_styles_update, self.swatches)
        self.editor.pack(fill="x", padx=4, pady=4)
        bg_frame = tk.LabelFrame(self, text="Background", bg="#f0f0f0")
        bg_frame.pack(fill="x", padx=10, pady=8)
        tk.Label(bg_frame, text="Color:", bg="#f0f0f0").pack(side="left", padx=4)
        self.bg_color_btn = tk.Button(bg_frame, text="Choose", bg=self.bg_color, width=8, command=self.choose_bg_color)
        self.bg_color_btn.pack(side="left", padx=4)
        self.bg_swatch_panel = BgSwatchPanel(bg_frame, self.bg_color, self.set_bg_quick_color, self.bg_swatches, self.on_bg_update)
        self.bg_swatch_panel.pack(side="left", padx=4)
        tk.Label(bg_frame, text="Alpha:", bg="#f0f0f0").pack(side="left", padx=4)
        self.bg_alpha_var = tk.DoubleVar(value=self.bg_alpha)
        self.bg_alpha_slider = ttk.Scale(bg_frame, from_=0.1, to=1.0, variable=self.bg_alpha_var, command=self.change_bg_alpha, length=120)
        self.bg_alpha_slider.pack(side="left", padx=4)
        menubar_frame = tk.LabelFrame(self, text="Menu Bar", bg="#f0f0f0")
        menubar_frame.pack(fill="x", padx=10, pady=8)
        tk.Label(menubar_frame, text="Color:", bg="#f0f0f0").pack(side="left", padx=4)
        self.menubar_color_btn = tk.Button(menubar_frame, text="Choose", bg=self.menubar_color, width=8, command=self.choose_menubar_color)
        self.menubar_color_btn.pack(side="left", padx=4)
        self.menubar_swatch_panel = MenuBarSwatchPanel(menubar_frame, self.menubar_color, self.set_menubar_quick_color, self.menubar_swatches, self.on_menubar_update)
        self.menubar_swatch_panel.pack(side="left", padx=4)
        ttk.Button(self, text="Close", command=self.close).pack(pady=10)
    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color", initialcolor=self.bg_color)
        if color and color[1]:
            self.bg_color = color[1]
            self.bg_color_btn.config(bg=self.bg_color)
            self.on_bg_update(self.bg_color, self.bg_alpha_var.get())
    def set_bg_quick_color(self, color):
        self.bg_color = color
        self.bg_color_btn.config(bg=color)
        self.on_bg_update(self.bg_color, self.bg_alpha_var.get())
    def change_bg_alpha(self, event=None):
        self.bg_alpha = self.bg_alpha_var.get()
        self.on_bg_update(self.bg_color, self.bg_alpha)
    def choose_menubar_color(self):
        color = colorchooser.askcolor(title="Choose Menu Bar Color", initialcolor=self.menubar_color)
        if color and color[1]:
            self.menubar_color = color[1]
            self.menubar_color_btn.config(bg=self.menubar_color)
            self.on_menubar_update(self.menubar_color)
    def set_menubar_quick_color(self, color):
        self.menubar_color = color
        self.menubar_color_btn.config(bg=color)
        self.on_menubar_update(self.menubar_color)
    def close(self):
        self.on_styles_update()
        self.on_bg_update(self.bg_color, self.bg_alpha)
        self.on_menubar_update(self.menubar_color)
        self.grab_release()
        self.destroy()

class MainMenuBar(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app = app
        self.menubar_color = app.menubar_color
        self.bg_alpha = app.bg_alpha
        self.bg_swatches = app.bg_swatches
        self.menubar_swatches = app.menubar_swatches
        self.collapsed = False
        self.build()
        self.update_bg()
    def build(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Script...", command=self.app.open_script)
        filemenu.add_command(label="Save Script As...", command=self.app.save_script)
        filemenu.add_separator()
        filemenu.add_command(label="Settings...", command=self.app.open_settings_panel)
        menubar.add_cascade(label="File", menu=filemenu)
        self.app.root.config(menu=menubar)
        self.style_buttons = []
        for idx, style in enumerate(self.app.style_presets):
            btn = tk.Button(self, text=style["name"], command=lambda i=idx: self.app.apply_style_to_selection(i),
                            font=(style["font"], 12, "bold") if idx > 0 else (style["font"], 12),
                            bg=self.menubar_color, fg="white" if self._is_dark(self.menubar_color) else "black")
            btn.pack(side="left", padx=2, pady=2)
            self.style_buttons.append(btn)
        tk.Label(self, text="  -Background-", bg=self.menubar_color, fg="white" if self._is_dark(self.menubar_color) else "black").pack(side="left", padx=(6,0))
        self.bg_swatch_buttons = []
        for cidx, color in enumerate(self.bg_swatches):
            b = tk.Button(self, bg=color, width=2, height=1, relief="flat",
                          highlightbackground="#fff" if self._is_dark(color) else "#000",
                          highlightcolor="#fff" if self._is_dark(color) else "#000",
                          highlightthickness=2, bd=0)
            b.pack(side="left", padx=1)
            b.bind("<Button-1>", lambda e, col=color: self.set_bg_quick_color(col))
            b.bind("<Button-3>", lambda e, c=cidx: self.customize_bg_swatch(c))
            self.bg_swatch_buttons.append(b)
        tk.Label(self, text="Alpha:", bg=self.menubar_color, fg="white" if self._is_dark(self.menubar_color) else "black").pack(side="left", padx=(10,2))
        self.bg_alpha_var = tk.DoubleVar(value=self.bg_alpha)
        self.bg_alpha_slider = ttk.Scale(self, from_=0.1, to=1.0, variable=self.bg_alpha_var, command=self.change_bg_alpha, length=120)
        self.bg_alpha_slider.pack(side="left", padx=2)
        tk.Label(self, text="  -Menu Bar-", bg=self.menubar_color, fg="white" if self._is_dark(self.menubar_color) else "black").pack(side="left", padx=(10,0))
        self.menubar_swatch_buttons = []
        for cidx, color in enumerate(self.menubar_swatches):
            b = tk.Button(self, bg=color, width=2, height=1, relief="flat",
                          highlightbackground="#fff" if self._is_dark(color) else "#000",
                          highlightcolor="#fff" if self._is_dark(color) else "#000",
                          highlightthickness=2, bd=0)
            b.pack(side="left", padx=1)
            b.bind("<Button-1>", lambda e, col=color: self.set_menubar_color(col))
            b.bind("<Button-3>", lambda e, c=cidx: self.customize_menubar_swatch(c))
            self.menubar_swatch_buttons.append(b)
        self.menubar_color_btn = tk.Button(self, text="Color", bg=self.menubar_color, fg="white" if self._is_dark(self.menubar_color) else "black", width=6, command=self.choose_menubar_color)
        self.menubar_color_btn.pack(side="left", padx=4)
        self.triangle_btn = tk.Button(self, text="▲", width=2, command=self.toggle_collapse)
        self.triangle_btn.pack(side="right", padx=4)
        self.settings_btn = tk.Button(self, text="Settings", command=self.app.open_settings_panel)
        self.settings_btn.pack(side="right", padx=2)
    def update_bg(self):
        self.menubar_color = self.app.menubar_color
        fg = "white" if self._is_dark(self.menubar_color) else "black"
        for widget in self.winfo_children():
            try:
                widget.config(bg=self.menubar_color, fg=fg)
            except:
                pass
        self.config(bg=self.menubar_color)
        for idx, b in enumerate(self.bg_swatch_buttons):
            color = self.bg_swatches[idx]
            b.config(bg=color,
                     highlightbackground="#fff" if self._is_dark(color) else "#000",
                     highlightcolor="#fff" if self._is_dark(color) else "#000")
        for idx, b in enumerate(self.menubar_swatch_buttons):
            color = self.menubar_swatches[idx]
            b.config(bg=color,
                     highlightbackground="#fff" if self._is_dark(color) else "#000",
                     highlightcolor="#fff" if self._is_dark(color) else "#000")
        self.menubar_color_btn.config(bg=self.menubar_color, fg=fg)
        for btn in self.style_buttons:
            btn.config(bg=self.menubar_color, fg=fg)
    def set_bg_quick_color(self, color):
        self.app.bg_color = color
        self.app.set_background()
        self.app.settings["bg_color"] = color
        save_settings(self.app.settings)
        self.update_bg()
    def customize_bg_swatch(self, cidx):
        color = colorchooser.askcolor(title="Customize Swatch", initialcolor=self.bg_swatches[cidx])
        if color and color[1]:
            self.bg_swatches[cidx] = color[1]
            self.bg_swatch_buttons[cidx].config(bg=color[1])
            self.set_bg_quick_color(color[1])
            self.app.settings["bg_swatches"] = self.bg_swatches
            save_settings(self.app.settings)
            self.update_bg()
    def set_menubar_color(self, color):
        self.app.menubar_color = color
        self.menubar_color = color
        self.app.settings["menubar_color"] = color
        save_settings(self.app.settings)
        self.update_bg()
    def customize_menubar_swatch(self, cidx):
        color = colorchooser.askcolor(title="Customize Menu Bar Swatch", initialcolor=self.menubar_swatches[cidx])
        if color and color[1]:
            self.menubar_swatches[cidx] = color[1]
            self.menubar_swatch_buttons[cidx].config(bg=color[1])
            self.set_menubar_color(color[1])
            self.app.settings["menubar_swatches"] = self.menubar_swatches
            save_settings(self.app.settings)
            self.update_bg()
    def choose_menubar_color(self):
        color = colorchooser.askcolor(title="Choose Menu Bar Color", initialcolor=self.menubar_color)
        if color and color[1]:
            self.set_menubar_color(color[1])
            self.update_bg()
    def change_bg_alpha(self, event=None):
        self.app.bg_alpha = self.bg_alpha_var.get()
        self.app.set_background()
        self.app.settings["bg_alpha"] = self.app.bg_alpha
        save_settings(self.app.settings)
        self.update_bg()
    def toggle_collapse(self):
        if not self.collapsed:
            for widget in self.winfo_children():
                if widget not in [self.triangle_btn]:
                    widget.pack_forget()
            self.triangle_btn.config(text="▼")
            self.collapsed = True
        else:
            for widget in self.winfo_children():
                widget.pack_forget()
            self.build()
            self.triangle_btn.config(text="▲")
            self.collapsed = False
    @staticmethod
    def _is_dark(color):
        color = color.lstrip("#")
        r, g, b = [int(color[i:i+2], 16) for i in (0, 2, 4)]
        return (0.299*r + 0.587*g + 0.114*b) < 128

class TelepromptaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teleprompta")
        self.settings = load_settings()
        self.text = None
        self.style_presets = self.settings["styles"]
        self.bg_color = self.settings["bg_color"]
        self.bg_alpha = self.settings["bg_alpha"]
        self.menubar_color = self.settings.get("menubar_color", DEFAULT_MENUBAR_COLOR)
        self.font_families = sorted(font.families())
        self.swatches = [list(s) for s in self.settings.get("swatches", DEFAULT_SWATCHES)]
        self.bg_swatches = list(self.settings.get("bg_swatches", DEFAULT_BG_SWATCHES))
        self.menubar_swatches = list(self.settings.get("menubar_swatches", DEFAULT_MENUBAR_SWATCHES))
        self.last_script = self.settings.get("last_script", None)
        self.script_dirty = False
        self.current_script_path = self.last_script
        self.create_widgets()
        self.apply_all_style_tags()
        self.set_background()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_last_script()
    def create_widgets(self):
        self.menu_bar = MainMenuBar(self.root, self)
        self.menu_bar.pack(side="top", fill="x")
        self.text = tk.Text(self.root, wrap="word", undo=True, bg=self.bg_color, fg=self.style_presets[0]["color"], insertbackground="white")
        self.text.pack(fill="both", expand=True)
        self.text.insert("1.0", self.settings["text"])
        self.text.tag_configure("body", font=(self.style_presets[0]["font"], self.style_presets[0]["size"]), foreground=self.style_presets[0]["color"])
        self.text.tag_add("body", "1.0", "end")
        self.text.bind("<<Modified>>", self.on_text_modified)
        self.text.bind("<Button-1>", self.save_mouse_index)
        self.text.bind("<B1-Motion>", self.select_text_motion)
        self.text.bind("<ButtonRelease-1>", self.release_mouse_index)
    def save_mouse_index(self, event):
        self.text.mark_set("insert", "@%d,%d" % (event.x, event.y))
        self.text.mark_set("anchor", "insert")
    def select_text_motion(self, event):
        self.text.mark_set("insert", "@%d,%d" % (event.x, event.y))
        self.text.tag_remove("sel", "1.0", "end")
        self.text.tag_add("sel", "anchor", "insert")
    def release_mouse_index(self, event):
        pass
    def on_text_modified(self, event=None):
        self.script_dirty = True
        self.text.edit_modified(False)
    def apply_style_to_selection(self, idx):
        tag = "body" if idx == 0 else f"style{idx+1}"
        try:
            start, end = self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            return
        self.text.tag_remove("body", start, end)
        for i in range(1, len(self.style_presets)):
            self.text.tag_remove(f"style{i+1}", start, end)
        self.text.tag_add(tag, start, end)
        self.script_dirty = True
    def apply_all_style_tags(self):
        self.text.tag_configure("body", font=(self.style_presets[0]["font"], self.style_presets[0]["size"]), foreground=self.style_presets[0]["color"])
        for idx, style in enumerate(self.style_presets[1:], 1):
            tag = f"style{idx+1}"
            self.text.tag_configure(
                tag,
                font=(style["font"], style["size"], "bold"),
                foreground=style["color"]
            )
        if hasattr(self, "menu_bar"):
            for idx, btn in enumerate(self.menu_bar.style_buttons):
                btn.config(text=self.style_presets[idx]["name"])
    def open_settings_panel(self):
        def on_styles_update():
            self.apply_all_style_tags()
            self.text.config(fg=self.style_presets[0]["color"])
            self.settings["styles"] = self.style_presets
            self.settings["swatches"] = self.swatches
            self.settings["bg_swatches"] = self.bg_swatches
            self.settings["menubar_color"] = self.menubar_color
            self.settings["menubar_swatches"] = self.menubar_swatches
            save_settings(self.settings)
            self.script_dirty = True
            if hasattr(self, "menu_bar"):
                self.menu_bar.update_bg()
        def on_bg_update(color, alpha):
            self.bg_color = color
            self.bg_alpha = alpha
            self.set_background()
            self.settings["bg_color"] = color
            self.settings["bg_alpha"] = alpha
            self.settings["swatches"] = self.swatches
            self.settings["bg_swatches"] = self.bg_swatches
            self.settings["menubar_color"] = self.menubar_color
            self.settings["menubar_swatches"] = self.menubar_swatches
            save_settings(self.settings)
            self.script_dirty = True
            if hasattr(self, "menu_bar"):
                self.menu_bar.update_bg()
        def on_menubar_update(color):
            self.menubar_color = color
            self.settings["menubar_color"] = color
            self.settings["menubar_swatches"] = self.menubar_swatches
            save_settings(self.settings)
            if hasattr(self, "menu_bar"):
                self.menu_bar.update_bg()
        SettingsPanel(
            self.root, self.style_presets, self.bg_color, self.bg_alpha, self.menubar_color,
            self.font_families, on_styles_update, on_bg_update, on_menubar_update,
            self.swatches, self.bg_swatches, self.menubar_swatches
        )
    def set_background(self):
        self.root.configure(bg=self.bg_color)
        if self.text:
            self.text.config(bg=self.bg_color)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                if widget != self.menu_bar:
                    widget.config(bg=self.bg_color)
                for child in widget.winfo_children():
                    try:
                        if widget != self.menu_bar:
                            child.config(bg=self.bg_color)
                    except:
                        pass
        self.root.attributes('-alpha', self.bg_alpha)
        self.root.attributes('-topmost', True)
        if hasattr(self, "menu_bar"):
            self.menu_bar.update_bg()
    def on_close(self):
        if self.script_dirty:
            response = messagebox.askyesnocancel("Save Changes?", "Do you want to save changes before exiting?")
            if response is None:
                return
            elif response:
                self.save_script()
        self.settings["text"] = self.text.get("1.0", "end-1c")
        self.settings["swatches"] = self.swatches
        self.settings["bg_swatches"] = self.bg_swatches
        self.settings["menubar_color"] = self.menubar_color
        self.settings["menubar_swatches"] = self.menubar_swatches
        self.settings["last_script"] = self.current_script_path
        save_settings(self.settings)
        self.root.destroy()
    def save_script(self):
        filetypes = [("Teleprompter Script", "*.teleprompt"), ("JSON", "*.json"), ("All Files", "*.*")]
        filename = filedialog.asksaveasfilename(defaultextension=".teleprompt", filetypes=filetypes)
        if filename:
            text = self.text.get("1.0", "end-1c")
            tags = self.get_tagged_ranges()
            export_script(filename, text, tags)
            self.current_script_path = filename
            self.script_dirty = False
            self.settings["last_script"] = filename
            save_settings(self.settings)
    def open_script(self):
        if self.script_dirty:
            response = messagebox.askyesnocancel("Save Changes?", "Do you want to save changes before opening another script?")
            if response is None:
                return
            elif response:
                self.save_script()
        filetypes = [("Teleprompter Script", "*.teleprompt"), ("JSON", "*.json"), ("All Files", "*.*")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            text, tags = import_script(filename)
            self.text.delete("1.0", "end")
            self.text.insert("1.0", text)
            for tag in self.text.tag_names():
                self.text.tag_remove(tag, "1.0", "end")
            for tag, ranges in tags.items():
                for start, end in ranges:
                    self.text.tag_add(tag, start, end)
            self.current_script_path = filename
            self.script_dirty = False
            self.settings["last_script"] = filename
            save_settings(self.settings)
    def load_last_script(self):
        if self.last_script and os.path.exists(self.last_script):
            text, tags = import_script(self.last_script)
            self.text.delete("1.0", "end")
            self.text.insert("1.0", text)
            for tag in self.text.tag_names():
                self.text.tag_remove(tag, "1.0", "end")
            for tag, ranges in tags.items():
                for start, end in ranges:
                    self.text.tag_add(tag, start, end)
            self.current_script_path = self.last_script
            self.script_dirty = False
    def get_tagged_ranges(self):
        tag_ranges = {}
        for tag in self.text.tag_names():
            ranges = []
            tag_indices = self.text.tag_ranges(tag)
            for i in range(0, len(tag_indices), 2):
                start = str(tag_indices[i])
                end = str(tag_indices[i+1])
                ranges.append((start, end))
            if ranges:
                tag_ranges[tag] = ranges
        return tag_ranges

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-topmost', True)
    app = TelepromptaApp(root)
    root.geometry("900x600")
    root.mainloop()
