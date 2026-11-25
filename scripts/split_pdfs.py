from concurrent.futures import ProcessPoolExecutor

from src.constants import *
from src.splitting import *


def main():
    create_folder(DICT_FOLDER)

    # The files will be replaced by the actual file paths.
    files = {
        "Dictionaire françois-caraibe": {"Dict": (7, 416)},
        "Dictionaire caraibe-françois": {"Dict": (114, 300)},
        "Grammaire caraibe": {
            "Grammaire": (42, 112),
            "Lettre": (128, 129),
            "Introduction": (130, 132),
            "Catéchisme": (134, 166),
            "Chanson": (170, 173)
        },
        "A Carib Dictionary": {"Dict": (27, 770)},
        "La langue arawak de Guyane": {
            "Lokono": (37, 239),
            "Français": (241, 315)
        },
        "Wayuu Dictionary": {
            "Wayuu": (12, 172),
            "English": (174, 296)
        },
        "Carib Grammar": {"Dict": (224, 451)},
        "Voyage de la France equinoxiale en l'isle de Cayenne": {"Dict": (0, 38)}
    }

    parallelize_split(files, DICT_FOLDER)


def parallelize_split(files, output_folder):
    if not files:
        raise ValueError("No files provided for splitting!")

    print(f"Starting the splitting process for {len(files)} files...")

    with ProcessPoolExecutor() as executor:
        futures = []

        for file_path, sections in files.items():
            futures.append(executor.submit(split, file_path, output_folder, **sections))

        for future in futures:
            future.result()

    print("Finished splitting all files.")


if __name__ == "__main__":
    main()
