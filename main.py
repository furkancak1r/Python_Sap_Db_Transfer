import tkinter as tk
from ui_handlers import setup_root, setup_buttons, setup_checkboxes_and_run_button, update_button_states
from setup_config import setup_entries

def main():
    root = tk.Tk()
    font_specs = setup_root(root)
    entries_source, entries_target = setup_entries(root, font_specs)

    # Get column_name and transfer_value directly from the entries dictionary
    column_name = entries_source.get('column_name').get()
    transfer_value = entries_source.get('transfer_value').get()
    target_column_name = entries_target.get('target_column_name').get()

    # Create a lambda to update button states including checkboxes
    lambda_update = lambda: update_button_states(
        save_button, update_button, delete_button,
        entries_source, entries_target,
        run_button, update_contacts_var, update_transfer_journal_var
    )

    # Pass lambda_update to setup_buttons to handle UI updates
    save_button, update_button, delete_button = setup_buttons(root, entries_source, entries_target, lambda_update)

    # Setup checkboxes and run button, now with correct column_name and column_value
    update_contacts_checkbox, run_button, update_contacts_var, update_transfer_journal_checkbox, update_transfer_journal_var = setup_checkboxes_and_run_button(
        root, lambda_update, entries_source, entries_target, column_name, transfer_value , target_column_name
    )

    # Configure checkboxes to update button states on change
    update_contacts_checkbox.config(command=lambda_update)
    update_transfer_journal_checkbox.config(command=lambda_update)

    # Initial state update
    lambda_update()

    root.mainloop()

if __name__ == "__main__":
    main()
