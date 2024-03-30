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

## Jupyter notebook

### Setting up

- [Configuring Jupyter Notebook in Windows Subsystem Linux (WSL2)](https://towardsdatascience.com/configuring-jupyter-notebook-in-windows-subsystem-linux-wsl2-c757893e9d69)

### Troubleshooting

**"File does not exist" from `read_csv`**

- Try re-connecting the notebook by reloading the window.

## Conda vs Pip packages

If a package is available from both conda and pip, it's generally recommended to install it with conda, but pip can be used if the package is not available through conda or if you need a specific version of the package that's only available through pip.

You can check if a package is available as conda packages with `conda search`.

```bash
conda search yfinance
```

## Selecting the "right" environment

For python files, select `Python: Select Interpreter` from the command pallett and select `/opt/conda/envs/ds-and-ml/bin/python`.

For Jupyter notebook files (`.ipynb`), `Notebook: Select Notebook Kernel` > `Python Environments` and select the same environment as the above.
