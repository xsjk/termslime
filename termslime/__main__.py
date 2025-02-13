import argparse as __argparse
import os as __os
import platform as __platform
import cv2 as __cv2
import numpy as __np
import random as __random
import time as __time
import threading as __threading
import queue as __queue
import joblib as __joblib
import re as __re
import pkgutil as __pkgutil
from datetime import timedelta

if __platform.system() == "Windows":
    __os.system("color")

ENABLE_AUDIO = __pkgutil.find_loader('ffpyplayer') is not None
if ENABLE_AUDIO:
    from ffpyplayer.player import MediaPlayer as __MediaPlayer

    
def __display_img(
    img: str | __np.ndarray,
    heightLimit: int,
    widthLimit: int,
    beginPadding: int,
    endPadding: int,
    leftPadding: int,
    interpolation: int,
    verbose: bool
) -> None:
    """
    Display an image by printing half blocks with foreground and background colors to the terminal.

    Args:
        img (str | np.ndarray): the path to the image file or the image array
        heightLimit (int): maximum number of lines of blocks to display the image in the terminal
        widthLimit (int): maximum number of blocks per line to display the image in the terminal
        beginPadding (int): number of empty lines before the image
        endPadding (int): number of empty lines after the image
        leftPadding (int): number of empty spaces at the beginning of each line of the image
        interpolation (int): interpolation method used to resize the image
        verbose (bool): if True, print more information
    """

    if isinstance(img, str):
        # open the image
        img = __np.fromfile(img, dtype=__np.uint8)
        img = __cv2.imdecode(img, __cv2.IMREAD_UNCHANGED)
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


class ProgressBar:

    BAR_COLOR_EMPTY = "\033[38;2;58;58;58m"
    BAR_COLOR_FULL = "\033[38;2;58;95;0m"
    TIME_COLOR = "\033[38;2;66;179;189m"

    def __init__(self, width: int, total: float, x: int = 0, y: int = 0) -> None:
        self.width = width
        self.total = total
        self.x = x
        self.y = y
        self.current = 0

    def init(self):
        time_str = f"{timedelta(seconds=0)} / {timedelta(seconds=int(self.total))}"
        self.bar_width = self.width - len(time_str) - 2
        print(end=f"\033[0m\033[{self.y};{self.x}H{self.BAR_COLOR_EMPTY}{'━'*self.bar_width}  {self.TIME_COLOR}{time_str}")

    def set(self, value: float) -> None:
        x = value / self.total * self.bar_width
        x_int = int(round(x))
        if x_int == self.bar_width:
            return self.finish()
        
        print(end=f"\033[0m\033[{self.y};{self.x}H{self.BAR_COLOR_FULL}{'━'*x_int}")
        print(end=f"╸{self.BAR_COLOR_EMPTY}" if x - int(x) < 0.5 else f"{self.BAR_COLOR_EMPTY}╺")
        print(end=f"{'━'*int(self.bar_width-x_int-1)}  {self.TIME_COLOR}{timedelta(seconds=int(value))}")

    def finish(self) -> None:
        print(end=f"\033[0m\033[{self.y};{self.x}H{self.BAR_COLOR_FULL}{'━'*self.bar_width}  {self.TIME_COLOR}{timedelta(seconds=int(self.total))}")

    def __enter__(self):
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            raise exc_value
        self.finish()

def __display_video(
    videoPath: str,
    heightLimit: int,
    widthLimit: int,
    beginPadding: int,
    endPadding: int,
    leftPadding: int,
    interpolation: int,
    ignoreFrameRate: bool,
    verbose: bool
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
        ignoreFrameRate (bool): if True, ignore the frame rate of the video and display the video as fast as possible
        verbose (bool): if True, print more information
    """

    cap = __cv2.VideoCapture(videoPath)

    fps = cap.get(__cv2.CAP_PROP_FPS)
    frameCount = int(cap.get(__cv2.CAP_PROP_FRAME_COUNT))
    if frameCount == 1:
        _, frame = cap.read()
        return __display_img(
            frame,
            heightLimit,
            widthLimit,
            beginPadding,
            endPadding,
            leftPadding,
            interpolation,
        )

    heightLimit -= 2 # line for progress bar

    # start the audio player
    if ENABLE_AUDIO:
        audio = __MediaPlayer(videoPath)
    
    duration = frameCount / fps

    if verbose:
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
                pU = frame[0, j]
                pL = frame[1, j]
                s += f"\033[{beginPadding+i//2+1};{leftPadding+j+1}H"
                s += f"\033[48;2;{pU[0]};{pU[1]};{pU[2]}m"
                s += f"\033[38;2;{pL[0]};{pL[1]};{pL[2]}m"
                s += "▄"
            return s

        def to_str(frame):
            return "".join(
                __joblib.Parallel()(
                    __joblib.delayed(row_to_str)(frame[i:i+2], i)
                    for i in range(0, frame.shape[0], 2)
                )
            )

        # wait for the first audio frame
        while ENABLE_AUDIO:
            audio_frame, val = audio.get_frame()
            if audio_frame:
                pic, time = audio_frame
                if time > 0:
                    break

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

        print_thread = __threading.Thread(target=print_str)
        print_thread.start()

        # first frame
        _, frame = cap.read()

        imgWidth, imgHeight = frame.shape[1], frame.shape[0]
        # calculate the resize ratio
        resizeRatio = max(1, imgHeight / (heightLimit * 2), imgWidth / widthLimit)
        newSize = (int(imgWidth / resizeRatio), int(imgHeight / resizeRatio / 2) * 2)


        with ProgressBar(
            width=newSize[0], 
            total=duration, 
            x=leftPadding+1, 
            y=beginPadding+newSize[1]//2+1
        ) as progress_bar:

            while frame is not None:
                resized_frame = __cv2.resize(frame, newSize, interpolation=interpolation)
                real_colored_frame = __cv2.cvtColor(resized_frame, __cv2.COLOR_BGR2RGBA)
                data_queue.put(to_str(real_colored_frame))

                cur_frame = cap.get(__cv2.CAP_PROP_POS_FRAMES)
        
                progress_bar.set(cur_frame / fps)

                if not ignoreFrameRate:
                    # sync video and virtual time
                    if virtual_time < cur_frame / fps:
                        __time.sleep(1 / fps)
                    else:
                        num_frames_to_skip = int(virtual_time * fps - cur_frame)
                        # print(end=f"\033[{1};0H\033[0m skip {num_frames_to_skip} frames")
                        if num_frames_to_skip > 0:
                            cap.set(__cv2.CAP_PROP_POS_FRAMES, cur_frame + num_frames_to_skip)

                _, frame = cap.read()


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
        print(f"\033[{beginPadding+newSize[1]//2+endPadding+2};1H", end="")

        cap.release()


def __get_file_type(path: str, verbose: bool = True) -> str:
    '''
    Get the file type of the file at the given path.

    Parameters
    ----------
    path : str
        The path to the file.

    Returns
    -------
    str : The file type of the file at the given path.

    Notes
    -----
    The file type is determined by the first few bytes of the file.
    If the file type cannot be determined, the file extension is returned.

    '''

    fmt2prefixes = {
        'jpg': rb"\xFF\xD8\xFF",
        'png': rb"\x89PNG\r\n\x1a\n",
        'bmp': rb"BM",
        'ppm': rb"P[0-6y]",
        'tiff': rb"MM\x00\x2A|II\x2A\x00|MM\x2A\x00|II\x00\x2A|MM\x00\x2B|II\x2B\x00",
        'gif': rb"GIF87a|GIF89a",
        'webp': rb"RIFF....WEBPVP8[ LX]",
        'mp4': rb"....ftyp(?:isom|MSNV|mp42|avc[13]|iso2|mp41)",
        'avi': rb"RIFF....AVI LIST",
        'mpeg': rb"\x00\x00\x01[\xB3\xBA]",
        'mov': rb"\x00\x00\x00\x14ftyp(?:qt|isom|mp42|mp41)",
        'mkv': rb"\x1A\x45\xDF\xA3",
        'flv': rb"FLV\x01",
        'wmv': rb"\x30\x26\xB2\x75\x8E\x66\xCF\x11",
        'ts': rb"\x47",
    }

    prefix = open(path, 'rb').read(32)
    
    for fmt, prefixes in fmt2prefixes.items():
        if __re.search(prefixes, prefix):
            if verbose:
                print(f"Determined file type: {fmt}")
            return fmt
    if verbose:
        print(f"Cannot determine file type, use file extension: {__os.path.splitext(path)[1][1:]}")
    return __os.path.splitext(path)[1][1:].casefold()

def __is_img_file(path: str, verbose: bool = False) -> bool:
    return __get_file_type(path, verbose) in ('jpg', 'png', 'bmp', 'ppm', 'tiff', 'webp')

def __is_video_file(path: str, verbose: bool = False) -> bool:
    return __get_file_type(path, verbose) in ('gif', 'mp4', 'avi', 'mpeg', 'mov', 'mkv', 'flv', 'wmv', 'ts')

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
        default=0,
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
    parser.add_argument(
        "-a"
        "--allFrames",
        dest="ignoreFrameRate",
        action="store_true",
        help="display all the frames of the video without considering the frame rate",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print more information",
    )

    # parse the arguments
    terminalSize = __os.get_terminal_size()
    args = parser.parse_args()
    if args.heightLimit is None:
        args.heightLimit = terminalSize.lines - args.beginPadding - args.endPadding
        if args.verbose:
            print("use default height limit:", args.heightLimit)
    if args.widthLimit is None:
        args.widthLimit = terminalSize.columns - args.leftPadding
        if args.verbose:
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

    if __is_img_file(filePath, args.verbose):
        __display_img(
            filePath,
            args.heightLimit,
            args.widthLimit,
            args.beginPadding,
            args.endPadding,
            args.leftPadding,
            args.interpolation,
            args.verbose
        )

    elif __is_video_file(filePath, args.verbose):
        __display_video(
            filePath,
            args.heightLimit,
            args.widthLimit,
            args.beginPadding,
            args.endPadding,
            args.leftPadding,
            args.interpolation,
            args.ignoreFrameRate,
            args.verbose
        )


if __name__ == "__main__":
    __main()
