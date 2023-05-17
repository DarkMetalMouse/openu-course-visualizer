from pyvis.network import Network
from course_scraper import load_courses, Course
import webbrowser


def get_color(course: Course) -> str:
    ''' Color coding according to course data'''
    if not course.required: 
        return "#ED7D31" # orange
    
    if course.domain == "מתמטיקה":
         return "#00B0F0" # blue

    #everything else is compsci
    return "#00B050" # green


def get_label(course: Course) -> str:
    '''
    Get the course label in the format:
    {id}: {name}
    {credit_num} credits(, advanced)?
    '''
    # U+202E is RTL text modifier
    # U+200E is LTR text modifier
    return f"{course.id}: {course.name}\n‮{course.credits} נק\"ז{', מתקדם' if course.advanced else ''}‎"


courses = load_courses()

# courses = [course for course in courses if course.must] # only must courses

# filter out all unknown courses
all_ids = {course.id for course in courses} # get ids of all known courses
for course in courses:
    # recrate lists using only the known ids
    course.must_courses = [id for id in course.must_courses if id in all_ids]
    course.recommend_courses = [id for id in course.recommend_courses if id in all_ids]

net = Network(notebook=True,directed=True,height="750px", width="100%")

# add nodes
for course in courses:
        net.add_node(course.id,
                    label=get_label(course),
                    color=get_color(course),
                    shape="box")

# add edges
for course in courses:
    for must in course.must_courses:
        net.add_edge(must, course.id, color="red",smooth=False)

    for rec in course.recommend_courses:
        net.add_edge(rec, course.id, color="blue",smooth=False)

net.toggle_physics(False) # nodes repelling off

net.show("course_graph.html")

webbrowser.open("course_graph.html")