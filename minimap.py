import tkinter as tk
import math
from PIL import Image, ImageTk
from ac_inputs import GetInfo, get_track_attributes


class MinimapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimap")
        self.canvas = tk.Canvas(
            root, width=map_data['width'], height=map_data['height'])
        self.canvas.pack()

        self.map_image_tk = ImageTk.PhotoImage(map_image)
        self.map_image_on_canvas = self.canvas.create_image(
            0, 0, anchor=tk.NW, image=self.map_image_tk)

        self.arrow_image = Image.open("assets/arrow32.png")
        self.arrow_image_tk = ImageTk.PhotoImage(self.arrow_image)
        self.arrow_on_canvas = None

        self.update_minimap()

    def update_minimap(self):
        # Clear the previous arrow
        if self.arrow_on_canvas:
            self.canvas.delete(self.arrow_on_canvas)

        # Get player coordinates and heading
        coords = gi.coordinates
        heading = gi.heading

        # Convert player coordinates to canvas coordinates
        player_x = map_data['x_offset'] + coords[0] * map_data['scale_factor']
        player_z = map_data['z_offset'] + coords[2] * map_data['scale_factor']

        # Calculate rotation for arrow
        arrow_image_rotated = self.arrow_image.rotate(
            math.degrees(-heading), expand=True)
        self.arrow_image_tk = ImageTk.PhotoImage(arrow_image_rotated)

        # Place the arrow on the canvas
        self.arrow_on_canvas = self.canvas.create_image(
            player_x, player_z, anchor=tk.CENTER, image=self.arrow_image_tk)

        # Schedule next update
        self.root.after(50, self.update_minimap)  # Update every 0.05 seconds


gi = GetInfo()
map_data = get_track_attributes()['map_data']
map_image = get_track_attributes()['map_image']

if __name__ == '__main__':
    root = tk.Tk()
    app = MinimapApp(root)
    root.mainloop()
