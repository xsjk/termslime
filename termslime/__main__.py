import colorful as __cf
import argparse as __argparse
import os as __os
import random as __random

# use true colors to display the image
__cf.use_true_colors()

def __display_img(
    imgPath: str,
    heightLimit: int,
    widthLimit: int,
    beginPadding: int,
    endPadding: int,
    leftPadding: int,
) -> None:
    
    """
    Display an image by printing half blocks with foreground and background colors to the terminal.

    Args:
        imgPath - the path to the image file
        heightLimit - maximum number of lines of blocks to display the image in the terminal
        widthLimit - maximum number of blocks per line to display the image in the terminal
        beginPadding - number of empty lines before the image
        endPadding - number of empty lines after the image
        leftPadding - number of empty spaces at the beginning of each line of the image
    """

    import PIL.Image as __Image

    # open the image and convert it to 256 colors and get its width and height
    img = __Image.open(imgPath).convert(mode="RGBA")
    imgWidth, imgHeight = img.size[0], img.size[1]

    # calculate the resize ratio
    resizeRatio = imgHeight / (heightLimit * 2) if imgHeight > heightLimit * 2 else 1
    resizeRatio = (
        imgWidth / widthLimit
        if int(imgWidth / resizeRatio) > widthLimit
        else resizeRatio
    )

    # compress the image to fit the width and height limits and make sure the compressed height is even
    imgResized = img.resize(
        (int(imgWidth / resizeRatio), int(imgHeight / resizeRatio / 2) * 2),
        __Image.Resampling.LANCZOS,
    )

    # print the begin padding
    print("\n" * beginPadding, end="")

    # for each two row numbers x and x+1 of pixels
    for x in range(0, imgResized.size[1], 2):
        # print the left padding
        print(" " * leftPadding, end="")

        # for each column number y of pixels
        for y in range(0, imgResized.size[0]):
            # initialize the palette
            p = {}

            # get the two pixels that will be displayed in the same block in the terminal
            pixelUpper = imgResized.getpixel((y, x))
            pixelLower = imgResized.getpixel((y, x + 1))

            # if the two pixels are transparent, print a space
            if pixelUpper[-1] == 0 and pixelLower[-1] == 0:
                print(" ", end="")

            # if only the upper pixel is transparent, print a lower half block with the lower pixel's color as the foreground color
            elif pixelUpper[-1] == 0:
                p["fore"] = tuple(pixelLower[:-1])
                with __cf.with_palette(p) as c:
                    print(c.fore("▄"), end="")

            # if only the lower pixel is transparent, print a upper half block with the upper pixel's color as the foreground color
            elif pixelLower[-1] == 0:
                p["fore"] = tuple(pixelUpper[:-1])
                with __cf.with_palette(p) as c:
                    print(c.fore("▀"), end="")

            # if either of the two pixels is transparent, print a lower half block with the corresponding pixel's color as the foreground and background colors
            else:
                p["fore"] = tuple(pixelLower[:-1])
                p["back"] = tuple(pixelUpper[:-1])
                with __cf.with_palette(p) as c:
                    print(c.fore_on_back("▄"), end="")

        # start a new row
        print()

    # print the end padding
    print("\n" * endPadding, end="")


def __display_video(
    videoPath: str,
    heightLimit: int,
    widthLimit: int,
    beginPadding: int,
    endPadding: int,
    leftPadding: int,
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
            interpolation=__cv2.INTER_LANCZOS4,
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

                p = {"fore": tuple(pixelLower), "back": tuple(pixelUpper)}
                with __cf.with_palette(p) as c:
                    print(c.fore_on_back("▄"), end="")

            # start a new row
            print()

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

    # parse the arguments
    terminalSize = __os.get_terminal_size()
    args = parser.parse_args()
    if args.heightLimit is None:
        args.heightLimit = terminalSize.lines - args.beginPadding - args.endPadding
    if args.widthLimit is None:
        args.widthLimit = terminalSize.columns - args.leftPadding

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
        # call the display funcPathtion and pass in the arguments
        __display_img(
            filePath,
            args.heightLimit,
            args.widthLimit,
            args.beginPadding,
            args.endPadding,
            args.leftPadding,
        )

    elif __is_video_file(filePath):
        # call the display function and pass in the arguments
        __display_video(
            filePath,
            args.heightLimit,
            args.widthLimit,
            args.beginPadding,
            args.endPadding,
            args.leftPadding,
        )


if __name__ == "__main__":
    __main()
