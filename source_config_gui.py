import tkinter as tk

def add_db_entries(root, font_specs, config_type, initial_config={}):
    row_offset = 0 if config_type == 'source' else 6
    translations = {
        'source': 'Kaynak',
        'target': 'Hedef'
    }
    
    # Türkçe metinleri kullanarak etiketleri oluştur
    labels = {
        "server": f"{translations[config_type]} Sunucusu:",
        "database": f"{translations[config_type]} Veritabanı:",
        "username": f"{translations[config_type]} Kullanıcı Adı:",
        "password": f"{translations[config_type]} Şifre:",
    }

    if config_type == 'source':
        labels.update({
            "column_name": "Kaynak Sütun Adı:",
            "transfer_value": "Kaynak Transfer Değeri:"
        })
    elif config_type == 'target':
        labels.update({
            "target_column_name": "Hedef Sütun Adı:"
        })

    entries = {}
    for idx, (key, label) in enumerate(labels.items()):
        label_widget = tk.Label(root, text=label, font=font_specs)
        label_widget.grid(row=idx + row_offset, column=0, sticky='w', padx=10, pady=5)
        
        entry = tk.Entry(root, font=font_specs, show="*" if key == "password" else "")
        entry.grid(row=idx + row_offset, column=1, sticky='ew', padx=(10, 2), pady=5)  # Adjusted padx to be minimal on the right side
        
        if key == "password":
            button_text = tk.StringVar(value="Göster")
            show_button = tk.Button(root, textvariable=button_text, command=lambda e=entry, b=button_text: toggle_password_visibility(e, b))
            show_button.grid(row=idx + row_offset, column=2, padx=(10, 10), sticky='w')  # Adjust to align closer to the entry
            if not initial_config.get(key, ""):
                show_button.config(state=tk.DISABLED)
        if initial_config:
            entry.insert(0, initial_config.get(key, ""))

        entries[key] = entry

    return entries

def toggle_password_visibility(entry, button_text):
    if entry.cget('show') == '*':
        entry.config(show='')
        button_text.set("Gizle")
    else:
        entry.config(show='*')
        button_text.set("Göster")
