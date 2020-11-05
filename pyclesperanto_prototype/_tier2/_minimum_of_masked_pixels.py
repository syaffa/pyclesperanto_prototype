from .._tier0 import Image
from .._tier0 import create
from .._tier0 import create_2d_xy
from .._tier0 import create_2d_yx
from .._tier0 import execute
from .._tier1 import transpose_xz
from .._tier1 import transpose_yz
from .._tier0 import pull
from .._tier1 import copy_slice

def __minimum_of_masked_pixels_reduction(input : Image, input_mask : Image, output : Image, output_mask : Image):
    parameters = {
        "dst_min": output,
        "dst_mask": output_mask,
        "mask": input_mask,
        "src": input
    }

    execute(__file__, 'minimum_of_masked_pixels_3d_2d_x.cl', 'minimum_of_masked_pixels_3d_2d', output.shape, parameters)

def _slice_to_stack(image : Image, stack : Image = None, num_slices = 1):
    # TODO: This might become a core method
    if stack is None:
        stack = create([num_slices, image.shape[0], image.shape[1]])

    for i in range(0, num_slices):
        copy_slice(image, stack, i)
    return stack

def minimum_of_masked_pixels(input : Image, mask : Image):
    """

    :param input:
    :return:
    """

    dimensionality = input.shape

    # analyse a 3D image by reducing it to 2D using special minimum projection
    if (len(dimensionality) == 3): # 3D image
        reduced_image = create_2d_xy(input)
        reduced_mask = create_2d_xy(mask)

        __minimum_of_masked_pixels_reduction(input, mask, reduced_image, reduced_mask)

        input = reduced_image
        mask = reduced_mask

    dimensionality = input.shape

    # analyse the 2D image by making a stack out of it first
    if (len(dimensionality) == 2): # 2D image
        temp_input = transpose_xz(input)
        temp_mask = transpose_xz(mask)

        reduced_image = create_2d_yx(temp_input)
        reduced_mask = create_2d_yx(temp_mask)

        __minimum_of_masked_pixels_reduction(temp_input, temp_mask, reduced_image, reduced_mask)

        input = _slice_to_stack(reduced_image)
        mask = _slice_to_stack(reduced_mask)

    # analyse a 1D image by making a stack out of it first
    temp_input = transpose_yz(input)
    temp_mask = transpose_yz(mask)

    reduced_image = create([1,1])
    reduced_mask = create([1,1])

    __minimum_of_masked_pixels_reduction(temp_input, temp_mask, reduced_image, reduced_mask)

    # return the single pixel value
    return (pull(reduced_image)[0])[0]
