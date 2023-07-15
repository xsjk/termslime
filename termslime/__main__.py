import argparse as __argparse
import os as __os
import platform as __platform
import cv2 as __cv2
import random as __random
import time as __time
import threading as __threading
import queue as __queue
import joblib as __joblib

if __platform.system() == "Windows":
    __os.system("color")
    
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

    resizeRatio = max(1, imgHeight / (heightLimit * 2), imgWidth / widthLimit)
    newSize = (int(imgWidth / resizeRatio), int(imgHeight / resizeRatio / 2) * 2)

    # compress the image to fit the width and height limits and make sure the compressed height is even
    imgResized = __cv2.resize(img, newSize, interpolation=interpolation)

    # print the begin padding
    print(end="\n" * beginPadding)
    # for each two row numbers x and x+1 of pixels
    for x in range(0, imgResized.shape[0], 2):
        # print the left padding
        print(end=" " * leftPadding)

        # for each column number y of pixels
        for y in range(0, imgResized.shape[1]):
            # get the two pixels that will be displayed in the same block in the terminal
            pU = imgResized[x, y]
            pL = imgResized[x + 1, y]

            # if the two pixels are transparent, print a space
            if pU[-1] == 0 and pL[-1] == 0:
                print(end=" ")

            # if only the upper pixel is transparent, print a lower half block with the lower pixel's color as the foreground color
            elif pU[-1] == 0:
                print(end=f"\033[0m\033[38;2;{pL[0]};{pL[1]};{pL[2]}m▄")

            # if only the lower pixel is transparent, print a upper half block with the upper pixel's color as the foreground color
            elif pL[-1] == 0:
                print(end=f"\033[0m\033[38;2;{pU[0]};{pU[1]};{pU[2]}m▀")

            # if either of the two pixels is transparent, print a lower half block with the corresponding pixel's color as the foreground and background colors
            else:
                print(end=f"\033[48;2;{pU[0]};{pU[1]};{pU[2]}m\033[38;2;{pL[0]};{pL[1]};{pL[2]}m▄")

        # start a new row
        print("\033[0m")

    # print the end padding
    print(end="\n" * endPadding)


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

    cap = __cv2.VideoCapture(videoPath)

    fps = cap.get(__cv2.CAP_PROP_FPS)
    frameCount = int(cap.get(__cv2.CAP_PROP_FRAME_COUNT))
    duration = frameCount / fps

    print(f"fps: {fps:.2f}")
    print(f"frame count: {frameCount}")
    print(f"duration: {duration:.2f}s")

    try:
        # clear the terminal
        print("\033[2J", end="")

        # hide the cursor
        print("\033[?25l", end="")

        data_queue = __queue.Queue(maxsize=1)
        running = True

        def row_to_str(frame, i):
            s = ""
            for j in range(frame.shape[1]):
                pU = frame[i, j]
                pL = frame[i + 1, j]
                s += f"\033[{beginPadding+i//2+1};{leftPadding+j+1}H"
                s += f"\033[48;2;{pU[0]};{pU[1]};{pU[2]}m"
                s += f"\033[38;2;{pL[0]};{pL[1]};{pL[2]}m"
                s += "▄"
            return s

        def to_str(frame):
            return "".join(
                __joblib.Parallel(n_jobs=16)(
                    __joblib.delayed(row_to_str)(frame, i)
                    for i in range(0, frame.shape[0], 2)
                )
            )

        start_time = __time.time()
        virtual_time: float = 0

        def print_str():
            nonlocal virtual_time

            while running:
                try:
                    s = data_queue.get(timeout=0.5)
                except __queue.Empty:
                    pass
                else:
                    print(end=s)
                    virtual_time = __time.time() - start_time
                    # print(end=f"\033[{2};0H\033[0m print FPS: {1/(__time.time()-t):.2f}")

        print_thread = __threading.Thread(target=print_str)
        print_thread.start()

        # first frame
        _, frame = cap.read()

        imgWidth, imgHeight = frame.shape[1], frame.shape[0]
        # calculate the resize ratio
        resizeRatio = max(1, imgHeight / (heightLimit * 2), imgWidth / widthLimit)
        newSize = (int(imgWidth / resizeRatio), int(imgHeight / resizeRatio / 2) * 2)

        while frame is not None:
            resized_frame = __cv2.resize(frame, newSize, interpolation=interpolation)
            real_colored_frame = __cv2.cvtColor(resized_frame, __cv2.COLOR_BGR2RGBA)
            data_queue.put(to_str(real_colored_frame))

            cur_frame = cap.get(__cv2.CAP_PROP_POS_FRAMES)

            if virtual_time < cur_frame / fps:
                # too fast
                __time.sleep(0.01)
            else:
                # too slow
                num_frames_to_skip = int(virtual_time * fps - cur_frame)
                print(end=f"\033[{1};0H\033[0m skip {num_frames_to_skip} frames")
                if num_frames_to_skip > 0:
                    cap.set(__cv2.CAP_PROP_POS_FRAMES, cur_frame + num_frames_to_skip)

            _, frame = cap.read()
            # print(end=f"\033[{1};0H\033[0m tostr FPS: {1/(__time.time()-t):.2f}")

    except KeyboardInterrupt:
        pass

    finally:
        running = False
        print_thread.join()

        # reset the foreground and background colors
        print("\033[0m", end="")

        # show the cursor
        print("\033[?25h", end="")

        # print the end padding
        print(f"\033[{beginPadding+newSize[1]//2+endPadding+1};1H", end="")

        cap.release()


def __is_img_file(path: str) -> bool:
    return any(path.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".bmp"))


def __is_video_file(path: str) -> bool:
    return any(path.endswith(ext) for ext in (".mp4", ".avi", ".mkv"))


def __main():
    """
    Entry point.
    """

    # set up the argument parser
    parser = __argparse.ArgumentParser(
        prog="tslime",
        description="Termslime displays images in your terminal with true colors. Project home page: https://github.com/xsjk/termslime.",
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
        choices=[v[6:] for v in dir(__cv2) if v.startswith("INTER_")],
    )

    # parse the arguments
    terminalSize = __os.get_terminal_size()
    args = parser.parse_args()
    if args.heightLimit is None:
        args.heightLimit = terminalSize.lines - args.beginPadding - args.endPadding
        print("use default height limit:", args.heightLimit)
    if args.widthLimit is None:
        args.widthLimit = terminalSize.columns - args.leftPadding
        print("use default width limit:", args.widthLimit)
    if args.heightLimit > terminalSize.lines:
        raise ValueError(f"height limit exceeds terminal height {terminalSize.lines}")
    if args.widthLimit > terminalSize.columns:
        raise ValueError(f"width limit exceeds terminal width {terminalSize.columns}")
    

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
