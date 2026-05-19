import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


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
    cv2.imshow("Pixel noise demo - press Q to stop", frame_bgr)

    key = cv2.waitKey(1) & 0xFF

    return key == ord("q")


def choose_default_pixels(frame_rgb):
    """
    Wybiera 5 pikseli na podstawie rozmiaru obrazu.

    Dzięki temu nie musimy na sztywno zakładać konkretnej rozdzielczości kamery.
    """

    height, width, _ = frame_rgb.shape

    pixels = [
        (height // 2, width // 2),
        (height // 3, width // 3),
        (height // 3, 2 * width // 3),
        (2 * height // 3, width // 3),
        (2 * height // 3, 2 * width // 3),
    ]

    return pixels


def collect_pixel_values(
    number_of_frames=600,
    camera_index=0,
    preview=True,
    selected_pixels=None,
):
    """
    Zbiera wartości RGB dla 5 wybranych pikseli w czasie.

    Wynik:
    {
        "pixel_1_y_x": {"R": [...], "G": [...], "B": [...]},
        ...
    }
    """

    camera = open_camera(camera_index)

    pixel_values = {}
    used_pixels = selected_pixels

    print("Start zbierania danych pikseli...")
    print(f"Liczba klatek do zebrania: {number_of_frames}")

    try:
        for frame_number in range(1, number_of_frames + 1):
            frame_bgr, frame_rgb = read_frame(camera)

            if used_pixels is None:
                used_pixels = choose_default_pixels(frame_rgb)

                for index, (y, x) in enumerate(used_pixels, start=1):
                    key = f"pixel_{index}_{y}_{x}"
                    pixel_values[key] = {
                        "R": [],
                        "G": [],
                        "B": [],
                    }

            for index, (y, x) in enumerate(used_pixels, start=1):
                key = f"pixel_{index}_{y}_{x}"

                r, g, b = frame_rgb[y, x]

                pixel_values[key]["R"].append(int(r))
                pixel_values[key]["G"].append(int(g))
                pixel_values[key]["B"].append(int(b))

            if frame_number % 50 == 0:
                print(f"Zebrano klatek: {frame_number} / {number_of_frames}")

            if preview:
                stop = show_preview(frame_bgr)

                if stop:
                    print("Przerwano przez użytkownika.")
                    break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    print("Zbieranie danych pikseli zakończone.")

    return pixel_values


def save_pixel_statistics(pixel_values, filename):
    """
    Zapisuje średnią i odchylenie standardowe dla każdego piksela i kanału RGB.
    """

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Statystyki wartości 5 wybranych pikseli w czasie\n")
        file.write("================================================\n\n")

        for pixel_name, channels in pixel_values.items():
            file.write(f"{pixel_name}\n")
            file.write("-" * len(pixel_name) + "\n")

            for channel_name in ["R", "G", "B"]:
                values = np.array(channels[channel_name], dtype=np.float64)

                mean = np.mean(values)
                std = np.std(values)

                file.write(
                    f"{channel_name}: "
                    f"μ = {mean:.4f}, "
                    f"σ = {std:.4f}, "
                    f"min = {np.min(values):.0f}, "
                    f"max = {np.max(values):.0f}\n"
                )

            file.write("\n")


def plot_pixel_distributions(pixel_values, output_folder):
    """
    Tworzy osobny histogram rozkładu wartości RGB dla każdego z 5 pikseli.
    """

    apply_plot_style()
    create_folder(output_folder)

    bins = np.arange(257)

    for pixel_name, channels in pixel_values.items():
        plt.figure()

        for channel_name in ["R", "G", "B"]:
            values = np.array(channels[channel_name], dtype=np.uint8)

            mean = np.mean(values)
            std = np.std(values)

            plt.hist(
                values,
                bins=bins,
                density=True,
                alpha=0.45,
                label=f"{channel_name}: μ={mean:.2f}, σ={std:.2f}",
            )

        plt.title(f"Rozkład wartości {pixel_name} w czasie")
        plt.xlabel("Wartość piksela")
        plt.ylabel("Prawdopodobieństwo")
        plt.xlim(0, 255)
        plt.legend()

        filename = os.path.join(
            output_folder,
            f"{pixel_name}_distribution.png"
        )

        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()


def plot_pixel_values_over_time(pixel_values, output_folder):
    """
    Tworzy wykres wartości R, G, B w czasie dla każdego z 5 pikseli.

    Ten wykres dobrze pokazuje, że nawet gdy kamera patrzy na pozornie stałą scenę,
    wartości pikseli delikatnie fluktuują.
    """

    apply_plot_style()
    create_folder(output_folder)

    for pixel_name, channels in pixel_values.items():
        plt.figure()

        for channel_name in ["R", "G", "B"]:
            values = np.array(channels[channel_name], dtype=np.uint8)

            plt.plot(
                values,
                linewidth=1.0,
                label=channel_name,
            )

        plt.title(f"Wartości RGB {pixel_name} w czasie")
        plt.xlabel("Numer klatki")
        plt.ylabel("Wartość piksela")
        plt.ylim(0, 255)
        plt.legend()

        filename = os.path.join(
            output_folder,
            f"{pixel_name}_values_over_time.png"
        )

        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()


def run_pixel_noise_demo(
    number_of_frames=600,
    camera_index=0,
    preview=True,
    output_folder="pixel_noise_output",
):
    """
    Główna funkcja pliku pokazowego.

    Uruchamia kamerę, zbiera wartości 5 pikseli w czasie,
    zapisuje statystyki oraz tworzy wykresy.
    """

    create_folder(output_folder)

    pixel_values = collect_pixel_values(
        number_of_frames=number_of_frames,
        camera_index=camera_index,
        preview=preview,
    )

    save_pixel_statistics(
        pixel_values=pixel_values,
        filename=os.path.join(output_folder, "pixel_statistics.txt"),
    )

    plot_pixel_distributions(
        pixel_values=pixel_values,
        output_folder=output_folder,
    )

    plot_pixel_values_over_time(
        pixel_values=pixel_values,
        output_folder=output_folder,
    )

    print("Demo szumu pikseli zakończone.")
    print(f"Wyniki zapisano w folderze: {output_folder}")


if __name__ == "__main__":
    run_pixel_noise_demo(
            number_of_frames=600,
            camera_index=0,
            preview=True,
            output_folder="pixel_noise_output",
    )