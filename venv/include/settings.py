# Golbal variable for project.

def init():

    global constant_window
    constant_window = None

    global constant_gui_console
    constant_gui_console = None

    global constant_gui_end
    constant_gui_end = None

    global preProcessImageFilter
    preProcessImageFilter = ['Gaussian Filter',
                             'Median Filter']

    global preProcessImageThreshold
    preProcessImageThreshold = ['OTSU',
                                'Gaussian Adaptive']

    global preProcessImageSmoothing
    preProcessImageSmoothing = ['Binary Closing',
                                'Binary Erosion']

    global list_segmentation
    list_segmentation = ['Watershed',
                         'Active Contour']

    global seletedConfiguration
    seletedConfiguration = dict()

    seletedConfiguration['optionFilter'] = 'None'
    seletedConfiguration['optionThreshold'] = 'None'
    seletedConfiguration['optionSmooth'] = 'None'
    seletedConfiguration['optionSegmentation'] = 'None'

    seletedConfiguration['SingleImageOriginal'] = ''
    seletedConfiguration['SingleImageFiltered'] = ''
    seletedConfiguration['SingleImageThreshold'] = ''
    seletedConfiguration['SingleImageSmoothed'] = ''

    global track_configuration
    track_configuration = dict()

    track_configuration['directory path'] = "../green_focus/"

    global evaluate_auto
    evaluate_auto = dict()
    evaluate_auto['Auto File Name'] = ""
    evaluate_auto['Manual File Name'] = "../Output/manualTracked.smd"

    global script_para
    script_para = []
