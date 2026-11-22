import os
import pymupdf

from constants import *


def create_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)


def split(file_input, output_folder, count, **pages):
    if not os.path.exists(file_input):
        raise ValueError("This file doesn't exist!")

    for section, page_range in pages.items():
        doc = pymupdf.open(file_input)

        split_helper(doc, output_folder, section, page_range)

        count += 1

    return count


def split_helper(doc, file_input, output_folder, section, page_range):
    if len(doc) < 1:
        raise ValueError("This file is empty!")

    pages = list(range(page_range[0], page_range[1] + 1))

    doc.select(pages)

    file_name = os.path.split(file_input)[-1] + " - " + section.capitalize() + PDF_SUFFIX
    save_path = output_folder + file_name

    if os.path.exists(save_path):
        print("{file_name} exists. Skipping...")

        return
    else:
        print("Saving to " + save_path + ".")

        doc.save(save_path)

    doc.close()

    return
