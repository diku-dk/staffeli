#!/usr/bin/env python3

import os

from assignment import get_cwd_assignment
from submission import find_student_id

def main():
    assignment = get_cwd_assignment()
    student_id = find_student_id(os.getcwd())
    print("https://absalon.ku.dk/courses/{}/gradebook/speed_grader?assignment_id={}#%7B%22student_id%22%3A%22{}%22%7D".format(
        assignment.course.id, assignment.id, student_id))

if __name__ == "__main__":
    main()
