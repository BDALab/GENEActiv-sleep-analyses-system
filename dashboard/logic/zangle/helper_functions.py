import logging
import math

from dashboard.logic.machine_learning import settings

logger = logging.getLogger(__name__)


# Function to compute angle according to van Hees method
def f_comp_angle(row):
    return math.degrees(math.atan(row['z axis [g]'] / ((row['x axis [g]'] ** 2 + row['y axis [g]'] ** 2) ** 0.5)))


# function to cut start of the DataFrames to match in time
def f_cut_start(df, df_PSG, csv_object, ps_object):
    # Match start
    # If ACG starts earlier than PSG -> cut start of ACG
    if df['time stamp'][0] < df_PSG['Time [hh:mm:ss]'][0]:
        # Find df index where time matches
        try:
            idx_start = df[(df['time stamp'].dt.day == df_PSG['Time [hh:mm:ss]'].dt.day[0]) &
                           (df['time stamp'].dt.hour == df_PSG['Time [hh:mm:ss]'].dt.hour[0]) &
                           (df['time stamp'].dt.minute == df_PSG['Time [hh:mm:ss]'].dt.minute[0]) &
                           (df['time stamp'].dt.second == df_PSG['Time [hh:mm:ss]'].dt.second[0])].index[0]
            # Drop df from 0 to idx_start
            df.drop(df.index[0:idx_start], inplace=True)
        except:
            logger.error(f"ACG {csv_object.filename} has no identical time stamp start with PSG {ps_object.filename}")
    # Else cut start of PSG
    else:
        # Find df_PSG index where time matches
        try:
            idx_start = df_PSG[(df['time stamp'].dt.day == df_PSG['Time [hh:mm:ss]'].dt.day[0]) &
                               (df['time stamp'].dt.hour[0] == df_PSG['Time [hh:mm:ss]'].dt.hour) &
                               (df['time stamp'].dt.minute[0] == df_PSG['Time [hh:mm:ss]'].dt.minute) &
                               (df['time stamp'].dt.second[0] == df_PSG['Time [hh:mm:ss]'].dt.second)].index[0]
            # Drop df_PSG from 0 to idx_start
            df_PSG.drop(df_PSG.index[0:idx_start], inplace=True)
        except:
            logger.error(f"PSG {ps_object.filename} has no identical time stamp start with ACG {csv_object.filename}")

    return


# function to cut end of the DataFrames to match in time
def f_cut_end(df, df_PSG, csv_object, ps_object):
    df.reset_index(inplace=True, drop=True)
    df_PSG.reset_index(inplace=True, drop=True)
    df_PSG_len = len(df_PSG.index) - 1
    df_len = len(df.index) - 1

    # Match end
    # If df ends earlier than df_PSG -> cut end of df_PSG
    if df['time stamp'][df_len] < df_PSG['Time [hh:mm:ss]'][df_PSG_len]:
        try:
            idx_end = df_PSG[(df['time stamp'].dt.hour[df_len] == df_PSG['Time [hh:mm:ss]'].dt.hour) &
                             (df['time stamp'].dt.minute[df_len] + 1 == df_PSG['Time [hh:mm:ss]'].dt.minute)].index[
                0]  # + 1 min
            # Drop df_PSG from df end to end
            df_PSG.drop(df_PSG.index[idx_end:(len(df_PSG.index))], inplace=True)
        except:
            logger.error(f"ACG {csv_object.filename} has no identical time stamp end with PSG {ps_object.filename}")
    # Else cut end of df
    else:
        try:
            idx_end = df[(df['time stamp'].dt.day == (df_PSG['Time [hh:mm:ss]'].dt.day[df_PSG_len])) &
                         (df['time stamp'].dt.hour == df_PSG['Time [hh:mm:ss]'].dt.hour[df_PSG_len]) &
                         (df['time stamp'].dt.minute == df_PSG['Time [hh:mm:ss]'].dt.minute[df_PSG_len]) &
                         (df['time stamp'].dt.second == df_PSG['Time [hh:mm:ss]'].dt.second[df_PSG_len])].index[0]
            # Drop df from df_PSG end to end
            df.drop(df.index[idx_end:(len(df.index))], inplace=True)
        except:
            logger.error(f"PSG {ps_object.filename} has no identical time stamp end with ACG {csv_object.filename}")

    return


# Function to decide sleep & wake epochs, first sleep time and sleep end time, if the accelerometer has been worn,
# sleep fragmentation and number of awakenings > 5, parameters: window of inactivity to decide SO, window to decide
# sleep after SO (both in seconds / 5 ... 5s resampling), angle threshold and ACG dataframe
def f_inactiv(first_threshold, time_window, angle, df):
    counter = 0
    first_sleep = False

    for index, value in df['abs_angle_change'].items():
        counter += 1

        # Angle change > angle -> woke up
        if value > angle:
            counter = 0
            # After first sleep
        elif (counter > time_window) & first_sleep:
            # Write S to state
            df.loc[index, settings.prediction_name] = "S"
        # First sleep
        elif (counter > first_threshold) & ~first_sleep:
            # Write S to state
            df.loc[index, settings.prediction_name] = "S"
            first_sleep = True