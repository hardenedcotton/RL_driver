import vgamepad as vg


class Gamepad():
    def __init__(self) -> None:
        self.gamepad = vg.VX360Gamepad()

    def apply_input(self, steer: float, gas: float, brake: float):
        assert steer >= -1 or steer <= 1, 'Steering out of bounds [-1, 1]'
        assert gas >= 0 or gas <= 1, 'Acceleration out of bounds [0, 1]'
        assert brake >= 0 or brake <= 1, 'Brake out of bounds [0, 1]'

        self.gamepad.left_joystick_float(steer, 0)   # Steering      [-1, 1]
        self.gamepad.left_trigger_float(gas)         # Acceleration  [0 , 1]
        self.gamepad.right_trigger_float(brake)      # Brake         [0 , 1]
        self.gamepad.update()                        # Submit input
