import os
import shutil

from camera import generate_random_data
from analysis import run_analysis
from pixel_noise_demo import run_pixel_noise_demo


def prepare_file_for_nist(
    source_file="output/random_after_mixing.bin",
    nist_data_folder="sts-2.1.2/data",
    target_filename="random_bytes.bin",
):
    """
    Kopiuje finalny plik generatora do folderu data używanego przez NIST STS.

    Źródło:
        output/random_after_mixing.bin

    Cel:
        sts-2.1.2/data/random_bytes.bin
    """

    if not os.path.exists(source_file):
        raise FileNotFoundError(
            f"Nie znaleziono pliku: {source_file}\n"
            "Najpierw uruchom generator."
        )

    if not os.path.exists(nist_data_folder):
        raise FileNotFoundError(
            f"Nie znaleziono folderu NIST data: {nist_data_folder}\n"
            "Sprawdź, czy folder sts-2.1.2 znajduje się w folderze projektu."
        )

    target_file = os.path.join(nist_data_folder, target_filename)

    shutil.copyfile(source_file, target_file)

    file_size_bytes = os.path.getsize(target_file)
    file_size_bits = file_size_bytes * 8

    print()
    print("Plik został przygotowany do testów NIST.")
    print("=======================================")
    print(f"Skopiowano z: {source_file}")
    print(f"Skopiowano do: {target_file}")
    print()
    print(f"Rozmiar pliku: {file_size_bytes} bajtów")
    print(f"Liczba bitów: {file_size_bits}")
    print()
    print("Aby uruchomić NIST STS, wpisz w terminalu:")
    print()
    print("cd sts-2.1.2")
    print(".\\assess.exe 1000000")
    print()
    print("Następnie w programie NIST wybierz:")
    print()
    print("0")
    print("data/random_bytes.bin")


def main():
    print("TRNG z szumu kamery")
    print("===================")
    print()
    print("Wybierz tryb działania:")
    print("1 - Uruchom generator")
    print("2 - Uruchom analizę wygenerowanych danych")
    print("3 - Uruchom demo szumu 5 pikseli")
    print("4 - Uruchom generator + analizę")
    print("5 - Uruchom wszystko")
    print("6 - Przygotuj plik do testów NIST")
    print()

    choice = input("Twój wybór: ")

    camera_index = 0

    if choice == "1":
        number_of_bits = int(input("Podaj liczbę bitów do wygenerowania: "))

        generate_random_data(
            number_of_bits=number_of_bits,
            camera_index=camera_index,
            output_folder="output",
            preview=True,
        )

    elif choice == "2":
        run_analysis(
            input_folder="output",
            analysis_folder="analysis_output",
        )

    elif choice == "3":
        number_of_frames = int(
            input("Podaj liczbę klatek do analizy pikseli, np. 600: ")
        )

        run_pixel_noise_demo(
            number_of_frames=number_of_frames,
            camera_index=camera_index,
            preview=True,
            output_folder="pixel_noise_output",
        )

    elif choice == "4":
        number_of_bits = int(input("Podaj liczbę bitów do wygenerowania: "))

        generate_random_data(
            number_of_bits=number_of_bits,
            camera_index=camera_index,
            output_folder="output",
            preview=True,
        )

        run_analysis(
            input_folder="output",
            analysis_folder="analysis_output",
        )

    elif choice == "5":
        number_of_bits = int(input("Podaj liczbę bitów do wygenerowania: "))
        number_of_frames = int(
            input("Podaj liczbę klatek do demo pikseli, np. 600: ")
        )

        generate_random_data(
            number_of_bits=number_of_bits,
            camera_index=camera_index,
            output_folder="output",
            preview=True,
        )

        run_analysis(
            input_folder="output",
            analysis_folder="analysis_output",
        )

        run_pixel_noise_demo(
            number_of_frames=number_of_frames,
            camera_index=camera_index,
            preview=True,
            output_folder="pixel_noise_output",
        )

    elif choice == "6":
        prepare_file_for_nist(
            source_file="output/random_after_mixing.bin",
            nist_data_folder="sts-2.1.2/data",
            target_filename="random_bytes.bin",
        )

    else:
        print("Niepoprawny wybór.")


if __name__ == "__main__":
    main()