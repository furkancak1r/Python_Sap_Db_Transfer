import tkinter as tk

def add_db_entries(root, font_specs, config_type, initial_config={}):
    row_offset = 0 if config_type == 'source' else 6  # Adjust offset depending on source or target
    labels = {
        "server": f"{config_type.capitalize()} Server:",
        "database": f"{config_type.capitalize()} Database:",
        "username": f"{config_type.capitalize()} Username:",
        "password": f"{config_type.capitalize()} Password:",
    }
    
    # Only add these fields if 'config_type' is 'source'
    if config_type == 'source':
        labels.update({
            "column_name": "Source Column Name:",  # Column name field specifically for the source
            "transfer_value": "Source Transfer Value:"  # Transfer value field specifically for the source
        })
    elif config_type == 'target':
        labels.update({
            "target_column_name": "Target Column Name:",  # Column name field specifically for the target
        })

    entries = {}
    for idx, (key, label) in enumerate(labels.items()):
        label_widget = tk.Label(root, text=label, font=font_specs)
        label_widget.grid(row=idx + row_offset, column=0, sticky='w', padx=10, pady=5)
        
        entry = tk.Entry(root, font=font_specs, show="*" if key == "password" else "")
        entry.grid(row=idx + row_offset, column=1, padx=10, pady=5)
        
        if key == "password":
            button_text = tk.StringVar(value="Show")
            show_button = tk.Button(root, textvariable=button_text, command=lambda e=entry, b=button_text: toggle_password_visibility(e, b))
            show_button.grid(row=idx + row_offset, column=2, padx=10)
            if not initial_config.get(key, ""):
                show_button.config(state=tk.DISABLED)
        if initial_config:
            entry.insert(0, initial_config.get(key, ""))
        entries[key] = entry

    return entries

def toggle_password_visibility(entry, button_text):
    if entry.cget('show') == '':
        entry.config(show='*')
        button_text.set("Show")
    else:
        entry.config(show='')
        button_text.set("Hide")
