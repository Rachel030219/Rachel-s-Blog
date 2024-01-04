"""
Copyright (C) 2024 Rachel030219

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import os
import sys
import math
from abc import abstractmethod

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import time
import colour
import imageio.v3 as iio
from colour.plotting import *
import exiftool

# here is the svg path used to draw the horseshoe, resized & flipped to fit 1.0x1.0 mpl axes, orig is 512x512
# src: https://commons.wikimedia.org/wiki/File:CIExy1931.svg
# svg_path = 'M 0.74023,0.26172 C 0.53262,0.46934 0.39414,0.60195 0.30527,0.69082 0.22871,0.76738 0.12168,0.83418 0.08203,0.83418 c -0.05605,-0.00000 -0.07715,-0.08809 -0.07715,-0.19238 0.00000,-0.11582 0.03594,-0.44414 0.12891,-0.59844 0.00000,-0.00000 0.02012,-0.03047 0.04238,-0.03906 L 0.74023,0.26172 z'
horseshoe_path = Path(np.array([[0.74023, 0.26172],
       [0.53262, 0.46934],
       [0.39414, 0.60195],
       [0.30527, 0.69082],
       [0.22871, 0.76738],
       [0.12168, 0.83418],
       [0.08203, 0.83418],
       [0.02598, 0.83418],
       [0.00488, 0.74609],
       [0.00488, 0.6418 ],
       [0.00488, 0.52598],
       [0.04082, 0.19766],
       [0.13379, 0.04336],
       [0.13379, 0.04336],
       [0.15391, 0.01289],
       [0.17617, 0.0043 ],
       [0.74023, 0.26172],
       [0.74023, 0.26172]]), np.array([1,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  2, 79],
                                      dtype=np.uint8))

# Classes used to parse ICC profiles.
# Referring to ICC.1:2022 standard, section 10.6 *curveType* and 10.18 *parametricCurveType*
class ConversionFunction:
    """
    Base class for conversion functions.
    It should be noted that in ICC profiles all values are encoded as big-endian.
    Since all conversion methods require a conversion from bytes to int, they should all follow byteorder 'big'.
    """

    @abstractmethod
    def convert_trc(self, pixels: np.ndarray) -> np.ndarray:
        pass


def parse_s15Fixed16Number(s15Fixed16Number: bytes) -> float:
    """
    Parse a s15Fixed16Number, which is a 4-byte signed fixed-point number, with 16 fractional bits.
    The first 16 bits are the integer part, and the last 16 bits are the fractional part.
    i.e. 0x00010000 represents 1, 0x80000000 represents -32768, 0x7FFFFFFF represents 32767 + (65535/65536), etc.
    :param s15Fixed16Number: a 4-byte signed fixed-point number, with 16 fractional bits.
    :return: a float number.
    """
    # first calculate the integer part
    integer_bytes = s15Fixed16Number[0:2]
    integer_part = int.from_bytes(integer_bytes, byteorder='big', signed=True)
    # then calculate the fractional part
    fractional_bytes = s15Fixed16Number[2:4]
    fractional_part = int.from_bytes(fractional_bytes, byteorder='big', signed=False) / np.iinfo(np.uint16).max
    if integer_part < 0:
        fractional_part = -fractional_part
    return integer_part + fractional_part


def parse_trc(trc_param: bytes) -> ConversionFunction:
    """
    Parse the TRC parameter.
    :param trc_param: TRC parameter, a 1D array, representing the sampled one-dimensional function.
    :return: a conversion function.
    """
    if not trc_param:
        return GammaConversion(gamma=2.2)
    trc_type = trc_param[0:4].decode('utf-8')
    if trc_type == 'curv':
        """
        For curv types, according to the standard,
        When n is equal to 0, an identity response is assumed.
        When n is equal to 1, then the curve value shall be interpreted as a gamma value, encoded as a u8Fixed8Number.
         Gamma shall be interpreted as the exponent in the equation y = xγ and not as an inverse.
        When n greater than 1, the curve values (a sampled one-dimensional function) are defined as follows:
         The first entry is located at 0,0,
         the last entry at 1,0,
         intermediate entries are uniformly spaced using an increment of 1,0/(n−1).
         Entries are encoded as uInt16 (values represented by the entries in the range 0,0 to 1,0 are from 0 to 65 535).
         Function values between the entries shall be obtained through linear interpolation.
        """
        n = int.from_bytes(trc_param[8:12], byteorder='big', signed=False)
        if n == 0:
            return GammaConversion(gamma=2.2)
        elif n == 1:
            return GammaConversion(gamma=(trc_param[12] + trc_param[13] / 256))
        elif n > 1:
            matrix = np.zeros(n)
            for i in range(n):
                matrix[i] = (int.from_bytes(trc_param[12 + i * 2: 12 + (i + 1) * 2], byteorder='big', signed=False)
                             / np.iinfo(np.uint16).max)
            return CurveConversion(matrix)
        else:
            raise ValueError(f'n should be greater than 0, got n: {n}')
    elif trc_type == 'para':
        curve_type = int.from_bytes(trc_param[8:10], byteorder='big', signed=False)
        length = math.ceil(len(trc_param[10:]) / 4)
        params = np.zeros(length)
        for i in range(length):
            params[i] = parse_s15Fixed16Number(trc_param[12 + i * 4: 12 + (i + 1) * 4])
        return ParametricConversion(curve_type, params)
    else:
        raise ValueError(f'TRC type {trc_type} not supported')


class ICCProfile:
    """
    Class to parse ICC profile.
    """
    _trc_param = {}
    _matrix = None
    _profile_description = None

    def __init__(self, icc_path: str):
        self.icc_path = icc_path

    def get_trc(self) -> dict:
        """
        Get the TRC function for a given channel.
        Reason for the three return values is that it is unable to guarantee that all channel are of the same type.
        Therefore, the caller should apply conversion on each channel separately.
        :return: three conversion functions, corresponding to R, G, and B channels.
        """
        if not self._trc_param:
            if self.icc_path is not None and os.path.exists(self.icc_path):
                with exiftool.ExifTool() as et:
                    trc_red_param = et.execute(*['-icc_profile:RedTRC', '-b', self.icc_path], raw_bytes=True)
                    trc_green_param = et.execute(*['-icc_profile:GreenTRC', '-b', self.icc_path], raw_bytes=True)
                    trc_blue_param = et.execute(*['-icc_profile:BlueTRC', '-b', self.icc_path], raw_bytes=True)
                    self._trc_param = {'R': parse_trc(trc_red_param), 'G': parse_trc(trc_green_param),
                                       'B': parse_trc(trc_blue_param)}
            else:
                self._trc_param = {'R': GammaConversion(gamma=2.2), 'G': GammaConversion(gamma=2.2),
                                   'B': GammaConversion(gamma=2.2)}
        return self._trc_param

    def get_matrix(self) -> np.ndarray:
        """
        Get the matrix for R, G and B channels. Matrices read from ICC profiles should be regarded as columns.
        :return: a 2D array with shape of (3, 3), representing the matrix.
        DEPRECATED: this method is not used anymore, because the matrix read from ICC profiles is converting to PCS XYZ.
        Though it is theoretically the same as CIE XYZ, we are not sure if it is the same in practice.
        Furthermore, their white points differ, in PCS (profile correction space) the white point is D50,
        while for CIE XYZ this is D65.
        Therefore, we use the matrix from *colour-science* instead, to keep the white point consistent.
        """
        if self._matrix is None:
            if self.icc_path is not None and os.path.exists(self.icc_path):
                with exiftool.ExifTool() as et:
                    red_column = list(
                        map(float, et.execute(*['-icc_profile:RedMatrixColumn', '-b', self.icc_path]).split(' ')))
                    green_column = list(
                        map(float, et.execute(*['-icc_profile:GreenMatrixColumn', '-b', self.icc_path]).split(' ')))
                    blue_column = list(
                        map(float, et.execute(*['-icc_profile:BlueMatrixColumn', '-b', self.icc_path]).split(' ')))
                    self._matrix = np.vstack([red_column, green_column, blue_column]).transpose()
                    print(f'using {self._matrix} for RGB to XYZ')
            else:
                self._matrix = colour.models.rgb.RGB_COLOURSPACE_sRGB.matrix_RGB_to_XYZ
        return self._matrix

    def get_profile_description(self) -> str:
        """
        Get the profile description.
        :return: a string, the profile description.
        """
        if self._profile_description is None:
            if self.icc_path is not None and os.path.exists(self.icc_path):
                with exiftool.ExifToolHelper() as et:
                    metadata = et.get_metadata(self.icc_path)
                    try:
                        self._profile_description = metadata[0]["ICC_Profile:ProfileDescription"]
                    except KeyError:
                        self._profile_description = 'sRGB'
            else:
                return 'sRGB'
        return self._profile_description


class CurveConversion(ConversionFunction):
    """
    Class used to carry out curve type conversion.
    """

    def __init__(self, matrix: np.array):
        """
        :param matrix: a 1D array, representing the sampled one-dimensional function.
        The matrix contains n values, splitting the range 0,0 to 1,0 into n−1 equal sized intervals.
        Each value represents a point of exactly a fraction
        Values between those fraction points should be calculated via linear interpolation.
        """
        self.matrix = matrix

    def convert_trc(self, pixels: np.ndarray) -> np.ndarray:
        """
        Convert the pixels using the curve function.
        :param pixels: a 1D array, the channel of pixels to be converted, whose dtype is float32.
        :return: a 1D array, converted and clipped to [0, 1].
        The standard says that the domain and range of the curve function is [0, 1], but it does not specify
        what to do when the output is out of range. Therefore, we clip it to [0, 1].
        """
        n = len(self.matrix)
        # np.interp does not check for out of range values, so we need to do it manually
        print(f'using matrix {self.matrix} for TRC curve conversion')
        if np.min(pixels) < 0 or np.max(pixels) > 1:
            raise ValueError(f'pixels should be in range [0, 1], got {np.min(pixels)} and {np.max(pixels)}')
        result_array = np.interp(pixels, np.linspace(0, 1, n), self.matrix)
        return np.clip(result_array, 0, 1)


class GammaConversion(ConversionFunction):
    """
    CLass used for gamma correction.
    Typically, for an image with gamma value of 2.2, the conversion function is y = x^2.2.
    """

    def __init__(self, gamma: float = 2.2):
        self.gamma = gamma

    def convert_trc(self, pixels: np.ndarray) -> np.ndarray:
        print(f'using gamma {self.gamma} for TRC conversion')
        if self.gamma != 1:
            return pixels ** self.gamma
        else:
            return pixels


class ParametricConversion(ConversionFunction):
    """
    Class used for parametric curve conversion.
    """

    def __init__(self, curve_type: int, params: np.ndarray):
        self.curve_type = curve_type
        self.params = params

    def convert_trc(self, pixels: np.ndarray) -> np.ndarray:
        """
        Convert the pixels using the parametric curve function. There are five types, referring to
        Table 68 in ICC:1-2022 standard.
        :param pixels: a 1D array, the channel of pixels to be converted, whose dtype is float32.
        :return: a 1D array, converted and clipped to [0, 1]. The standard says that:
        > Any function value outside the range shall be clipped to the range of the function.
        Therefore, we do the clipping before returning.
        """
        print(f'using type {self.curve_type} and params {self.params} for TRC parametric curve conversion')
        if self.curve_type == 0:
            return GammaConversion(gamma=self.params[0].astype(float)).convert_trc(pixels)
        elif self.curve_type == 1:
            g = self.params[0]
            a = self.params[1]
            b = self.params[2]
            result_array = np.piecewise(pixels, [pixels < -b / a, pixels >= -b / a],
                                        [lambda x: 0, lambda x: (a * x + b) ** g])
        elif self.curve_type == 2:
            g = self.params[0]
            a = self.params[1]
            b = self.params[2]
            c = self.params[3]
            result_array = np.piecewise(pixels, [pixels < -b / a, pixels >= -b / a],
                                        [lambda x: c, lambda x: ((a * x + b) ** g + c)])
        elif self.curve_type == 3:
            g = self.params[0]
            a = self.params[1]
            b = self.params[2]
            c = self.params[3]
            d = self.params[4]
            result_array = np.piecewise(pixels, [pixels < d, pixels >= d],
                                        [lambda x: c * x, lambda x: (a * x + b) ** g])
        elif self.curve_type == 4:
            g = self.params[0]
            a = self.params[1]
            b = self.params[2]
            c = self.params[3]
            d = self.params[4]
            e = self.params[5]
            f = self.params[6]
            result_array = np.piecewise(pixels, [pixels < d, pixels >= d],
                                        [lambda x: (c * x + f), lambda x: ((a * x + b) ** g + e)])
        else:
            raise ValueError(f'curve type {self.curve_type} not supported')
        return np.clip(result_array, 0, 1)


def plot_xy_coordinates_with_color(xy_array, output_png_path):
    start_time = time.time()

    # convert xy_array to xyY, then XYZ and RGB ('sRGB' color space for plotting)
    xy2_array = colour.xy_to_xyY(xy_array, 0.6)
    xyz_array = colour.xyY_to_XYZ(xy2_array)
    rgb_array = colour.XYZ_to_RGB(xyz_array, colour.RGB_COLOURSPACES['sRGB'])
    rgb_array_clipped = np.clip(rgb_array, 0, 1)

    # plot
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 9))
    ax.set_title('CIE 1931 Chromaticity Diagram')
    # draw horseshoe
    horseshoe_patch = PathPatch(horseshoe_path, facecolor='none', edgecolor='#DDDDDD', linewidth=0.5)
    ax.add_patch(horseshoe_patch)
    # draw xy coordinates
    ax.scatter(xy2_array[:, 0], xy2_array[:, 1], color=rgb_array_clipped, s=0.05, edgecolors=None, linewidths=0)
    # setup axes
    ax.set_xlim(0, 0.8)
    ax.set_ylim(0, 0.9)
    ax.xaxis.set_ticks(np.arange(0, 0.9, 0.1))
    ax.yaxis.set_ticks(np.arange(0, 1.0, 0.1))
    # draw white point and annotation
    ax.scatter(0.3125, 0.329043, color='#DDDDDD', s=5, edgecolors=None, linewidths=0)
    ax.scatter(0.3125, 0.329043, color=(0, 0, 0, 0), s=20, edgecolors='#DDDDDD', linewidths=0.5)
    ax.text(0.325, 0.319, 'D65', color='#DDDDDD', fontsize=6, ha='center', va='center')
    ax.scatter(0.3402, 0.37461 , color='#DDDDDD', s=5, edgecolors=None, linewidths=0)
    ax.scatter(0.3402, 0.37461 , color=(0, 0, 0, 0), s=20, edgecolors='#DDDDDD', linewidths=0.5)
    ax.text(0.353, 0.365, 'D50', color='#DDDDDD', fontsize=6, ha='center', va='center')

    plt.savefig(output_png_path, format='jpg', dpi=500, facecolor='#000000')
    plt.close()
    print('Drawing Chromaticity Diagram spent: {:.2f} seconds'.format(time.time() - start_time))


def image_to_cie_xy(image_path) -> np.ndarray:
    start_time = time.time()
    # read image file
    try:
        img = iio.imread(image_path)
    except FileNotFoundError:
        print("file not found!")
        exit(1)
    # extract image color space using exiftool
    image_data = np.array(img, dtype=np.float32)
    # if image is integer, normalize it to floating [0, 1]
    if np.issubdtype(img.dtype, np.integer):
        print(f"original image is {str(img.dtype):s}, normalizing to float32 [0, 1]")
        image_data = image_data / np.iinfo(img.dtype).max
    else:
        print(f"original image is {str(img.dtype):s}, no need to normalize")

    # if image is RGBA, convert it to RGB by removing alpha channel
    if image_data.shape[2] == 4:
        print("original image is RGBA, removing alpha channel")
        image_data = image_data[:, :, :3]
    # reshape image data to 2D array
    pixels = image_data.reshape(-1, 3)

    # convert RGB (if format is RGB, from corresponding color space, or 'sRGB' by default) to XYZ and then xy
    icc_profile = ICCProfile(image_path)
    pixels_corrected = np.zeros(pixels.shape)
    for i, channel in enumerate(['R', 'G', 'B']):
        pixels_corrected[:, i] = icc_profile.get_trc()[channel].convert_trc(pixels[:, i])

    colorspace = icc_profile.get_profile_description()
    colorspace_split = colorspace.split(' ')
    for i in range(len(colorspace_split), 0, -1):
        if ' '.join(colorspace_split[:i]) in colour.RGB_COLOURSPACES:
            colorspace = ' '.join(colorspace_split[:i])
            break
    try:
        pixels_xyz = colour.RGB_to_XYZ(pixels_corrected, colour.RGB_COLOURSPACES[colorspace])
        print(f"original colorspace {icc_profile.get_profile_description():s} found, using {colorspace:s} for conversion")
    except KeyError:
        pixels_xyz = colour.RGB_to_XYZ(pixels_corrected, colour.RGB_COLOURSPACES['sRGB'])
        print(f"colorspace {icc_profile.get_profile_description():s} is not supported, using sRGB")
    xy_array = colour.XYZ_to_xy(pixels_xyz)
    print('Computing XYZ and xy spent: {:.2f} seconds'.format(time.time() - start_time))

    return xy_array


if __name__ == "__main__":
    '''
    The Python script converts image RGB data to CIE xy chromaticity coordinates and RGB values
    using imageio and NumPy (function image_to_cie_xy). 
    It then visualizes these coordinates on the CIE 1931 Chromaticity Diagram 
    with Matplotlib, coloring each point according to 
    its RGB value (function plot_xy_coordinates_with_color). 
    The development focused on optimizing data processing and visualization, 
    utilizing vectorized operations for efficiency, 
    ensuring accurate color representation, and producing visual output.
    '''
    # use first param as path
    image_path = "test.jpg"
    if len(sys.argv) > 1 and sys.argv[1] != "":
        print('Using image file: ' + sys.argv[1])
        image_path = sys.argv[1]
    else:
        print('Using default image file: ' + image_path)
    xy_coordinates = image_to_cie_xy(image_path)

    output_png_path = os.path.splitext(image_path)[0] + '_diagram.jpg'
    plot_xy_coordinates_with_color(xy_coordinates, output_png_path)
