import tkinter as tk
from tkinter import messagebox
from config_manager import save_config, delete_config
from data_operations import check_and_update_ocrd, transfer_based_on_condition,account_plan_transfer_and_exclude_balances,tax_run_transfer,exchange_rate_run_transfer,user_update_ousr


def handle_config(entries, update=False):
    source_config = {key: entry.get() for key, entry in entries.items()
                     if not key.endswith("_button")}
    save_config(source_config, "source")
    msg = "Configuration updated successfully." if update else "Configuration saved successfully."
    messagebox.showinfo("Info", msg)


def save_configs(entries_source, entries_target):
    for entries, config_type in [(entries_source, 'source'), (entries_target, 'target')]:
        config_data = {key: entry.get() for key, entry in entries.items()
                       if not key.endswith("_button")}
        save_config(config_data, config_type)
    messagebox.showinfo("Success", "Configurations saved successfully!")


def delete_configs(entries_list, update_ui_callback):
    for entries in entries_list:
        for config_type in ['source', 'target']:
            delete_config(config_type)
            for entry in entries.values():
                entry.delete(0, tk.END)
    messagebox.showinfo("Info", "Configurations deleted.")
    update_ui_callback()


def execute_contacts_run(entries_source, entries_target, callback):

    success = check_and_update_ocrd(
        entries_source, entries_target)
    if success:
        messagebox.showinfo("Success", "Muhataplar aktarımı başarılı!")
    else:
        messagebox.showerror("Error", "Muhataplar aktarılırken hata meydana geldi!.")
    callback()


def execute_transfer_based_on_condition_run(entries_source, entries_target, column_name, column_value, target_column_name,callback):
    # Perform database operations
    success = transfer_based_on_condition(
        entries_source, entries_target, column_name, column_value,target_column_name)
    if success:
        messagebox.showinfo("Success", "Yevmiye kayıtları aktarımı başarılı!")
    else:
        messagebox.showerror("Error", "Yevmiye kayıtları aktarılırken hata meydana geldi!.")
    callback()

def execute_account_plan_transfer_and_exclude_balances_run(entries_source, entries_target, callback):
    success = account_plan_transfer_and_exclude_balances(
        entries_source, entries_target)
    if success:
        messagebox.showinfo("Success", "Hesap planı aktarımı başarılı!")
    else:
        messagebox.showerror("Error", "Hesap planı aktarılırken hata meydana geldi!.")
    callback()
    
def execute_tax_run(entries_source, entries_target, callback):
    success = tax_run_transfer(
        entries_source, entries_target)
    if success:
        messagebox.showinfo("Success", "Vergi kodları ve oranları aktarımı başarılı!")
    else:
        messagebox.showerror("Error", "Vergi kodları ve oranları aktarılırken hata meydana geldi!.")
    callback()    
    
def execute_exchange_rate_run(entries_source, entries_target, callback):
    success = exchange_rate_run_transfer(
        entries_source, entries_target)
    if success:
        messagebox.showinfo("Success", "Döviz kurları aktarımı başarılı!")
    else:
        messagebox.showerror("Error", "Döviz kurları aktarılırken hata meydana geldi!.")
    callback()    
    
def execute_user_run(entries_source, entries_target, callback):
    success = user_update_ousr(
        entries_source, entries_target)
    if success:
        messagebox.showinfo("Success", "Kullanıcılar aktarımı başarılı!")
    else:
        messagebox.showerror("Error", "Kullanıcılar aktarılırken hata meydana geldi!.")
    callback()    