import re
import requests
from dataclasses import dataclass
from typing import Iterable, List
import pickle
import os
import itertools


PICKLE_FILENAME = "courses.pickle"
DEGREE_PAGE_URL = "https://academic.openu.ac.il/CS/computer/program/AF.aspx?version=108"
# This splitting string only applies to B.Sc.
# Change it to suit your degree page
DEGREE_PAGE_CHOICE_SPLITTER = "בחירה - לפחות 27-31"


@dataclass
class Course:
    id: int
    name: str
    credits: int
    advanced: bool
    domain: str
    required: bool
    must_courses: Iterable[int]
    recommend_courses: Iterable[int]


def get_course_by_id(courses: Iterable[Course], id: int) -> Course:
    try:
        return [course for course in courses if course.id == id][0]
    except IndexError:
        return None


def cleanup_hebrew(string: str) -> str:
    '''remove the RTL and LTR symbols'''
    return string.replace("&#x202c;", "").replace("&#x202b;", "")


def manual_filter(courses: List[Course]) -> None:
    '''Make manual changes to the Course list'''

    # this course has a very long name
    get_course_by_id(courses, 20476).name = "מתמטיקה בדידה"
    get_course_by_id(courses, 20425).name = "הסתברות ומבוא לסטטיסטיקה למדמ\"ח"

    # 3 regular credits + 2 advanced credits
    get_course_by_id(courses, 20604).credits = 5


def scrape_data() -> List[Course]:
    '''Scrape the data and parse it'''

    # Download the degree page
    response = requests.get(DEGREE_PAGE_URL)
    content = response.content.decode('utf-8')

    # split it into must and choice
    before, after = content.split(DEGREE_PAGE_CHOICE_SPLITTER, 1)
    must_url_matches = re.findall(
        r'https*://www.openu.ac.il/courses/\d+\.htm', before)
    choise_url_matches = re.findall(
        r'https*://www.openu.ac.il/courses/\d+\.htm', after)

    # make sure we have that information when we create the Course instance
    urls = itertools.chain([(url, True) for url in must_url_matches], [
                           (url, False) for url in choise_url_matches])

    # parse the urls
    courses = []
    for url_match, required in urls:
        response = requests.get(url_match)
        # no idea why they use a different encoding
        page_content = response.content.decode('windows-1255')

        # get the title
        title_match = re.search(r'<title>(.*?)</title>', page_content)

        # title is in format "{RTL}id name{LTR}"
        id, name = cleanup_hebrew(title_match.group(1)).split(" ", 1)

        # extract credits and course level
        credits, level = re.findall(
            r'(\d+) נקודות זכות ברמה (רגילה|מתקדמת)', page_content)[0]
        advanced = level == "מתקדמת"

        # domain is "science / mathematics" or "science / computer science"
        domain = re.search(r'<strong>\s*שיוך:\s*<\/strong>(.*?)<\/p>',
                           page_content, re.DOTALL).group(1).split("/")[1].strip()

        # parse prerequisite courses
        requirements = re.search(
            r'<p>\s*<img src="gifs/triangle.jpg" \b.*?>(.*?)<\/p>', page_content, re.DOTALL).group(1)
        try:
            # assume all courses mentioned before the word are required
            # and all the ones after it are not
            before, after = requirements.split("מומלץ")
        except ValueError:
            before, after = requirements, ""
        # parse prerequisite course ids
        must = list([int(x) for x in re.findall(
            r'https*://www\.openu\.ac\.il/courses/(\d+)\.htm', before)])
        recommend = list([int(x) for x in re.findall(
            r'https*://www\.openu\.ac\.il/courses/(\d+)\.htm', after)])

        courses.append(Course(id=int(id),
                              name=name,
                              credits=int(credits),
                              advanced=advanced,
                              domain=domain,
                              required=required,
                              must_courses=must,
                              recommend_courses=recommend))

    # filter out all unknown courses
    all_ids = {course.id for course in courses}  # get ids of all known courses
    for course in courses:
        # recrate lists using only the known ids
        course.must_courses = [
            id for id in course.must_courses if id in all_ids]
        course.recommend_courses = [
            id for id in course.recommend_courses if id in all_ids]

    # hand made modifications to the output
    manual_filter(courses)

    return courses


def load_courses() -> List[Course]:
    """
    Load the courses array from disk, or download it if it doesn't exist.
    Caution: There is no security built in to this, verify the pickle file yourself.
    """
    try:
        with open('courses.pickle', 'rb') as f:
            courses = pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError):
        courses = scrape_data()

        with open('courses.pickle', 'wb') as f:
            pickle.dump(courses, f)
    return courses


if __name__ == "__main__":
    # force scrape the courses
    if os.path.isfile(PICKLE_FILENAME):
        os.remove(PICKLE_FILENAME)
    print(load_courses())
