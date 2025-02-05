import tkinter as tk


class AreaSelector:
    def __init__(self, master):
        self.master = master
        self.master.attributes("-fullscreen", True)
        self.master.attributes("-alpha", 0.5)
        self.master.bind("<ButtonPress-1>", self.start_selection)
        self.master.bind("<B1-Motion>", self.update_selection)
        self.master.bind("<ButtonRelease-1>", self.finish_selection)

        self.selection_rect = None
        self.start_x = 0
        self.start_y = 0

    def start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.selection_rect = self.master.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def update_selection(self, event):
        self.master.coords(
            self.selection_rect, self.start_x, self.start_y, event.x, event.y
        )

    def finish_selection(self, event):
        x1, y1, x2, y2 = self.master.coords(self.selection_rect)
        self.master.destroy()
        print("Selected area:", x1, y1, x2, y2)


if __name__ == "__main__":
    root = tk.Tk()
    app = AreaSelector(root)
    root.mainloop()
