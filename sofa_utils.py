import os
import numpy as np
import pysofaconventions as pysofa
from netCDF4 import Dataset
import time

def create_srir_sofa(
    filepath,
    rirs,
    source_pos,
    mic_pos,
    db_name="Default_db",
    room_name="Room_name",
    listener_name="foa",
    sr=24000,
    comment="N/A",
):
    """
    Creates a SOFA file with spatial room impulse response data.

    This function generates a SOFA (Spatially Oriented Format for Acoustics) file to store spatial room impulse responses (SRIRs).
    It includes metadata about the recording environment, such as source and microphone positions, room characteristics, and listener details.

    Parameters:
        filepath (str): The path where the SOFA file will be created or overwritten.
        rirs (numpy.array): A 3D array of room impulse responses (measurements x receivers x samples).
        source_pos (numpy.array): The positions of the sound sources (measurements x coordinates).
        mic_pos (numpy.array): The positions of the microphones/listeners (measurements x coordinates).
        db_name (str, optional): Name of the database. Default is "Default_db".
        room_name (str, optional): Name of the room. Default is "Room_name".
        listener_name (str, optional): Name of the listener. Default is "foa".
        sr (int, optional): Sampling rate of the impulse responses. Default is 24000 Hz.
        comment (str, optional): Additional comments. Default is "N/A".

    Returns:
        None: The function does not return a value. It creates or overwrites a SOFA file at the specified filepath.
    """
    M = rirs.shape[0] #number of measurements ie number of source positions
    R = rirs.shape[1] #number of receivers ie number of mic capsules
    N = rirs.shape[2] #number of samples per measurement (per RIR)
    E = 1 #Number of emitters per measurement (1 per measurement)
    I = 1 #Singleton dimesion, always 1
    C = 3 #Coordinate dimension, always 3

    assert rirs.shape == (M, R, N)
    assert source_pos.shape == (M, C)

    # Need to delete it first if file already exists
    if os.path.exists(filepath):
        print(f"Overwriting {filepath}")
        os.remove(filepath)
    rootgrp = Dataset(filepath, "w", format="NETCDF4")

    # ----------Required Attributes----------#

    rootgrp.Conventions = "SOFA"
    rootgrp.Version = "2.1"
    rootgrp.SOFAConventions = "SingleRoomSRIR"
    rootgrp.SOFAConventionsVersion = "1.0"
    rootgrp.APIName = "pysofaconventions"
    rootgrp.APIVersion = "0.1.5"
    rootgrp.AuthorContact = "chris.ick@nyu.edu"
    rootgrp.Organization = "Music and Audio Research Lab - NYU"
    rootgrp.License = "Use whatever you want"
    rootgrp.DataType = "FIR"
    rootgrp.DateCreated = time.ctime(time.time())
    rootgrp.DateModified = time.ctime(time.time())
    rootgrp.Title = db_name + " - " + room_name
    rootgrp.RoomType = "shoebox"
    rootgrp.DatabaseName = db_name
    rootgrp.ListenerShortName = listener_name
    rootgrp.RoomShortName = room_name
    rootgrp.Comment = comment

    # ----------Required Dimensions----------#

    rootgrp.createDimension("M", M)
    rootgrp.createDimension("N", N)
    rootgrp.createDimension("E", E)
    rootgrp.createDimension("R", R)
    rootgrp.createDimension("I", I)
    rootgrp.createDimension("C", C)

    # ----------Required Variables----------#
    listenerPositionVar = rootgrp.createVariable("ListenerPosition", "f8", ("M", "C"))
    listenerPositionVar.Units = "metre"
    listenerPositionVar.Type = "cartesian"
    listenerPositionVar[:] = mic_pos

    listenerUpVar = rootgrp.createVariable("ListenerUp", "f8", ("I", "C"))
    listenerUpVar.Units = "metre"
    listenerUpVar.Type = "cartesian"
    listenerUpVar[:] = np.asarray([0, 0, 1])

    # Listener looking forward (+x direction)
    listenerViewVar = rootgrp.createVariable("ListenerView", "f8", ("I", "C"))
    listenerViewVar.Units = "metre"
    listenerViewVar.Type = "cartesian"
    listenerViewVar[:] = np.asarray([1, 0, 0])

    # single emitter for each measurement
    emitterPositionVar = rootgrp.createVariable(
        "EmitterPosition", "f8", ("E", "C", "I")
    )
    emitterPositionVar.Units = "metre"
    emitterPositionVar.Type = "spherical"
    # Equidistributed speakers in circle
    emitterPositionVar[:] = np.zeros((E, C, I))

    sourcePositionVar = rootgrp.createVariable("SourcePosition", "f8", ("M", "C"))
    sourcePositionVar.Units = "metre"
    sourcePositionVar.Type = "cartesian"
    sourcePositionVar[:] = source_pos

    sourceUpVar = rootgrp.createVariable("SourceUp", "f8", ("I", "C"))
    sourceUpVar.Units = "metre"
    sourceUpVar.Type = "cartesian"
    sourceUpVar[:] = np.asarray([0, 0, 1])

    sourceViewVar = rootgrp.createVariable("SourceView", "f8", ("I", "C"))
    sourceViewVar.Units = "metre"
    sourceViewVar.Type = "cartesian"
    sourceViewVar[:] = np.asarray([1, 0, 0])

    receiverPositionVar = rootgrp.createVariable(
        "ReceiverPosition", "f8", ("R", "C", "I")
    )
    receiverPositionVar.Units = "metre"
    receiverPositionVar.Type = "cartesian"
    receiverPositionVar[:] = np.zeros((R, C, I))

    samplingRateVar = rootgrp.createVariable("Data.SamplingRate", "f8", ("I"))
    samplingRateVar.Units = "hertz"
    samplingRateVar[:] = sr

    delayVar = rootgrp.createVariable("Data.Delay", "f8", ("I", "R"))
    delay = np.zeros((I, R))
    delayVar[:, :] = delay

    dataIRVar = rootgrp.createVariable("Data.IR", "f8", ("M", "R", "N"))
    dataIRVar.ChannelOrdering = "acn"  # standard ambi ordering
    dataIRVar.Normalization = "sn3d"
    dataIRVar[:] = rirs

    # ----------Close it----------#

    rootgrp.close
    print(f"SOFA file saved to {filepath}")