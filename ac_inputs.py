import os
import platform
import sys
from sim_info import info
import configparser

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


def read_map_config(path):
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


def count_attributes(cls):
    return len([attr for attr in dir(cls) if not attr.startswith('__') and not callable(getattr(cls, attr))])


class GetInfo:
    def __init__(self) -> None:
        pass

    @property
    def track_name(self):
        '''
        Name of the track and layout

        [Track, Layout]
        '''
        return [info.static.track, info.static.trackConfiguration][:]

    @property
    def track_name(self):
        '''
        Name of the track and layout.
        Layout will return empty if there are none.

        [Track, Layout]
        '''
        return [info.static.track, info.static.trackConfiguration]

    @property
    def car_name(self):
        '''Model of the car'''
        return info.static.carModel

    @property
    def auto_shifter_on(self):
        '''Returns if auto shifter is enabled'''
        return info.physics.autoShifterOn

    @property
    def wheel_slip(self):
        '''
        Slippage of the wheels (I think above 0.5 is bad)

        [Front Left, Front Right, Rear Left, Rear Right]
        '''
        return info.physics.wheelSlip[:]

    @property
    def steer_angle(self):
        '''
        Angle of steer

        [-1, 1]
        '''
        return info.physics.steerAngle

    @property
    def speed(self):
        '''Speed in KM/h'''
        return info.physics.speedKmh

    @property
    def wheels_offtrack(self):
        '''Returns the number of wheels that are currently off the track.'''
        return info.physics.numberOfTyresOut

    @property
    def car_damage(self):
        '''
        Returns the damage status of the car. 
        (Above 100 stability issues, Around 150 is death)

        [Front, Rear, Left, Right, Highest Damage]
        '''
        return info.physics.carDamage[:]

    @property
    def last_lap(self):
        '''
        Time of the last lap as an integer.

        Last 3 digit is milliseconds, the rest is seconds.

        [SSSSsss]
        '''
        return info.graphics.iLastTime

    @property
    def best_lap(self):
        '''
        Time of the best lap as an integer.

        Last 3 digit is milliseconds, the rest is seconds.

        [SSSSsss]
        '''
        return info.graphics.bestTime

    @property
    def track_completion(self):
        '''
        Returns the completed track ratio from 0 to 1.

        Uses track spline.
        '''
        return info.graphics.normalizedCarPosition

    @property
    def performance_meter(self):
        '''
        Returns the time difference on the current point on track.
        (Negative is better.)
        '''
        return info.physics.performanceMeter

    @property
    def heading(self):
        '''
        Angle of the car

        [-pi, pi]
        '''
        return info.physics.heading

    @property
    def coordinates(self):
        '''Returns [x,y,z]'''
        return info.graphics.carCoordinates[:]


gi = GetInfo()

assetto_corsa_root = 'D:\\SteamLibrary\\steamapps\\common\\assettocorsa\\'
tracks_root = 'content\\tracks\\'

current_track = f'{assetto_corsa_root}{tracks_root}{gi.track_name[0]}'
if gi.track_name[1]:
    current_track = f'{current_track}\\{gi.track_name[1]}'

track_map = f'{current_track}\\map.png'
track_map_data = f'{current_track}\\data\\map.ini'


if __name__ == '__main__':
    print(f'Track: {gi.track_name}')
    print(f'Car: {gi.car_name}')
    print(f'Class attribute count: {count_attributes(gi)}')

    # print(read_map_config(track_map_data))
