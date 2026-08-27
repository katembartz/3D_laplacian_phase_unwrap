# 3D MRI Phase Unwrapping

3-dimensional phase processing pipeline (unwrapping and background removal) for MRI phase images in Python.

If you use this code in your work, please cite the following:

**Publication:** 
```
Bartz, KM, et al., "A Three-Dimensional Phase Unwrapping Method Applied to Paramagnetic Rim Lesion Visualization," in [Proceedings of ISMRM Workshop on White Matter: MR Imaging and Beyond, Marseille, France, October 14 -- 16, 2026], 2026.
```

**Citation:**
```
@inproceedings{bartz2026_3DLapl,
  title={A Three-Dimensional Phase Unwrapping Method Applied to Paramagnetic Rim Lesion Visualization},
  author={Bartz, Kathleen M and Moretti, Giulia S and Bacchetti, Anna and Lee, Nathanael and Zhang, Jinwei and Remedios, Samuel W and Saidha, Shiv and Calabresi, Peter and Carass, Aaron and Prince, Jerry L and Dewey, Blake E},
  booktitle={"Proceedings of ISMRM Workshop on White Matter: MR Imaging and Beyond, Marseille, France, October 14 -- 16, 2026"},
  year={2026}
}
```

Please also cite the original 2D method from which this repository was adapted from:
```
Blake E. Dewey. (2022). Laplacian-based Phase Unwrapping in Python. Zenodo. [https://doi.org/10.5281/zenodo.7198990](https://doi.org/10.5281/zenodo.7198991)
```
The original github repository is located at: https://github.com/blakedewey/phase_unwrap

## Installation and Usage 

We recommend starting from a fresh python installation.
```
conda create -n phase_unwrap_3D python=3.10
conda activate phase_unwrap_3D
```

Clone and install this repository:
```
git clone https://github.com/katembartz/3D_laplacian_phase_unwrap.git
cd 3D_laplacian_phase_unwrap
pip install .
```

Usage:
```
unwrap-phase-3D /path/to/phase_image.nii.gz
```
An optional tag `--output path/to/output` will save the unwrapped image to that path. If not provided, the unwrapped image will be saved to the same directory as the input image with '_unwrapped_3D' appended to the filename (before the .nii.gz).

