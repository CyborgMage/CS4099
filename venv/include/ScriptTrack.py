import cv2
import os
import numpy as np

from scipy import ndimage as ndi
from skimage import measure, img_as_float
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu, threshold_local
from skimage.segmentation import (clear_border,
                                  inverse_gaussian_gradient,
                                  morphological_geodesic_active_contour)
from skimage.morphology import binary_closing, watershed, binary_erosion
from multiprocessing import Pool
from time import time
from itertools import groupby

import settings
from F_TrackHandler import *
from F_smdParser import *
from Cell import *

# This file is kind of script to run multiple methods of tracking in one go and compare them.

# ========================== Track and generate SMD ===================================
# Create 3D Images
def watershed_3d_segment(group):

    filename = [settings.track_configuration['directory path'] + f for f in group]

    # Create 3D Images
    images = []
    for fil in filename:
        image = cv2.imread(fil, 0)
        if image.shape is None:
            image = images[-1]
        else:
            try:
                cleared = preprocessImageCustom(image)
            except ValueError:
                continue
            images.append(cleared)
    image = np.dstack(images)

    distance = ndi.distance_transform_edt(image)

    # Pre-Processess and Label via Watershed.
    local_max = peak_local_max(distance, indices=False, min_distance=100,
                               labels=image, footprint=np.ones((int(8), int(8), 2)))
    markers = ndi.label(local_max)[0]
    label_im = watershed(-distance, markers, mask=image)

    # Filter
    label_info = measure.regionprops(label_im.astype(int))
    # PENDING
    for p in label_info:
        # PENDING - Try for different configuration
        if p.area > 100 or p.area < 500:
            label_im = removeLabel(label_im, p)
    cellList = outputInfo3D(label_info, filename[0])
    # PENDING
    # cellList = clusterTrimmer(cellList)

    # Output
    report = "Finished processing {}, found {} cells.".format(filename[0], len(cellList))
    # update_console(report)
    print(report)
    return cellList


def active_contour_3d_segment(group):
    filename = [settings.track_configuration['directory path'] + f for f in group]

    # Create 3D Images
    images = []
    for fil in filename:
        image = cv2.imread(fil, 0)
        if image.shape is None:
            image = images[-1]
        else:
            try:
                cleared = preprocessImageCustom(image)
            except ValueError:
                continue

            cleared = img_as_float(cleared)
            images.append(cleared)

    image = np.dstack(images)

    # ====================================
    gimage = inverse_gaussian_gradient(image)

    # Initial level set
    init_ls = np.ones(image.shape, dtype=np.int8)
    label_im = morphological_geodesic_active_contour(gimage, 250, init_ls,
                                                     smoothing=1, balloon=-1,
                                                     threshold=0.9)

    # Filter
    label_image = measure.label(label_im)
    label_info = measure.regionprops(label_image)

    for p in label_info:
        # PENDING
        if p.area < 100 or p.area > 500:
            label_im = removeLabel(label_im, p)
    cellList = outputInfo3D(label_info, filename[0])
    # PENDING
    # cellList = clusterTrimmer(cellList)

    # Output
    print("Finished processing {}, found {} cells.".format(filename[0], len(cellList)))
    return cellList


def perform_segmentation(model_no):
    print('Reading the files....')

    # Loads the Files in Directory
    files = os.listdir(settings.track_configuration['directory path'])
    files = sorted(files)
    groupedFiles = [list(g) for k, g in groupby(files, key=lambda x: x[:4])]

    print('Creating Pool for multi threading....')
    # Multithreading - Detects Cells
    pool = Pool()
    t0 = time()
    paramList = []
    print('Starting the cell segmentation. It will take time....')
    for group in groupedFiles:
        paramList.append(group)

    if model_no == 1:
        listsOfCells = pool.map(watershed_3d_segment, paramList)
    if model_no == 2:
        listsOfCells = pool.map(active_contour_3d_segment, paramList)

    t1 = time()
    pool.close()
    pool.join()

    print("Detection Complete, took {} seconds".format(t1 - t0))

    return listsOfCells


def outputInfo3D(labels, filename):
    cellList = []
    counter = 0
    filename = filename.split("X")[1]
    filename = filename.split(".")[0]
    filename = filename.split("L")
    time = int(filename[0])
    for lab in labels:
        cell = Cell(counter)
        cell.addLocTime(time,int(lab.centroid[0]), int(lab.centroid[1]), int(lab.centroid[2]))
        cellList.append(cell)
        counter = counter + 1
    return cellList


def cellSort(cell):
    return cell.locOverTime[0].time


def removeLabel(label_image, p):
    match = label_image == p.label
    label_image[match] = 0
    return label_image


def tracker(listsOfCells, write_filename):
    cellLists = listsOfCells[0]

    print("Length of cells found in first {}".format(len(cellLists)))

    t0 = time()
    disca = []

    # Link cells in tracking.
    counter = 0
    for lis in listsOfCells[1:]:
        # lis = clusterTrimmer(lis)
        cellLists, discarded = iterateThroughCells(lis, cellLists)
        disca = disca + discarded
        print(counter, len(cellLists), len(disca))
        counter += 1

    t1 = time()

    # Re-add Dead Cells. - Filter away short cells.
    cellLists = cellLists + disca
    cellLists = [x for x in cellLists if not tooShort(x, 10)]

    # Output Data
    cellLists.sort(key=cellSort)
    counter = 0
    for cell in cellLists:
        cell.id = counter
        counter += 1
    print("Finished. Took {} seconds to process".format(t1 - t0))
    outputDataCustom(cellLists, write_filename)


def preprocessImageCustom(image):
    # Filter selection
    if settings.param[0] == 1:
        image = ndi.gaussian_filter(image, sigma=1)
    if settings.param[0] == 2:
        image = ndi.median_filter(image, size=5)

    # Threshold selection
    if settings.param[1] == 1:
        t = threshold_otsu(image)
        image = image > t
    if settings.param[1] == 2:
        block_size = 701
        adaptive_thresh = threshold_local(image, block_size, offset=0)
        image = image > adaptive_thresh

    # Smooth selection
    if settings.param[2] == 1:
        image = binary_closing(image)
        cleared = clear_border(image)
    if settings.param[2] == 2:
        image = binary_erosion(image)
        cleared = clear_border(image)

    return cleared


# Output Framework for Lists of Cells.
def outputDataCustom(cellLists, write_filename):
    text = "SIMI*BIOCELL\n400\n---\n0\n---\n1 1\n0\n---\n"
    for cell in cellLists:
        text += str(cell)
    txt_output = open("../Output/" + write_filename + ".sbd", 'w')
    txt_output.write(text)
    txt_output.close()


def main_track():
    # param = ['filter', 'threhsold', 'smooth']

    settings.param = [1, 1, 1]
    listsOfCells = perform_segmentation(1)
    write_filename = 'GF-OT-BC-WS'
    tracker(listsOfCells, write_filename)
    # ================================================
    settings.param = [1, 2, 1]
    listsOfCells = perform_segmentation(1)
    write_filename = 'GF-AT-BC-WS'
    tracker(listsOfCells, write_filename)
    # ================================================
    settings.param = [1, 1, 1]
    listsOfCells = perform_segmentation(2)
    write_filename = 'GF-OT-BC-AC'
    tracker(listsOfCells, write_filename)
    # ================================================
    settings.param = [1, 2, 1]
    listsOfCells = perform_segmentation(2)
    write_filename = 'GF-AT-BC-AC'
    tracker(listsOfCells, write_filename)
    # ================================================
# ========================== Track and generate SMD ===================================


# =================================== SMD TO CSV ======================================
def main_evaluate():
    manual_tracked_file_path = '../Output/manualTracked.smd'

    auto_tracked_SBD = [('../Output/GF-AT-BC-AC.sbd', '../Results/ErrorTrack GF-AT-BC-AC.csv',
                         '../Results/ErrorCentroid GF-AT-BC-AC.csv', '../Results/ErrorDeath GF-AT-BC-AC.csv'),
                        ('../Output/GF-AT-BC-WS.sbd', '../Results/ErrorTrack GF-AT-BC-WS.csv',
                         '../Results/ErrorCentroid GF-AT-BC-WS.csv', '../Results/ErrorDeath GF-AT-BC-WS.csv'),
                        ('../Output/GF-OT-BC-AC.sbd', '../Results/ErrorTrack GF-OT-BC-AC.csv',
                         '../Results/ErrorCentroid GF-OT-BC-AC.csv', '../Results/ErrorDeath GF-OT-BC-AC.csv'),
                        ('../Output/GF-OT-BC-WS.sbd', '../Results/ErrorTrack GF-OT-BC-WS.csv',
                         '../Results/ErrorCentroid GF-OT-BC-WS.csv', '../Results/ErrorDeath GF-OT-BC-WS.csv')]

    # for _tuple in auto_tracked_SBD:
        # error_tracking(_tuple[0], manual_tracked_file_path, _tuple[1])
        # error_centroid(_tuple[0], manual_tracked_file_path, _tuple[2])
        # error_death(_tuple[0], manual_tracked_file_path, _tuple[3])

    print('Done')


# =================================== SMD TO CSV ======================================

if __name__ == '__main__':
    settings.init()
    settings.track_configuration['directory path'] = "../green_focus/"
    main_evaluate()
