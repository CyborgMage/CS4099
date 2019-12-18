import settings


# Update console window about activties.
def update_console(text):
    settings.constant_gui_console.insert(settings.constant_gui_end, text + '\n')
    settings.constant_gui_console.yview(settings.constant_gui_end)
    # console_area.delete('1.0', END)
    settings.constant_window.update()
