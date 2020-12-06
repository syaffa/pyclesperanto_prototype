from .._tier1 import copy
from .._tier0 import empty_image_like
from .._tier0 import push_zyx
from .._tier0 import push
from .._tier0 import execute
from .._tier0 import plugin_function
from .._tier0 import Image
from .._tier0 import create_none
from .._tier0 import create
from .._tier0 import create_image

@plugin_function(output_creator=create_none)
def resample(source : Image, destination : Image = None, factor_x : float = 1, factor_y : float = 1, factor_z : float = 1, linear_interpolation : bool = False):
    """

    Parameters
    ----------
    source
    destination
    factor_x
    factor_y
    factor_z
    linear_interpolation

    Returns
    -------

    """
    import numpy as np

    source_dimensions = source.shape
    if len(source_dimensions) == 2:
        transform_matrix = np.asarray([
            [1.0 / factor_x, 0, 0],
            [0, 1.0 / factor_y, 0]
        ])
        destination_dimensions = [int(factor_y * source_dimensions[0]), int(factor_x * source_dimensions[1])]
    else:
        transform_matrix = np.asarray([
            [1.0 / factor_x, 0, 0, 0],
            [0, 1.0 / factor_y, 0, 0],
            [0, 0, 1.0 / factor_z, 0]
        ])
        destination_dimensions = [int(factor_z * source_dimensions[0]), int(factor_y * source_dimensions[1]),
                                  int(factor_x * source_dimensions[2])]

    # create an output image in case none is given
    if destination is None:
        destination = create(destination_dimensions)

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

    execute(__file__, 'affine_transform_' + str(len(destination.shape)) + 'd' + kernel_suffix + '_x.cl',
            'affine_transform_' + str(len(destination.shape)) + 'd' + kernel_suffix, destination.shape, parameters)

    return destination
