#!/usr/bin/env python3
"""
VTracer Vectorize - GIMP 3.0 Plugin
Converts raster images to SVG vector graphics using VTracer

Installation:
1. pip install vtracer
2. Copy the 'vtracer-vectorize' folder to your GIMP plugins directory
   (Edit > Preferences > Folders > Plug-ins)
3. Restart GIMP

Usage:
Filters > VTracer > Vectorize to SVG
"""

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gimp, GimpUi, Gtk, GLib, Gio, GObject
import sys
import os
import tempfile

try:
    import vtracer
    VTRACER_AVAILABLE = True
except ImportError:
    VTRACER_AVAILABLE = False


class VTracerVectorize(Gimp.PlugIn):
    """GIMP Plugin to vectorize images using VTracer"""

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        return ['vtracer-vectorize']

    def do_set_i18n(self, name):
        return False

    def do_create_procedure(self, name):
        if name == 'vtracer-vectorize':
            procedure = Gimp.ImageProcedure.new(
                self,
                name,
                Gimp.PDBProcType.PLUGIN,
                self.vectorize,
                None
            )

            procedure.set_image_types("*")
            procedure.set_sensitivity_mask(
                Gimp.ProcedureSensitivityMask.DRAWABLE
            )

            procedure.set_menu_label("Vectorize to SVG...")
            procedure.add_menu_path("<Image>/Filters/VTracer/")

            procedure.set_documentation(
                "Vectorize image to SVG",
                "Converts the current image to SVG vector graphics using VTracer",
                name
            )
            procedure.set_attribution(
                "AEther Handmade",
                "MIT License",
                "2025"
            )

            # Parameters
            procedure.add_string_argument(
                "output-path",
                "Output Path",
                "Path to save the SVG file (leave empty for temp file)",
                "",
                GObject.ParamFlags.READWRITE
            )

            procedure.add_int_argument(
                "color-mode",
                "Color Mode",
                "0=Color, 1=Binary",
                0, 1, 0,
                GObject.ParamFlags.READWRITE
            )

            procedure.add_int_argument(
                "filter-speckle",
                "Filter Speckle",
                "Discard patches smaller than this (1-100)",
                1, 100, 4,
                GObject.ParamFlags.READWRITE
            )

            procedure.add_int_argument(
                "color-precision",
                "Color Precision",
                "Number of colors (1-256)",
                1, 256, 8,
                GObject.ParamFlags.READWRITE
            )

            procedure.add_double_argument(
                "corner-threshold",
                "Corner Threshold",
                "Corner detection threshold (0-180)",
                0.0, 180.0, 60.0,
                GObject.ParamFlags.READWRITE
            )

            procedure.add_double_argument(
                "segment-length",
                "Segment Length",
                "Curve segment length (0.5-10)",
                0.5, 10.0, 4.0,
                GObject.ParamFlags.READWRITE
            )

            procedure.add_double_argument(
                "splice-threshold",
                "Splice Threshold",
                "Splice threshold (0-180)",
                0.0, 180.0, 45.0,
                GObject.ParamFlags.READWRITE
            )

            procedure.add_choice_argument(
                "path-precision",
                "Path Precision",
                "SVG path precision",
                Gimp.Choice.new_with_values(
                    ("low", 0, "Low (smaller file)", None),
                    ("medium", 1, "Medium", None),
                    ("high", 2, "High (more detail)", None),
                ),
                "medium",
                GObject.ParamFlags.READWRITE
            )

            return procedure

        return None

    def vectorize(self, procedure, run_mode, image, n_drawables, drawables, config, run_data):
        """Main vectorization function"""

        if not VTRACER_AVAILABLE:
            return procedure.new_return_values(
                Gimp.PDBStatusType.EXECUTION_ERROR,
                GLib.Error(
                    message="VTracer not installed. Run: pip install vtracer"
                )
            )

        if n_drawables != 1:
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR,
                GLib.Error(message="Please select exactly one layer")
            )

        drawable = drawables[0]

        # Show dialog if interactive mode
        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init("vtracer-vectorize")

            dialog = GimpUi.ProcedureDialog.new(procedure, config, "VTracer Vectorize")
            dialog.fill(None)

            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(
                    Gimp.PDBStatusType.CANCEL,
                    GLib.Error()
                )

            dialog.destroy()

        # Get parameters
        output_path = config.get_property("output-path")
        color_mode = config.get_property("color-mode")
        filter_speckle = config.get_property("filter-speckle")
        color_precision = config.get_property("color-precision")
        corner_threshold = config.get_property("corner-threshold")
        segment_length = config.get_property("segment-length")
        splice_threshold = config.get_property("splice-threshold")
        path_precision_choice = config.get_property("path-precision")

        # Map path precision
        precision_map = {"low": 1, "medium": 2, "high": 3}
        path_precision = precision_map.get(path_precision_choice, 2)

        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_in:
            tmp_input = tmp_in.name

        if not output_path:
            output_path = tempfile.mktemp(suffix='.svg')

        try:
            # Export current image to temp PNG
            Gimp.get_pdb().run_procedure(
                'file-png-export',
                [
                    GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
                    GObject.Value(Gimp.Image, image),
                    GObject.Value(GObject.TYPE_INT, 1),
                    GObject.Value(
                        GObject.TYPE_BOXED,
                        Gimp.ObjectArray.new(Gimp.Drawable, [drawable], False)
                    ),
                    GObject.Value(Gio.File, Gio.File.new_for_path(tmp_input)),
                ]
            )

            # Run VTracer
            mode = "binary" if color_mode == 1 else "color"

            svg_str = vtracer.convert_image_to_svg_py(
                tmp_input,
                colormode=mode,
                filter_speckle=filter_speckle,
                color_precision=color_precision,
                corner_threshold=corner_threshold,
                length_threshold=segment_length,
                splice_threshold=splice_threshold,
                path_precision=path_precision
            )

            # Write SVG
            with open(output_path, 'w') as f:
                f.write(svg_str)

            # Show success message
            Gimp.message(f"SVG saved to: {output_path}")

            # Try to open in default application
            try:
                Gio.AppInfo.launch_default_for_uri(
                    f"file://{output_path}",
                    None
                )
            except:
                pass

        except Exception as e:
            return procedure.new_return_values(
                Gimp.PDBStatusType.EXECUTION_ERROR,
                GLib.Error(message=str(e))
            )
        finally:
            # Cleanup temp input
            if os.path.exists(tmp_input):
                os.unlink(tmp_input)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(VTracerVectorize.__gtype__, sys.argv)
