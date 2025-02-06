import pyautogui
import cv2
import numpy as np
import keyboard
import time
import numpy as np
from windows_capture import WindowsCapture, Frame, InternalCaptureControl

DEBUG = False
target_fps = 60
frame_size = (426, 240)

# Output video
out = cv2.VideoWriter(
    "output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), target_fps, frame_size
)

# Part of the screen to capture
# Every Error From on_closed and on_frame_arrived Will End Up Here
capture = WindowsCapture(
    cursor_capture=False,
    draw_border=None,
    monitor_index=1,
    window_name=None,
)
# frame delta as 100ns intervals
frame_delta = (1_000_000_000 / 100) / target_fps

# timespan as 100ns intervals
data = {"last_frame_timespan": 0, "prev_timespan": -1}
if DEBUG:
    print("frame_delta:", frame_delta)


@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    if data["prev_timespan"] < 0:
        data["prev_timespan"] = frame.timespan
    prev_timespan = data["prev_timespan"]
    delta = frame.timespan - prev_timespan
    data["prev_timespan"] = frame.timespan
    data["last_frame_timespan"] += delta

    if DEBUG:
        delta_ms = delta * 100 / 1_000_000
        last_frame_timespan_ms = data["last_frame_timespan"] * 100 / 1_000_000
        print(
            f"d: {delta_ms} ms   lf: {last_frame_timespan_ms}   fd: {frame_delta * 100 / 1_000_000}"
        )

    if data["last_frame_timespan"] >= frame_delta:
        # Save The Frame As An Image To The Specified Path
        frame = cv2.cvtColor(frame.frame_buffer, cv2.COLOR_RGBA2RGB)
        frame = cv2.resize(frame, frame_size)

        while data["last_frame_timespan"] >= frame_delta:
            data["last_frame_timespan"] -= frame_delta
            if DEBUG:
                print("  cap")
            out.write(frame)

    # Gracefully stop capture thread
    if keyboard.is_pressed("n"):
        out.release()
        capture_control.stop()
        cv2.destroyAllWindows()


# Called When The Capture Item Closes Usually When The Window Closes, Capture
# Session Will End After This Function Ends
@capture.event
def on_closed():
    print("Capture Session Closed")


capture.start()
