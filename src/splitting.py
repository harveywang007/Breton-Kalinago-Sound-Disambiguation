import os
import pymupdf

from constants import *


def create_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)


def split(file_input, output_folder, **pages):
    if not os.path.exists(file_input):
        raise ValueError("This file doesn't exist!")

    if not pages:
        raise ValueError("No page ranges provided for splitting.")

    for section, page_range in pages.items():
        doc = pymupdf.open(file_input)

        split_helper(doc, file_input, output_folder, section, page_range)


def split_helper(doc, file_input, output_folder, section, page_range):
    if len(doc) < 1:
        doc.close()
        raise ValueError("This file is empty!")

    pages = list(range(page_range[0], page_range[1] + 1))

    doc.select(pages)

    file_name_full = os.path.split(file_input)[-1]
    file_name_only, _ = os.path.splitext(file_name_full)

    file_name = file_name_only + " - " + section.capitalize() + PDF_SUFFIX
    save_path = os.path.join(output_folder, file_name)

    if os.path.exists(save_path):
        print(f"{file_name} exists. Skipping...")
        doc.close()
        return

    print("Saving to " + save_path + ".")
    doc.save(save_path)
    doc.close()

    return
