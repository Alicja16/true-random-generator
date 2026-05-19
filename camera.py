import os
import cv2
import numpy as np


MIN_VALUE = 2
MAX_VALUE = 253


def create_output_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


def open_camera(camera_index=0):
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        raise RuntimeError("Nie udało się otworzyć kamery.")

    return camera


def read_frame(camera):
    success, frame_bgr = camera.read()

    if not success:
        raise RuntimeError("Nie udało się pobrać klatki z kamery.")

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    return frame_bgr, frame_rgb


def show_preview(frame_bgr):
    cv2.imshow("Camera preview - press Q to stop", frame_bgr)

    key = cv2.waitKey(1) & 0xFF

    return key == ord("q")


def get_filtered_rgb_values(frame_rgb):
    """
    Zwraca wartości R, G, B po filtrze 2-253.

    Zgodnie z artykułem odrzucamy wartości brzegowe,
    ponieważ mogą pochodzić z nasycenia / clippingu matrycy.
    """

    values = frame_rgb.reshape(-1)

    filtered_values = values[
        (values >= MIN_VALUE) & (values <= MAX_VALUE)
    ]

    return filtered_values.astype(np.uint8)


def get_bits_from_values(values):
    """
    Pobiera najmłodszy bit z każdej wartości piksela.
    """

    bits = values & 1

    return bits.astype(np.uint8)


def flip_bits(bits):
    """
    Odwraca bity:
    0 -> 1
    1 -> 0
    """

    return 1 - bits


def transpose_shuffle(bits, required_length):
    """
    Mieszanie zgodne z pseudokodem z artykułu.

    Ważne:
    - wymiar macierzy wyznaczamy jako floor(sqrt(required_length)),
    - do macierzy trafia pierwsze size * size bitów,
    - macierz zapisujemy wierszami, a odczytujemy kolumnami,
    - wszystkie pozostałe bity dopisujemy na końcu.

    Dzięki temu liczba zer i jedynek przed oraz po mieszaniu
    pozostaje identyczna, bo mieszanie jest tylko zmianą kolejności bitów.
    """

    bits = np.array(bits, dtype=np.uint8)

    if len(bits) < required_length:
        raise ValueError("Liczba zebranych bitów jest mniejsza niż required_length.")

    size = int(np.sqrt(required_length))
    square_length = size * size

    square_bits = bits[:square_length]
    extra_bits = bits[square_length:]

    matrix = square_bits.reshape(size, size)

    mixed_square_bits = matrix.T.reshape(-1)

    mixed_bits = np.concatenate([mixed_square_bits, extra_bits])

    return mixed_bits.astype(np.uint8)


def bits_to_bytes(bits):
    """
    Zamienia bity 0/1 na bajty.

    Jeśli liczba bitów nie dzieli się przez 8,
    końcówka jest obcinana tylko na potrzeby pliku binarnego.
    """

    bits = np.array(bits, dtype=np.uint8)

    full_length = (len(bits) // 8) * 8
    bits = bits[:full_length]

    return np.packbits(bits)


def save_bin_file(filename, byte_data):
    with open(filename, "wb") as file:
        file.write(byte_data.tobytes())


def save_npy_file(filename, data):
    np.save(filename, data)


def generate_random_data(
    number_of_bits=100_000_000,
    camera_index=0,
    output_folder="output",
    preview=True,
):
    """
    Główna funkcja generatora.

    number_of_bits oznacza minimalną docelową liczbę bitów.

    Generator zbiera całe sublisty bitów z kolejnych klatek.
    Dlatego finalnie liczba bitów może być trochę większa niż number_of_bits,
    bo ostatnia klatka może dostarczyć więcej bitów niż dokładnie brakowało.

    To jest bliższe pseudokodowi z artykułu:
    while NumSoFar < NumNeeded:
        pobierz klatkę
        pobierz sublistę bitów
        dodaj sublistę do sekwencji
    """

    create_output_folder(output_folder)

    camera = open_camera(camera_index)

    bits_before_mixing = []
    rgb_values_before_filter = []
    rgb_values_after_filter = []

    frame_number = 0
    interrupted = False

    print("Start generatora...")
    print(f"Minimalna docelowa liczba bitów: {number_of_bits}")

    try:
        while len(bits_before_mixing) < number_of_bits:
            frame_bgr, frame_rgb = read_frame(camera)

            frame_number += 1

            all_rgb_values = frame_rgb.reshape(-1).astype(np.uint8)
            filtered_rgb_values = get_filtered_rgb_values(frame_rgb)

            bits = get_bits_from_values(filtered_rgb_values)

            if frame_number % 2 == 0:
                bits = flip_bits(bits)

            bits_before_mixing.extend(bits.tolist())

            rgb_values_before_filter.extend(all_rgb_values.tolist())
            rgb_values_after_filter.extend(filtered_rgb_values.tolist())

            if frame_number % 10 == 0:
                print(
                    f"Klatki: {frame_number}, "
                    f"bity: {len(bits_before_mixing)} / {number_of_bits}"
                )

            if preview:
                stop = show_preview(frame_bgr)

                if stop:
                    interrupted = True
                    print("Przerwano przez użytkownika.")
                    break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    if interrupted and len(bits_before_mixing) < number_of_bits:
        raise RuntimeError(
            "Generowanie zostało przerwane przed uzyskaniem wymaganej liczby bitów. "
            "Pliki nie zostały zapisane jako pełny wynik."
        )

    bits_before_mixing = np.array(bits_before_mixing, dtype=np.uint8)

    print("Mieszanie bitów...")

    bits_after_mixing = transpose_shuffle(
        bits=bits_before_mixing,
        required_length=number_of_bits,
    )

    bytes_before_mixing = bits_to_bytes(bits_before_mixing)
    bytes_after_mixing = bits_to_bytes(bits_after_mixing)

    rgb_values_before_filter = np.array(rgb_values_before_filter, dtype=np.uint8)
    rgb_values_after_filter = np.array(rgb_values_after_filter, dtype=np.uint8)

    print("Sprawdzanie, czy mieszanie zachowało liczbę zer i jedynek...")

    zeros_before = int(np.sum(bits_before_mixing == 0))
    ones_before = int(np.sum(bits_before_mixing == 1))

    zeros_after = int(np.sum(bits_after_mixing == 0))
    ones_after = int(np.sum(bits_after_mixing == 1))

    if zeros_before != zeros_after or ones_before != ones_after:
        raise RuntimeError(
            "Błąd mieszania: liczba zer lub jedynek zmieniła się po transpozycji."
        )

    print("OK: liczba zer i jedynek przed oraz po mieszaniu jest identyczna.")

    print("Zapisywanie plików...")

    save_npy_file(
        os.path.join(output_folder, "bits_before_mixing.npy"),
        bits_before_mixing,
    )

    save_npy_file(
        os.path.join(output_folder, "bits_after_mixing.npy"),
        bits_after_mixing,
    )

    save_npy_file(
        os.path.join(output_folder, "rgb_values_before_filter.npy"),
        rgb_values_before_filter,
    )

    save_npy_file(
        os.path.join(output_folder, "rgb_values_after_filter.npy"),
        rgb_values_after_filter,
    )

    save_bin_file(
        os.path.join(output_folder, "random_before_mixing.bin"),
        bytes_before_mixing,
    )

    save_bin_file(
        os.path.join(output_folder, "random_after_mixing.bin"),
        bytes_after_mixing,
    )

    print("Generator zakończył działanie.")
    print(f"Liczba użytych klatek: {frame_number}")
    print(f"Minimalna wymagana liczba bitów: {number_of_bits}")
    print(f"Rzeczywista liczba bitów przed mieszaniem: {len(bits_before_mixing)}")
    print(f"Rzeczywista liczba bitów po mieszaniu: {len(bits_after_mixing)}")
    print(f"Liczba bajtów przed mieszaniem: {len(bytes_before_mixing)}")
    print(f"Liczba bajtów po mieszaniu: {len(bytes_after_mixing)}")

    return bits_before_mixing, bits_after_mixing


if __name__ == "__main__":
    generate_random_data(
        number_of_bits=100_000_000,
        camera_index=0,
        output_folder="output",
        preview=False
    )