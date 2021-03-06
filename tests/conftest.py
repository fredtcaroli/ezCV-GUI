import os

import cv2
import pytest

from ezcv_gui.controller import EzCVController


@pytest.fixture(scope='session')
def datadir():
    curr_dir = os.path.dirname(__file__)
    return os.path.join(curr_dir, 'data')


@pytest.fixture
def test_img_fname(datadir):
    return os.path.join(datadir, 'img.png')


@pytest.fixture
def test_img(test_img_fname):
    return cv2.imread(test_img_fname)


@pytest.fixture
def controller():
    return EzCVController()
