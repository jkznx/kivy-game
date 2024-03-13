from kivy.graphics import Rectangle, Color, Triangle

def draw_background(widget, SCREEN_W, SCREEN_H):
    with widget.canvas:

        # Draw sky
        Color(0.529, 0.808, 0.922)
        Rectangle(pos=(0, 0), size=(SCREEN_W, SCREEN_H))

        # Draw grass
        Color(0.173, 0.353, 0.090)
        grass_height = SCREEN_H
        Rectangle(pos=(0, 0), size=(SCREEN_W, grass_height))

        # Draw road
        road_height = SCREEN_H * 0.8
        road_top_y = (SCREEN_H - road_height) / 2 + road_height
        Color(0.412, 0.412, 0.412)
        Rectangle(pos=(0, (SCREEN_H - road_height) / 2), size=(SCREEN_W, road_height))

        # Draw center line
        Color(1, 1, 1)
        line_height = SCREEN_H * 0.04
        for y in range(int((SCREEN_H - road_height) / 2), int((SCREEN_H + road_height) / 2), int(line_height * 2)):
            Rectangle(pos=(SCREEN_W / 2 - 5, y), size=(10, line_height))

        # Draw left and right boundaries
        boundary_width = SCREEN_W * 0.05
        Color(0.173, 0.353, 0.090)
        Rectangle(pos=(0, 0), size=(boundary_width, SCREEN_H))
        Rectangle(pos=(SCREEN_W - boundary_width, 0), size=(boundary_width, SCREEN_H))

        # Draw start and finish lines
        Color(1, 1, 1)
        line_width = SCREEN_W * 0.02
        Rectangle(pos=(SCREEN_W / 2 - line_width / 2, 0), size=(line_width, grass_height))
        Rectangle(pos=(SCREEN_W / 2 - line_width / 2, SCREEN_H - grass_height), size=(line_width, grass_height))
