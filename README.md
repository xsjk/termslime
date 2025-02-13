<div align="center">

<h1><b>Termslime</b></h1>

<p>Termslime displays images or videos in your terminal with true colors.</p>

<p>
    <img src="https://img.shields.io/pypi/v/termslime.svg">
    <img src="https://img.shields.io/pypi/pyversions/termslime.svg">
    <img src="https://img.shields.io/github/last-commit/xsjk/termslime">
</p>

</div>


## Contents

+ [Requirements](#requirements)
+ [Installation](#installation)
+ [Usage](#usage)
+ [Credits](#credits)


## Requirements

+ A terminal emulator with true color support.
+ Python >= 3.7.


## Installation

```shell
pip install git+https://github.com/xsjk/termslime.git
```


## Usage

```
usage: tslime [-h] [-hl HEIGHTLIMIT] [-wl WIDTHLIMIT] [-bp BEGINPADDING] [-ep ENDPADDING] [-lp LEFTPADDING] [--interpolation {AREA,BITS,BITS2,CUBIC,LANCZOS4,LINEAR,LINEAR_EXACT,MAX,NEAREST,NEAREST_EXACT,TAB_SIZE,TAB_SIZE2}] [-a--allFrames] path

Termslime displays images in your terminal with true colors. Project home page: https://github.com/xsjk/termslime.

positional arguments:
  path                  path to an image file or a directory containing image files

options:
  -h, --help            show this help message and exit
  -hl HEIGHTLIMIT, --heightLimit HEIGHTLIMIT
                        maximum number of lines of blocks to display the image in the terminal
  -wl WIDTHLIMIT, --widthLimit WIDTHLIMIT
                        maximum number of blocks per line to display the image in the terminal
  -bp BEGINPADDING, --beginPadding BEGINPADDING
                        number of empty lines before the image
  -ep ENDPADDING, --endPadding ENDPADDING
                        number of empty lines after the image
  -lp LEFTPADDING, --leftPadding LEFTPADDING
                        number of empty spaces at the beginning of each line of the image
  --interpolation {AREA,BITS,BITS2,CUBIC,LANCZOS4,LINEAR,LINEAR_EXACT,MAX,NEAREST,NEAREST_EXACT,TAB_SIZE,TAB_SIZE2}
                        interpolation method used to resize the image
  -a--allFrames         display all the frames of the video without considering the frame rate
```

## Examples

You can find the example files in the [examples](examples) directory.

Display an image in the terminal with adpative height and width limits:
```shell
tslime test.jpg
```
![](screenshots/screenshot1.png)

Display a transparent image in the terminal with adpative height and width limits:
```shell
tslime test.png
```
![](screenshots/screenshot2.png)

Play a video in the terminal with adpative height and width limits:
```shell
tslime test.mp4
```
![](screenshots/screenshot3.png)

## Credits

This project is greatly inspired by [this post](https://lucamug.medium.com/terminal-pixel-art-ad386d186dad).

The following projects are crucial to the development of this project:
+ [opencv-python](https://docs.opencv.org/4.x/)
+ [joblib](https://joblib.readthedocs.io/en/latest/)


## Uninstallation

```shell
pip uninstall termslime
```

---
*<p align="center">This project is published under [MIT](LICENSE).<br>A [Gary Zhang](https://github.com/garyzbm) and [xsjk](https://github.com/xsjk) project.<br>- :tada: -</p>*