# Learn Algo Trade

## Running on Windows 11

- WSL: Ubuntu-20.04 (WSL2)
- Python 3.9.12
- Anaconda3: conda 4.13.0

### Exporting conda environment

First, run `conda update pip` with admin permission inside activated conda environment. This will tell conda which packages were installed with pip.
Then, run the following command to export packages installed via conda and pip.

```bash
conda env export > conda_environment_export.yml
```
