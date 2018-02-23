import myo as libmyo; libmyo.init()  # NOQA
from myo.lowlevel.enums import Arm, Pose, WarmupState
from myo import StreamEmg
import time
import sys
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import argparse
import requests

parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
parser.add_argument('-d', '--description', type=str, default='',
                    help='The description of the reconding session')
parser.add_argument('-s', '--store', nargs='*', type=str,
                    default=['file', 'stdout'],
                    choices=['stdout', 'file', 'local', 'dev', 'prod'],
                    help='Where should results be stored?')
parser.add_argument('-e',action='store', default='emg_test.csv',
                    type=argparse.FileType('a'), dest='f_emg',
                    help='EMG Output file path if outputting to a file via --store file')
parser.add_argument('-i', action='store', default='imu_test.csv',
                    type=argparse.FileType('a'), dest='f_imu',
                    help='IMU Output file path if outputting to a file via --store file')
parser.add_argument('-t', '--timedelay', type=int ,default=10000000,
                    help='Time to run the data collection for')  
args = parser.parse_args()

MYO_MAKE_MODEL = 'Thalmic Labs Myo 1'


class MyoMotionData:

    def __init__(self):
        self.orientation = {'w': 0, 'x': 0, 'y': 0, 'z': 0}
        self.acceleration = {'x': 0, 'y': 0, 'z': 0}
        self.gyroscope = {'x': 0, 'y': 0, 'z': 0}
        self.pose = Pose.rest.name
        self.locked = False
        self.rssi = 0
        self.emg = [0, 0, 0, 0, 0, 0, 0, 0]
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.time = None

    def toCSV(self):
        csv_ori = ','.join(str(v) for v in self.orientation.values()) + ','
        csv_acc = ','.join(str(v) for v in self.acceleration.values()) + ','
        csv_gyro = ','.join(str(v) for v in self.gyroscope.values()) + ','
        csv_emg = ','.join(str(v) for v in self.emg) + ','
        csv_time = str(self.time) + ','
        csv_pose = str(self.pose) + ','
        csv_lock = str(self.locked) + ','
        csv_rssi = str(self.rssi) + ','
        csv_roll = str(self.roll) + ','
        csv_pitch = str(self.pitch) + ','
        csv_yaw = str(self.yaw) + '\n'
        return csv_time + csv_ori + csv_acc + csv_gyro + csv_pose + csv_emg + csv_lock + csv_rssi + csv_roll + csv_pitch + csv_yaw 
class MyoState:
    def __init__(self, device_id):
        self.device_id = device_id
        self.device_make_model = MYO_MAKE_MODEL
        self.motiondata = MyoMotionData()
        self.warm = WarmupState.unknown.name
        self.arm = Arm.unknown.name
        self.sync = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    
    def toCSV(self):
        return str(self.device_id) + ',' + str(self.warm) + ',' + str(self.sync) + ',' + str(self.arm) + ',' + self.motiondata.toCSV()

 
class Listener(libmyo.DeviceListener):

    def __init__(self):
        super(Listener, self).__init__()
        self.samples = 0
        self.myo_states = {}
        self.motiondata = {}
        for store in args.store:
            if store == 'file':
                header = 'Device ID, Warm?, Sync, Arm, Timestamp, Orientation_W, Orientation_X, Orientation_Y, Orientation_Z, Acc_X, Acc_Y, Acc_Z, Gyro_X, Gyro_Y, Gyro_Z, Pose, EMG_1, EMG_2, EMG_3, EMG_4, EMG_5, EMG_6, EMG_7, EMG_8,Locked, RSSI, Roll, Pitch, Yaw \n'
                args.f_emg.write(header)
                args.f_imu.write(header)        

    def emg_output(self, myo):
        ""
        for store in args.store:
            if store == 'file':
                args.f_emg.write(self.myo_states[myo.value].toCSV())
            if store == 'stdout':
                print(self.myo_states[myo.value].toCSV())
        #state.motiondata = MyoMotionData()

    def imu_output(self,myo):
        for store in args.store:
            if store == 'file':
                args.f_imu.write(self.myo_states[myo.value].toCSV())
            if store == 'stdout':
                x = 1
    
    # Time Stamp Format: ##########.###### -> UTC time. Microseconds  
    def on_connect(self, myo, timestamp, firmware_version):
        myo.vibrate('short') # Sanity Check for Connection
        myo.set_stream_emg(libmyo.StreamEmg.enabled) # Enable EMG Streaming
        myo.request_rssi()
        myo.request_battery_level()
        if myo.value not in self.myo_states:
            self.myo_states[myo.value] = MyoState(myo.value)
            self.motiondata[myo.value] = []

    def on_rssi(self, myo, timestamp, rssi):
        if rssi:
            self.myo_states[myo.value].rssi = rssi

    def on_pose(self, myo, timestamp, pose):
        if pose:
            self.myo_states[myo.value].pose = pose
                
    def on_emg_data(self, myo, timestamp, emg):
        UTC = datetime.fromtimestamp(int(timestamp/1000000)).strftime('%Y-%m-%d %H:%M:%S')
        uSec = timestamp%10000000
        self.myo_states[myo.value].motiondata.emg = emg
        self.myo_states[myo.value].motiondata.time = str(UTC) + ' '  + str(uSec)
        self.emg_output(myo)
        self.samples = self.samples + 1
        
    def on_orientation_data(self, myo, timestamp, orientation):
        UTC = datetime.fromtimestamp(int(timestamp/1000000)).strftime('%Y-%m-%d %H:%M:%S')
        uSec = timestamp%10000000
        self.myo_states[myo.value].motiondata.orientation = {
                'w': orientation.w,
                'x': orientation.x,
                'y': orientation.y,
                'z': orientation.z,
            }
        self.myo_states[myo.value].motiondata.roll = orientation.roll
        self.myo_states[myo.value].motiondata.pitch = orientation.pitch
        self.myo_states[myo.value].motiondata.yaw = orientation.yaw
        self.myo_states[myo.value].motiondata.time = str(UTC) + ' '  + str(uSec)
        self.imu_output(myo)
        
    def on_accelerometor_data(self, myo, timestamp, acceleration):
        UTC = datetime.fromtimestamp(int(timestamp/1000000)).strftime('%Y-%m-%d %H:%M:%S')
        uSec = timestamp%10000000
        self.myo_states[myo.value].motiondata.acceleration = {
                'x': acceleration.x,
                'y': acceleration.y,
                'z': acceleration.z,
            }
        self.myo_states[myo.value].motiondata.time = str(UTC) + ' '  + str(uSec)


    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        if gyroscope:
            self.myo_states[myo.value].motiondata.gyroscope = {
                'x': gyroscope.x,
                'y': gyroscope.y,
                'z': gyroscope.z,
            }

    def on_unlock(self, myo, timestamp):
        self.myo_states[myo.value].motiondata.locked = False

    def on_lock(self, myo, timestamp):
        self.myo_states[myo.value].motiondata.locked = True

    def on_disconnect(self, myo, timestamp):
        print(self.samples)

    def on_arm_sync(self, myo, timestamp, arm, x_direction, rotation,
                    warmup_state):
        """
        Called when a Myo armband and an arm is synced.
        """
        self.myo_states[myo.value].sync = True
        self.myo_states[myo.value].warm = warmup_state.name
        self.myo_states[myo.value].arm = arm.name

    def on_arm_unsync(self, myo, timestamp):
        """
        Called when a Myo armband and an arm is unsynced.
        """
        self.myo_states[myo.value].sync = False
        self.myo_states[myo.value].arm = Arm.unknown.name

    def on_battery_level_received(self, myo, timestamp, level):
        """
        Called when the requested battery level received.
        """

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        """
        Called when the warmup completed.
        """
        self.myo_states[myo.value].warm = True


if __name__ == '__main__':
    print("Hello World")
    feed = libmyo.Feed()
    hub = libmyo.Hub()
    hub.set_locking_policy(libmyo.LockingPolicy.none)
    listener = Listener()
    hub.run(100,listener)
    t_d = time.time() + args.timedelay
    try:
        while hub.running and time.time() < t_d:
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nQuitting...")
    finally:
        print("Shutting Down Hub...")
        print(1/(args.timedelay/listener.samples))
        hub.shutdown()  # !! crucial
    while hub.running:
        time.sleep(0.25)
    time.sleep(2)
    args.f_emg.close()
    args.f_imu.close()
    print("Myo Data Collection Shutting Down")
