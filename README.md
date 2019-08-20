# conda-export

`conda env export` loses the specific channel information for each dependency. I think this sucks.

This script converts the output of 
```bash
conda list --show-channel-urls
```
to an `env.yml file`, correctly mapping dependencies with non-default channels to those channels e.g.

```bash
# packages in environment at /home/railton/miniconda3/envs/hacking:
#
# Name                    Version                   Build  Channel
blas                      1.0                         mkl    defaults
ca-certificates           2019.6.16            hecc5488_0    conda-forge
certifi                   2019.6.16                py37_1    conda-forge
click                     7.0                      pypi_0    pypi
cycler                    0.10.0                   py37_0    defaults
cython                    0.29.7                   pypi_0    pypi
dbus                      1.13.6               h746ee38_0    defaults
expat                     2.2.6                he6710b0_0    defaults
```
gets converted to 
```yaml
name: hacking
channels:
  - conda-forge
  - defaults
dependencies:
  - blas=1.0=mkl
  - conda-forge::ca-certificates=2019.6.16=hecc5488_0
  - conda-forge::certifi=2019.6.16=py37_1
  - cycler=0.10.0=py37_0
  - dbus=1.13.6=h746ee38_0
  - expat=2.2.6=he6710b0_0
  - pip:
    - click==7.0
    - cython==0.29.7
```
instead of the standard output of `conda env export` where the channels are not mapped to dependencies:
```yaml
name: hacking
channels:
  - conda-forge
  - defaults
dependencies:
  - blas=1.0=mkl
  - ca-certificates=2019.6.16=hecc5488_0
  - certifi=2019.6.16=py37_1
  - cycler=0.10.0=py37_0
  - dbus=1.13.6=h746ee38_0
  - expat=2.2.6=he6710b0_0
  - pip:
    - click==7.0
    - cython==0.29.7
```

## Usage

```bash
$ python3 conda_export.py -h
usage: conda_export.py [-h] -n ENV_NAME [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -n ENV_NAME, --name ENV_NAME
                        conda environment name (must exist)
  -o OUTPUT, --output OUTPUT
                        destination of output file (default: env_$ENV_NAME.yml
                        in $PWD)
```

## Dependencies

Needs the `ruamel.yaml` package which you can install via either

```bash
pip install ruamel.yaml
conda install ruamel.yaml -c conda-forge
```
