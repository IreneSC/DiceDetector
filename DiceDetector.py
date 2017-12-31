import numpy as np
import cv2
import math
import os
import random
import matplotlib.pyplot as plt

MIN_DOT_AREA = 50
NUM_ELLIPSE_POINTS=20
SHAPE_RET_THRESHOLD=0.3


def find_dots(contours,ellipse_display_image=None):
    """Find which of the contours correspond to dice dots

    Uses a method of comparison by which it finds approximating ellipses
    and compares their similarity to the original contour using matchShape()

    :param contours: the contours from the image
    :param ellipse_display_image: optional image on which to draw the ellipses found
    :return: list of dots found (as ellipses)
    """
    dots =[]
    for cnt in contours:
        contour_area = cv2.contourArea(cnt)
        if contour_area < MIN_DOT_AREA or len(cnt)<5:
            continue

        # fit ellipse and compare
        ellipse = cv2.fitEllipse(cnt)
        (center, axes, angle)=ellipse
        int_center=tuple([int(z) for z in center])
        int_axes = tuple([int(z/2) for z in axes])
        ellipse_cnt=cv2.ellipse2Poly(int_center,int_axes,int(angle),0,360,int(360/NUM_ELLIPSE_POINTS))
        ret = cv2.matchShapes(cnt, ellipse_cnt, 1, 0.0)
        print(ret)
        # TODO: find correct threshold for ellipse/not ellipse
        if ret>SHAPE_RET_THRESHOLD:
            continue

        if ellipse_display_image is not None:
            cv2.ellipse(ellipse_display_image,ellipse,(255,0,0),1)
        dots.append(ellipse)

    if ellipse_display_image is not None:
        cv2.imshow('ellipses',ellipse_display_image)
    return dots


def process_image(image_name):
    """Process the image to eliminate noise/increase contrast on dice

    :param image_name: the name of the image to load and process
    :return: the processed (grayscale) image
    """
    # TODO: improve processing to better isolate dots
    img = cv2.bitwise_not(cv2.imread(image_name, 0))
    cv2.imshow('bw', img)
    img_color = cv2.imread(image_name, cv2.IMREAD_COLOR)
    cv2.imshow(image_name[0:image_name.index('.')] + "_" + 'original.jpg', img_color)
    blur = cv2.GaussianBlur(img_color, (5, 5), 0)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    cv2.imshow('gray', gray)
    ret, thresh = cv2.threshold(gray, 200, 225, 0)
    cv2.imshow('thresh', thresh)
    return gray


def find_contours(image,contours_display_image=None):
    """find contours in processed image using edge detection

    :param image: the image to find contours in
    :param contours_display_image: optional image on which to show the contours found
    :return: contours
    """
    edges = cv2.Canny(image, 10, 200)
    cv2.imshow('canny', edges)
    bluredges = cv2.GaussianBlur(edges, (5, 5), 0)
    retedge, threshedge = cv2.threshold(bluredges, 50, 255, cv2.THRESH_BINARY)
    edges = threshedge
    im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    for i in range(len(contours) - 1, -1, -1):
        if hierarchy[0][i][2] < 0:  # no children, inner contour
            del contours[i]
    if contours_display_image is not None:
        cv2.drawContours(contours_display_image, contours, -1, (255, 0, 0), 1)
        cv2.imshow(contours.jpg, contours_display_image)
    return contours


def detect_dice(image_name):
    """Locate dice in an image (incomplete)

    :param image_name: the name of the image to search for dice
    """
    processed=process_image(image_name)
    contours=find_contours(processed)
    dots=find_dots(contours,cv2.imread(IMAGE_NAME,cv2.IMREAD_COLOR))
    # TODO: Separate out faces of die based on dots


if __name__ == '__main__':
    IMAGE_NAME = "testimages/narrow/" + random.choice(os.listdir("testimages/narrow/"))
    # Good example test images:
    # IMAGE_NAME = "testimages/narrow/dice_narrow_1514.jpg"
    # IMAGE_NAME = "testimages/narrow/dice_narrow_3725.jpg"
    # IMAGE_NAME = "testimages/narrow/dice_narrow_4165.jpg"
    # IMAGE_NAME = "testimages/narrow/dice_narrow_5261.jpg"
    # IMAGE_NAME = "testimages/narrow/dice_narrow_9229.jpg"
    # IMAGE_NAME = "testimages/narrow/dice_narrow_17430.jpg"
    # IMAGE_NAME = "testimages/narrow/dice_narrow_6033.jpg"

    print(IMAGE_NAME)
    detect_dice(IMAGE_NAME)
    # TODO: change helper functions to use the image itself, not the name (stop loading it multiple times)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
