# Camera-Based True Random Number Generator (TRNG)

A Python implementation of a True Random Number Generator based on digital camera image noise.

This project implements a camera-based random number generator inspired by the scientific paper:

> R. Li, **"A True Random Number Generator Algorithm From Digital Camera Image Noise For Varying Lighting Conditions,"**  
> *SoutheastCon 2015*, Fort Lauderdale, FL, USA, 2015, pp. 1–8.  
> DOI: **10.1109/SECON.2015.7132901**  
> Official source link: https://doi.org/10.1109/SECON.2015.7132901

The original paper is not included in this repository due to publication licensing restrictions.  
Instead, the official DOI link is provided above as the source reference.

The generator uses a standard camera as a physical entropy source. Random bits are extracted from natural pixel-level noise present in digital camera frames. The implementation follows the main idea from the source paper: it uses all three RGB color channels, removes saturated pixel values, extracts the least significant bit from accepted pixel values, flips bits from every second frame, and applies transpose-based shuffling.

---

## 📂 Repository contents

| File / folder | Description |
|---|---|
| `camera.py` | Main camera-based TRNG generator. It captures frames from the camera, converts them from BGR to RGB, filters pixel values to the `2–253` range, extracts least significant bits, flips bits from every second frame, performs transpose-based shuffling, and saves generated random data. |
| `analysis.py` | Analysis module for generated TRNG data. It reads files produced by `camera.py` and creates text statistics, byte histograms, RGB brightness histograms, and bit-balance plots before and after mixing. |
| `pixel_noise_demo.py` | Demonstration module showing that selected camera pixels fluctuate over time. It records RGB values of fixed pixels across multiple frames and visualizes their distributions. |
| `main.py` | Main console menu for running the generator, analysis, pixel-noise demo, and preparing the final binary file for NIST STS tests. |
| `.gitignore` | Excludes virtual environment, Python cache files, NIST STS package, and generated output folders. |

---

## 🟠 Features

* Camera-based physical entropy source
* Implementation based on a scientific TRNG paper
* Uses all three RGB channels
* Filters pixel values to the range `2–253`
* Extracts one least significant bit from each accepted pixel value
* Flips bits from every second frame
* Applies transpose-based bitstream shuffling
* Saves final random output as a binary `.bin` file
* Saves intermediate NumPy `.npy` files for analysis
* Generates bit-balance statistics
* Generates entropy statistics
* Generates byte histograms for values `0–255`
* Generates RGB brightness histograms before and after filtering
* Demonstrates real camera noise using fixed-pixel observation
* Includes a helper option for preparing data for NIST STS testing

---

## 🟠 Algorithm overview

The generator follows the main algorithmic steps described in the source paper.

For each camera frame:

1. A frame is captured from the camera.
2. The frame is converted from OpenCV `BGR` format to `RGB`.
3. Pixel values from all three channels are used.
4. Values outside the range `2–253` are discarded.
5. The least significant bit is extracted from every remaining pixel value.
6. Bits from every second frame are inverted.
7. Bits from all frames are collected into one sequence.
8. The sequence is shuffled by writing bits row by row into a square matrix and reading them column by column.
9. The final bit sequence is packed into bytes and saved as a binary file.

Final output file:

```text
output/random_after_mixing.bin
```

This is the main generated random binary file.

---

## 🟠 Why the range `2–253` is used

Digital camera pixel values are stored in the range:

```text
0–255
```

Values close to the boundaries may be affected by saturation or clipping. These boundary values can introduce bias into the generated bitstream.

The source paper avoids this problem by selecting only brightness values from:

```text
2–253
```

This project follows the same approach.

---

## 🟠 Why only the least significant bit is used

The least significant bit is most affected by small fluctuations in pixel brightness. These fluctuations come from physical noise sources in the camera sensor and image acquisition process.

The implementation uses one bit per accepted pixel value because this is the conservative approach described in the source paper for maintaining better randomness quality under varying lighting conditions.

---

## 🟠 Why bits are flipped every second frame

The raw bit sequence may still contain frame-dependent bias or local patterns.

To reduce this effect, bits from every second frame are inverted:

```text
0 → 1
1 → 0
```

This follows the algorithmic idea described in the source paper and helps compensate for frame-level bias.

---

## 🟠 Why transpose-based shuffling is used

After collecting raw bits, the sequence is shuffled.

The generator writes bits into a square matrix in row-major order and reads them back in column-major order. This operation changes the order of bits without changing the number of zeros and ones.

This step helps reduce visible patterns caused by sensor structure, neighboring pixels, and frame ordering.

---

## 🟠 Requirements

Python packages:

```text
opencv-python
numpy
matplotlib
```

Install dependencies:

```bash
pip install opencv-python numpy matplotlib
```

---

## 🟠 Run the project

Start the project from the main menu:

```bash
python main.py
```

Available options:

```text
1 - Run generator
2 - Run analysis of generated data
3 - Run 5-pixel noise demo
4 - Run generator + analysis
5 - Run everything
6 - Prepare file for NIST STS tests
```

---

## 🟠 Generate random data

To run only the generator, choose:

```text
1 - Run generator
```

Then enter the number of bits to generate, for example:

```text
100000000
```

The generator saves files in:

```text
output/
```

Generated files:

| File | Description |
|---|---|
| `bits_before_mixing.npy` | Bit sequence before transpose-based shuffling. Each bit is stored as a NumPy value `0` or `1`. |
| `bits_after_mixing.npy` | Bit sequence after transpose-based shuffling. Used for analysis. |
| `random_before_mixing.bin` | Binary data before final shuffling. |
| `random_after_mixing.bin` | Final generated random binary output. This is the main file for testing and further use. |
| `rgb_values_before_filter.npy` | RGB values collected before applying the `2–253` filter. Used for analysis plots. |
| `rgb_values_after_filter.npy` | RGB values collected after applying the `2–253` filter. Used for analysis plots. |

---

## 🟠 Analyze generated data

To analyze already generated data, choose:

```text
2 - Run analysis of generated data
```

The analysis module does not capture new camera frames. It reads files from:

```text
output/
```

and saves results in:

```text
analysis_output/
```

Generated analysis files:

| File | Description |
|---|---|
| `statistics_before_mixing.txt` | Entropy, number of bits, number of bytes, number of zeros and ones, and percentage balance before mixing. |
| `statistics_after_mixing.txt` | Entropy, number of bits, number of bytes, number of zeros and ones, and percentage balance after mixing. |
| `byte_histogram_before_mixing.png` | Histogram of byte values `0–255` before transpose-based shuffling. |
| `byte_histogram_after_mixing.png` | Histogram of byte values `0–255` after transpose-based shuffling. |
| `bit_balance_before_after.png` | Comparison of zero/one balance before and after mixing. |
| `rgb_histogram_before_filter.png` | RGB brightness histogram before filtering. |
| `rgb_histogram_after_filter.png` | RGB brightness histogram after applying the `2–253` filter. |
| `rgb_bit_balance.png` | Zero/one balance calculated separately for R, G, and B channels. |

---

## 🟠 Pixel noise demonstration

The file `pixel_noise_demo.py` is a demonstration tool. It is not required for generating random numbers.

It shows that even when the camera observes a mostly stable scene, selected pixels do not keep perfectly constant RGB values. Their values fluctuate over time, which demonstrates the presence of camera noise.

To run it from the menu, choose:

```text
3 - Run 5-pixel noise demo
```

The program captures multiple frames and tracks RGB values of five fixed pixels.

Generated files are saved in:

```text
pixel_noise_output/
```

Example output files:

| File | Description |
|---|---|
| `pixel_statistics.txt` | Mean, standard deviation, minimum, and maximum RGB values for selected pixels. |
| `*_distribution.png` | Histograms showing RGB value distributions for selected pixels. |
| `*_values_over_time.png` | Plots showing RGB values changing from frame to frame. |

This helps explain why camera noise can be used as a physical entropy source.

---

## 🟠 NIST STS testing

The project includes a helper option for preparing the final binary output for NIST STS.

To prepare the file, choose:

```text
6 - Prepare file for NIST STS tests
```

This copies:

```text
output/random_after_mixing.bin
```

to:

```text
sts-2.1.2/data/random_bytes.bin
```

Then run NIST STS manually:

```bash
cd sts-2.1.2
.\assess.exe 1000000
```

For Git Bash or Linux-like terminal:

```bash
cd sts-2.1.2
./assess.exe 1000000
```

When prompted, select binary input mode and provide:

```text
data/random_bytes.bin
```

The value:

```text
1000000
```

means that NIST STS will test sequences of 1,000,000 bits.

---

## 🟠 Notes about binary files

The generator internally works with bits represented as `0` and `1`.

However, a `.bin` file stores bytes. Therefore, the final bit sequence is packed into bytes before saving:

```text
8 bits → 1 byte
```

The main final output file is:

```text
output/random_after_mixing.bin
```

This file contains the generated random bitstream packed into binary form.

---

## 🟠 Limitations

* Randomness quality depends on the camera sensor and lighting conditions.
* NIST STS is not bundled with this repository.
* This project is educational and experimental.
* The output should be statistically tested before any serious use.

---

## 🟠 Source article

This implementation is based on the following scientific paper:

R. Li, **"A True Random Number Generator Algorithm From Digital Camera Image Noise For Varying Lighting Conditions,"**  
*SoutheastCon 2015*, Fort Lauderdale, FL, USA, 2015, pp. 1–8.  
DOI: **10.1109/SECON.2015.7132901**  
Official source link: https://doi.org/10.1109/SECON.2015.7132901

The article itself is not included in this repository due to publication licensing restrictions.

---

## Author

**Alicja P.**

Educational Python project implementing a camera-based True Random Number Generator inspired by digital camera image noise.
