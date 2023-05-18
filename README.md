# openu-course-visualizer
Create an interactive graph visualization of the courses for degrees in The Open University of Israel. 
Currently tested only with [B.Sc in CompSci](https://academic.openu.ac.il/CS/computer/program/AF.aspx?version=108)

## Usage
Run the [pyvis_graph.py](/pyvis_graph.py).

The program will scrape the website using the url in [course_scraper.py](/course_scraper.py#L11).
An HTML file containing the [interactive graph](https://pyvis.readthedocs.io/en/latest/tutorial.html) with be created and opened.

The default view is a hierarchical view, where dependencies go from left to right. Red means required courses and blue means reccomended courses.

## Requirements
 * python
 * any web browser
 * `pip install -r requirements.txt`

## Contributing
I encourage you to change this program to suit your needs. Feel free to open issues and PRs with your code changes :)

## Screenshots
![full graph](https://github.com/DarkMetalMouse/openu-course-visualizer/assets/51059131/304942d2-8347-4862-a927-165fb3f208b0)
![highlighted course 1](https://github.com/DarkMetalMouse/openu-course-visualizer/assets/51059131/fc5c5f3e-da5c-49ab-9901-e063ee8663f1)
![highlighted course 2](https://github.com/DarkMetalMouse/openu-course-visualizer/assets/51059131/bbcc13d6-195c-4b3e-aad6-f17268e9320d)
