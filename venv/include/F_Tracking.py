import cv2
import os
import numpy as np

from scipy import ndimage as ndi
from skimage import measure, img_as_float
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.segmentation import (clear_border,
                                  inverse_gaussian_gradient,
                                  morphological_geodesic_active_contour)
from skimage.morphology import binary_closing, watershed
from multiprocessing import Pool
from time import time
from itertools import groupby, chain

from F_TrackHandler import *
from F_Lib import update_console
import settings
from Cell import *

def segmentation_select():
    if settings.seletedConfiguration['optionSegmentation'] == settings.list_segmentation[0]:
        perform_watershed()
    if settings.seletedConfiguration['optionSegmentation'] == settings.list_segmentation[1]:
        perform_active_contour()


def perform_watershed():
    listsOfCells = perform_segmentation(1)
    tracker(listsOfCells)


def perform_active_contour():
    listsOfCells = perform_segmentation(2)
    tracker(listsOfCells)


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
                cleared = preprocessImage(image)
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
        if p.area < 100 or p.area > 500:
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
                cleared = preprocessImage(image)
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
    update_console('Reading the files....')

    # Loads the Files in Directory
    files = os.listdir(settings.track_configuration['directory path'])
    files = sorted(files)
    groupedFiles = [list(g) for k, g in groupby(files, key=lambda x: x[:4])]

    update_console('Creating Pool for multi threading....')
    # Multithreading - Detects Cells
    pool = Pool()
    t0 = time()
    paramList = []
    update_console('Starting the cell segmentation. It will take time....')
    for group in groupedFiles:
        paramList.append(group)

    if model_no == 1:
        listsOfCells = pool.map(watershed_3d_segment, paramList)
    if model_no == 2:
        listsOfCells = pool.map(active_contour_3d_segment, paramList)

    t1 = time()
    pool.close()
    pool.join()

    update_console("Detection Complete, took {} seconds".format(t1 - t0))

    return listsOfCells

def tracker(listsOfCells):
    update_console('\nStarting cell tracking over different frames..')

    cellLists = listsOfCells[0]
    update_console("Length of cells found in first frame is: {}".format(len(cellLists)))

    t0 = time()
    disca = []

    # Link cells in tracking.
    counter = 0
    for lis in listsOfCells[1:]:
        # lis = clusterTrimmer(lis)
        cellLists, discarded = iterateThroughCells(lis, cellLists)
        disca = disca + discarded
        # print(counter, len(cellLists), len(disca))
        counter += 1

    # Output Data
    cellLists.sort(key=cellSort)
    counter = 0
    for cell in cellLists:
        cell.id = counter
        counter += 1

    # Re-add Dead Cells. - Filter away short cells.
    cellLists = cellLists + disca
    cellLists = [x for x in cellLists if not tooShort(x, 10)]

    # Cell death
    # Step 1: Filter down all the cell which are not tracked for more than 10 frames.
    cell_dead_filter = [x for x in cellLists if len(x.locOverTime) > 10]

    for single_cell in cell_dead_filter:
        first_loc = single_cell.locOverTime[0]
        last_loc = single_cell.locOverTime[-1]

        # Check for boundary conditions.
        if (100 < last_loc.x < 400) and (100 < last_loc.y < 400) and (3 < last_loc.z < 10):
            if first_loc.time < 300:
                update_console('Cell death: ID: {}, Frame: {}'.format(single_cell.id, last_loc.time))

    #Mitosis detection: construct list of lists wherein first list index corresponds to cell birth frame. Assign tracked
    #cells appropriately.
    #From frame 1 onwards, iterate through every pair wherein both members do not have a listed parent, test if their
    #regressed velocities intersect or fall within a tolerance band. Then compare to older cells for a sufficiently
    #small distance between point at that frame and point of intersection, create mitosis event when match found.
    #Minimum observed distance between cells a useful metric to determine this threshold?

    #account for frame -1 births? determine how manual smd handles births prior to frame 0
    novelCells = []
    for single_cell in cellLists:
        cellBirth = single_cell.getBirth()
        if cellBirth >= -1:
            single_cell.regressLocTime()
            novelCells.append(single_cell)

    #mitosis_threshold = float("inf")
    mitosis_threshold = distFloor * 2

    #No parent restriction necessary?
    for single_cell1 in cellLists:
        if single_cell1.daughterL is None:
            for single_cell2 in novelCells:
                if (single_cell1 is not single_cell2) and single_cell2.parent is None:
                    cell1_pos = single_cell1.locAt(single_cell2.regressedLocTime.time)
                    if cell1_pos is not None and cellPointDist(cell1_pos, single_cell2.regressedLocTime) <= mitosis_threshold:
                        size = len(single_cell1.locOverTime)
                        idx_list = [idx + 1 for idx, val in enumerate(single_cell1.locOverTime) if val == cell1_pos]
                        splitLocTime = [single_cell1.locOverTime[i: j] for i, j in zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))]
                        if len(splitLocTime) <= 1:
                            break
                        single_cell1.locOverTime = splitLocTime[0]
                        left_daughter = Cell(counter)
                        counter += 1
                        left_daughter.locOverTime = splitLocTime[1]
                        cellLists.append(left_daughter)
                        single_cell1.mitosis(left_daughter, single_cell2)
                        update_console('Cell split: ID: {} Frame: {}'.format(single_cell1.id, single_cell2.getBirth()))
                        break
                else:
                    break

    t1 = time()
    update_console("Finished. Took {} seconds to process".format(t1 - t0))

    outputData(cellLists)


# Next process
def preprocessImage(image):
    image = ndi.gaussian_filter(image, sigma=1)
    t = threshold_otsu(image)
    image = image > t

    image = binary_closing(image)
    cleared = clear_border(image)
    return cleared


def removeLabel(label_image, p):
    match = label_image == p.label
    label_image[match] = 0
    return label_image


def outputInfo3D(labels, filename):
    cellList = []
    counter = 0
    filename = filename.split("X")[1]
    filename = filename.split(".")[0]
    filename = filename.split("L")
    time_ = int(filename[0])
    for lab in labels:
        cell = Cell(counter)
        cell.addLocTime(time_,int(lab.centroid[0]), int(lab.centroid[1]), int(lab.centroid[2]))
        cellList.append(cell)
        counter = counter + 1
    return cellList


def cellSort(cell):
    return cell.locOverTime[0].time


# #  Remove Clustered Objects
# def clusterTrimmer(cellList):
#     df = pd.DataFrame.from_records([c.to_dict_cluster() for c in cellList])
#     clustering = DBSCAN(eps=20, min_samples=8).fit(df)
#     counter = 0
#     for lab in clustering.labels_:
#         cellList[counter].setClustered(lab)
#         counter += 1
#     cellList = [cell for cell in cellList if cell.clustered > -1]
#     return cellList

# ================================= TRACKING ======================================
