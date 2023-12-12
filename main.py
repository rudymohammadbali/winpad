import datetime
import os
import re
import sys
import tkinter
import webbrowser

import customtkinter as ctk
from PIL import Image
from customtkinter import filedialog as fd

from assets.ctk_dropdown import CTkScrollableDropdownFrame
from assets.settings_handler import SettingsHandler
from assets.title_menu import CTkMenuBar, CustomDropdownMenu

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
icons = {
    "close": ctk.CTkImage(light_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\up_black.png"),
                          dark_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\up_white.png"), size=(20, 20)),
    "open": ctk.CTkImage(light_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\down_black.png"),
                         dark_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\down_white.png"), size=(20, 20)),
    "theme": ctk.CTkImage(light_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\theme_black.png"),
                          dark_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\theme_white.png"), size=(20, 20)),
    "font": ctk.CTkImage(light_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\font_black.png"),
                         dark_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\font_white.png"), size=(20, 20)),
    "close_window": ctk.CTkImage(light_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\close_black.png"),
                                 dark_image=Image.open(f"{CURRENT_PATH}\\assets\\icons\\close_white.png"),
                                 size=(20, 20))
}
LOGO_PATH = f"{CURRENT_PATH}\\assets\\icons\\logo.ico"

DROPDOWN = {
    "x": 0,
    "alpha": 1.0,
    "corner_radius": 5,
    "frame_corner_radius": 5,
    "hover": False,
    "justify": "left"
}

ctk.set_default_color_theme(f"{CURRENT_PATH}\\assets\\theme.json")


class CTkDialog(ctk.CTkToplevel):
    def __init__(self,
                 master: any = None,
                 width: int = 400,
                 height: int = 200,
                 title: str = "Go to Line",
                 option: str = "goto",
                 font: tuple = None,
                 topmost: bool = True):

        super().__init__()

        self.event = None
        self.old_y = None
        self.old_x = None
        self.selected_option = None
        self.selected_button = None
        self.master_window = master

        self.width = 250 if width < 250 else width
        self.height = 150 if height < 150 else height

        if self.master_window is None:
            self.spawn_x = int((self.winfo_screenwidth() - self.width) / 2)
            self.spawn_y = int((self.winfo_screenheight() - self.height) / 2)
        else:
            self.spawn_x = int(
                self.master_window.winfo_width() * .5 + self.master_window.winfo_x() - .5 * self.width + 7)
            self.spawn_y = int(
                self.master_window.winfo_height() * .5 + self.master_window.winfo_y() - .5 * self.height + 20)

        self.after(10)
        self.geometry(f"{self.width}x{self.height}+{self.spawn_x}+{self.spawn_y}")
        self.title(title)
        self.resizable(width=False, height=False)

        self.overrideredirect(True)

        if topmost:
            self.attributes("-topmost", True)
        else:
            self.transient(self.master_window)

        if sys.platform.startswith("win"):
            self.transparent_color = self._apply_appearance_mode(self.cget("fg_color"))
            self.attributes("-transparentcolor", self.transparent_color)
        elif sys.platform.startswith("darwin"):
            self.transparent_color = 'systemTransparent'
            self.attributes("-transparent", True)
        else:
            self.transparent_color = '#000001'

        self.lift()

        self.config(background=self.transparent_color)
        self.protocol("WM_DELETE_WINDOW", self.hide_dialog)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.x = self.winfo_x()
        self.y = self.winfo_y()
        self._title = title
        self.font = font

        self.frame_top = ctk.CTkFrame(self, width=self.width, corner_radius=5, border_width=0)
        self.frame_top.grid(sticky="nsew")
        self.frame_top.bind("<B1-Motion>", self.move_window)
        self.frame_top.bind("<ButtonPress-1>", self.old_xy_set)

        self.frame_top.grid_columnconfigure(0, weight=1)
        self.frame_top.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self.frame_top, width=1, text=self._title, font=("", 18, "normal"))
        self.title_label.grid(row=0, column=0, sticky="nw", padx=20, pady=(20, 5))
        self.title_label.bind("<B1-Motion>", self.move_window)
        self.title_label.bind("<ButtonPress-1>", self.old_xy_set)

        if option == "goto":
            self.nb_label = ctk.CTkLabel(self.frame_top, text="Line number")
            self.nb_label.grid(row=1, column=0, sticky="nw", padx=20, pady=5)
            self.nb_entry = ctk.CTkEntry(self.frame_top, placeholder_text="1234", border_width=0,
                                         corner_radius=5)
            self.nb_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=5, columnspan=2)

            self.go_btn = ctk.CTkButton(self.frame_top, text="Go to", corner_radius=5,
                                        command=lambda: self.go_to_callback(self.nb_entry.get()))
            self.go_btn.grid(row=3, column=0, sticky="ew", padx=(20, 5), pady=20)
            self.cancel_btn = ctk.CTkButton(self.frame_top, text="Cancel", corner_radius=5,
                                            command=self.hide_dialog)
            self.cancel_btn.grid(row=3, column=1, sticky="ew", padx=(5, 20), pady=20)
        elif option == "replace":
            self.find_entry = ctk.CTkEntry(self.frame_top, placeholder_text="Find", border_width=0,
                                           corner_radius=5)
            self.find_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=5, columnspan=2)

            self.replace_entry = ctk.CTkEntry(self.frame_top, placeholder_text="Replace", border_width=0,
                                              corner_radius=5)
            self.replace_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=5, columnspan=2)

            self.replace_btn = ctk.CTkButton(self.frame_top, text="Replace all", corner_radius=5,
                                             command=lambda: self.replace_callback(old=self.find_entry.get(),
                                                                                   new=self.replace_entry.get()))
            self.replace_btn.grid(row=3, column=0, sticky="ew", padx=(20, 5), pady=20)
            self.cancel_btn = ctk.CTkButton(self.frame_top, text="Cancel", corner_radius=5,
                                            command=self.hide_dialog)
            self.cancel_btn.grid(row=3, column=1, sticky="ew", padx=(5, 20), pady=20)
        elif option == "find":
            self.find_entry2 = ctk.CTkEntry(self.frame_top, placeholder_text="Find", border_width=0,
                                            corner_radius=5)
            self.find_entry2.grid(row=1, column=0, sticky="ew", padx=20, pady=20, columnspan=2)

            self.find_btn = ctk.CTkButton(self.frame_top, text="Find all", corner_radius=5,
                                          command=lambda: self.find_callback(self.find_entry2.get()))
            self.find_btn.grid(row=2, column=0, sticky="ew", padx=(20, 5), pady=20)
            self.cancel_btn = ctk.CTkButton(self.frame_top, text="Cancel", corner_radius=5,
                                            command=self.hide_dialog)
            self.cancel_btn.grid(row=2, column=1, sticky="ew", padx=(5, 20), pady=20)

        if self.winfo_exists():
            self.grab_set()

    def go_to_callback(self, line_nb):
        self.master_window.goto_func(line_nb)
        self.after(100, self.hide_dialog)

    def replace_callback(self, old, new):
        self.master_window.replace_func(old, new)
        self.after(100, self.hide_dialog)

    def find_callback(self, text):
        self.master_window.find_func(text)
        self.after(100, self.hide_dialog)

    def old_xy_set(self, event):
        self.old_x = event.x
        self.old_y = event.y

    def move_window(self, event):
        self.y = event.y_root - self.old_y
        self.x = event.x_root - self.old_x
        self.geometry(f'+{self.x}+{self.y}')

    def hide_dialog(self):
        self.grab_release()
        self.destroy()


def open_help():
    webbrowser.open("https://github.com/iamironman0/winpad/discussions/categories/q-a")


class WinPad(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("710x710")
        self.minsize(width=710, height=710)
        self.title("WinPad")
        self.iconbitmap(LOGO_PATH)
        self.center_window(710, 710)

        self.settings_handler = SettingsHandler()
        self.loaded_settings = self.settings_handler.load_settings()

        self.fonts = list(tkinter.font.families())
        self.styles = ["Normal", "Italic", "Bold", "Underline", "Overstrike"]
        self.sizes = [str(i) for i in range(8, 49)]
        self.check_var = ctk.StringVar(value="on")

        self.file_path = None

        self.ln_col_label = None
        self.status_bar_shown = True
        self.status_frame = None
        self.error_message = None
        self.top = None
        self.preview_label = None
        self.size_option = None
        self.style_option = None
        self.family_option = None
        self.font_frame2 = None
        self.font_frame1 = None
        self.font_update_btn = None
        self.font_frame3 = None
        self.theme_update_btn = None
        self.radio_var = tkinter.Variable(value=self.loaded_settings["theme"])
        self.textbox = None
        self.theme_frame3 = None
        self.settings_frame = None
        self.grid_columnconfigure(0, weight=1)

        ctk.set_appearance_mode(self.loaded_settings["theme"])

        self.grid_rowconfigure(1, weight=1)

        self.title_menu()
        self.text_editor()
        self.status_bar()

    def title_menu(self):
        menu = CTkMenuBar(self, width=50, padx=20, pady=5, border_width=0, bg_color=("gray90", "gray13"))

        button_1 = menu.add_cascade("File", anchor="center", corner_radius=3)
        button_2 = menu.add_cascade("Edit", anchor="center", corner_radius=3)
        button_3 = menu.add_cascade("View", anchor="center", corner_radius=3)
        menu.add_cascade("Settings", command=self.settings_ui, anchor="center", corner_radius=3)

        dropdown1 = CustomDropdownMenu(widget=button_1, border_width=0, corner_radius=8)
        dropdown1.add_option(option="New Window", command=self.new_window)
        dropdown1.add_option(option="Open", command=self.open_file)
        dropdown1.add_option(option="Save", command=self.save)
        dropdown1.add_option(option="Save as", command=self.save_as)
        dropdown1.add_separator()
        dropdown1.add_option(option="Exit", command=self.destroy_window)

        dropdown2 = CustomDropdownMenu(widget=button_2, border_width=0, corner_radius=8)
        dropdown2.add_option(option="Undo", command=self.undo)
        dropdown2.add_option(option="Cut", command=self.cut)
        dropdown2.add_option(option="Copy", command=self.copy)
        dropdown2.add_option(option="Pase", command=self.paste)
        dropdown2.add_option(option="Delete", command=self.delete)
        dropdown2.add_separator()
        dropdown2.add_option(option="Find", command=self.find_window)
        dropdown2.add_option(option="Replace", command=self.replace_window)
        dropdown2.add_option(option="Go to", command=self.goto_window)
        dropdown2.add_separator()
        dropdown2.add_option(option="Select all", command=self.select_all)
        dropdown2.add_option(option="Time/Date", command=self.insert_date)

        dropdown3 = CustomDropdownMenu(widget=button_3, border_width=0, corner_radius=8)
        zoom_submenu = dropdown3.add_submenu("Zoom                                  >")
        zoom_submenu.add_option("Zoom in", command=self.zoom_in)
        zoom_submenu.add_option("Zoom out", command=self.zoom_out)
        zoom_submenu.add_option("Restore default zoom", command=self.zoom_reset)
        dropdown3.add_option(option="Status bar", command=self.toggle_status_bar)

    def text_editor(self):
        loaded_settings = self.settings_handler.load_settings()
        font = (loaded_settings["family"], int(loaded_settings["size"]), loaded_settings["style"])
        word_wrap = loaded_settings.get("word_wrap", "word")
        self.textbox = ctk.CTkTextbox(self, font=font, undo=True, wrap=word_wrap, border_width=0,
                                      fg_color="transparent")
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.textbox.bind('<KeyRelease>', self.update_status)

    def settings_ui(self):
        try:
            self.textbox.destroy()
            widgets = self.status_frame.winfo_children()
            for widget in widgets:
                widget.destroy()
            self.status_frame.destroy()
        except tkinter.TclError:
            pass
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=0)
        self.settings_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew", rowspan=2)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self.settings_frame, text="Settings", font=("", 32, "bold"))
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        close_btn = ctk.CTkButton(self.settings_frame, text="", font=("", 18), width=50, height=30,
                                  command=self.destroy_settings, hover=False, fg_color="transparent",
                                  image=icons["close_window"])
        close_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        theme_frame1 = ctk.CTkFrame(self.settings_frame, height=60, corner_radius=0, border_width=0)
        theme_frame1.grid(row=1, column=0, sticky="nsew", padx=(20, 0), pady=(10, 5))
        theme_frame2 = ctk.CTkFrame(self.settings_frame, height=60, corner_radius=0, border_width=0)
        theme_frame2.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=(10, 5))
        self.theme_frame3 = ctk.CTkFrame(self.settings_frame, height=60, corner_radius=3, border_width=0)

        theme_label1 = ctk.CTkLabel(theme_frame1, text=" App theme", font=("", 16), image=icons["theme"],
                                    compound="left")
        theme_label1.grid(row=0, column=0, sticky="w", padx=20, pady=(5, 0))

        theme_label2 = ctk.CTkLabel(theme_frame1, text="Select which app theme to display", font=("", 13))
        theme_label2.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 5))

        self.theme_update_btn = ctk.CTkButton(theme_frame2, text="", width=50, height=25, corner_radius=3,
                                              image=icons["open"],
                                              fg_color="transparent", hover_color=("gray90", "gray13"),
                                              command=self.update_theme_view)
        self.theme_update_btn.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.font_frame1 = ctk.CTkFrame(self.settings_frame, height=60, corner_radius=0, border_width=0)
        self.font_frame1.grid(row=4, column=0, sticky="nsew", padx=(20, 0), pady=(10, 5))
        self.font_frame2 = ctk.CTkFrame(self.settings_frame, height=60, corner_radius=0, border_width=0)
        self.font_frame2.grid(row=4, column=1, sticky="nsew", padx=(0, 20), pady=(10, 5))
        self.font_frame3 = ctk.CTkFrame(self.settings_frame, height=60, corner_radius=3, border_width=0)

        font_label1 = ctk.CTkLabel(self.font_frame1, text=" Font", font=("", 16), image=icons["font"],
                                   compound="left")
        font_label1.grid(row=0, column=0, sticky="w", padx=20, pady=20)

        self.font_update_btn = ctk.CTkButton(self.font_frame2, text="", width=50, height=25, corner_radius=3,
                                             image=icons["open"],
                                             fg_color="transparent", hover_color=("gray90", "gray13"),
                                             command=self.update_font_view)
        self.font_update_btn.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        about_label = ctk.CTkLabel(self.settings_frame, text="About this app", font=("", 16, "bold"))
        about_label.grid(row=6, column=0, sticky="w", padx=40, pady=(20, 2))
        version_label = ctk.CTkLabel(self.settings_frame, text="WinPad 23.12.09", font=("", 12), height=2)
        version_label.grid(row=7, column=0, sticky="w", padx=40, pady=(2, 0))
        copyright_label = ctk.CTkLabel(self.settings_frame, text="@ 2023 iamironman", font=("", 12), height=2)
        copyright_label.grid(row=8, column=0, sticky="w", padx=40, pady=(0, 20))

        help_btn = ctk.CTkButton(self.settings_frame, text="Help", corner_radius=3, command=open_help)
        help_btn.grid(row=9, column=0, sticky="w", padx=40, pady=0)

    def update_font_view(self):
        loaded_settings = self.settings_handler.load_settings()
        if self.font_update_btn.cget("corner_radius") == 3:
            self.font_update_btn.configure(image=icons["close"])
            self.font_update_btn.configure(corner_radius=4)
            self.font_frame3.grid(row=5, column=0, sticky="nsew", padx=20, pady=(0, 10), columnspan=2)
            self.font_frame3.grid_columnconfigure(0, weight=1)

            label1 = ctk.CTkLabel(self.font_frame3, text="Family", font=("", 13))
            label1.grid(row=0, column=0, sticky="w", padx=40, pady=(20, 10))
            self.family_option = ctk.CTkOptionMenu(self.font_frame3, width=200)
            self.family_option.grid(row=0, column=1, sticky="e", padx=40, pady=(20, 10))
            CTkScrollableDropdownFrame(self.family_option, values=self.fonts, **DROPDOWN,
                                       command=lambda new_value=self.family_option: self.update_callback(
                                           key_name="family", value=f"{new_value}"))
            self.family_option.set(loaded_settings["family"].capitalize())

            label2 = ctk.CTkLabel(self.font_frame3, text="Style", font=("", 13))
            label2.grid(row=1, column=0, sticky="w", padx=40, pady=10)
            self.style_option = ctk.CTkOptionMenu(self.font_frame3, width=200)
            self.style_option.grid(row=1, column=1, sticky="e", padx=40, pady=10)
            CTkScrollableDropdownFrame(self.style_option, values=self.styles, **DROPDOWN,
                                       command=lambda new_value=self.style_option: self.update_callback(
                                           key_name="style", value=f"{new_value}"))
            self.style_option.set(loaded_settings["style"].capitalize())

            label3 = ctk.CTkLabel(self.font_frame3, text="Size", font=("", 13))
            label3.grid(row=2, column=0, sticky="w", padx=40, pady=(10, 20))
            self.size_option = ctk.CTkOptionMenu(self.font_frame3, width=200)
            self.size_option.grid(row=2, column=1, sticky="e", padx=40, pady=(10, 20))
            CTkScrollableDropdownFrame(self.size_option, values=self.sizes, **DROPDOWN,
                                       command=lambda new_value=self.size_option: self.update_callback(
                                           key_name="size", value=f"{new_value}"))
            self.size_option.set(loaded_settings["size"])

            label4 = ctk.CTkLabel(self.font_frame3, text="Word Wrap", font=("", 13))
            label4.grid(row=3, column=0, sticky="w", padx=40, pady=(10, 20))
            wrap_check = ctk.CTkCheckBox(self.font_frame3, text="", onvalue="word", offvalue="none",
                                         variable=self.check_var,
                                         command=self.update_check)
            wrap_check.grid(row=3, column=1, sticky="e", padx=40, pady=(10, 20))
            if loaded_settings["word_wrap"] == "word":
                wrap_check.select()
            else:
                wrap_check.deselect()

            self.preview_label = ctk.CTkLabel(self.font_frame3, text="The sound of ocean waves calms my soul.")
            self.preview_label.grid(row=4, column=0, sticky="nsew", padx=40, pady=20, columnspan=2)
            self.update_preview()

        else:
            self.font_frame3.grid_forget()
            self.font_update_btn.configure(image=icons["open"])
            self.font_update_btn.configure(corner_radius=3)

    def update_check(self):
        new_value = self.check_var.get()
        self.settings_handler.save_settings({"word_wrap": new_value})
        self.textbox.destroy()

    def update_callback(self, key_name: str, value: str):
        new_value = str(value).lower()
        self.settings_handler.save_settings({key_name: new_value})

        if key_name == "family":
            self.family_option.set(value)
        elif key_name == "style":
            self.style_option.set(value)
        elif key_name == "size":
            self.size_option.set(value)

        self.update_preview()

    def update_preview(self):
        loaded_settings = self.settings_handler.load_settings()
        font = (loaded_settings["family"], int(loaded_settings["size"]), loaded_settings["style"])
        self.preview_label.configure(font=font)

    def update_theme(self):
        get_theme = self.radio_var.get()
        ctk.set_appearance_mode(get_theme)
        self.settings_handler.save_settings({"theme": get_theme})

    def update_theme_view(self):
        if self.theme_update_btn.cget("corner_radius") == 3:
            self.theme_update_btn.configure(image=icons["close"])
            self.theme_update_btn.configure(corner_radius=4)
            self.theme_frame3.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10), columnspan=2)

            radiobutton_1 = ctk.CTkRadioButton(self.theme_frame3, text="Light", value="light", variable=self.radio_var,
                                               command=self.update_theme)
            radiobutton_1.grid(row=0, column=0, sticky="w", padx=40, pady=10)

            radiobutton_2 = ctk.CTkRadioButton(self.theme_frame3, text="Dark", value="dark", variable=self.radio_var,
                                               command=self.update_theme)
            radiobutton_2.grid(row=1, column=0, sticky="w", padx=40, pady=10)

            radiobutton_3 = ctk.CTkRadioButton(self.theme_frame3, text="Use system setting", value="system",
                                               variable=self.radio_var,
                                               command=self.update_theme)
            radiobutton_3.grid(row=2, column=0, sticky="w", padx=40, pady=10)
        else:
            self.theme_frame3.grid_forget()
            self.theme_update_btn.configure(image=icons["open"])
            self.theme_update_btn.configure(corner_radius=3)

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_height = int((screen_width / 2) - (width / 2))
        window_width = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{window_height}+{window_width}")

    def update_status(self, event=None):
        if self.status_bar_shown:
            line, column = self.textbox.index("insert").split(".")
            self.ln_col_label.configure(text="Ln {}, Col {}".format(line, column))

    def toggle_status_bar(self):
        if self.status_bar_shown:
            widgets = self.status_frame.winfo_children()
            for widget in widgets:
                widget.destroy()
            self.status_frame.destroy()
            self.status_bar_shown = False
        else:
            self.status_bar()

    def status_bar(self):
        self.status_frame = ctk.CTkFrame(self, height=50, corner_radius=0, border_width=0)
        self.status_frame.grid(row=2, column=0, padx=0, pady=0, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        line, column = self.textbox.index("insert").split(".")
        self.ln_col_label = ctk.CTkLabel(self.status_frame, text="Ln {}, Col {}".format(line, column), font=("", 11))
        self.ln_col_label.grid(row=0, column=0, padx=20, pady=0, sticky="w")

        font_size = self.textbox.cget("font")[1]
        zoom_percent = int((int(font_size) / 14) * 100)
        zoom_label = ctk.CTkLabel(self.status_frame, text=f"Zoom: {zoom_percent}%", font=("", 11))
        zoom_label.grid(row=0, column=1, padx=20, pady=0, sticky="ew")

        encoding_label = ctk.CTkLabel(self.status_frame, text="CRLF", font=("", 11))
        encoding_label.grid(row=0, column=3, padx=20, pady=0, sticky="ew")

        encoding_label = ctk.CTkLabel(self.status_frame, text="UTF-8", font=("", 11))
        encoding_label.grid(row=0, column=4, padx=20, pady=0, sticky="e")

        self.status_bar_shown = True

    def zoom_in(self):
        current_font = self.textbox.cget("font")
        new_font_size = current_font[1] + 2
        self.textbox.configure(font=(current_font[0], new_font_size, current_font[2]))

    def zoom_out(self):
        current_font = self.textbox.cget("font")
        new_font_size = int(current_font[1]) - 2
        if new_font_size > 9:
            self.textbox.configure(font=(current_font[0], new_font_size, current_font[2]))

    def zoom_reset(self):
        loaded_settings = self.settings_handler.load_settings()
        self.textbox.configure(font=(loaded_settings["family"], int(loaded_settings["size"]), loaded_settings["style"]))

    def find_window(self):
        CTkDialog(master=self, title="Find text", option="find")

    def find_func(self, text):
        self.textbox.tag_remove('sel', '1.0', "end")
        if text:
            idx = '1.0'
            while 1:
                idx = self.textbox.search(text, idx, nocase=1, stopindex="end")
                if not idx:
                    break
                last_idx = '%s+%dc' % (idx, len(text))
                self.textbox.tag_add('sel', idx, last_idx)
                idx = last_idx
                self.textbox.focus_set()

    def replace_window(self):
        CTkDialog(master=self, title="Replace text", option="replace")

    def replace_func(self, old, new):
        text_content = self.textbox.get("1.0", "end")
        text_content = re.sub(r'\b' + old + r'\b', new, text_content)
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text_content)

    def insert_date(self):
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)
        self.textbox.insert("end", f" {now}")

    def goto_window(self):
        CTkDialog(master=self, title="Go to Line", option="goto")

    def goto_func(self, line_number):
        try:
            self.textbox.mark_set("insert", f"{line_number}.0")
            self.textbox.see("insert")
            self.textbox.focus_set()
        except tkinter.TclError:
            pass

    def select_all(self):
        self.textbox.tag_add("sel", "0.0", "end")
        self.textbox.focus_set()

    def paste(self):
        # Paste from the clipboard
        text_to_paste = self.clipboard_get()
        self.textbox.insert(tkinter.INSERT, text_to_paste)

    def delete(self):
        if self.textbox.tag_ranges("sel"):
            self.textbox.delete("sel.first", "sel.last")

    def copy(self):
        if self.textbox.tag_ranges("sel"):
            text_to_copy = self.textbox.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)

    def cut(self):
        if self.textbox.tag_ranges("sel"):
            text_to_cut = self.textbox.get("sel.first", "sel.last")
            self.textbox.delete("sel.first", "sel.last")

            self.clipboard_clear()
            self.clipboard_append(text_to_cut)

    def undo(self):
        try:
            self.textbox.edit_undo()
        except tkinter.TclError:
            pass

    def save_as(self):
        file_path = fd.asksaveasfilename(defaultextension=".txt", initialfile="Untitled",
                                         filetypes=[("Text documents", "*.txt"), ("All files (*.*)", "*.*")])
        if file_path:
            text = self.textbox.get("0.0", "end")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)

    def save(self):
        if self.file_path:
            text = self.textbox.get("0.0", "end")
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(text)

    def open_file(self):
        self.file_path = fd.askopenfilename()
        if self.file_path:
            with open(self.file_path, "r", encoding="utf-8") as file:
                text = file.read()

            self.textbox.insert("0.0", text)

    @staticmethod
    def new_window():
        window = WinPad()
        window.mainloop()

    def destroy_settings(self):
        self.settings_frame.destroy()
        self.text_editor()
        if self.status_bar_shown:
            self.status_bar()

    def destroy_window(self):
        self.destroy()


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        app = WinPad()
        app.mainloop()
    else:
        print("This app only support Windows system!")
