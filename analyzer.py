import sys
import cv2 as cv
import numpy as np
# ---- Useful functions ----
output = []
def init_video(video_file):
    """
    Given the name of the video, prepares the stream and checks that everything works as intended
    """
    capture = cv.VideoCapture(video_file)
    nFrames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv.CAP_PROP_FPS)
    if fps != 0:
        waitPerFrameInMillisec = int(1 / fps * 1000 / 1)

        #print('Num. Frames = ', nFrames)
        #print('Frame Rate = ', fps, ' frames per sec')
        #print('----')

        return capture
    else:
        return None


def display_img(img, delay=1000):
    """
    One liner that displays the given image on screen
    """
    cv.imshow("Vid", img)
    cv.waitKey(delay)


def display_video(my_video, frame_inc=100, delay=100):
    """
    Displays frames of the video in a dumb way.
    Used to see if everything is working fine
    my_video = VideoCapture object
    frame_inc = Number of increments between each frame displayed
    delay = time delay between each image
    """
    cpt = 0
    ret, img = my_video.read()

    if img is not None:
        cv.namedWindow("Vid", cv.WINDOW_AUTOSIZE)
    else:
        return None

    nFrames = int(my_video.get(cv.CAP_PROP_FRAME_COUNT))
    while cpt < nFrames:
        for ii in range(frame_inc):
            ret, img = my_video.read()
            cpt += 1

        cv.imshow("Vid", img)
        cv.waitKey(delay)


def grab_images(video_file, frame_inc=100, delay=100):
    """
    Walks through the entire video and save image for each increment
    """
    my_video = init_video(video_file)
    if my_video is not None:
        # Display the video and save every increment frames
        cpt = 0
        ret, img = my_video.read()

        if img is not None:
            cv.namedWindow("Vid", cv.WINDOW_AUTOSIZE)
        else:
            return None

        nFrames = int(my_video.get(cv.CAP_PROP_FRAME_COUNT))
        while ret:
            cv.imshow("Vid", img)
            out_name = f"data/output/{cpt}.jpg"
            cv.imwrite(out_name, img)
            #print(out_name, str(nFrames))
            cv.waitKey(delay)
            ret, img = my_video.read()
            cpt += 1
    else:
        return None


def to_gray(img):
    """
    Converts the input to gray levels
    Returns a one channel image
    """
    grey_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return grey_img


def grey_histogram(img, nBins=64):
    """
    Returns a one-dimensional histogram for the given image
    The image is expected to have one channel, 8 bits depth
    nBins can be defined between 1 and 255
    """
    hist = cv.calcHist([img], [0], None, [nBins], [0, 256])
    return hist


def extract_bright(grey_img, histogram=False):
    """
    Extracts the brightest part of the image.
    Expected to be the LEDs (provided that there is a dark background)
    Returns a Thresholded image
    histogram defines if we use the hist calculation to find the best margin
    """
    # Searches for image maximum (brightest pixel)
    # We expect the LEDs to be brighter than the rest of the image
    maxVal = np.max(grey_img)
    #print("Brightest pixel val is %d" % (maxVal))

    # We retrieve only the brightest part of the image
    # Here is use a fixed margin (80%), but you can use hist to enhance this one
    if 0:
        # Histogram may be used to wisely define the margin
        # We expect a huge spike corresponding to the mean of the background
        # and another smaller spike of bright values (the LEDs)
        hist = grey_histogram(img, nBins=64)
        hminValue, hmaxValue, hminIdx, hmaxIdx = cv.minMaxLoc(hist)
        margin = 0  # statistics to be calculated using hist data
    else:
        margin = 0.8

    thresh = 150#int(maxVal * margin)  # in pixel value to be extracted
    #print("Threshold is defined as %d" % (thresh))

    _, thresh_img = cv.threshold(grey_img, thresh, 255, cv.THRESH_BINARY)

    return thresh_img



def find_leds(thresh_img):
    """
    Given a binary image showing the brightest pixels in an image,
    returns a result image, displaying found leds in a rectangle
    """
    contours, _ = cv.findContours(thresh_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    regions = []

    for cnt in contours:
        x, y, width, height = cv.boundingRect(cnt)
        if height > 15:
            sensitivity = 25
            regions.append((x, y, width, height))

    out_img = np.copy(grey_img)
    out_img = cv.cvtColor(out_img, cv.COLOR_GRAY2BGR)

    for x, y, width, height in regions:
        pt1 = x, y
        pt2 = x + width, y + height
        color = (0, 0, 255)
        cv.rectangle(out_img, pt1, pt2, color, 2)

    return out_img, regions


def leds_positions(regions):
    """
    Function using the regions in input to calculate the position of found leds
    """
    centers = []
    for x, y, width, height in regions:
        centers.append([x + (width / 2), y + (height / 2)])

    return centers


if __name__ == '__main__':
    video_file = "video.mov"
    capture = cv.VideoCapture(video_file)
    if 0:
        # do once once, create some images out of the video
        grab_images(video_file, frame_inc=100, delay=100)
    a = 0
    b = 0

    while a < int(capture.get(cv.CAP_PROP_FRAME_COUNT)):

        img = cv.imread(f"data/output/{a}.jpg")
        if img is not None:
            # Displays the image I'll be working with
            display_img(img, delay=100)
        else:
            print("IMG not found !")
            sys.exit(0)

        # Starts image processing here
        # Turns to a one-channel image
        grey_img = to_gray(img)
        display_img(grey_img, 1000)
        # Detect the brightest point in the image:
        thresh_img = extract_bright(grey_img)
        display_img(thresh_img, delay=1000)

        # We want to extract the elements left and count their number
        led_img, regions = find_leds(thresh_img)
        display_img(led_img, delay=1000)

        centers = leds_positions(regions)

        #print("Total number of LEDs found: %d !" % (len(centers)))
        #print("###")
        #print("LED positions:")
        byte = [0,0,0,0,0,0,0,0]
        for c in centers:
            pass
            y = int(c[1])
            if 200 < y < 300:
                byte[0] = 1
            elif 400 < y < 500:
                byte[1] = 1
            elif 550 < y < 650:
                byte[2] = 1
            elif 750 < y < 850:
                byte[3] = 1
            elif 950 < y < 1050:
                byte[4] = 1
            elif 1150 < y < 1250:
                byte[5] = 1
            elif 1350 < y < 1450:
                byte[6] = 1
            elif 1450 < y < 1550:
                byte[7] = 1
            print("x : %d; y : %d" % (int(c[0]), int(c[1])))
        print(byte)
        if b != 0:
            if output[b - 1] != byte:
                output.append(byte)
                b += 1
        else:
            output.append(byte)
            b += 1
        #print("###")
        a += 1
        with open("output.txt", "w") as f:
            f.write("")
        for i in output:
            with open("output.txt", "a") as f:
                f.write(str(i)+'\n')
        print(a)