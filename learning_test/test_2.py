
previous_direction = "left"
current_direction = "down"
if previous_direction == "up" and current_direction != "down":
    current_direction = "up"
    print("UP, DONE")
if previous_direction == "down" and current_direction != "up":
    current_direction = "down"
    print("down, DONE")
if previous_direction == "left" and current_direction != "right":
    current_direction = "left"
    print("left, DONE")
if previous_direction == "right" and current_direction != "left":
    current_direction = "right"
    print("right, DONE")