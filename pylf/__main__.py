# coding: utf-8
import argparse
import os
import sys
import time

import PIL.Image
import PIL.ImageFont
import yaml

import pylf


ENCODING = "utf-8"

TEXT_FILE = "content.txt"

TEMPLATE_FILE = "template.yml"
FONT_FILE_NAME = "font"
BACKGROUND_FILE_NAME = "background"

OUTPUT_DIRECTORY = "out"
OUTPUT_FORMAT = "png"

DESCRIPTION = """
在预先配置好的手写项目上模拟手写

手写项目须含以下文件：
{text_file}\t\t\t待手写内容（须为UTF-8编码）
{font_file_name}.[ttf|...]\t\t\t用于手写的字体，须为TrueType或OpenType字体文件
{background_file_name}.[png|jpg|...]\t用于手写的背景图片，图片格式须被Pillow库和PyLf
\t\t\t\t库所支持
{template_file}\t\t\t用于手写的其余参数（须为UTF-8编码）
{output_directory}\t\t\t\t存放生成图片的文件夹（此文件夹可由程序自动创建）

{template_file}示例：
================================================================================
margin:  # 页边距（单位：像素）
  left: 150
  right: 150
  top: 200
  bottom: 200
line_spacing: 150  # 行间距（单位：像素）
font_size: 100  # 字体大小（单位：像素）
word_spacing: 0  # 字间距，缺省值：0（单位：像素）
color: "black"  # 字体颜色，缺省值："black"，详情：https://pillow.readthedocs.io/en/5.2.x/reference/ImageColor.html#color-names

# 以下为随机参数，用于调节相关量的随机性强弱，值越高相关量的随机性越明显
line_spacing_sigma: 3.1  # 行间距的高斯分布的σ，缺省值：font_size / 32
font_size_sigma: 1.6  # 字体大小的高斯分布的σ，缺省值：font_size / 64
word_spacing_sigma: 3.1  # 字间距的高斯分布的σ，缺省值：font_size / 32
perturb_x_sigma: 3.1  # 笔画水平位置的高斯分布的σ，缺省值：font_size / 32
perturb_y_sigma: 3.1  # 笔画竖直位置的高斯分布的σ，缺省值：font_size / 32
perturb_theta_sigma: 0.07  # 笔画旋转角度的高斯分布的σ，缺省值：0.07
================================================================================
""".format(
    text_file=TEXT_FILE,
    font_file_name=FONT_FILE_NAME,
    background_file_name=BACKGROUND_FILE_NAME,
    template_file=TEMPLATE_FILE,
    output_directory=OUTPUT_DIRECTORY
)


def run(*args):
    args = _parse_args(args)
    images = pylf.handwrite(
        _get_text(args.project),
        _get_template(args.project)
    )
    _output(args.project, images, args.quiet)


def _parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        add_help=False
    )
    parser.add_argument(
        "project",
        help="手写项目的路径"
    )
    parser.add_argument(
        "-h", "--help",
        action="help",
        help="显示此帮助信息并退出"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="运行时关闭输出"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="PyLf {}".format(pylf.__version__),
        help="显示程序版本号并退出"
    )
    return parser.parse_args(args)


def _get_text(parent: str):
    path = os.path.join(parent, TEXT_FILE)
    with open(path, encoding=ENCODING) as file:
        return file.read()


def _get_template(parent: str):
    with open(
            os.path.join(parent, TEMPLATE_FILE),
            encoding=ENCODING
    ) as file:
        template = yaml.safe_load(file)

    template["background"] = PIL.Image.open(
        os.path.join(parent, _get_file(parent, BACKGROUND_FILE_NAME))
    )

    template["font"] = PIL.ImageFont.truetype(
        os.path.join(parent, _get_file(parent, FONT_FILE_NAME))
    )
    return template


def _get_file(parent: str, name: str) -> str:
    return next(
        (f for f in os.listdir(parent) if f.startswith(name + '.'))
    )


def _output(parent: str, images, quiet: bool):
    path = _get_output_path(parent)
    for index, image in enumerate(images):
        image.save(
            os.path.join(path, "{}.{}".format(index, OUTPUT_FORMAT))
        )
    if quiet:
        return
    msg = "成功生成{}张图片！请查看文件夹{}。"
    print(msg.format(len(images), path))


def _get_output_path(parent: str) -> str:
    path = os.path.join(
        parent,
        OUTPUT_DIRECTORY,
        "{:.6f}".format(time.time()).replace('.', '')
    )
    os.makedirs(path, exist_ok=True)
    return path


def main():
    run(*sys.argv[1:])


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()