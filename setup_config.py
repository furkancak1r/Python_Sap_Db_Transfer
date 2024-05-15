import tkinter as tk
from source_config_gui import add_db_entries
from config_manager import read_config


def setup_entries(root, font_specs):
    source_initial_config = read_config('source')
    target_initial_config = read_config('target')
    entries_source = add_db_entries(
        root, font_specs, 'source', source_initial_config)
    entries_target = add_db_entries(
        root, font_specs, 'target', target_initial_config)
    return entries_source, entries_target
