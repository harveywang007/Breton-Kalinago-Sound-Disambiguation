import multiprocessing
from concurrent.futures import ProcessPoolExecutor

from src.constants import *
from src.splitting import *


def main():
    create_folder(DICT_FOLDER)

    # The files will be replaced by the actual file paths.
    files = {
        "Dictionaire françois-caraibe": {},
        "Dictionaire caraibe-françois": {},
        "A Carib Dictionary": {},
        "Trilingual Garifuna Dictionary": {},
        "Diccionario Garífuna-Español guatemalteco": {},
        "A Grammar Sketch and Lexicon of Arawak": {},
        "La langue arawak de Guyane": {},
        "Diccionario basico ilustrado Wayuunaiki": {},
        "Wayuu Dictionary": {},
        "Carib Grammar": {},
        "Kalihna - Nederlands Woordenboek": {},
        "Karaïbs - Nederlands woordenboek": {},
        "Introduction à la langue des galibis": {},
        "Véritable relation": {},
        "Voyage de la France equinoxiale en l'isle de Cayenne": {}
    }

    parallize_split(files, DICT_FOLDER)


def parallize_split(files, output_folder):
    if not files:
        raise ValueError("No files provided for splitting!")

    with ProcessPoolExecutor() as executor:
        executor.map(split, files)


if __name__ == "__main__":
    main()
