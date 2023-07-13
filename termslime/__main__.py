import argparse as __argparse
import os as __os
import cv2 as __cv2
import random as __random

def __display_img(
    imgPath: str,
    heightLimit: int,
    widthLimit: int,
    beginPadding: int,
    endPadding: int,
    leftPadding: int,
    interpolation: int,
) -> None:
    """
    Display an image by printing half blocks with foreground and background colors to the terminal.

    Args:
        imgPath (str): the path to the image file
        heightLimit (int): maximum number of lines of blocks to display the image in the terminal
        widthLimit (int): maximum number of blocks per line to display the image in the terminal
        beginPadding (int): number of empty lines before the image
        endPadding (int): number of empty lines after the image
        leftPadding (int): number of empty spaces at the beginning of each line of the image
        interpolation (int): interpolation method used to resize the image
    """

    # open the image
    img = __cv2.imread(imgPath, __cv2.IMREAD_UNCHANGED)
    img = __cv2.cvtColor(img, __cv2.COLOR_BGR2RGBA)
    imgWidth, imgHeight = img.shape[1], img.shape[0]

    # calculate the resize ratio
    resizeRatio = imgHeight / (heightLimit * 2) if imgHeight > heightLimit * 2 else 1
    resizeRatio = (
        imgWidth / widthLimit
        if int(imgWidth / resizeRatio) > widthLimit
        else resizeRatio
    )

    # compress the image to fit the width and height limits and make sure the compressed height is even
    imgResized = __cv2.resize(
        img,
        (int(imgWidth / resizeRatio), int(imgHeight / resizeRatio / 2) * 2),
        interpolation=interpolation,
    )

    # print the begin padding
    print("\n" * beginPadding, end="")
    # for each two row numbers x and x+1 of pixels
    for x in range(0, imgResized.shape[0], 2):
        # print the left padding
        print(" " * leftPadding, end="")

        # for each column number y of pixels
        for y in range(0, imgResized.shape[1]):
            # initialize the palette
            p = {}

            # get the two pixels that will be displayed in the same block in the terminal
            pixelUpper = imgResized[x, y]
            pixelLower = imgResized[x + 1, y]

            # if the two pixels are transparent, print a space
            if pixelUpper[-1] == 0 and pixelLower[-1] == 0:
                print(" ", end="")

            # if only the upper pixel is transparent, print a lower half block with the lower pixel's color as the foreground color
            elif pixelUpper[-1] == 0:
                print(f"\033[38;2;{pixelLower[0]};{pixelLower[1]};{pixelLower[2]}m▄", end="")

            # if only the lower pixel is transparent, print a upper half block with the upper pixel's color as the foreground color
            elif pixelLower[-1] == 0:
                print(f"\033[48;2;{pixelUpper[0]};{pixelUpper[1]};{pixelUpper[2]}m▀", end="")

            # if either of the two pixels is transparent, print a lower half block with the corresponding pixel's color as the foreground and background colors
            else:
                print(f"\033[48;2;{pixelUpper[0]};{pixelUpper[1]};{pixelUpper[2]}m\033[38;2;{pixelLower[0]};{pixelLower[1]};{pixelLower[2]}m▄", end="")

        # start a new row
        print("\033[0m")

    # print the end padding
    print("\n" * endPadding, end="")


def __display_video(
    videoPath: str,
    heightLimit: int,
    widthLimit: int,
    beginPadding: int,
    endPadding: int,
    leftPadding: int,
    interpolation: int,
) -> None:
    """
    Display a video by printing half blocks with foreground and background colors to the terminal.

    Args:
        videoPath (str): the path to the video file
        heightLimit (int): maximum number of lines of blocks to display the image in the terminal
        widthLimit (int): maximum number of blocks per line to display the image in the terminal
        beginPadding (int): number of empty lines before the image
        endPadding (int): number of empty lines after the image
        leftPadding (int): number of empty spaces at the beginning of each line of the image
        interpolation (int): interpolation method used to resize the image
    """

    import cv2 as __cv2

    cap = __cv2.VideoCapture(videoPath)

    # __os.system("cls" if __platform.system() == "Windows" else "clear")
    print("\033[2J", end="")

    while cap.isOpened():
        ret, frame = cap.read()

        # move the cursor to the top left corner of the terminal
        print("\033[0;0H", end="")

        # clear the terminal
        imgWidth, imgHeight = frame.shape[1], frame.shape[0]

        # calculate the resize ratio
        resizeRatio = (
            imgHeight / (heightLimit * 2) if imgHeight > heightLimit * 2 else 1
        )
        resizeRatio = (
            imgWidth / widthLimit
            if int(imgWidth / resizeRatio) > widthLimit
            else resizeRatio
        )

        # compress the image to fit the width and height limits and make sure the compressed height is even
        imgResized = __cv2.resize(
            frame,
            (int(imgWidth / resizeRatio), int(imgHeight / resizeRatio / 2) * 2),
            interpolation=interpolation,
        )

        # print the begin padding
        print("\n" * beginPadding, end="")
        # for each two row numbers x and x+1 of pixels
        for x in range(0, imgResized.shape[0], 2):
            # print the left padding
            print(" " * leftPadding, end="")

            # for each column number y of pixels
            for y in range(0, imgResized.shape[1]):
                # initialize the palette

                # get the two pixels that will be displayed in the same block in the terminal
                pixelUpper = imgResized[x, y]
                pixelLower = imgResized[x + 1, y]

                print(f"\033[48;2;{pixelUpper[0]};{pixelUpper[1]};{pixelUpper[2]}m\033[38;2;{pixelLower[0]};{pixelLower[1]};{pixelLower[2]}m▄", end="")

            # start a new row
            print("\033[0m")

        # print the end padding
        print("\n" * endPadding, end="")

    cap.release()


def __is_img_file(path: str) -> bool:
    return (
        path.endswith(".png")
        or path.endswith(".jpg")
        or path.endswith(".jpeg")
        or path.endswith(".bmp")
    )


def __is_video_file(path: str) -> bool:
    return path.endswith(".mp4") or path.endswith(".avi") or path.endswith(".mkv")


def __main():
    """
    Entry point.
    """

    # set up the argument parser
    parser = __argparse.ArgumentParser(
        prog="tslime",
        description="Termslime displays images in your terminal with true colors. Project home page: https://github.com/garyzbm/termslime.",
    )

    # add arguments
    parser.add_argument(
        "path",
        type=str,
        help="path to an image file or a directory containing image files",
    )
    parser.add_argument(
        "-hl",
        "--heightLimit",
        type=int,
        default=None,
        help="maximum number of lines of blocks to display the image in the terminal",
    )
    parser.add_argument(
        "-wl",
        "--widthLimit",
        type=int,
        default=None,
        help="maximum number of blocks per line to display the image in the terminal",
    )
    parser.add_argument(
        "-bp",
        "--beginPadding",
        type=int,
        default=1,
        help="number of empty lines before the image",
    )
    parser.add_argument(
        "-ep",
        "--endPadding",
        type=int,
        default=0,
        help="number of empty lines after the image",
    )
    parser.add_argument(
        "-lp",
        "--leftPadding",
        type=int,
        default=1,
        help="number of empty spaces at the beginning of each line of the image",
    )
    parser.add_argument(
        "--interpolation",
        type=str,
        default="AREA",
        help="interpolation method used to resize the image",
        choices=[v[6:] for v in dir(__cv2) if v.startswith('INTER_')],
    )

    # parse the arguments
    terminalSize = __os.get_terminal_size()
    args = parser.parse_args()
    if args.heightLimit is None:
        args.heightLimit = terminalSize.lines - args.beginPadding - args.endPadding
    if args.widthLimit is None:
        args.widthLimit = terminalSize.columns - args.leftPadding
    args.interpolation = getattr(__cv2, f"INTER_{args.interpolation}")

    # get path from the arguments
    filePath = args.path
    assert __os.path.exists(filePath), f"{filePath} does not exist"

    # if imgPath is a path to a directory
    if __os.path.isdir(filePath):
        # randomly choose an image from the directory and make imgPath the path to that image
        imgList = [file for file in __os.listdir(filePath) if __is_img_file(file)]
        assert len(imgList) > 0, f"{filePath} does not contain any image files"
        filePath = __os.path.join(filePath, __random.choice(imgList))

    if __is_img_file(filePath):
        __display_img(
            filePath,
            args.heightLimit,
            args.widthLimit,
            args.beginPadding,
            args.endPadding,
            args.leftPadding,
            args.interpolation,
        )

    elif __is_video_file(filePath):
        __display_video(
            filePath,
            args.heightLimit,
            args.widthLimit,
            args.beginPadding,
            args.endPadding,
            args.leftPadding,
            args.interpolation,
        )


if __name__ == "__main__":
    __main()
