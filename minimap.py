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

        self.sensors_on_canvas = []

        self.update_minimap()

    def update_minimap(self):
        if self.arrow_on_canvas:
            self.canvas.delete(self.arrow_on_canvas)
        for sensor in self.sensors_on_canvas:
            self.canvas.delete(sensor)
        self.sensors_on_canvas.clear()

        coords = gi.coordinates
        heading = gi.heading

        player_x = map_data['x_offset'] + coords[0] * map_data['scale_factor']
        player_z = map_data['z_offset'] + coords[2] * map_data['scale_factor']

        arrow_image_rotated = self.arrow_image.rotate(
            math.degrees(-heading), expand=True)
        self.arrow_image_tk = ImageTk.PhotoImage(arrow_image_rotated)

        self.arrow_on_canvas = self.canvas.create_image(
            player_x, player_z, anchor=tk.CENTER, image=self.arrow_image_tk)

        sensors = gi.get_sensors(
            min_sensor_distance=10, min_sensor_count=15, FOV_degrees=180)

        for sensor in sensors:
            sensor_x = map_data['x_offset'] + \
                sensor[0] * map_data['scale_factor']
            sensor_z = map_data['z_offset'] + \
                sensor[1] * map_data['scale_factor']

            if self.is_on_track(sensor_x, sensor_z):
                sensor_color = "green"
            else:
                sensor_color = "red"

            sensor_on_canvas = self.canvas.create_oval(
                sensor_x - 3, sensor_z - 3, sensor_x + 3, sensor_z + 3, fill=sensor_color
            )
            self.sensors_on_canvas.append(sensor_on_canvas)

        self.root.after(50, self.update_minimap)

    def is_on_track(self, x, z):
        # Check if coordinates are within the bounds of the map image
        if 0 <= int(x) < map_image.width and 0 <= int(z) < map_image.height:
            try:

                pixel_color = map_image.getpixel((int(x), int(z)))

                alpha_value = pixel_color[3]

                if alpha_value == 255:
                    return True
                else:
                    return False

            except Exception as e:
                print(f"Error checking pixel color at ({x}, {z}):", e)
                return False
        else:
            return False


gi = GetInfo()
map_data = get_track_attributes()['map_data']
map_image = get_track_attributes()['map_image']

if __name__ == '__main__':
    root = tk.Tk()
    app = MinimapApp(root)
    root.mainloop()
