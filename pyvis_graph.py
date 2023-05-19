import colorsys
import webbrowser
from typing import Iterable, List

from pyvis.network import Network

from course_analyzer import LeveledCourse, topological_sort, find_max_level
from course_scraper import Course, load_courses

DARKEN_MOD = 0.7
SATURATION = 0.6
VALUE = 1

def get_color(course: Course) -> str:
    ''' Color coding according to course data'''
    if not course.required:
        return "#ED7D31"  # orange

    if course.domain == "מתמטיקה":
        return "#00B0F0"  # blue

    # everything else is compsci
    return "#00B050"  # green


def split_by_level(courses: Iterable[LeveledCourse]) -> List[Iterable[LeveledCourse]]:
    levels = []
    while (level_courses := [course for course in courses if course.level == len(levels)]):
        levels.append(level_courses)
    return levels


def sort_required_first(split_courses: List[Iterable[LeveledCourse]]) -> None:
    for courses in split_courses:
        courses.sort(reverse=True, key=lambda c: c.required)


def generate_rainbow_array(num_colors):
    rainbow = []

    # Generate colors using the HSV color space
    for i in range(num_colors):
        hue = i / num_colors
        rgb = colorsys.hsv_to_rgb(hue, SATURATION, VALUE)  # Convert HSV to RGB
        color = '#%02x%02x%02x' % tuple(
            int(c * 255) for c in rgb)  # Convert RGB to hex
        rainbow.append(color)

    return rainbow


def darken_color(hex_color):
    # Convert hex color to RGB values
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    # Calculate the darker RGB values, convert back to hex format and return
    return f"#{int(r * DARKEN_MOD):02x}{int(g * DARKEN_MOD):02x}{int(b * DARKEN_MOD):02x}"


def get_topological_colors(colors: List[str], course: LeveledCourse) -> str:
    return colors[course.level] if course.required else darken_color(colors[course.level])


def get_label(course: Course) -> str:
    '''
    Get the course label in the format:
    {id}: {name}
    {credit_num} credits(, advanced)?
    '''
    # U+202E is RTL text modifier
    # U+200E is LTR text modifier
    return f"{course.id}: {course.name}\n‮{course.credits} נק\"ז{', מתקדם' if course.advanced else ''}‎"


courses = topological_sort(load_courses())

courses_by_level = split_by_level(courses)
sort_required_first(courses_by_level)

net = Network(notebook=True, directed=True, height="900px",
              width="100%", select_menu=True, layout=True)


node_ids = {}
# add nodes
colors = generate_rainbow_array(find_max_level(courses)+1)
for level in courses_by_level:
    for i, course in enumerate(level):
        id = i*100000+course.id
        node_ids[course.id] = id
        net.add_node(id,
                     label=get_label(course),
                     color=get_topological_colors(colors, course),
                     level=course.level,
                     shape="box")

# add edges
for course in courses:
    for must in course.must_courses:
        net.add_edge(node_ids[must], node_ids[course.id],
                     color="red", smooth=False)

    for rec in course.recommend_courses:
        net.add_edge(node_ids[rec], node_ids[course.id],
                     color="blue", smooth=False)

net.set_options("""
var options = {
    "configure": { "enabled": false },
    "physics": { "enabled": false },
    "interaction": { "navigationButtons": true },
    "layout": {
        "hierarchical": {
            "enabled": true,
            "levelSeparation": 250,
            "direction": "LR",
            "treeSpacing": 75,
            "nodeSpacing": 75
        }
    }
}""")

net.show("course_graph.html")
webbrowser.open("course_graph.html")
