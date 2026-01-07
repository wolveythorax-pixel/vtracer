# VTracer Plugins for GIMP & Inkscape

Plugins that bring VTracer's powerful image-to-vector conversion directly into your favorite image editors.

## Features

- **One-click vectorization** - Convert raster images (PNG, JPG) to SVG vectors
- **Multiple presets** - Quick options for logos, illustrations, and photos
- **Fine-grained control** - Adjust all VTracer parameters
- **Batch processing** - Vectorize multiple images at once (Inkscape)

---

## Prerequisites

### Install VTracer Python Package

```bash
pip install vtracer
```

Or with pipx (recommended for system-wide installation):

```bash
pipx install vtracer
```

---

## GIMP Plugin Installation

### Requirements
- GIMP 3.0+ (uses Python 3 and GObject Introspection)
- Python 3.8+
- vtracer package

### Installation Steps

1. **Find your GIMP plugins folder:**
   - Open GIMP
   - Go to `Edit > Preferences > Folders > Plug-ins`
   - Note one of the listed directories

2. **Copy the plugin folder:**
   ```bash
   # Linux example
   cp -r plugins/gimp/vtracer-vectorize ~/.config/GIMP/3.0/plug-ins/

   # Make it executable
   chmod +x ~/.config/GIMP/3.0/plug-ins/vtracer-vectorize/vtracer-vectorize.py
   ```

   **Windows:**
   Copy `plugins/gimp/vtracer-vectorize` folder to:
   `%APPDATA%\GIMP\3.0\plug-ins\`

   **macOS:**
   Copy to: `~/Library/Application Support/GIMP/3.0/plug-ins/`

3. **Restart GIMP**

### Usage

1. Open an image in GIMP
2. Go to `Filters > VTracer > Vectorize to SVG...`
3. Adjust settings and click OK
4. SVG will be saved and opened in your default viewer

---

## Inkscape Extension Installation

### Requirements
- Inkscape 1.0+
- Python 3.8+
- vtracer package

### Installation Steps

1. **Find your Inkscape extensions folder:**
   - Open Inkscape
   - Go to `Edit > Preferences > System`
   - Look for "User extensions" path

2. **Copy the extension files:**
   ```bash
   # Linux
   cp plugins/inkscape/vtracer_vectorize.* ~/.config/inkscape/extensions/

   # Windows
   # Copy to: %APPDATA%\inkscape\extensions\

   # macOS
   # Copy to: ~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/
   ```

3. **Restart Inkscape**

### Usage

1. Open or create a document in Inkscape
2. Import or place a raster image (File > Import)
3. Select the image
4. Go to `Extensions > VTracer > VTracer Vectorize`
5. Choose a preset or customize settings
6. Click Apply

The vectorized result will appear as a group of paths, positioned where the original image was.

---

## Settings Guide

### Color Mode
- **Color** - Full color vectorization (best for photos, illustrations)
- **Binary** - Black and white only (best for logos, line art)

### Filter Speckle (1-100)
Removes small patches/noise. Higher values = cleaner output but may lose detail.
- Logos/icons: 4-8
- Photos: 2-4

### Color Precision (1-256)
Number of colors in the output. More colors = larger file but more faithful reproduction.
- Simple logos: 4-8
- Illustrations: 8-16
- Photos: 16-64

### Corner Threshold (0-180°)
Angle at which curves become corners. Lower = more corners, higher = smoother curves.
- Sharp graphics: 45-60
- Smooth illustrations: 60-90

### Segment Length (0.5-10)
Minimum length of curve segments. Lower = more detail, higher = simpler paths.
- Detailed: 2-3
- Simple: 4-6

### Splice Threshold (0-180°)
Controls curve splicing. Usually fine at default (45°).

### Path Precision (1-8)
Decimal precision for SVG coordinates. Higher = larger file but more accurate.
- Web graphics: 1-2
- Print/precision: 3-4

---

## Presets

### Black & White (bw)
Best for: Logos, line art, signatures, stamps
- Binary color mode
- Medium filtering
- Good for clean, simple graphics

### Poster
Best for: Illustrations, cartoon-style images, limited color artwork
- Color mode with limited palette
- Balanced settings
- Good middle-ground for most artwork

### Photo
Best for: Photographs, complex images, full-color artwork
- Full color mode
- High color precision
- More detail preservation

---

## Troubleshooting

### "VTracer not installed" error
Make sure vtracer is installed for the same Python that GIMP/Inkscape uses:
```bash
# Check which Python Inkscape uses
inkscape --extension-python

# Install vtracer for that Python
/path/to/python -m pip install vtracer
```

### Plugin doesn't appear in menu
- Make sure files are in the correct folder
- Check file permissions (must be executable on Linux/macOS)
- Restart the application completely

### Poor quality output
- Try different presets
- Use PNG instead of JPG (no compression artifacts)
- Increase color precision for complex images
- Decrease filter speckle for more detail

### Large SVG file size
- Reduce color precision
- Increase filter speckle
- Use binary mode if colors aren't needed
- Reduce path precision

---

## Contributing

Found a bug or want to improve the plugins?

1. Fork this repository
2. Make your changes
3. Submit a pull request

---

## License

MIT License - same as VTracer

## Credits

- [VTracer](https://github.com/visioncortex/vtracer) - The core vectorization engine
- [AEther Handmade](https://github.com/wolveythorax-pixel/aether-handmade) - Plugin development
