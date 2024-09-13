import math
import tkinter as tk

import numpy as np
from PIL import Image, ImageTk

from ac_inputs import GetInfo


class MinimapApp:
    def __init__(self, root):
        self.gi = GetInfo()
        self.root = root
        self.root.title("Minimap")
        self.canvas = tk.Canvas(
            root, width=self.gi.map_data['width'], height=self.gi.map_data['height'])
        self.canvas.pack()

        self.map_image_tk = ImageTk.PhotoImage(self.gi.map_image)
        self.map_image_on_canvas = self.canvas.create_image(
            0, 0, anchor=tk.NW, image=self.map_image_tk)

        self.arrow_image = Image.open("assets/arrow32.png")
        self.arrow_image_tk = ImageTk.PhotoImage(self.arrow_image)
        self.arrow_on_canvas = None

        self.sensors_on_canvas = []
        self.sensor_info = self.canvas.create_text(
            50, 20, anchor='nw', text='', font=("Arial", 12), fill="black")

        # self.triggered_sensors = [0]*5

        self.display_data = self.create_data_on_canvas()
        self.update_minimap()

    def draw_car(self):
        if self.arrow_on_canvas:
            self.canvas.delete(self.arrow_on_canvas)

        player_x = self.gi.map_data['x_offset'] + \
            self.gi.coordinates[0] * self.gi.map_data['scale_factor']
        player_z = self.gi.map_data['z_offset'] + \
            self.gi.coordinates[2] * self.gi.map_data['scale_factor']

        arrow_image_rotated = self.arrow_image.rotate(
            (math.degrees(-self.gi.heading)+180), expand=True)
        self.arrow_image_tk = ImageTk.PhotoImage(arrow_image_rotated)

        self.arrow_on_canvas = self.canvas.create_image(
            player_x, player_z, anchor=tk.CENTER, image=self.arrow_image_tk)

    def draw_sensors(self, all_sensors, triggered_sensors):
        for sensor in self.sensors_on_canvas:
            self.canvas.delete(sensor)
        self.sensors_on_canvas.clear()

        for sensor in all_sensors:
            sensor_x = sensor[0]
            sensor_z = sensor[1]
            if sensor[2] in triggered_sensors[1:-1]:  # True if sensor is in track
                sensor_color = "green"

            else:
                sensor_color = "red"

            sensor_on_canvas = self.canvas.create_oval(
                sensor_x - 3, sensor_z - 3, sensor_x + 3, sensor_z + 3, fill=sensor_color
            )
            self.sensors_on_canvas.append(sensor_on_canvas)

    def create_data_on_canvas(self):

        self.data_text_items = []
        y_offset = 200  # Starting y-position

        data = {
            'sensor_distance': 0,
            'sensor_mean_angle': 0,
            'performance_meter': self.gi.performance_meter,
            'speed': self.gi.speed,
            'steer_angle': self.gi.steer_angle,
            'track_completion': self.gi.track_completion,
            'wheel_slip_FL': self.gi.wheel_slip[0],
            'wheel_slip_FR': self.gi.wheel_slip[1],
            'wheel_slip_RL': self.gi.wheel_slip[2],
            'wheel_slip_RR': self.gi.wheel_slip[3],
            'wheels_offtrack': self.gi.wheels_offtrack}

        for i, key in enumerate(data.keys()):
            text_item = self.canvas.create_text(
                200, y_offset + i * 20, anchor='w', text=f"{key}: {data[key]}", font=("Arial", 12), fill="black")
            self.data_text_items.append(text_item)

    def update_data_on_canvas(self, triggered_sensors):
        sensor_distance = triggered_sensors[0]
        sensor_mean_angle = triggered_sensors[-1]

        data = {
            'sensor_distance': sensor_distance,
            'sensor_mean_angle': sensor_mean_angle,
            'performance_meter': self.gi.performance_meter,
            'speed': self.gi.speed,
            'steer_angle': self.gi.steer_angle,
            'track_completion': self.gi.track_completion,
            'wheel_slip_FL': self.gi.wheel_slip[0],
            'wheel_slip_FR': self.gi.wheel_slip[1],
            'wheel_slip_RL': self.gi.wheel_slip[2],
            'wheel_slip_RR': self.gi.wheel_slip[3],
            'wheels_offtrack': self.gi.wheels_offtrack}

        for i, (key, value) in enumerate(data.items()):
            # Update each text item with the new value
            self.canvas.itemconfig(
                self.data_text_items[i], text=f"{key}: {value}")

    def update_minimap(self):

        all_sensors, triggered_sensors = self.gi.get_sensors(
            min_sensor_distance=10, min_sensor_count=5, FOV_degrees=90)

        self.draw_car()
        self.draw_sensors(all_sensors, triggered_sensors)
        self.update_data_on_canvas(triggered_sensors)

        self.root.after(50, self.update_minimap)


# gi = GetInfo()

if __name__ == '__main__':
    root = tk.Tk()
    app = MinimapApp(root)
    root.mainloop()
