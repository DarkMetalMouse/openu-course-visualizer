from pyvis.network import Network
from course_scraper import load_courses, Course
from course_analyzer import topological_sort
import webbrowser

DARKEN_MOD = 0.8
COLORS = ['#e15759', '#f28e2c', '#edc949',
          '#59a14f', '#76b7b2', '#4e79a7', '#b07aa1']

def get_color(course: Course) -> str:
    ''' Color coding according to course data'''
    if not course.required:
        return "#ED7D31"  # orange

    if course.domain == "מתמטיקה":
        return "#00B0F0"  # blue

    # everything else is compsci
    return "#00B050"  # green


def darken_color(hex_color):
    # Convert hex color to RGB values
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    # Calculate the darker RGB values, convert back to hex format and return
    return f"#{int(r * DARKEN_MOD):02x}{int(g * DARKEN_MOD):02x}{int(b * DARKEN_MOD):02x}"


def get_topological_colors(course: Course) -> str:
    return COLORS[course.level] if course.required else darken_color(COLORS[course.level])


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
courses = topological_sort(load_courses())

# courses = [course for course in courses if course.must] # only must courses

net = Network(notebook=True, directed=True, height="750px", width="100%")

# add nodes
for course in courses:
    net.add_node(course.id,
                 label=get_label(course),
                 color=get_topological_colors(course),
                 shape="box")

# add edges
for course in courses:
    for must in course.must_courses:
        net.add_edge(must, course.id, color="red", smooth=False)

    for rec in course.recommend_courses:
        net.add_edge(rec, course.id, color="blue", smooth=False)

net.toggle_physics(False)  # nodes repelling off

net.show("course_graph.html")

webbrowser.open("course_graph.html")
