import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
import time

ORIENT_DICT = {"R": "L", "A": "P", "I": "S", "L": "R", "P": "A", "S": "I"}
GAUSS_STDEV = 10.0


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        custom_message = (
            f"{message}\n\n"
            f"See https://github.com/katembartz/3D_laplacian_phase_unwrap and https://github.com/blakedewey/phase_unwrap for full instructions."
        )
        super().error(custom_message)


def check_3d(obj: nib.Nifti1Image) -> nib.Nifti1Image:
    if len(obj.shape) > 3:
        print("Input image is 4D, assuming phase image is 2nd volume.")
        obj_list = nib.four_to_three(obj)
        obj = obj_list[1]  # Assume phase image is 2nd volume
    return obj


def unwrap_phase_3D(phase_obj: nib.Nifti1Image) -> nib.Nifti1Image:
    print("Unwrapping phase image.")
    phase_data = phase_obj.get_fdata().astype(np.float32)
    if phase_data.max() > 3.15:
        if phase_data.min() >= 0:
            norm_phase = ((phase_data / phase_data.max()) * 2 * np.pi) - np.pi
        else:
            norm_phase = (phase_data / phase_data.max()) * np.pi
    else:
        norm_phase = phase_data

    dim = norm_phase.shape
    # x coordinates
    tmp = np.array(
        range(int(np.floor(-dim[0] / 2)), int(np.floor(dim[0] / 2)))
    ) / float(dim[0])

    tmp = tmp.reshape((dim[0], 1, 1))
    xx = np.tile(tmp, (1, dim[1], dim[2]))

    # y coordinates
    tmp = np.array(
        range(int(np.floor(-dim[1] / 2)), int(np.floor(dim[1] / 2)))
    ) / float(dim[1])

    tmp = tmp.reshape((1, dim[1], 1))
    yy = np.tile(tmp, (dim[0], 1, dim[2]))

    # z coordinates
    tmp = np.array(
        range(int(np.floor(-dim[2] / 2)), int(np.floor(dim[2] / 2)))
    ) / float(dim[2])

    tmp = tmp.reshape((1, 1, dim[2]))
    zz = np.tile(tmp, (dim[0], dim[1], 1))

    # radial squared frequency grid
    kk2 = xx**2 + yy**2 + zz**2
    hp1 = gauss_filter_3D(dim[0], GAUSS_STDEV, dim[1], GAUSS_STDEV, dim[2], GAUSS_STDEV)

    filter_phase = np.zeros_like(norm_phase)
    with np.errstate(divide="ignore", invalid="ignore"):
        lap_sin = -4.0 * (np.pi**2) * icfft(kk2 * cfft(np.sin(norm_phase)))
        lap_cos = -4.0 * (np.pi**2) * icfft(kk2 * cfft(np.cos(norm_phase)))
        lap_theta = np.cos(norm_phase) * lap_sin - np.sin(norm_phase) * lap_cos
        tmp = np.array(-cfft(lap_theta) / (4.0 * (np.pi**2) * kk2))
        tmp[np.isnan(tmp)] = 1.0
        tmp[np.isinf(tmp)] = 1.0
        kx2 = tmp * (1 - hp1)
        filter_phase = np.real(icfft(kx2))

    filter_phase *= -1.0 

    filter_obj = nib.Nifti1Image(filter_phase, phase_obj.affine, phase_obj.header)
    filter_obj.set_data_dtype(np.float32)
    return filter_obj


def cfft(img_array: np.ndarray) -> np.ndarray:
    return np.fft.fftshift(np.fft.fftn(np.fft.fftshift(img_array)))


def icfft(freq_array: np.ndarray) -> np.ndarray:
    return np.fft.fftshift(np.fft.ifftn(np.fft.fftshift(freq_array)))


def gauss_filter_3D(dimx: int, stdevx: float, dimy: int, stdevy: float, dimz: int, stdevz: float) -> np.ndarray:
    if dimx % 2 == 0:
        centerx = (dimx / 2.0) + 1
    else:
        centerx = (dimx + 1) / 2.0

    if dimy % 2 == 0:
        centery = (dimy / 2.0) + 1
    else:
        centery = (dimy + 1) / 2.0

    if dimz % 2 == 0:
        centerz = (dimz / 2.0) + 1
    else:
        centerz = (dimz + 1) / 2.0

    kki = np.arange(1, dimy + 1).reshape(dimy, 1, 1) - centery
    kkj = np.arange(1, dimx + 1).reshape(1, dimx, 1) - centerx
    kkk = np.arange(1, dimz + 1).reshape(1, 1, dimz) - centerz

    gy = gauss(kki, stdevx)
    gx = gauss(kkj, stdevy)
    gz = gauss(kkk, stdevz)

    h = gy * gx * gz

    h /= h.sum()
    h /= h.max()

    return h


def gauss(r: np.ndarray, std0: float) -> np.ndarray:
    return np.exp(-(r**2) / (2 * (std0**2))) / (std0 * np.sqrt(2 * np.pi))


def main(args=None):
    print(
        "\n"
        "If you are using this software in a publication, please cite the following:\n"
        "Bartz, KM, et al., A Three-Dimensional Phase Unwrapping Method Applied to Paramagnetic Rim Lesion Visualization, "
        "in [Proceedings of ISMRM Workshop on White Matter: MR Imaging and Beyond, Marseille, France, October 14 -- 16, 2026], 2026."
        "\n"
        "and"
        "\n"
        "Dewey, BE, Laplacian-based Phase Unwrapping in Python, Zenodo, 2022. "
        "https://doi.org/10.5281/zenodo.7198990"
        "\n"
    )
    parser = ArgumentParser(
        description="Unwrap 3D MRI phase images using Laplacian-based phase unwrapping. "
        "See https://github.com/katembartz/3D_laplacian_phase_unwrap for full instructions."
    )
    parser.add_argument(
        "phase_image",
        metavar="PHASE_IMAGE",
        type=Path,
        help="Path to input phase image",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional output filepath. Default is ${PHASE_IMAGE}_unwrapped_3D.nii.gz",
    )
    parsed = parser.parse_args(args)

    parsed.phase_image = parsed.phase_image.resolve()
    if parsed.output is None:
        parsed.output = parsed.phase_image.parent / parsed.phase_image.name.replace(
            ".nii.gz", "_unwrapped_3D.nii.gz"
        )
    else:
        parsed.output = parsed.output.resolve()

    if not parsed.phase_image.exists():
        parser.error(f"Input file not found: {parsed.phase_image}")
    if not parsed.output.parent.exists():
        parser.error(f"Output directory not found: {parsed.output.parent}")

    obj = nib.Nifti1Image.load(parsed.phase_image)

    filter_obj = unwrap_phase_3D(obj)

    filter_obj.to_filename(parsed.output)