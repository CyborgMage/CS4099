from scipy import ndimage as ndi
from skimage.filters import threshold_otsu, threshold_local
from skimage.morphology import binary_closing, binary_erosion, erosion, dilation
from skimage.segmentation import clear_border
from PIL import Image
import numpy as np
import cv2
import settings

# File to apply different preprocessing techniques on image.

def filter_select():
    filename = settings.seletedConfiguration['SingleImageOriginal']
    image = cv2.imread(filename, 0)

    if settings.seletedConfiguration['optionFilter'] == settings.preProcessImageFilter[0]:
        image = gaussian_filter(image)
    elif settings.seletedConfiguration['optionFilter'] == settings.preProcessImageFilter[1]:
        image = median_filter(image)

    # Show image
    saveImage(image, 1)
    return True


def threshold_select():

    image = settings.seletedConfiguration['SingleImageFiltered']
    image = np.array(image)

    if settings.seletedConfiguration['optionThreshold'] == settings.preProcessImageThreshold[0]:
        image = otsu(image)
    elif settings.seletedConfiguration['optionThreshold'] == settings.preProcessImageThreshold[1]:
        image = adaptive(image)

    # Show image
    saveImage(image, 2)
    return True


def smooth_select():

    image = settings.seletedConfiguration['SingleImageThreshold']
    image = np.array(image)

    if settings.seletedConfiguration['optionSmooth'] == settings.preProcessImageSmoothing[0]:
        image = binaryClosing(image)
    elif settings.seletedConfiguration['optionSmooth'] == settings.preProcessImageSmoothing[1]:
        image = function_erosion(image)

    # Show image
    saveImage(image, 3)
    return True


# ====================== Threshold =======================
# All the threshold function output are binary.
def otsu(image):
    t = threshold_otsu(image)
    image = image > t
    return image


def adaptive(image):
    block_size = 701
    adaptive_thresh = threshold_local(image, block_size, offset=0)
    image = image > adaptive_thresh
    return image


# ====================== Smoothed =======================
def binaryClosing(image):
    image = binary_closing(image)
    cleared = clear_border(image)
    return cleared


def function_erosion(image):
    image = binary_erosion(image)
    cleared = clear_border(image)
    return cleared


# ====================== Filter =======================
def gaussian_filter(image):
    image = ndi.gaussian_filter(image, sigma=1)
    return image


def median_filter(image):
    image = ndi.median_filter(image, size=5)
    return image


# Output Cell Images for Preview and Video.
def saveImage(image, location):
    image = Image.fromarray(image)

    if location == 1:
        settings.seletedConfiguration['SingleImageFiltered'] = image
    elif location == 2:
        settings.seletedConfiguration['SingleImageThreshold'] = image
    elif location == 3:
        settings.seletedConfiguration['SingleImageSmoothed'] = image
