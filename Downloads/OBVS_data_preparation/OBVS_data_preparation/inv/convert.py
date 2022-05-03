import argparse
import os
import sys
import shutil
import math
import random
import re
from transformer import Transformer

def iterate_dir(source, dest, ratio, copy_xml):
    source = source.replace('\\', '/')
    dest = dest.replace('\\', '/')
    train_dir = os.path.join(dest, 'train/images')
    labelst_dir = os.path.join(dest, 'train/labels')
    test_dir = os.path.join(dest, 'valid/images')
    labels_dir = os.path.join(dest, 'valid/labels')

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(labelst_dir):
        os.makedirs(labelst_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    if not os.path.exists(labels_dir):
        os.makedirs(labels_dir)

    images = [f for f in os.listdir(source)
              if re.search(r'([a-zA-Z0-9\s_\\.\-\(\):])+(?i)(.jpg|.jpeg|.png)$', f)]

    num_images = len(images)
    num_test_images = math.ceil(ratio*num_images)

    for i in range(num_test_images):
        idx = random.randint(0, len(images)-1)
        filename = images[idx]
        shutil.move(os.path.join(source, filename),
                 os.path.join(test_dir, filename))
        if copy_xml:
            xml_filename = os.path.splitext(filename)[0]+'.txt'
            shutil.move(os.path.join(source, xml_filename),
                     os.path.join(labels_dir, xml_filename))
        images.remove(images[idx])

    for filename in images:
        shutil.move(os.path.join(source, filename),
                 os.path.join(train_dir, filename))
        if copy_xml:
            xml_filename = os.path.splitext(filename)[0]+'.txt'
            shutil.move(os.path.join(source, xml_filename),
                     os.path.join(labelst_dir, xml_filename))

def main():
    parser = argparse.ArgumentParser(description="Formatter from ImageNet xml to Darknet text format")
    parser.add_argument("-src", help="Relative location of xml files directory", required=True)
    parser.add_argument("-out", help="Relative location of output txt files directory", default="data")
    parser.add_argument("-c", help="Relative path to classes file", default="classes.txt")
   
    parser.add_argument(
        '-i', '--imageDir',
        help='Path to the folder where the image dataset is stored. If not specified, the CWD will be used.',
        type=str,
        default=os.getcwd()
    )
    parser.add_argument(
        '-o', '--outputDir',
        help='Path to the output folder where the train and test dirs should be created. '
             'Defaults to the same directory as IMAGEDIR.',
        type=str,
        default=None
    )
    parser.add_argument(
        '-r', '--ratio',
        help='The ratio of the number of test images over the total number of images. The default is 0.1.',
        default=0.2,
        type=float)
    parser.add_argument(
        '-t', '--txt',
        help='Set this flag if you want the xml annotation files to be processed and copied over.',
        action='store_true'
    )
    args = parser.parse_args()

    if args.outputDir is None:
        args.outputDir = args.out
    
    xml_dir = os.path.join(os.path.dirname(os.path.realpath('__file__')), args.src)
    if not os.path.exists(xml_dir):
        print("Provide the correct folder for xml files.")
        sys.exit()

    out_dir = os.path.join(os.path.dirname(os.path.realpath('__file__')), args.out)
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if not os.access(out_dir, os.W_OK):
        print("%s folder is not writeable." % out_dir)
        sys.exit()
    
    class_file = os.path.join(os.path.dirname(os.path.realpath('__file__')), args.c)

    if not os.access(class_file, os.F_OK):
        print("%s file is missing." % class_file)
        sys.exit()

    if not os.access(class_file, os.R_OK):
        print("%s file is not readable." % class_file)
        sys.exit()
    
    transformer = Transformer(xml_dir=xml_dir, out_dir=out_dir, class_file=class_file)
    transformer.transform()
    for filename in os.listdir(xml_dir):
        if filename.endswith(".jpg") or filename.endswith(".PNG") or filename.endswith(".JPEG"):
                  shutil.move(os.path.join(xml_dir, filename),
                     os.path.join(out_dir, filename))
    #shutil.rmtree(xml_dir, ignore_errors=False, onerror=None)
    iterate_dir(args.out, args.outputDir, args.ratio, args.txt)
    


if __name__ == "__main__":
    main()
