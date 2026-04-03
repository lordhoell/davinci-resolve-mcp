# Fusion Tool Reference

## Table of Contents
- [Common Tool Types](#common-tool-types)
- [TextPlus Inputs](#textplus-inputs)
- [Background Inputs](#background-inputs)
- [Merge Inputs](#merge-inputs)
- [Transform Inputs](#transform-inputs)
- [Connection Patterns](#connection-patterns)
- [Modifier Types](#modifier-types)
- [Discovering Tool Types](#discovering-tool-types)

---

## Common Tool Types

Use these IDs with `comp_add_tool(comp_id, tool_id)`:

**Generators (create output):**
- `TextPlus` - Styled text with full typography control
- `Background` - Solid color / gradient background
- `Plasma` - Procedural plasma generator
- `FastNoise` - Procedural noise generator
- `MediaIn` - Input from timeline (auto-created in Resolve Fusion comps)
- `Loader` - Load media from disk

**Compositing:**
- `Merge` - Composite foreground over background (the core compositing node)
- `ChannelBooleans` - Channel operations
- `MatteControl` - Matte refinement

**Filters:**
- `Blur` - Gaussian blur
- `Glow` - Glow effect
- `Sharpen` - Sharpen filter
- `BrightnessContrast` - Brightness/contrast adjustment
- `ColorCorrector` - Full color correction
- `ColorCurves` - Curve-based color adjustment
- `HueCurves` - Hue-based adjustment

**Transform:**
- `Transform` - 2D transform (position, rotation, scale)
- `Resize` - Resolution change
- `Crop` - Crop image
- `DVE` - Digital video effect (3D perspective)

**Masks:**
- `RectangleMask` - Rectangle mask
- `EllipseMask` - Ellipse mask
- `PolylineMask` - Freeform bezier mask
- `BitmapMask` - Bitmap-based mask

**Output:**
- `MediaOut` - Output to timeline (auto-created in Resolve Fusion comps)
- `Saver` - Save output to disk

---

## TextPlus Inputs

Set with `tool_set_input(text_id, input_name, value)`:

| Input | Type | Description |
|-------|------|-------------|
| `StyledText` | string | The text content |
| `Font` | string | Font family name (use `fusion_get_font_list` to discover) |
| `Style` | string | Font style ("Bold", "Italic", "Bold Italic") |
| `Size` | float | Text size (0.0 - 1.0, relative to frame height) |
| `Red1` | float | Text color red (0.0 - 1.0) |
| `Green1` | float | Text color green (0.0 - 1.0) |
| `Blue1` | float | Text color blue (0.0 - 1.0) |
| `Alpha1` | float | Text opacity (0.0 - 1.0) |
| `Center` | table | Position {x, y} (0.0-1.0, 0.5/0.5 = center) |
| `Tracking` | float | Letter spacing |
| `LineSpacing` | float | Line spacing multiplier |
| `HorizontalJustification` | int | 0=Left, 1=Center, 2=Right |
| `VerticalJustification` | int | 0=Top, 1=Center, 2=Bottom |
| `Enabled1` | bool | Enable/disable first shading element |
| `Type1` | int | Shading type (0=Text, 1=Border, 2=Shadow, 3=Background) |
| `Enabled2` | bool | Enable second shading (border) |
| `Thickness2` | float | Border thickness |
| `Red2`/`Green2`/`Blue2` | float | Border color |
| `Enabled4` | bool | Enable fourth shading (shadow) |
| `Offset4` | table | Shadow offset {x, y} |
| `Softness4` | float | Shadow blur |

---

## Background Inputs

| Input | Type | Description |
|-------|------|-------------|
| `TopLeftRed` | float | Red (0.0 - 1.0) |
| `TopLeftGreen` | float | Green (0.0 - 1.0) |
| `TopLeftBlue` | float | Blue (0.0 - 1.0) |
| `TopLeftAlpha` | float | Alpha (0.0 - 1.0) |
| `Width` | int | Image width in pixels |
| `Height` | int | Image height in pixels |
| `Depth` | int | Bit depth (1=8bit, 2=16bit, 3=16float, 4=32float) |
| `Type` | string | "Solid" or "Gradient" |

---

## Merge Inputs

| Input | Type | Description |
|-------|------|-------------|
| `Background` | Image | Background input (connect via `tool_connect_input`) |
| `Foreground` | Image | Foreground input (connect via `tool_connect_input`) |
| `Center` | table | Foreground position {x, y} |
| `Size` | float | Foreground scale (1.0 = 100%) |
| `Angle` | float | Foreground rotation (degrees) |
| `Blend` | float | Opacity of foreground (0.0 - 1.0) |
| `ApplyMode` | string | Blend mode ("Normal", "Screen", "Multiply", "Overlay", etc.) |
| `EffectMask` | Image | Optional mask input |

---

## Transform Inputs

| Input | Type | Description |
|-------|------|-------------|
| `Input` | Image | Image to transform |
| `Center` | table | Center of transform {x, y} |
| `Size` | float | Scale (1.0 = 100%) |
| `Angle` | float | Rotation in degrees |
| `Pivot` | table | Pivot point {x, y} |
| `XSize` | float | Horizontal scale |
| `YSize` | float | Vertical scale |
| `Aspect` | float | Aspect ratio |
| `FlipHoriz` | bool | Horizontal flip |
| `FlipVert` | bool | Vertical flip |

---

## Connection Patterns

Connect tools with `tool_connect_input(receiving_tool_id, input_name, source_tool_id)`:

**Basic composite (text over background):**
```
Background --> Merge.Background
TextPlus   --> Merge.Foreground
```

**Chain of filters:**
```
MediaIn --> Blur.Input
Blur    --> BrightnessContrast.Input
BC      --> MediaOut.Input
```

**Text with mask:**
```
Background   --> Merge.Background
TextPlus     --> Merge.Foreground
EllipseMask  --> Merge.EffectMask
```

**Lower third (two text layers):**
```
Background --> Merge1.Background
TextPlus1  --> Merge1.Foreground        (name)
Merge1     --> Merge2.Background
TextPlus2  --> Merge2.Foreground        (title)
Merge2     --> Merge3.Background
MediaIn    --> Merge3.Foreground... wait, reverse:
MediaIn    --> Merge3.Background
Merge2     --> Merge3.Foreground
```

Correct lower third pattern:
```
Background  --> Merge1.Background
TextPlus1   --> Merge1.Foreground
Merge1      --> Merge2.Background
TextPlus2   --> Merge2.Foreground
MediaIn     --> MergeFinal.Background
Merge2      --> MergeFinal.Foreground
MergeFinal  --> MediaOut
```

---

## Modifier Types

Add to an input with `tool_add_modifier(tool_id, input_name, modifier_type)`:

| Modifier | Purpose |
|----------|---------|
| `BezierSpline` | Keyframe animation with bezier curves |
| `XYPath` | Animated 2D position path |
| `PolyPath` | Polyline animation path |
| `Expression` | Expression-driven values |
| `Calculation` | Math expression modifier |
| `Perturbation` | Random/noise animation |
| `Probe` | Probe another tool's value |

After adding BezierSpline, get it and set keyframes:
```
1. tool_add_modifier(tool_id, "Size", "BezierSpline")
2. tool_get_input_list(tool_id)  -- find the input
3. spline_get_spline_from_input(input_id)  --> spline_id
4. spline_set_keyframes(spline_id, {"0": 0.0, "30": 1.0})
```

---

## Discovering Tool Types

List all available tool types:
```
fusion_get_reg_list("CT_Tool")           -- Regular tools
fusion_get_reg_list("CT_Filter")         -- Filters
fusion_get_reg_list("CT_FilterSource")   -- Generators/sources
fusion_get_reg_list("CT_Modifier")       -- Animation modifiers
fusion_get_reg_list("CT_Mask")           -- Mask tools
fusion_get_reg_list("CT_3D")             -- 3D tools
```

Get details about a specific tool type:
```
fusion_get_reg_attrs("TextPlus")  --> {name, category, help, inputs, outputs...}
```

List available fonts:
```
fusion_get_font_list()  --> [font names...]
```
