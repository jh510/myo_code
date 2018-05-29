
import numpy as np
import pandas as pd
import os
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt


# Reads Myo File and Saves Pickle
def import_myo_csv_file(path,               # Path to CSV File
                        import_file_name,   # Name of CSV File
                        save_file_name='test.pkl'):    # Name to Save (Include Path)
    file_path = os.path.join(path, import_file_name)
    df = pd.read_csv(file_path, low_memory=False) # Low Memory set to False due to large file size
    df[' Arm'] = df[' Arm'].astype('category')    # Set datatype for Arm
    df[' Warm?'] = df[' Warm?'].astype('category')# Set dataype for Warm
    df[' Timestamp'] = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S %f') for x in df[' Timestamp']] # Covert Timestamp to Datetime
    df = fix_myo_arms(df_myo= df) # Fix arm category based on device id
    df.to_pickle(save_file_name)                  # Save Myo Dataframe to Pickle
    return df # Dataframe of Myo Data


# Fixes Arm Column based on Device ID
def fix_myo_arms(df_myo): # Myo Dataframe
    left_id = df_myo.loc[df_myo[' Arm'] == 'left']
    left_id = left_id['Device ID'].iloc[0]
    right_id = df_myo.loc[df_myo[' Arm'] == 'right']
    right_id = right_id['Device ID'].iloc[0]
    df_myo[' Arm'].loc[df_myo['Device ID'] == left_id] = 'left'
    df_myo[' Arm'].loc[df_myo['Device ID'] == right_id] = 'right'
    return df_myo


# Parses Myo dataframe based on arm
def parse_myo_hand(df_myo):
    df_left_hand  = df_myo.loc[df_myo[' Arm'] == 'left']
    df_right_hand = df_myo.loc[df_myo[' Arm'] == 'right']
    return df_left_hand, df_right_hand


# Generates Datetime based on wanted Timestamps
def get_time_from_timestamp(df_myo,             # Myo Dataframe
                            procedure_hour,     # Hour
                            procedure_minute,   # Minute
                            procedure_second    # Second
                            ):
    experiment_date  = df_myo[' Timestamp'].iloc[0]  # Get timestamp from dataframe
    experiment_year  = experiment_date.date().year   # Automatically generate year, month, and day
    experiment_month = experiment_date.date().month
    experiment_day   = experiment_date.date().day
    return_time = pd.Timestamp(experiment_year, experiment_month, experiment_day,
                               procedure_hour, procedure_minute, procedure_second)
    return return_time # Return Timestamps


# Returns dataframe between start and stop times
def parse_procedure(df_myo,     # Myo Dataframe
                    start_time,
                    stop_time):
    df_procedure = df_myo[(df_myo[' Timestamp'] > start_time) & (df_myo[' Timestamp'] < stop_time)]
    return df_procedure # Procedure dataframe


# Plots All EMG Channels by Specified Hand
def generate_emg_plot(df_procedure,         # Dataframe to Plot
                      hand='both',          # Which hand to plot (right, left) or both hands (both)
                      plot_title='Test',
                      fig_name='test.png'): # File Name to Save
    plt.rcParams['figure.figsize'] = [24, 12]
    emg_name_list = [' EMG_1', ' EMG_2', ' EMG_3', ' EMG_4',  # List of EMG Channels
                     ' EMG_5', ' EMG_6', ' EMG_7', ' EMG_8']
    emg_name_index = [0, 1, 2, 3]
    # For Plotting Single Hand
    if (hand == 'right') | (hand == 'left'):
        fig, axes = plt.subplots(nrows=4, ncols=2)
        plt.suptitle(plot_title + ' ' + hand, fontsize=32)
        if hand == 'right':
            tmp, df_procedure = parse_myo_hand(df_procedure)
            del tmp
        else:
            df_procedure, tmp = parse_myo_hand(df_procedure)
            del tmp
        for ax, emg_index in zip(axes, emg_name_index): # Cycle Through Subplots
            emg_name = emg_name_list[emg_index * 2]
            ax[0].set_title(emg_name, fontsize=22)
            ax[0].set_xlabel('Time', fontsize=22)
            ax[0].set_ylabel('EMG Value', fontsize=22)
            ax[0].plot(df_procedure[' Timestamp'], df_procedure[emg_name])
            ax[0].set_ylim(-200, 200)
            emg_name = emg_name_list[emg_index * 2 + 1]
            ax[1].set_title(emg_name, fontsize=22)
            ax[1].set_xlabel('Time', fontsize=22)
            ax[1].set_ylabel('EMG Value', fontsize=22)
            ax[1].plot(df_procedure[' Timestamp'], df_procedure[emg_name])
            ax[1].set_ylim(-200, 200)
            plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                               wspace=None, hspace=0.6)
    # For Plotting Both Hands
    elif hand == 'both':
        fig, axes = plt.subplots(nrows=4, ncols=4)
        plt.suptitle(plot_title + ' Both Hands', fontsize=32)
        df_left, df_right = parse_myo_hand(df_procedure)
        for ax, emg_index in zip(axes, emg_name_index): # Cycle Through Subplots
            emg_name = emg_name_list[emg_index * 2]
            ax[0].set_title('Left Hand: ' + emg_name, fontsize=22)
            ax[0].set_xlabel('Time', fontsize=22)
            ax[0].set_ylabel('EMG Value', fontsize=22)
            ax[0].plot(df_left[' Timestamp'], df_left[emg_name])
            ax[0].set_ylim(-200, 200)
            ax[2].set_title('Right Hand: ' + emg_name, fontsize=22)
            ax[2].set_xlabel('Time', fontsize=22)
            ax[2].set_ylabel('EMG Value', fontsize=22)
            ax[2].plot(df_right[' Timestamp'], df_right[emg_name])
            ax[2].set_ylim(-200, 200)
            emg_name = emg_name_list[emg_index * 2 + 1]
            ax[1].set_title('Left Hand: ' + emg_name, fontsize=22)
            ax[1].set_xlabel('Time', fontsize=22)
            ax[1].set_ylabel('EMG Value', fontsize=22)
            ax[1].plot(df_left[' Timestamp'], df_left[emg_name])
            ax[1].set_ylim(-200, 200)
            ax[3].set_title('Right Hand: ' + emg_name, fontsize=22)
            ax[3].set_xlabel('Time', fontsize=22)
            ax[3].set_ylabel('EMG Value', fontsize=22)
            ax[3].plot(df_right[' Timestamp'], df_right[emg_name])
            ax[3].set_ylim(-200, 200)
            plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                wspace=0.3, hspace=0.6)
    # Error Check for Hand
    else:
        print('Error: Unknown Hand')
        print('Use right, left, or both')
        return 1
    plt.savefig(fig_name, bbox_inches='tight') # Save Figure
    return fig # Return Figure containing Plots


# Plots All IMU Channels by Specified Hand
def generate_imu_plot(df_procedure,         # Dataframe to Plot
                      hand='both',          # Which hand to plot (right, left) or both hands (both)
                      plot_title='Test',
                      fig_name='test.png'): # File Name to Save
    plt.rcParams['figure.figsize'] = [24, 12]
    imu_name_list = [' Acc_X', ' Acc_Y', ' Acc_Z'  # List of IMU Channels
                     ' Gyro_X', ' Gyro_Y', ' Gyro_Z']
    # For Plotting Single Hand
    if (hand == 'right') | (hand == 'left'):
        fig, axes = plt.subplots(nrows=1, ncols=2)
        plt.suptitle(plot_title + ' ' + hand, fontsize=32)
        if hand == 'right':
            tmp, df_procedure = parse_myo_hand(df_procedure)
            del tmp
        else:
            df_procedure, tmp = parse_myo_hand(df_procedure)
            del tmp
        axes[0].set_title('Acceleration', fontsize=22)
        axes[0].set_xlabel('Time', fontsize=22)
        axes[0].set_ylabel('Acceleration Value', fontsize=22)
        axes[0].plot(df_procedure[' Timestamp'], df_procedure[' Acc_X'], 'r')
        axes[0].plot(df_procedure[' Timestamp'], df_procedure[' Acc_Y'], 'b')
        axes[0].plot(df_procedure[' Timestamp'], df_procedure[' Acc_Z'], 'g')
        axes[0].legend(['X', 'Y', 'Z'])
        axes[0].set_ylim(-2, 2)
        axes[1].set_title('Orientation', fontsize=22)
        axes[1].set_xlabel('Time', fontsize=22)
        axes[1].set_ylabel('Orientation', fontsize=22)
        axes[1].plot(df_procedure[' Timestamp'], df_procedure[' Roll'], 'r')
        axes[1].plot(df_procedure[' Timestamp'], df_procedure[' Pitch'], 'b')
        axes[1].plot(df_procedure[' Timestamp'], df_procedure[' Yaw '], 'g')
        axes[1].legend(['Roll', 'Pitch', 'Yaw'])
        axes[1].set_ylim(-3.2, 3.2)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                wspace=None, hspace=0.6)
    # For Plotting Both Hands
    elif hand == 'both':
        fig, axes = plt.subplots(nrows=2, ncols=2)
        plt.suptitle(plot_title + ' Both Hands', fontsize=32)
        indexes = [0,1]
        df_left, df_right = parse_myo_hand(df_procedure)
        for ax, index in zip(axes,indexes): # Cycle Through Subplots
            if index == 0:
                df_hand = df_left
                ax[0].set_title('Left Hand: Acceleration', fontsize=22)
                ax[1].set_title('Left Hand: Orientation', fontsize=22)
            else:
                df_hand = df_right
                ax[0].set_title('Right Hand: Acceleration', fontsize=22)
                ax[1].set_title('Right Hand: Orientation', fontsize=22)
            ax[0].set_xlabel('Time', fontsize=22)
            ax[0].set_ylabel('Acceleration Value', fontsize=22)
            ax[0].plot(df_hand[' Timestamp'], df_hand[' Acc_X'], 'r')
            ax[0].plot(df_hand[' Timestamp'], df_hand[' Acc_Y'], 'b')
            ax[0].plot(df_hand[' Timestamp'], df_hand[' Acc_Z'], 'g')
            ax[0].legend(['X', 'Y', 'Z'])
            ax[0].set_ylim(-2, 2)
            ax[1].set_xlabel('Time', fontsize=22)
            ax[1].set_ylabel('Orientation', fontsize=22)
            ax[1].plot(df_hand[' Timestamp'], df_hand[' Roll'], 'r')
            ax[1].plot(df_hand[' Timestamp'], df_hand[' Pitch'], 'b')
            ax[1].plot(df_hand[' Timestamp'], df_hand[' Yaw '], 'g')
            ax[1].set_ylim(-3.2, 3.2)
            ax[1].legend(['Roll', 'Pitch', 'Yaw'])
            plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                wspace=0.3, hspace=0.6)
    # Error Check for Hand
    else:
        print('Error: Unknown Hand')
        print('Use right, left, or both')
        return 1
    plt.savefig(fig_name, bbox_inches='tight') # Save Figure
    return fig # Return Figure containing Plots


if __name__ == '__main__':
    #test = import_myo_csv_file(path='', import_file_name='emg_p1.csv', save_file_name='p1_data.pkl' ) # Read File
    test = pd.read_pickle('p1_data.pkl')                            # Read Pickle
    t_left,t_right = parse_myo_hand(df_myo=test)                    # Parse Hands
    start = get_time_from_timestamp(df_myo = test, procedure_hour=9,procedure_minute=33, procedure_second=40)
    stop = get_time_from_timestamp(df_myo=test, procedure_hour=9, procedure_minute=35, procedure_second=50)
    procedure = parse_procedure(test, start_time=start, stop_time=stop) # Get Procedure


