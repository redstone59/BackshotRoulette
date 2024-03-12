import tkinter as tk
from tkinter import ttk
from backshot import *
import time

def font(size: int, bold = False):
    font_name = "Arial Black" if bold else "Arial"
    return (font_name, size)

def get_int_value(widget: tk.Spinbox):
    value = widget.get()
    if value.isdigit():
        return int(value)
    raise ValueError()

def string_to_item(item_string: str):
    item_string = item_string.lower()
    items = []
    
    for char in item_string:
        match char:
            case "h":
                items += [Items.HANDCUFFS]
            case "s":
                items += [Items.HAND_SAW]
            case "c":
                items += [Items.CIGARETTES]
            case "b":
                items += [Items.BEER]
            case "m":
                items += [Items.MAGNIFYING_GLASS]
    
    return items

class GraphicBackshot: # ha ha ha ha ha
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Backshot Roulette GUI")
        self.window.geometry("480x720")
        self.window.resizable(True, False)
        
        self.set_up_labels()
        self.set_up_inputs()
    
    def set_up_inputs(self):
        self.maximum_health = tk.Spinbox(self.window,
                                         from_ = 2,
                                         to = 5,
                                         font = font(16),
                                         state = "readonly"
                                         )
        self.maximum_health.grid(row = 1, column = 1)
        self.dealer_health = tk.Spinbox(self.window,
                                        from_ = 1,
                                        to = 5,
                                        font = font(16),
                                        state = "readonly"
                                        )
        self.dealer_health.grid(row = 2, column = 1)
        self.player_health = tk.Spinbox(self.window,
                                        from_ = 1,
                                        to = 5,
                                        font = font(16),
                                        state = "readonly"
                                        )
        self.player_health.grid(row = 3, column = 1)
        
        self.live_shells = tk.Spinbox(self.window,
                                      from_ = 0,
                                      to = 4,
                                      font = font(16),
                                      state = "readonly"
                                      )
        self.live_shells.grid(row = 5, column = 1)
        self.blank_shells = tk.Spinbox(self.window,
                                       from_ = 0,
                                       to = 4,
                                       font = font(16),
                                       state = "readonly"
                                       )
        self.blank_shells.grid(row = 6, column = 1)
        
        self.dealer_items = tk.Entry(self.window,
                                     font = font(16)
                                     )
        self.dealer_items.grid(row = 8, column = 1)
        self.player_items = tk.Entry(self.window,
                                     font = font(16)
                                     )
        self.player_items.grid(row = 9, column = 1)
        
        self.handcuffed = ttk.Combobox(self.window,
                                          values = ["Not handcuffed", "Has already skipped turn", "Has not skipped turn"],
                                          font = font(16),
                                          state = "readonly"
                                          )
        self.handcuffed.current(0)
        self.handcuffed.grid(row = 11, column = 1)
        
        self.gun_is_sawed = tk.IntVar()
        self.is_players_turn = tk.IntVar(value = 1)
        
        self.current_shell = ttk.Combobox(self.window,
                                          values = ["Unknown", "Live", "Blank"],
                                          font = font(16),
                                          state = "readonly"
                                          )
        self.current_shell.current(0)
        self.current_shell.grid(row = 12, column = 1)
        
        self.sawed_button = tk.Checkbutton(self.window,
                                           variable = self.gun_is_sawed,
                                           onvalue = 1,
                                           offvalue = 0
                                           )
        self.sawed_button.grid(row = 13, column = 1)
        
        self.turn_button = tk.Checkbutton(self.window,
                                           variable = self.is_players_turn,
                                           onvalue = 1,
                                           offvalue = 0
                                           )
        self.turn_button.grid(row = 14, column = 1)
        
        tk.Button(self.window,
                  text = "Search",
                  font = font(20),
                  command = lambda: self.search()
                  ).grid(row = 15, column = 0, columnspan = 2)
        
    
    def set_up_labels(self):
        tk.Label(self.window,
                 text = "Backshot Roulette GUI",
                 font = font(32)
                 ).grid(row = 0, column = 0, columnspan = 2, sticky = "N")
        tk.Label(self.window,
                 text = "Maximum Health",
                 font = font(20)
                 ).grid(row = 1, column = 0, sticky = "E")
        tk.Label(self.window,
                 text = "Dealer's Health",
                 font = font(20)
                 ).grid(row = 2, column = 0, sticky = "E")
        tk.Label(self.window,
                 text = "Player's Health",
                 font = font(20)
                 ).grid(row = 3, column = 0, sticky = "E")
        tk.Label(self.window).grid(row = 4, column = 0)
        tk.Label(self.window,
                 text = "# Live Shells",
                 font = font(20)
                 ).grid(row = 5, column = 0, sticky = "E")
        tk.Label(self.window,
                 text = "# Blank Shells",
                 font = font(20)
                 ).grid(row = 6, column = 0, sticky = "E")
        tk.Label(self.window).grid(row = 7, column = 0)
        tk.Label(self.window,
                 text = "Dealer Items",
                 font = font(20)
                 ).grid(row = 8, column = 0, sticky = "E")
        tk.Label(self.window,
                 text = "Player Items",
                 font = font(20)
                 ).grid(row = 9, column = 0, sticky = "E")
        tk.Label(self.window).grid(row = 10, column = 0)
        tk.Label(self.window,
                 text = "Handcuffed?",
                 font = font(20)
                 ).grid(row = 11, column = 0, sticky = "E")
        tk.Label(self.window,
                 text = "Current Shell?",
                 font = font(20)
                 ).grid(row = 12, column = 0, sticky = "E")
        tk.Label(self.window,
                 text = "Sawed Gun?",
                 font = font(20)
                 ).grid(row = 13, column = 0, sticky = "E")
        tk.Label(self.window,
                 text = "Player's Turn?",
                 font = font(20)
                 ).grid(row = 14, column = 0, sticky = "E")
        
        self.result_label = tk.Label(self.window,
                                text = "",
                                font = font(18)
                                )
        self.result_label.grid(row = 16, column = 0, columnspan = 2)
        
    def search(self):
        self.result_label["text"] = "Searching..."
        
        is_players_turn = bool(self.is_players_turn.get())
        max_health = get_int_value(self.maximum_health)
        dealer_health = max(max_health, get_int_value(self.dealer_health))
        player_health = max(max_health, get_int_value(self.player_health))
        lives = get_int_value(self.live_shells)
        blanks = get_int_value(self.blank_shells)
        dealer_items = string_to_item(self.dealer_items.get())[:8]
        player_items = string_to_item(self.player_items.get())[:8]
        
        position = BuckshotRouletteMove(is_players_turn,
                                max_health, dealer_health, player_health,
                                lives, blanks,
                                dealer_items,
                                player_items)
        
        match self.current_shell.get():
            case "Unknown":
                current_shell = None
            case "Live":
                current_shell = "live"
            case "Blank":
                current_shell = "blank"
        
        position.current_shell = current_shell
        
        match self.handcuffed.get():
            case "Not handcuffed":
                handcuffed = 0
            case "Has already skipped turn":
                handcuffed = 1
            case "Has not skipped turn":
                handcuffed = 2
        
        position.handcuffed = handcuffed
        position.gun_is_sawed = bool(self.gun_is_sawed.get())
        
        self.result_label["text"] = BackshotRoulette().search(18, position).gui_string()
    
    def start(self):
        self.window.mainloop()

GraphicBackshot().start()