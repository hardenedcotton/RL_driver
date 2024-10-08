import configparser
import math
import os
import platform
import sys
import time
import tkinter as tk
import numpy as np

from PIL import Image, ImageOps, ImageTk

from sim_info import info

# print(info.graphics.tyreCompound, info.physics.rpms, info.static.playerNick)

if platform.architecture()[0] == "64bit":
    sysdir = "stdlib64"
else:
    sysdir = "stdlib"

marker_file = "init_done.marker"

if not os.path.exists(marker_file):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), sysdir))
    os.environ['PATH'] = os.environ['PATH'] + ";."

    with open(marker_file, "w") as f:
        f.write("This system is initialized.")

    print("Initialization completed and marker file created.")
else:
    print("Initialization already done. Skipping setup.")


def count_info_attributes(cls):
    return [attr for attr in dir(cls) if not attr.startswith('__') and not callable(getattr(cls, attr))]


class GetInfo:
    def __init__(self) -> None:
        current_track = self.get_track_attributes()
        self.map_data = current_track['map_data']
        self.map_image = current_track['map_image']

    @ property
    def track_name(self):
        '''
        Name of the track and layout.
        Layout will return empty if there are none.

        [Track, Layout]
        '''
        return [info.static.track, info.static.trackConfiguration]

    @ property
    def car_name(self):
        '''Model of the car'''
        return info.static.carModel

    @ property
    def auto_shifter_on(self):
        '''Returns if auto shifter is enabled'''
        return info.physics.autoShifterOn

    @ property
    def wheel_slip(self):
        '''
        Slippage of the wheels (I think above 0.5 is bad)

        [Front Left, Front Right, Rear Left, Rear Right]
        '''
        return info.physics.wheelSlip[:]

    @ property
    def steer_angle(self):
        '''
        Angle of steer

        [-1, 1]
        '''
        return info.physics.steerAngle

    @ property
    def speed(self):
        '''Speed in KM/h'''
        return info.physics.speedKmh

    @ property
    def wheels_offtrack(self):
        '''Returns the number of wheels that are currently off the track.'''
        return info.physics.numberOfTyresOut

    @ property
    def car_damage(self):
        '''
        Returns the damage status of the car.
        (Above 100 stability issues, Around 150 is death)

        [Front, Rear, Left, Right, Highest Damage]
        '''
        return info.physics.carDamage[:]

    @ property
    def last_lap(self):
        '''
        Time of the last lap as an integer.

        Last 3 digit is milliseconds, the rest is seconds.

        [SSSSsss]
        '''
        return info.graphics.iLastTime

    @ property
    def best_lap(self):
        '''
        Time of the best lap as an integer.

        Last 3 digit is milliseconds, the rest is seconds.

        [SSSSsss]
        '''
        return info.graphics.bestTime

    @ property
    def track_completion(self):
        '''
        Returns the completed track ratio from 0 to 1.

        Uses track spline.
        '''
        return info.graphics.normalizedCarPosition

    @ property
    def performance_meter(self):
        '''
        Returns the time difference on the current point on track.
        (Negative is better.)
        '''
        return info.physics.performanceMeter

    @ property
    def heading(self):
        '''
        Angle of the car

        [-pi, pi]
        '''
        return info.physics.heading

    @ property
    def coordinates(self):
        '''Returns [x,y,z]'''
        return info.graphics.carCoordinates[:]

    def gauss(self, n, sigma=50, range=(0, 1)):
        r = np.arange(-int(n/2), int(n/2)+1)
        result = np.array([1 / (sigma * np.sqrt(2*np.pi)) *
                          np.exp(-float(x)**2/(2*sigma**2)) for x in r])
        result = (result - min(result)) / (max(result) - min(result))
        if range != (0, 1):
            result = result * (range[1] - range[0]) + range[0]
        return result

    def read_map_config(self, path):
        config = configparser.ConfigParser()

        # Read the .ini file
        config.read(path)
        parameters = {}
        if 'PARAMETERS' in config:
            for key in config['PARAMETERS']:
                value = config.get('PARAMETERS', key)
                if value.isdigit():
                    parameters[key] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    parameters[key] = float(value)
                else:
                    parameters[key] = value

        return parameters

    def get_track_attributes(self):
        assetto_corsa_root = 'D:\\SteamLibrary\\steamapps\\common\\assettocorsa\\'
        tracks_root = 'content\\tracks\\'

        current_track = f'{assetto_corsa_root}{tracks_root}{self.track_name[0]}'
        if self.track_name[1]:
            current_track = f'{current_track}\\{self.track_name[1]}'

        track_map_path = f'{current_track}\\map.png'
        map_data_path = f'{current_track}\\data\\map.ini'
        map_data = self.read_map_config(map_data_path)
        map_image = Image.open(track_map_path)

        map_ = {'map_data': map_data,
                'map_image': map_image}

        return map_

    prev_sensor_mean_angle = 0

    def all_sensors(self):
        return self.get_sensors()
    sensors = []
    triggered_sensors = []

    def get_sensors(self, min_sensor_distance=10, min_sensor_count=5, FOV_degrees=90):
        coords = self.coordinates
        heading = self.heading

        FOV_radians = np.radians(FOV_degrees)

        sensor_distance = max(min_sensor_distance *
                              self.speed/50, min_sensor_distance)

        sensor_count = max(
            int(np.ceil(min_sensor_count * sensor_distance/25) // 2 * 2 + 1), min_sensor_count)

        angles = np.linspace(-FOV_radians/2, FOV_radians/2,
                             sensor_count) + np.radians(90)  # offset is due to heading being off by -90 degrees
        # FIXME Sensor drawer has a problem, i shouldn't really offset it
        # angles = np.arcsin(angles) * FOV_radians / 2
        # distance_offset = self.gauss(
        #     sensor_count, 500/self.speed, (.25, 1))
        distance_offset = [1]*sensor_count
        # FIXME The top of the gaussian is sparse, fix it
        #
        sensors = []
        triggered_sensors = [sensor_distance]
        triggered_sensors_gauss = []
        for idx, angle in enumerate(angles):
            sensor_x = self.map_data['x_offset'] + \
                coords[0] + sensor_distance * distance_offset[idx] * \
                np.cos(heading + angle) * self.map_data['scale_factor']

            sensor_z = self.map_data['z_offset'] + \
                coords[2] + sensor_distance * distance_offset[idx] * \
                np.sin(heading + angle) * self.map_data['scale_factor']
            is_sensor_on_track = self.is_sensor_on_track(
                sensor_x, sensor_z)

            sensors.append((sensor_x, sensor_z, angle))
            gausser = self.gauss(sensor_count, sensor_count)

            if is_sensor_on_track:
                triggered_sensors.append(angle)
                triggered_sensors_gauss.append(angle*gausser[idx])

        sensor_mean_angle = np.degrees(
            np.mean(triggered_sensors[1:]))-90
        # FIXME dot appears on the wrong side with gauss

        # sensor_mean_angle = np.degrees(
        #     np.mean(triggered_sensors_gauss[1:]))-90

        if np.isnan(sensor_mean_angle):
            sensor_mean_angle = self.prev_sensor_mean_angle
        self.prev_sensor_mean_angle = sensor_mean_angle

        triggered_sensors.append(sensor_mean_angle)
        return sensors, triggered_sensors

    def is_sensor_on_track(self, x, z):
        # Check if coordinates are within the bounds of the map image
        if 0 <= int(x) < self.map_image.width and 0 <= int(z) < self.map_image.height:
            try:
                pixel_color = self.map_image.getpixel((int(x), int(z)))
                alpha_value = pixel_color[3]
                return True if alpha_value == 255 else False

            except Exception as e:
                print(f"Error checking pixel color at ({x}, {z}):", e)
                return False
        else:
            return False


gi = GetInfo()

current_track = gi.get_track_attributes()


if __name__ == '__main__':
    print(f'Track: {gi.track_name}')
    print(f'Car: {gi.car_name}')
    print(f'Class attribute count: {len(count_info_attributes(gi))}')
    print(current_track['map_data'])
