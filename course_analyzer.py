from collections import deque
from dataclasses import dataclass
from typing import Iterable
from course_scraper import Course


@dataclass
class LeveledCourse(Course):
    level: int

    def __init__(self, course: Course, level: int):
        super().__init__(**course.__dict__)
        self.level = level


def assign_all_levels(courses: Iterable[Course]) -> Iterable[Course]:
    '''This is what I wrote'''
    course_levels = {}
    visited_courses = set()
    current_courses = set()
    level = 0
    remaining_courses = {course.id for course in courses}
    while remaining_courses:
        for course in courses:
            if course.id in visited_courses:
                continue
            if set(course.must_courses + course.recommend_courses).issubset(visited_courses):
                course_levels[course.id] = level
                current_courses.add(course.id)
                remaining_courses.remove(course.id)
        visited_courses.update(current_courses)
        current_courses.clear()
        level += 1

    return [LeveledCourse(course, level=course_levels[course.id]) for course in courses]


def topological_sort(courses: Iterable[Course]) -> Iterable[Course]:
    '''
    This function was written by ChatGPT.

    Performs a topological sort on a collection of courses.
    This function uses the Kahn's algorithm to perform a topological sort, which has a time complexity of O(n + m),
    where n is the number of courses and m is the number of prerequisites.
    '''
    graph = {course.id: [] for course in courses}
    indegrees = {course.id: 0 for course in courses}

    # Build the graph and calculate the indegrees
    for course in courses:
        for prereq in course.must_courses + course.recommend_courses:
            graph[prereq].append(course.id)
            indegrees[course.id] += 1

    # Perform a topological sort using a queue
    queue = deque(
        [course.id for course in courses if indegrees[course.id] == 0])
    levels = {course.id: 0 for course in courses}
    while queue:
        curr = queue.popleft()
        for neighbor in graph[curr]:
            indegrees[neighbor] -= 1
            if indegrees[neighbor] == 0:
                queue.append(neighbor)
                levels[neighbor] = levels[curr] + 1

    return [LeveledCourse(course, level=levels[course.id]) for course in courses]


def find_max_level(courses: Iterable[LeveledCourse]) -> int:
    return max(course.level for course in courses)

if __name__ == "__main__":
    import timeit

    setup = "from __main__ import load_courses, assign_all_levels, topological_sort; courses = load_courses()"
    stmt1 = "assign_all_levels(courses)"
    stmt2 = "topological_sort(courses)"

    time1 = timeit.timeit(stmt=stmt1, setup=setup, number=100000)
    time2 = timeit.timeit(stmt=stmt2, setup=setup, number=100000)

    print("assign_all_levels:", time1)
    print("topological_sort:", time2)

    # assign_all_levels: 5.267825200004154
    # assign_all_levels_chatgpt: 4.458090699998138

    # ChatGPT wrote faster ;)
