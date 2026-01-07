#!/usr/bin/env python3
"""
VTracer Vectorize - Inkscape Extension
Converts raster images to SVG vector graphics using VTracer

Installation:
1. pip install vtracer
2. Copy vtracer_vectorize.py and vtracer_vectorize.inx to your Inkscape extensions folder:
   - Linux: ~/.config/inkscape/extensions/
   - Windows: %APPDATA%\inkscape\extensions\
   - macOS: ~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/
3. Restart Inkscape

Usage:
Extensions > VTracer > VTracer Vectorize
"""

import inkex
from inkex import Image, Group
import os
import tempfile
import base64
from urllib.parse import urlparse
from urllib.request import urlopen
import re

try:
    import vtracer
    VTRACER_AVAILABLE = True
except ImportError:
    VTRACER_AVAILABLE = False


class VTracerVectorize(inkex.EffectExtension):
    """Inkscape extension to vectorize embedded/linked images using VTracer"""

    def add_arguments(self, pars):
        # Options tab
        pars.add_argument("--tab", type=str, default="options")
        pars.add_argument("--colormode", type=str, default="color")
        pars.add_argument("--filter_speckle", type=int, default=4)
        pars.add_argument("--color_precision", type=int, default=8)
        pars.add_argument("--corner_threshold", type=float, default=60.0)
        pars.add_argument("--length_threshold", type=float, default=4.0)
        pars.add_argument("--splice_threshold", type=float, default=45.0)
        pars.add_argument("--path_precision", type=int, default=2)

        # Preset tab
        pars.add_argument("--preset", type=str, default="custom")

        # Hidden description params (Inkscape requires them)
        pars.add_argument("--filter_speckle_help", type=str, default="")
        pars.add_argument("--color_precision_help", type=str, default="")
        pars.add_argument("--corner_threshold_help", type=str, default="")
        pars.add_argument("--length_threshold_help", type=str, default="")
        pars.add_argument("--splice_threshold_help", type=str, default="")
        pars.add_argument("--path_precision_help", type=str, default="")
        pars.add_argument("--about_text", type=str, default="")

    def get_preset_settings(self, preset):
        """Get predefined settings for presets"""
        presets = {
            "bw": {
                "colormode": "binary",
                "filter_speckle": 4,
                "color_precision": 6,
                "corner_threshold": 60,
                "length_threshold": 4.0,
                "splice_threshold": 45,
                "path_precision": 2
            },
            "poster": {
                "colormode": "color",
                "filter_speckle": 4,
                "color_precision": 8,
                "corner_threshold": 60,
                "length_threshold": 4.0,
                "splice_threshold": 45,
                "path_precision": 2
            },
            "photo": {
                "colormode": "color",
                "filter_speckle": 2,
                "color_precision": 16,
                "corner_threshold": 90,
                "length_threshold": 2.0,
                "splice_threshold": 45,
                "path_precision": 3
            }
        }
        return presets.get(preset, None)

    def extract_image_data(self, image_element):
        """Extract image data from an Inkscape image element"""
        href = image_element.get('{http://www.w3.org/1999/xlink}href') or image_element.get('href')

        if not href:
            return None, None

        # Handle data URI (embedded image)
        if href.startswith('data:'):
            # Parse data URI: data:image/png;base64,xxxxx
            match = re.match(r'data:image/(\w+);base64,(.+)', href)
            if match:
                img_format = match.group(1)
                img_data = base64.b64decode(match.group(2))
                return img_data, img_format

        # Handle file path (linked image)
        elif href.startswith('file://'):
            filepath = urlparse(href).path
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    img_data = f.read()
                ext = os.path.splitext(filepath)[1].lower().replace('.', '')
                return img_data, ext

        # Handle relative path
        elif not href.startswith('http'):
            # Try relative to SVG file
            svg_dir = os.path.dirname(self.options.input_file) if self.options.input_file else ''
            filepath = os.path.join(svg_dir, href)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    img_data = f.read()
                ext = os.path.splitext(filepath)[1].lower().replace('.', '')
                return img_data, ext

        return None, None

    def effect(self):
        if not VTRACER_AVAILABLE:
            inkex.errormsg(
                "VTracer is not installed!\n\n"
                "Please install it with:\n"
                "  pip install vtracer\n\n"
                "Then restart Inkscape."
            )
            return

        # Get selected images
        images = [elem for elem in self.svg.selection if isinstance(elem, Image)]

        if not images:
            inkex.errormsg(
                "No images selected!\n\n"
                "Please select one or more raster images (PNG, JPG) to vectorize."
            )
            return

        # Get settings (use preset if not custom)
        if self.options.preset != "custom":
            settings = self.get_preset_settings(self.options.preset)
        else:
            settings = {
                "colormode": self.options.colormode,
                "filter_speckle": self.options.filter_speckle,
                "color_precision": self.options.color_precision,
                "corner_threshold": self.options.corner_threshold,
                "length_threshold": self.options.length_threshold,
                "splice_threshold": self.options.splice_threshold,
                "path_precision": self.options.path_precision
            }

        # Process each selected image
        for image in images:
            self.vectorize_image(image, settings)

    def vectorize_image(self, image_element, settings):
        """Vectorize a single image element"""

        # Extract image data
        img_data, img_format = self.extract_image_data(image_element)

        if img_data is None:
            inkex.errormsg(f"Could not read image data from element")
            return

        # Get image position and size
        x = float(image_element.get('x', 0))
        y = float(image_element.get('y', 0))
        width = image_element.get('width')
        height = image_element.get('height')

        # Save to temp file
        suffix = f'.{img_format}' if img_format else '.png'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(img_data)
            tmp_path = tmp.name

        try:
            # Run VTracer
            svg_str = vtracer.convert_image_to_svg_py(
                tmp_path,
                colormode=settings["colormode"],
                filter_speckle=settings["filter_speckle"],
                color_precision=settings["color_precision"],
                corner_threshold=settings["corner_threshold"],
                length_threshold=settings["length_threshold"],
                splice_threshold=settings["splice_threshold"],
                path_precision=settings["path_precision"]
            )

            # Parse the SVG output and extract paths
            from lxml import etree
            svg_tree = etree.fromstring(svg_str.encode())

            # Create a group for the vectorized content
            group = Group()
            group.set('id', f'vectorized_{image_element.get_id()}')

            # Apply transform to position the group where the image was
            if x != 0 or y != 0:
                group.set('transform', f'translate({x}, {y})')

            # Get the viewBox from the generated SVG to calculate scaling
            viewbox = svg_tree.get('viewBox')
            if viewbox and width and height:
                vb_parts = viewbox.split()
                if len(vb_parts) == 4:
                    vb_width = float(vb_parts[2])
                    vb_height = float(vb_parts[3])
                    img_width = float(width.replace('px', ''))
                    img_height = float(height.replace('px', ''))

                    scale_x = img_width / vb_width if vb_width else 1
                    scale_y = img_height / vb_height if vb_height else 1

                    if scale_x != 1 or scale_y != 1:
                        existing_transform = group.get('transform', '')
                        group.set('transform', f'{existing_transform} scale({scale_x}, {scale_y})'.strip())

            # Copy all path elements from the generated SVG
            for elem in svg_tree.iter():
                if elem.tag.endswith('path'):
                    path = inkex.PathElement()
                    path.set('d', elem.get('d'))
                    if elem.get('fill'):
                        path.set('style', f'fill:{elem.get("fill")};stroke:none')
                    group.append(path)
                elif elem.tag.endswith('rect'):
                    rect = inkex.Rectangle()
                    for attr in ['x', 'y', 'width', 'height', 'fill']:
                        if elem.get(attr):
                            if attr == 'fill':
                                rect.set('style', f'fill:{elem.get(attr)};stroke:none')
                            else:
                                rect.set(attr, elem.get(attr))
                    group.append(rect)

            # Add group to parent of original image
            parent = image_element.getparent()
            parent.insert(list(parent).index(image_element), group)

            # Optionally remove original image (keep it for now, just hide it)
            image_element.set('style', 'display:none')

        except Exception as e:
            inkex.errormsg(f"Error vectorizing image: {str(e)}")

        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    VTracerVectorize().run()
