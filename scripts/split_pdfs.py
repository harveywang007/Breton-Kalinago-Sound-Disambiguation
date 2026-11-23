import multiprocessing
from concurrent.futures import ProcessPoolExecutor

from src.constants import *
from src.splitting import *


def main():
    create_folder(DICT_FOLDER)

    files = [
        "Dictionaire françois-caraibe",
        "Dictionaire caraibe-françois",
        "A Carib Dictionary",
        "Trilingual Garifuna Dictionary",
        "Diccionario Garífuna-Español guatemalteco",
        "A Grammar Sketch and Lexicon of Arawak",
        "La langue arawak de Guyane",
        "Diccionario basico ilustrado Wayuunaiki",
        "Wayuu Dictionary",
        "Carib Grammar",
        "Kalihna - Nederlands Woordenboek",
        "Karaïbs - Nederlands woordenboek",
        "Introduction à la langue des galibis",
        "Véritable relation",
        "Voyage de la France equinoxiale en l'isle de Cayenne"
    ]

    parallize_split(files, output_folder, **pages)


def parallize_split(files, output_folder, **pages):
    if not files:
        raise ValueError("No files provided for splitting!")

    for file_input in files:
        if not os.path.exists(file_input):
            raise ValueError("This file doesn't exist!")

    if not pages:
        raise ValueError("No page ranges provided for splitting.")

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = []
        for section, page_range in pages.items():
            for file_input in files:
                futures.append(executor.submit(split_helper, file_input, output_folder, section, page_range))

        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
