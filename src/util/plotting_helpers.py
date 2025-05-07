# Zachary Katz
# zachary_katz@mines.edu
# 07 May 2025


# Utility functions for plotting scripps grounding lines

# Imports
import shapefile
from cartopy.mpl.geoaxes import GeoAxes
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def load_shapefile(
    path: str,
) -> tuple[list[shapefile._Record], list[shapefile.Shape], list[str]]:
    """
    Load the Scripps grounding line and return a grouped list of Records and Shapes

    Parameters
    ----------
    path : str
        Path to Scripps groudning line .shp file. Folder must include whole download to work.
    """
    sf = shapefile.Reader(path)
    fields = sf.fields[1:]  # Skip deletion flag
    field_names = [field[0] for field in fields]

    records = sf.records()
    shapes = sf.shapes()

    return records, shapes, field_names


def filter_shapefile(
    records: list[shapefile._Record], shapes: list[shapefile.Shape], bbox: list[float]
) -> tuple[list[shapefile._Record], list[shapefile.Shape]]:
    """
    Subset the Scripps grounding line to only include polygons that are visible in bounding box bbox.

    Parameters
    ----------
    records : list[shapefile._Record]
        Shapely record containing shape classification
    shapes : list[shapefile.Shape]
        Shapely shape points
    bbox : list[float]
        Four floats in form [xmin, ymin, xmax, ymax] in projection PS71 (Polar Stereographic 71)
    """

    filtered_records = []
    filtered_shapes = []
    for record, shape in zip(records, shapes):
        shape_bbox = shape.bbox
        # Checks if any part of the shape is within the bounding box
        if (
            shape_bbox[0] < bbox[2]
            and shape_bbox[2] > bbox[0]
            and shape_bbox[1] < bbox[3]
            and shape_bbox[3] > bbox[1]
        ):
            filtered_records.append(record)
            filtered_shapes.append(shape)

    return filtered_records, filtered_shapes


def plot_shapefile(
    records: list[shapefile._Record],
    shapes: list[shapefile.Shape],
    ax: GeoAxes,
    field_names: list[str],
    colors: list[str],
    fill: bool,
) -> None:
    """
    Plots the given records and shapes on axis ax.

    Parameters
    ----------
    records : list[shapefile._Record]
        Shapely record containing shape classification
    shapes : list[shapefile.Shape]
        Shapely shape points
    ax : cartopy.mpl.geoaxes.GeoAxes
        Axes to polot on
    colors : list[str]
       [Grounded ice color, Ice Shelf color]; Must be length 2
    fill: bool
        Fill in the polygons if true
    """

    for record, shape in zip(records, shapes):
        classification = record[field_names.index("Id_text")]
        points = shape.points
        parts = list(shape.parts)
        parts.append(
            len(points)
        )  # Append the end index of the last part of the shapefile
        for i in range(len(parts) - 1):
            part = points[parts[i] : parts[i + 1]]
            if (
                classification == "Isolated island"
                or classification == "Ice rise or connected island"
                or classification == "Grounded ice or land"
            ):
                if fill:
                    ax.fill(*zip(*part), color=colors[0], linewidth=0.5, zorder=2)
                else:
                    ax.plot(*zip(*part), color=colors[0], linewidth=1, zorder=2)
            elif classification == "Ice shelf":
                if fill:
                    ax.fill(*zip(*part), color=colors[1], linewidth=0.5, zorder=2)
                else:
                    ax.plot(*zip(*part), color=colors[1], linewidth=1, zorder=2)
            else:
                print(f"Unknown classification: {classification}")


def plot_inset(
    fig: Figure,
    location: list[float],
    bbox: list[float],
    records: list[shapefile._Record],
    shapes: list[shapefile.Shape],
    field_names: list[str],
) -> GeoAxes:
    """
    Plots an inset of Antarctica with bounding box highlighted

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to add inset to
    location : list[float]
        Four floats in the form [left, bottom, width, height], in fraction of figure width and height
    bbox : list[float]
       Four floats in form [xmin, ymin, xmax, ymax] in projection PS71 (Polar Stereographic 71)
    records : list[shapefile._Record]
        Shapely record containing shape classification
    shapes : list[shapefile.Shape]
        Shapely shape points
    field_names:
        Shapely field names
    """

    # Make inset and remove borders
    ps71_projection = ccrs.Stereographic(
        central_latitude=-90, central_longitude=0, true_scale_latitude=-71
    )
    inset = fig.add_axes(location, projection=ps71_projection)
    inset.patch.set_facecolor("none")
    for spine in inset.spines.values():
        spine.set_visible(False)
    inset.set_xticks([])
    inset.set_yticks([])

    # Plot map of Antarctica
    plot_shapefile(
        records, shapes, inset, field_names, ["lightgray", "lightblue"], fill=True
    )
    rect = plt.Rectangle(
        (
            bbox[0],
            bbox[1],
        ),
        bbox[2] - bbox[0],
        bbox[3] - bbox[1],
        zorder=3,
        linewidth=2,
        edgecolor="red",
        facecolor="none",
    )
    inset.add_patch(rect)

    return inset
