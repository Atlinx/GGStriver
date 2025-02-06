import tkinter as tk
import cv2
import numpy as np
from PIL import ImageColor
import skimage.color as skc


def color_dist(color_a, color_b):
    return np.sum(np.abs(np.array(color_a) - np.array(color_b)))


class Rect:
    def __init__(self, start, end, color=(255, 0, 0), thickness=1):
        self.start = np.array(start)
        self.end = np.array(end)
        if isinstance(color, str):
            color = ImageColor.getrgb(color)
        self.color = color
        self.thickness = thickness

    def size(self) -> tuple[int, int]:
        return self.end - self.start

    def grid_iter(self, size, edge_offset=0):
        grid_size = np.array(size) - np.array((1, 1))
        offset = self.size() / grid_size
        for y in range(grid_size[1] + 1):
            for x in range(grid_size[0] + 1):
                curr_off = np.array((x, y)) * offset
                curr_pos = np.array(self.start + curr_off, dtype=np.int64)
                x_on_edge = x == 0 or x == grid_size[0]
                y_on_edge = y == 0 or y == grid_size[1]
                if not (x_on_edge and y_on_edge):
                    if x == 0:
                        curr_pos += (-edge_offset, 0)
                    elif x == grid_size[0]:
                        curr_pos += (edge_offset, 0)
                    if y == 0:
                        curr_pos += (0, -edge_offset)
                    elif y == grid_size[1]:
                        curr_pos += (0, edge_offset)
                yield curr_pos

    def as_grid(self, size, edge_offset=0):
        return np.array(list(self.grid_iter(size, edge_offset)))

    # return rectangle as start and end
    def cv_rect(self):
        return (self.start, self.end, self.color, self.thickness)

    def get_inputs(
        self,
        frame: cv2.typing.MatLike,
        grid_size,
        bg_colors,
        activation_threshold: int,
        edge_offset: int = 0,
    ):
        for i in range(len(bg_colors)):
            if isinstance(bg_colors[i], str):
                bg_colors[i] = ImageColor.getrgb(bg_colors[i])
        res = []
        print("\n\n")
        for i, point in enumerate(self.grid_iter(grid_size, edge_offset)):
            pixel = list(reversed(frame[point[1], point[0]]))
            activated = True
            act_dist = 0
            for bg_color in bg_colors:
                if color_dist(bg_color, pixel) < activation_threshold:
                    activated = False
                    act_dist = color_dist(bg_color, pixel)
                    break
            print(
                f"  [{i}]: p: {str(point):<10} got color: {str(tuple(pixel)):<20} activated ? {f'XXX {act_dist}' if activated else f'{act_dist}'}"
            )
            res.append(activated)
        return np.array(res)


JOYSTICK_BG_COLORS = [
    (245, 0, 13),
    (186, 181, 171),
    (190, 193, 208),
    (178, 0, 99),
    (183, 192, 192),
    (170, 175, 181),
    (185, 80, 73),
    (166, 127, 115),
    (148, 0, 133),
    (232, 0, 47),
    "#949291",
    "#908e93",
    "#939594",
    "#928c89",
    "#8d9396",
    "#be155f",
    "#b30566",
    "#ad0864",
    "#d1025b",
    "#df004b",
    "#ea0344",
    "#f20336",
    "#f00a29",
]
JOYSTICK_OFFSET = 2

INPUT_RECT = Rect((22, 20), (115, 64), "#f51a1a")
OFFSET = 2
JOYSTICK_RECT = Rect((28 + OFFSET, 26 + OFFSET), (62 - OFFSET, 60 - OFFSET), "#1a9df5")
BUTTON_RECT = Rect((74, 33), (107, 56), "#671af5")
print("size: ", INPUT_RECT.size())
print("grid: ", INPUT_RECT.as_grid((3, 2)))


# get input
def get_joystick_inputs(frame):
    inputs = JOYSTICK_RECT.get_inputs(
        frame, (3, 3), JOYSTICK_BG_COLORS, 20, JOYSTICK_OFFSET
    )
    i = 0
    res_str = "........\n"
    for y in range(3):
        res_str += "|"
        for x in range(3):
            res_str += ("X" if inputs[i] else " ") + " "
            i += 1
        res_str += "|\n"
    res_str += "''''''''\n"
    print(res_str)
    return inputs


# Input video
SKIPPED_FRAMES = 2000

frame_count = 0
frames = []
cap = cv2.VideoCapture("output_1.mp4")
while cap.isOpened():
    ret, frame = cap.read()
    frame_count += 1
    if frame_count > SKIPPED_FRAMES:
        frames.append(frame)
    if not ret:
        break

frame_pointer = 0
current_input = {
    "left": False,
    "down": False,
    "right": False,
    "up": False,
    "p": False,
    "s": False,
    "d": False,
    "k": False,
    "hs": False,
    "rc": False,
    "dash": False,
}
key_input = " "
while key_input != "n":
    frame = frames[frame_pointer]
    frame = cv2.medianBlur(frame, 3)
    # get input
    inputs = get_joystick_inputs(frame)
    if np.count_nonzero(inputs) == 1:
        continue
    cv2.imwrite("frame.png", frame)

    # overlay
    frame = cv2.rectangle(frame, *INPUT_RECT.cv_rect())
    frame = cv2.rectangle(frame, *JOYSTICK_RECT.cv_rect())
    # for point in JOYSTICK_RECT.as_grid((3, 3), JOYSTICK_OFFSET):
    #     cv2.circle(frame, point, 3, JOYSTICK_RECT.color, 1)
    # frame = cv2.rectangle(frame, *BUTTON_RECT.cv_rect())
    # for point in BUTTON_RECT.as_grid((4, 3)):
    #     cv2.circle(frame, point, 3, BUTTON_RECT.color, 1)
    frame = cv2.resize(frame, (1280, 720), interpolation=0)
    cv2.imshow("frame", frame)

    key_input = chr(cv2.waitKey() & 0xFF)
    match key_input:
        # joystick inputs
        case "a":
            current_input["left"] = True
            current_input["right"] = False
            break
        case "s":
            current_input["down"] = True
            current_input["up"] = False
            break
        case "d":
            current_input["right"] = True
            current_input["left"] = False
            break
        case " ":
            current_input["up"] = True
            current_input["down"] = False
            break
        case "x":
            # reset stick to neutral
            current_input["up"] = False
            current_input["down"] = False
            current_input["left"] = False
            current_input["right"] = False
            break
        # moves
        case "u":
            current_input["p"] = not current_input["p"]
            break
        case "i":
            current_input["s"] = not current_input["s"]
            break
        case "o":
            current_input["d"] = not current_input["d"]
            break
        case "p":
            current_input["dash"] = not current_input["dash"]
            break
        case "j":
            current_input["k"] = not current_input["k"]
            break
        case "k":
            current_input["hs"] = not current_input["hs"]
            break
        case "l":
            current_input["rc"] = not current_input["rc"]
            break
        # move frame left and right
        case chr(0):
            print("up")
            break
        case chr(1):
            print("down")
            break
        case chr(2):
            print("left")
            break
        case chr(3):
            print("right")
            break


cap.release()
cv2.destroyAllWindows()
