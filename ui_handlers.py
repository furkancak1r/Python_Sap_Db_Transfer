import tkinter as tk
from config_manager import read_config
from config_handlers import save_configs, delete_configs, execute_contacts_run, execute_transfer_based_on_condition_run, execute_account_plan_transfer_and_exclude_balances_run,execute_tax_run,execute_exchange_rate_run,execute_user_run
from tkinter import messagebox


def update_button_states(save_button, update_button, delete_button, entries_source, entries_target, run_button, contacts_var, transfer_var, plan_var,tax_var,exchange_rate_var,user_var):
    # Check if any entry has content
    active = any(entry.get() for entry in entries_source.values()) or any(
        entry.get() for entry in entries_target.values())
    save_button.config(state='normal' if not active else 'disabled')
    update_button.config(state='normal' if active else 'disabled')
    delete_button.config(state='normal' if active else 'disabled')

    # Enable 'Run' button if at least one checkbox is checked
    run_button.config(state='normal' if contacts_var.get()
                      or transfer_var.get() or plan_var.get() or tax_var.get() or exchange_rate_var.get() or user_var.get() else 'disabled')


def setup_root(root, width=650, height=600):
    root.title("SAP Aktarım")
    font_specs = ("Arial", 12)
    center_window(root, width, height)
    return font_specs


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')


def setup_buttons(root, entries_source, entries_target, update_ui_callback):
    save_button = tk.Button(root, text="Ayarları Kaydet", command=lambda: save_configs(
        entries_source, entries_target))
    update_button = tk.Button(root, text="Ayarları Güncelle",
                              command=lambda: save_configs(entries_source, entries_target))
    delete_button = tk.Button(root, text="Ayarları Sil", command=lambda: delete_configs(
        [entries_source, entries_target], update_ui_callback))

    save_button.grid(row=12, column=0, padx=10, pady=10)
    update_button.grid(row=12, column=1, padx=10, pady=10)
    delete_button.grid(row=12, column=2, padx=10, pady=10)
    return save_button, update_button, delete_button


def setup_checkboxes_and_run_button(root, update_button_states, entries_source, entries_target, column_name, column_value, target_column_name):
    contacts_var = tk.BooleanVar(value=False)
    transfer_var = tk.BooleanVar(value=False)
    plan_var = tk.BooleanVar(value=False)
    tax_var = tk.BooleanVar(value=False)
    exchange_rate_var = tk.BooleanVar(value=False)
    user_var = tk.BooleanVar(value=False)
    contacts_checkbox = tk.Checkbutton(
        root, text="Muhatapları Güncelle", variable=contacts_var, command=update_button_states)
    transfer_checkbox = tk.Checkbutton(
        root, text="Yevmiye Kayıtlarını Güncelle", variable=transfer_var, command=update_button_states)
    plan_checkbox = tk.Checkbutton(
        root, text="Hesap Planını Güncelle", variable=plan_var, command=update_button_states)
    tax_checkbox = tk.Checkbutton(
        root, text="Vergi Kodlarını ve Oranlarını Güncelle", variable=tax_var, command=update_button_states)
    exchange_rate_checkbox = tk.Checkbutton(
        root, text="Döviz Kurlarını Güncelle", variable=exchange_rate_var, command=update_button_states)
    user_checkbox = tk.Checkbutton(
        root, text="Kullanıcıları Güncelle", variable=user_var, command=update_button_states)
    
    contacts_checkbox.grid(row=13, column=0, padx=10, pady=10)
    transfer_checkbox.grid(row=13, column=1, padx=10, pady=10)
    plan_checkbox.grid(row=13, column=2, padx=10, pady=10)
    tax_checkbox.grid(row=14, column=0, padx=10, pady=10)
    exchange_rate_checkbox.grid(row=14, column=1, padx=10, pady=10)
    user_checkbox.grid(row=14, column=2, padx=10, pady=10)
    run_button = tk.Button(root, text="Çalıştır", state='disabled', command=lambda: run_operations(
        contacts_var, transfer_var, entries_source, entries_target, column_name, column_value, target_column_name, plan_var, tax_var,exchange_rate_var,user_var))
    run_button.grid(row=15, column=1, padx=10, pady=10)

    return contacts_checkbox, run_button, contacts_var, transfer_checkbox, transfer_var, plan_checkbox, plan_var, tax_checkbox, tax_var, exchange_rate_checkbox, exchange_rate_var,user_checkbox,user_var


def run_operations(contacts_var, transfer_var, entries_source, entries_target, column_name, column_value, target_column_name, plan_var, tax_var,exchange_rate_var,user_var):
    # This dictionary will track the completion status of each operation
    operation_status = {
        'contacts': False,
        'transfer': False,
        'plan': False,
        'tax': False,
        'exchange_rate': False,
        'user': False
    }

    # Define callbacks for each operation
    def contacts_callback():
        operation_status['contacts'] = True
        check_complete()

    def transfer_callback():
        operation_status['transfer'] = True
        check_complete()

    def plan_callback():
        operation_status['plan'] = True
        check_complete()
        
    def tax_callback():
        operation_status['tax'] = True
        check_complete()
    def exchange_rate_callback():
        operation_status['exchange_rate'] = True
        check_complete()
    def user_callback():
        operation_status['user'] = True
        check_complete()    
            
    # This function checks if all initiated operations are completed and shows a message
    def check_complete():
        if ((not contacts_var.get() or operation_status['contacts']) and
           (not transfer_var.get() or operation_status['transfer']) and
           (not plan_var.get() or operation_status['plan']) and
            (not tax_var.get() or operation_status['tax']) and
            (not exchange_rate_var.get() or operation_status['exchange_rate']) and
            (not user_var.get() or operation_status['user_rate'])):
            messagebox.showinfo(
                "Başarılı", "Tüm aktarımlar başarıyla tamamlandı!")

    # Execute operations based on checkbox states
    if user_var.get():
        execute_user_run(entries_source, entries_target, user_callback)
    if exchange_rate_var.get():
        execute_exchange_rate_run(entries_source, entries_target, exchange_rate_callback)
    if plan_var.get():
        execute_account_plan_transfer_and_exclude_balances_run(
            entries_source, entries_target, plan_callback)
    if tax_var.get():
        execute_tax_run(entries_source, entries_target, tax_callback)
    if contacts_var.get():
        execute_contacts_run(entries_source, entries_target, contacts_callback)
    if transfer_var.get():
        execute_transfer_based_on_condition_run(
            entries_source, entries_target, column_name, column_value, target_column_name, transfer_callback)
