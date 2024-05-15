import tkinter as tk  # tkinter'ı içe aktar
from config_manager import read_config  # read_config fonksiyonunu içe aktar

def update_button_state(entries_source, entries_target, save_button, update_button, delete_button):
    # Checks configuration presence for both source and target
    initial_config_source = read_config("source")
    initial_config_target = read_config("target")

    # Determine button states based on the presence of either configuration
    config_exists = initial_config_source or initial_config_target
    save_button.config(state=tk.DISABLED if config_exists else tk.NORMAL)
    update_button.config(state=tk.NORMAL if config_exists else tk.DISABLED)
    delete_button.config(state=tk.NORMAL if config_exists else tk.DISABLED)

    # Update password button state based on the source password field
    password_button_source = entries_source.get('password_button')
    if password_button_source:
        password_button_source.config(state=tk.NORMAL if entries_source['password'].get() else tk.DISABLED)

    # Similarly update for target, if necessary
    password_button_target = entries_target.get('password_button')
    if password_button_target:
        password_button_target.config(state=tk.NORMAL if entries_target['password'].get() else tk.DISABLED)
