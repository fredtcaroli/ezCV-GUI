# ezCV-GUI

Graphical interface for creating computer vision pipelines.

After you created and saved your pipeline you can simply load it into a python script using:

```python
import cv2
from ezcv import CompVizPipeline

# Loading pipeline
with open('config.yaml') as f:
    pipeline = CompVizPipeline.load(f)

# Running on a test image
img = cv2.imread('test_image.png')
result_img, ctx = pipeline.run(img)
```

`ezCV` can be installed separately from `ezCV-GUI`, so you don't have to install pyQt6 when you don't
need it. For more information on how `ezCV` works, read the [project's page](https://github.com/fredtcaroli/ezCV).

## Installing

>**NOTE**: We don't have an easy `pip install` or `conda install` command yet, sorry.
> I swear it's easy to install without it though.

We recommend that you first setup a conda environment with python version 3.7:

```
conda create -n ezcv python=3.7
conda activate ezcv
```

Then you'll need to install OpenCV and Poetry:

```
conda install -y opencv
pip install poetry
```

Finally, download the project's source code and run:

```
poetry install
```

## Running

```
python scripts/ezcv-gui.py
```
