import xml.etree.ElementTree as ET
import svgwrite
from svgpath2mpl import parse_path
import random

def extract_path_from_svg_data(svg_data):
    print("Incoming SVG Data:", svg_data)

    # Convert the dictionary to an SVG string
    svg_str = ''.join(chr(int(value)) for value in svg_data.values())
    print("Constructed SVG String:", svg_str)

    namespace = "{http://www.w3.org/2000/svg}"
    try:
        root = ET.fromstring(svg_str)
        paths = [element for element in root.findall('.//{}path'.format(namespace))]
        extracted_path = parse_path(paths[0].attrib['d']) if paths else None
        print("Extracted Path:", extracted_path)
        return extracted_path
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return None

def get_point_at_length(vertices, distance):
    total_length = 0
    for i in range(len(vertices) - 1):
        segment_length = ((vertices[i+1][0] - vertices[i][0])**2 + (vertices[i+1][1] - vertices[i][1])**2)**0.5
        if segment_length == 0:  # skip zero-length segments
            continue
        if total_length + segment_length >= distance:
            t = (distance - total_length) / segment_length
            x = (1-t)*vertices[i][0] + t*vertices[i+1][0]
            y = (1-t)*vertices[i][1] + t*vertices[i+1][1]
            return x, y
        total_length += segment_length
    return None


def compute_bounding_box(points):
    min_x = min([point[0] for point in points])
    max_x = max([point[0] for point in points])
    min_y = min([point[1] for point in points])
    max_y = max([point[1] for point in points])
    return min_x, min_y, max_x, max_y

def generate_ripped_svg_from_svg_data(svg_data, jaggedness=40):
    path_obj = extract_path_from_svg_data(svg_data)
    if not path_obj:
        print("No path data found in SVG.")
        return None

    vertices = path_obj.vertices
    polyline_points = []

    # sample points from the path and adjust with jaggedness
    total_length = sum(((vertices[i+1][0] - vertices[i][0])**2 + (vertices[i+1][1] - vertices[i][1])**2)**0.5 for i in range(len(vertices) - 1))
    i = 0
    while i < total_length:
        point = get_point_at_length(vertices, i)
        print("Sampled Point:", point)
        x, y = point
        y += random.randint(-jaggedness, jaggedness)  # adjust the y value for jaggedness
        polyline_points.append((x, y))
        i += jaggedness

    # compute bounding box of the polyline points
    min_x, min_y, max_x, max_y = compute_bounding_box(polyline_points)

    # create SVG canvas that fits the bounding box dimensions
    dwg = svgwrite.Drawing(size=(max_x - min_x, max_y - min_y), profile='tiny')

    # adjust polyline points based on the bounding box
    adjusted_points = [(x - min_x, y - min_y) for x, y in polyline_points]

    polyline = dwg.polyline(points=adjusted_points, fill="none", stroke="white")
    dwg.add(polyline)
    
    final_svg = dwg.tostring()
    print("Final SVG:", final_svg)
    
    return final_svg
