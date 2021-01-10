from typing import Union

from .._tier0 import plugin_function
from .._tier0 import Image
from .._tier0 import push_zyx
from ._AffineTransform3D import AffineTransform3D
import numpy as np

@plugin_function
def affine_transform(source : Image, destination : Image = None, transform : Union[np.ndarray, AffineTransform3D] = None, linear_interpolation : bool = False):
    """
    Applies an affine transform to an image.

    Parameters
    ----------
    source : Image
        image to be transformed
    destination : Image, optional
        image where the transformed image should be written to
    transform : 4x4 numpy array or AffineTransform3D object
        transform matrix or object describing the transformation
    linear_interpolation: bool
        not implemented yet

    Returns
    -------
    destination

    """
    import numpy as np
    from .._tier0 import empty_image_like
    from .._tier0 import execute
    from .._tier1 import copy

    # we invert the transform because we go from the target image to the source image to read pixels
    if isinstance(transform, AffineTransform3D):
        transform_matrix = np.asarray(transform.copy().inverse())
    else:
        transform_matrix = np.linalg.inv(transform)

    gpu_transform_matrix = push_zyx(transform_matrix)

    kernel_suffix = ''
    if linear_interpolation:
        image = empty_image_like(source)
        copy(source, image)
        source = image
        kernel_suffix = '_interpolate'


    parameters = {
        "input": source,
        "output": destination,
        "mat": gpu_transform_matrix
    }

    execute(__file__, '../clij-opencl-kernels/kernels/affine_transform_' + str(len(destination.shape)) + 'd' + kernel_suffix + '_x.cl',
            'affine_transform_' + str(len(destination.shape)) + 'd' + kernel_suffix, destination.shape, parameters)


    return destination