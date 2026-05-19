import os
import numpy as np
import matplotlib.pyplot as plt


MIN_VALUE = 2
MAX_VALUE = 253


def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def apply_plot_style():
    plt.rcParams.update({
        "figure.figsize": (13, 6),
        "axes.grid": True,
        "grid.alpha": 0.6,
        "grid.linestyle": "-",
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 11,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
    })


def load_bits(filename):
    return np.load(filename, mmap_mode="r")


def load_rgb_values(filename):
    return np.load(filename, mmap_mode="r")


def load_bytes(filename):
    return np.fromfile(filename, dtype=np.uint8)


def count_bits(bits):
    zeros = int(np.sum(bits == 0))
    ones = int(np.sum(bits == 1))
    total = zeros + ones

    if total == 0:
        zeros_percent = 0.0
        ones_percent = 0.0
    else:
        zeros_percent = zeros / total * 100
        ones_percent = ones / total * 100

    return zeros, ones, zeros_percent, ones_percent, total


def calculate_entropy(byte_data):
    byte_data = np.asarray(byte_data, dtype=np.uint8)

    if len(byte_data) == 0:
        return 0.0

    counts = np.bincount(byte_data, minlength=256)
    probabilities = counts / np.sum(counts)
    probabilities = probabilities[probabilities > 0]

    entropy = -np.sum(probabilities * np.log2(probabilities))

    return float(entropy)


def save_statistics(filename, bits, byte_data):
    zeros, ones, zeros_percent, ones_percent, total_bits = count_bits(bits)
    entropy = calculate_entropy(byte_data)
    total_bytes = len(byte_data)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Statystyki sekwencji\n")
        file.write("====================\n\n")

        file.write(f"Liczba bitów: {total_bits}\n")
        file.write(f"Liczba bajtów: {total_bytes}\n\n")

        file.write(f"Liczba zer: {zeros}\n")
        file.write(f"Liczba jedynek: {ones}\n\n")

        file.write(f"Procent zer: {zeros_percent:.6f}%\n")
        file.write(f"Procent jedynek: {ones_percent:.6f}%\n\n")

        file.write(f"Entropia bajtów: {entropy:.6f} / 8\n")


def check_mixing_preserves_bits(bits_before, bits_after):
    """
    Mieszanie przez transpozycję nie może zmienić liczby zer i jedynek.
    Może zmienić tylko kolejność bitów.
    """

    before = count_bits(bits_before)
    after = count_bits(bits_after)

    zeros_before, ones_before = before[0], before[1]
    zeros_after, ones_after = after[0], after[1]

    if zeros_before != zeros_after or ones_before != ones_after:
        print("UWAGA: Liczba zer/jedynek przed i po mieszaniu jest różna.")
        print("To oznacza, że porównywane dane nie są tą samą sekwencją po permutacji.")
        print("Najczęstsza przyczyna: stare pliki w folderze output albo różne długości danych.")
        print()
        print(f"Przed mieszaniem: 0={zeros_before}, 1={ones_before}")
        print(f"Po mieszaniu:     0={zeros_after}, 1={ones_after}")
    else:
        print("OK: mieszanie zachowało identyczną liczbę zer i jedynek.")


def plot_byte_histogram(byte_data, title, filename):
    apply_plot_style()

    byte_data = np.asarray(byte_data, dtype=np.uint8)

    counts = np.bincount(byte_data, minlength=256)
    expected = len(byte_data) / 256

    x = np.arange(256)

    plt.figure()

    plt.bar(
        x,
        counts,
        width=0.8,
        alpha=0.9,
    )

    plt.axhline(
        expected,
        linestyle="--",
        linewidth=1.8,
        label="Wartość oczekiwana",
    )

    plt.title(title)
    plt.xlabel("Wartość bajtu")
    plt.ylabel("Liczba wystąpień")
    plt.xlim(-5, 260)
    plt.legend()

    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_bit_balance(bits_before, bits_after, filename):
    apply_plot_style()

    before_stats = count_bits(bits_before)
    after_stats = count_bits(bits_after)

    labels = ["Przed mieszaniem", "Po mieszaniu"]

    zeros_percent = [
        before_stats[2],
        after_stats[2],
    ]

    ones_percent = [
        before_stats[3],
        after_stats[3],
    ]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(9, 6))

    plt.bar(
        x - width / 2,
        zeros_percent,
        width,
        label="0",
        alpha=0.9,
    )

    plt.bar(
        x + width / 2,
        ones_percent,
        width,
        label="1",
        alpha=0.9,
    )

    plt.axhline(
        50,
        linestyle="--",
        linewidth=1.8,
        label="Idealnie 50%",
    )

    plt.xticks(x, labels)
    plt.ylim(0, 55)

    plt.title("Balans bitów 0/1 przed i po mieszaniu")
    plt.ylabel("Udział [%]")
    plt.legend(loc="lower left")

    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def split_rgb_values(rgb_values):
    """
    Dane z camera.py są zapisane jako:
    R, G, B, R, G, B, R, G, B, ...

    Dlatego odtwarzamy je do postaci:
    [R, G, B]
    [R, G, B]
    [R, G, B]
    """

    usable_length = (len(rgb_values) // 3) * 3
    rgb_values = rgb_values[:usable_length]

    rgb = rgb_values.reshape(-1, 3)

    red = rgb[:, 0]
    green = rgb[:, 1]
    blue = rgb[:, 2]

    return red, green, blue


def plot_rgb_histogram_before_filter(rgb_values_before_filter, filename):
    apply_plot_style()

    red, green, blue = split_rgb_values(rgb_values_before_filter)

    bins = np.arange(257)

    plt.figure()

    plt.hist(
        red,
        bins=bins,
        histtype="step",
        linewidth=1.2,
        label="R",
    )

    plt.hist(
        green,
        bins=bins,
        histtype="step",
        linewidth=1.2,
        label="G",
    )

    plt.hist(
        blue,
        bins=bins,
        histtype="step",
        linewidth=1.2,
        label="B",
    )

    plt.yscale("log")

    plt.title("Histogram jasności RGB przed filtrowaniem")
    plt.xlabel("Wartość jasności")
    plt.ylabel("Liczba wystąpień")
    plt.xlim(0, 255)
    plt.legend()

    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_rgb_histogram_after_filter(rgb_values_before_filter, filename):
    apply_plot_style()

    red, green, blue = split_rgb_values(rgb_values_before_filter)

    red = red[(red >= MIN_VALUE) & (red <= MAX_VALUE)]
    green = green[(green >= MIN_VALUE) & (green <= MAX_VALUE)]
    blue = blue[(blue >= MIN_VALUE) & (blue <= MAX_VALUE)]

    bins = np.arange(MIN_VALUE, MAX_VALUE + 2)

    plt.figure()

    plt.hist(
        red,
        bins=bins,
        histtype="step",
        linewidth=1.2,
        label="R",
    )

    plt.hist(
        green,
        bins=bins,
        histtype="step",
        linewidth=1.2,
        label="G",
    )

    plt.hist(
        blue,
        bins=bins,
        histtype="step",
        linewidth=1.2,
        label="B",
    )

    plt.yscale("log")

    plt.title("Histogram jasności RGB po filtrze 2-253")
    plt.xlabel("Wartość jasności")
    plt.ylabel("Liczba wystąpień")
    plt.xlim(0, 255)
    plt.legend()

    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_rgb_bit_balance(rgb_values_before_filter, filename):
    apply_plot_style()

    red, green, blue = split_rgb_values(rgb_values_before_filter)

    channels = {
        "R": red,
        "G": green,
        "B": blue,
    }

    zeros_percent = []
    ones_percent = []

    for channel_name in ["R", "G", "B"]:
        values = channels[channel_name]

        values = values[
            (values >= MIN_VALUE) & (values <= MAX_VALUE)
        ]

        bits = values & 1

        zeros = int(np.sum(bits == 0))
        ones = int(np.sum(bits == 1))
        total = zeros + ones

        if total == 0:
            zeros_percent.append(0.0)
            ones_percent.append(0.0)
        else:
            zeros_percent.append(zeros / total * 100)
            ones_percent.append(ones / total * 100)

    x = np.arange(3)
    width = 0.35

    plt.figure(figsize=(9, 6))

    plt.bar(
        x - width / 2,
        zeros_percent,
        width,
        label="0",
        alpha=0.9,
    )

    plt.bar(
        x + width / 2,
        ones_percent,
        width,
        label="1",
        alpha=0.9,
    )

    plt.axhline(
        50,
        linestyle="--",
        linewidth=1.8,
        label="Idealnie 50%",
    )

    plt.xticks(x, ["R", "G", "B"])
    plt.ylim(0, 55)

    plt.title("Balans bitów 0/1 dla kanałów RGB")
    plt.xlabel("Kanał")
    plt.ylabel("Udział [%]")
    plt.legend(loc="lower left")

    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def run_analysis(
    input_folder="output",
    analysis_folder="analysis_output",
):
    create_folder(analysis_folder)

    print("Wczytywanie plików generatora...")

    bits_before = load_bits(
        os.path.join(input_folder, "bits_before_mixing.npy")
    )

    bits_after = load_bits(
        os.path.join(input_folder, "bits_after_mixing.npy")
    )

    bytes_before = load_bytes(
        os.path.join(input_folder, "random_before_mixing.bin")
    )

    bytes_after = load_bytes(
        os.path.join(input_folder, "random_after_mixing.bin")
    )

    rgb_values_before_filter = load_rgb_values(
        os.path.join(input_folder, "rgb_values_before_filter.npy")
    )

    print("Sprawdzanie poprawności mieszania...")
    check_mixing_preserves_bits(bits_before, bits_after)

    print("Zapisywanie statystyk TXT...")

    save_statistics(
        filename=os.path.join(analysis_folder, "statistics_before_mixing.txt"),
        bits=bits_before,
        byte_data=bytes_before,
    )

    save_statistics(
        filename=os.path.join(analysis_folder, "statistics_after_mixing.txt"),
        bits=bits_after,
        byte_data=bytes_after,
    )

    print("Tworzenie histogramów bajtów...")

    plot_byte_histogram(
        byte_data=bytes_before,
        title="Histogram wartości bajtów 0-255 przed mieszaniem",
        filename=os.path.join(analysis_folder, "byte_histogram_before_mixing.png"),
    )

    plot_byte_histogram(
        byte_data=bytes_after,
        title="Histogram wartości bajtów 0-255 po mieszaniu",
        filename=os.path.join(analysis_folder, "byte_histogram_after_mixing.png"),
    )

    print("Tworzenie wykresu balansu bitów...")

    plot_bit_balance(
        bits_before=bits_before,
        bits_after=bits_after,
        filename=os.path.join(analysis_folder, "bit_balance_before_after.png"),
    )

    print("Tworzenie histogramów RGB...")

    plot_rgb_histogram_before_filter(
        rgb_values_before_filter=rgb_values_before_filter,
        filename=os.path.join(analysis_folder, "rgb_histogram_before_filter.png"),
    )

    plot_rgb_histogram_after_filter(
        rgb_values_before_filter=rgb_values_before_filter,
        filename=os.path.join(analysis_folder, "rgb_histogram_after_filter.png"),
    )

    print("Tworzenie wykresu udziału 0/1 dla kanałów RGB...")

    plot_rgb_bit_balance(
        rgb_values_before_filter=rgb_values_before_filter,
        filename=os.path.join(analysis_folder, "rgb_bit_balance.png"),
    )

    print("Analiza zakończona.")

if __name__ == "__main__":
    run_analysis()