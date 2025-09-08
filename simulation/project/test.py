from manim import *

class CirclesWithList(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stations_tasks = []
        self.orders = []
    def construct(self):
        # Create circles with numbers
        circle1 = Circle(radius=0.7, color=BLUE).set_fill(BLUE, opacity=0.5)
        circle2 = Circle(radius=0.7, color=RED).set_fill(RED, opacity=0.5)
        circle3 = Circle(radius=0.7, color=WHITE).set_fill(WHITE, opacity=0.5)

        # circle1.move_to(UP*3)
        circle1.move_to(LEFT*2)
        circle2.move_to(UP*3)
        # circle2.move_to(ORIGIN)
        circle3.move_to(RIGHT*3)

        num1 = Text("1").move_to(circle1.get_center())
        num2 = Text("2").move_to(circle2.get_center())
        num3 = Text("3").move_to(circle3.get_center())

        # Group circles and numbers
        group1 = VGroup(circle1, num1)
        group2 = VGroup(circle2, num2)
        group3 = VGroup(circle3, num3)

        # Arrows from 1 -> 3 and 2 -> 3
        arrow1 = Arrow(start=circle1.get_right(), end=circle3.get_left(), buff=0.2)
        arrow2 = Arrow(start=circle2.get_right(), end=circle3.get_left(), buff=0.2)

        # Create list above
        items = [Text(f"Item {i+1}", font_size=30) for i in range(6)]
        item_list = VGroup(*[items[i].next_to(items[i-1], DOWN, aligned_edge=LEFT)
                             if i > 0 else items[i]
                             for i in range(len(items))])
        item_list.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        item_list.to_edge(LEFT)

        # Animate
        self.play(FadeIn(group1), FadeIn(group2), FadeIn(group3))
        self.play(Create(arrow1), Create(arrow2))
        self.play(FadeIn(item_list))

        self.wait(2)

        new_num1 = Text(f"1").move_to(circle1.get_center())
        new_num2 = Text(f"1").move_to(circle2.get_center())
        new_num3 = Text(f"1").move_to(circle3.get_center())

        # Update numbers
        self.play(Transform(num1, new_num1), Transform(num2, new_num2), Transform(num3, new_num3))
        self.wait(2)

    def add_to_scene(self):
        for task in self.stations_tasks:
            station_one = task[0]
            station_two = task[1]
            station_three = task[2]
            self.add(station_one, station_two, station_three)

        count = 0
        for order in self.orders:
            self.add(order)
            count += 1
            if count >= 6:
                break
        
if __name__ == "__main__":
    scene = CirclesWithList()
    scene.render()