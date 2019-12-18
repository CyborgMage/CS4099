from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter.scrolledtext import ScrolledText
from F_Preprocessing import *
from F_Tracking import *
from F_smdParser import *
import settings

settings.init()

size_Height = 300
size_Width = 300

window = Tk()


# Calculate error in tracking.
def fn_error_tracking():
    if settings.evaluate_auto['Auto File Name'] == "":
        update_console('ERROR: No file selected.')
    else:
        update_console('Starting evaluation for error in cell tracking...')
        temp_str = settings.evaluate_auto['Auto File Name']
        temp_str = temp_str.split('/')[-1]
        temp_str = temp_str.split('.')[0]
        csv_file_name = '../Results/ErrorTrack <Name>.csv'.replace('<Name>', temp_str)
        error_tracking(settings.evaluate_auto['Auto File Name'], settings.evaluate_auto['Manual File Name'],
                       csv_file_name)
        update_console('Completed evaluation for error in cell tracking...')


# Calculate error in centroid.
def fn_error_centroid():
    if settings.evaluate_auto['Auto File Name'] == "":
        update_console('ERROR: No file selected.')
    else:
        update_console('Starting evaluation for error in cell centroid detection...')
        temp_str = settings.evaluate_auto['Auto File Name']
        temp_str = temp_str.split('/')[-1]
        temp_str = temp_str.split('.')[0]
        csv_file_name = '../Results/ErrorTrack <Name>.csv'.replace('<Name>', temp_str)
        error_centroid(settings.evaluate_auto['Auto File Name'], settings.evaluate_auto['Manual File Name'],
                       csv_file_name)
        update_console('Completed evaluation for error in cell centroid detection...')


# Generic functions for updating image placeholer.
def label_image_update(label, filename):
    image = Image.open(filename)
    image = image.resize((size_Width, size_Height), Image.ANTIALIAS)

    selectedImage = ImageTk.PhotoImage(image)
    label.image = selectedImage
    label.config(image=selectedImage)


# Update image placeholder.
def label_image_direct_update(label, image):
    # image = Image.open(filename)
    image = image.resize((size_Width, size_Height), Image.ANTIALIAS)

    selected_image = ImageTk.PhotoImage(image)
    label.image = selected_image
    label.config(image=selected_image)


# Select single file for processing
def single_file_select(singleImageLabel1):
    filename = filedialog.askopenfilename(initialdir="../green_focus/", title="Select file")
    singleEntryDir.delete(0, END)
    singleEntryDir.insert(0, filename)
    label_image_update(singleImageLabelOriginal, filename)
    settings.seletedConfiguration['SingleImageOriginal'] = filename
    update_console('File selected: ' + filename)


# Evaluation function.
def single_evaluate_file_select():
    filename = filedialog.askopenfilename(initialdir="../Output/", title="Select file")
    entry_SBDFile.delete(0, END)
    entry_SBDFile.insert(0, filename)
    settings.evaluate_auto['Auto File Name'] = filename
    update_console('Auto Tracked file selected: ' + filename)


# Track filter change and apply.
def filterChange(*args):
    settings.seletedConfiguration['optionFilter'] = optionVariableFilter.get()
    update_console('Filter selected: ' + optionVariableFilter.get())

    if filter_select():
        filename = settings.seletedConfiguration['SingleImageFiltered']
        label_image_direct_update(singleImageLabelFiltered, filename)
        update_console('Filter applied successfully.')


# Track threshold change and apply.
def thresholdChange(*args):
    settings.seletedConfiguration['optionThreshold'] = optionVariableThreshold.get()
    update_console('Threshold selected: ' + optionVariableThreshold.get())

    if threshold_select():
        filename = settings.seletedConfiguration['SingleImageThreshold']
        label_image_direct_update(singleImageLabelThreshold, filename)
        update_console('Threshold applied successfully.')


# Track smooth change and apply.
def smoothChange(*args):
    settings.seletedConfiguration['optionSmooth'] = optionVariableSmooth.get()
    update_console('Smooth technique selected: ' + optionVariableSmooth.get())

    if smooth_select():
        filename = settings.seletedConfiguration['SingleImageSmoothed']
        label_image_direct_update(singleImageLabelSmoothed, filename)
        update_console('Smoothing applied successfully.')


def segmentation_change(*args):
    settings.seletedConfiguration['optionSegmentation'] = optionVariableSegmentation.get()
    update_console('Segmentation selected: ' + optionVariableSegmentation.get())


def start_tracking():
    update_console('Tracking started... ')
    if segmentation_select():
        print('Completed')


# =================================== Layout ===================================
window.title('Cell Tracking')
# window.geometry("1200x800")

# Header
headerForSingleFile = Label(window, text="IMAGE PROCESSING TECHNIQUES")
headerForSingleFile.grid(row=0, column=0)

ttk.Separator(window, orient='horizontal').grid(column=0,
                                                row=1, columnspan=5, sticky='ew')
# ============================== Single File - Left Navigation =================
# Label Image
file_choose_frame = Frame(window)
file_choose_frame.grid(row=2, column=0)

Label(file_choose_frame, text="Select image:").grid(row=0, column=0)
# Entry
entry_filter_default_text = StringVar(window, value='Select only .TIFF image..')
singleEntryDir = Entry(file_choose_frame, text=".", textvariable=entry_filter_default_text)
singleEntryDir.grid(row=0, column=1)
# Button
singleBtnDirChoose = Button(file_choose_frame, text="Select", command=lambda: single_file_select(singleImageLabelOriginal))
singleBtnDirChoose.grid(row=0, column=2)

# Label Filter
filter_choose_frame = Frame(window)
filter_choose_frame.grid(row=2, column=1)

Label(filter_choose_frame, text="Select filter:").grid(row=0, column=1)
optionVariableFilter = StringVar(filter_choose_frame)
optionVariableFilter.set('-- None --')
optionVariableFilter.trace("w", filterChange)

singleOptionFilter = OptionMenu(filter_choose_frame, optionVariableFilter, *settings.preProcessImageFilter)
singleOptionFilter.config(width=20)
singleOptionFilter.grid(row=0, column=2)

# Label Threshold
threshold_choose_frame = Frame(window)
threshold_choose_frame.grid(row=2, column=2)

Label(threshold_choose_frame, text="Select Threshold:").grid(row=0, column=0)
optionVariableThreshold = StringVar(threshold_choose_frame)
optionVariableThreshold.set('-- None --')
optionVariableThreshold.trace("w", thresholdChange)

singleOptionThreshold = OptionMenu(threshold_choose_frame, optionVariableThreshold, *settings.preProcessImageThreshold)
singleOptionThreshold.config(width=20)
singleOptionThreshold.grid(row=0, column=1)

# Label Smoothing
smoothing_choose_frame = Frame(window)
smoothing_choose_frame.grid(row=2, column=3)

Label(smoothing_choose_frame, text="Select Smoothing:").grid(row=0, column=0)
optionVariableSmooth = StringVar(smoothing_choose_frame)
optionVariableSmooth.set('-- None --')
optionVariableSmooth.trace("w", smoothChange)

singleOptionSmooth = OptionMenu(smoothing_choose_frame, optionVariableSmooth, *settings.preProcessImageSmoothing)
singleOptionSmooth.config(width=20)
singleOptionSmooth.grid(row=0, column=1)

# ============================== Single File - Middle Navigation ================
singleImagePlaceHolder = ImageTk.PhotoImage(file='../Resources/placeholder.png')
singleImageLabelOriginal = Label(window, image=singleImagePlaceHolder)
singleImageLabelOriginal.config(width=size_Width, height=size_Height)
singleImageLabelOriginal.grid(row=3, column=0, padx=5, pady=5)

singleImageLabelFiltered = Label(window, image=singleImagePlaceHolder)
singleImageLabelFiltered.config(width=size_Width, height=size_Height)
singleImageLabelFiltered.grid(row=3, column=1, padx=5, pady=5)

singleImageLabelThreshold = Label(window, image=singleImagePlaceHolder)
singleImageLabelThreshold.config(width=size_Width, height=size_Height)
singleImageLabelThreshold.grid(row=3, column=2, padx=5, pady=5)

singleImageLabelSmoothed = Label(window, image=singleImagePlaceHolder)
singleImageLabelSmoothed.config(width=size_Width, height=size_Height)
singleImageLabelSmoothed.grid(row=3, column=3, padx=5, pady=5)

ttk.Separator(window, orient='horizontal').grid(column=0,
                                                row=4, columnspan=5, sticky='ew')
# ============================== Tracking ================================
headerForTracking = Label(window, text="3D CELL TRACKING")
headerForTracking.grid(row=5, column=0)
headerForEvaluation = Label(window, text="EVALUATE / VISUALIZE TRACKED CELL")
headerForEvaluation.grid(row=5, column=1)

ttk.Separator(window, orient='horizontal').grid(column=0,
                                                row=6, columnspan=5, sticky='ew')
# ========================== Tracking - Segmentation choose ==============
# ---------- Tracking
segmentation_choose_frame = Frame(window)
segmentation_choose_frame.grid(row=7, column=0)

Label(segmentation_choose_frame, text="Select Segmentation:").grid(row=0, column=0)
optionVariableSegmentation = StringVar(segmentation_choose_frame)
optionVariableSegmentation.set('-- None --')
optionVariableSegmentation.trace("w", segmentation_change)

singleOptionSegmentation = OptionMenu(segmentation_choose_frame, optionVariableSegmentation, *settings.list_segmentation)
singleOptionSegmentation.config(width=15)
singleOptionSegmentation.grid(row=0, column=1)

# Button
btn_tracking = Button(segmentation_choose_frame, text="Start Tracking", command=lambda: start_tracking())
btn_tracking.config(width=25)
btn_tracking.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# ---------- Evaluation
evaluation_choose_frame = Frame(window)
evaluation_choose_frame.grid(row=7, column=1)
Label(evaluation_choose_frame, text="Select Auto tracked file:").grid(row=0, column=0)
# Entry
entry_evaluation_default_text = StringVar(window, value='Select only .SBD image..')
entry_SBDFile = Entry(evaluation_choose_frame, text=".", textvariable=entry_evaluation_default_text)
entry_SBDFile.grid(row=1, column=0)
# Button
btn_sbd_file_choose = Button(evaluation_choose_frame, text="Select", command=lambda: single_evaluate_file_select())
btn_sbd_file_choose.grid(row=1, column=1)
# Button
btn_error_tracking = Button(evaluation_choose_frame, text="Evaluate Tracking Error", command=lambda: fn_error_tracking())
btn_error_tracking.grid(row=2, column=0, padx=5, pady=5)
btn_error_centroid = Button(evaluation_choose_frame, text="Evaluate Centroid Error", command=lambda: fn_error_centroid())
btn_error_centroid.grid(row=2, column=1, padx=5, pady=5)

# ============================================ Status Area ========================================
ttk.Separator(window, orient='horizontal').grid(column=0,
                                                row=8, columnspan=5, sticky='ew')
# ============================== Tracking ================================
headerForConsole = Label(window, text="CONSOLE WINDOW")
headerForConsole.grid(row=9, column=0)

ttk.Separator(window, orient='horizontal').grid(column=0,
                                                row=10, columnspan=5, sticky='ew')

console_area = ScrolledText(window)
console_area.config(width=150, height=15, font=('Arial', 10), bg='Black', fg='White')
console_area.grid(row=11, column=0, columnspan=4)
console_area.insert(END, ' ====================================== CELL TRACKING =================================== \n')

settings.constant_gui_console = console_area
settings.constant_gui_end = END
settings.constant_window = window

window.mainloop()
