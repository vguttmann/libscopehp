import serial
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import re
from typing import Tuple


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        `expression`:
            input expression in which the error occurred
        
        `message`:
            explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class scope:
    """54645A/D Scope Interface Class.

    Subclasses:
        acquire: The ACQuire subsystem.
        analog: The ANALog Subsystem.
        calibrate: The CALibrate subsystem.
        channel: The CHANnel Subsystem.

    Attributes:
        port: The port the scope is connected to.
        model: The model of scope.
        baudrate: The serial baudrate to use for the scope.
        serialObject: The actual `serial.Serial` connection to the scope.
    """

    def __init__(self, port: str, model: str, baudrate: int) -> None:
        self.port = port
        self.model = model
        self.baudrate = baudrate
        self.serialObject = serial.Serial(port = self.port, baudrate = self.baudrate, bytesize = EIGHTBITS, stopbits = STOPBITS_ONE, xonxoff = False, rtscts = False, dsrdtr = True, parity = PARITY_NONE, timeout = 1)
    
    def send(message: str):
        """Sends a message to the scope attached at the specified port

        Emits the message to the scope.
        Be CAREFUL, *NO* checks are in place and EVERYTHING is emitted to the scope DIRECTLY. 

        Arguments:
            `message(str)`: A properly formatted message string
        """
        scope.serialObject.open()
        scope.serialObject.write(message.encode('utf-8'))
        while scope.serialObject.out_waiting is not 0:
            pass
        scope.serialObject.close()

    def receive():
        return str(scope.serialObject.read_until())


    class acquire:
        """The ACQuire subsystem.
        
        Methods:
            `setCompletionCriteria(criteria: int)`:
                Sets the criteria for how much information needs 
                to be captured to complete an acquisition.
        
            `getCompletionCriteria()`:
                Returns the current completion criteria.
            
            `setCount(count: int)`:
                Sets the numbers of samples to be used in averaging mode.
            
            `getCount()`:
                Returns the current number of samples to be used in averaging mode.

            `setDither(dither: bool)`:
                Dis/Enabled dithering.
            
            `getDither()`:
                Checks whether dithering is dis/enabled.

            `setType(type: str)`:
                Sets the type of acquisition.

            `getType()`:
                Checks the type of acquisition.

            `getPoints()`:
                Gets the number of points that the hardware will acquire from the input signal.
        """

        def __init__(self) -> None:
            pass

        def setCompletionCriteria(criteria: int):
            """Sets completion criteria for acquisitions.

            Sets how full acquisition memory needs to be for an acquisition to be completed.

            Arguments:
                `criteria(int)`: An integer between 0 and 100, which describes how full acquisition memory needs to be to complete one acquisition

            Raises:
                `InputError`: In case `criteria` is invalid, an `InputError` exception will be raised.
            """
            if(criteria < 0 or criteria > 100):
                raise InputError(criteria, 'Must be an int between 0 and 100.')
            else:
                scope.send(f":ACQ:COMP {criteria}\n")

        def getCompletionCriteria() -> int:
            """Gets the current completion criteria set in the scope.

            Gets the information how full acquisition memory needs to be for an acquisition to be completed. Criteria must be 0-100, that describes how full acquisition memory needs to be to complete one acquisition.

            Returns:
                `int`: [0 - 100]
            """

            scope.send(":ACQ:COMP?")
            return int(scope.receive())
        
        def setCount(count: int):
            """Sets the amount of samples to average per time bucket in averaging mode.

            The number must be a power of 2, with the exponent ranging from 0 to 8 

            Arguments:
                `count(int)`: [1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256]
            
            Raises:
                `InputError`: In case `count` is invalid, an `InputError` exception will be raised.
            """
            if(count not in {1, 2, 4, 8, 16, 32, 64, 128, 256}):
                raise InputError(count, 'Must be a power of 2 with an exponent between 0 and 8!')
            else:
                scope.send(f":ACQ:COUN {count}\n")
        
        def getCount() -> int:
            """Gets the current number of samples to average per time bucket in averaging mode.

            The number will be a power of 2, with the exponent ranging from 0 to 8.

            Returns:
                `int`: any int.
            """
            scope.send(":ACQ:COUN?")
            return int(scope.receive())

        def setDither(dither: bool):
            """Dis/Enables dithering.

            For slow sweep speeds, a small random time offset is added to the sampling clock to avoid aliasing. Dithering is turned on by default, however, some functions, such as FFT, require dithering to be disabled.

            Arguments:
                `dither(bool)`: [True | False]
            """

            scope.send(f":ACQ:DITH {'ON' if dither else 'OFF'}\n")

        def getDither() -> bool:
            """Checks whether dithering is dis/enabled.

            Returns "ON" if dithering is on, and "OFF" if dithering is off.

            Returns:
                `String`: [ON | OFF]
            """

            scope.send(":ACQ:DITH?")
            return scope.receive()

        def setType(type: str):
            """Sets the type of acquisition.

            Selects between the four modes that there are: NORMal, AVERage, PEAK and REALtime. Only the short forms are used. In AVERage, the count number is set by the `setCount()` command.

            Arguments:
                `type(str)`: [NORM | AVER | PEAK | REAL]

            Raises:
                `InputError`: In case `type` is not "NORM", "AVER", "PEAK" or "REAL" an InputError will be raised
            """

            if(type not in {'NORM', 'AVER', 'PEAK', 'REAL'}):
                raise InputError(type, 'Must be "NORM", "AVER", "PEAK" or "REAL"!')
            else:
                scope.send(f":ACQ:TYPE {type}\n")

        def getType() -> str:
            """Checks the type of acquisition.

            Returns "NORM", "AVER", "PEAK", or "REAL" depending on the current acquisition mode.

            Returns:
                `str`: any str.
            """
            scope.send(":ACQ:TYPE?")
            return scope.receive()

        def getPoints() -> Tuple(int, int):
            """Gets the number of points that the hardware will acquire from the input signal.
            
            Returns:
                `tuple(int, int)`: Analague Points and Digital Points respectivley.
            """
            scope.send(":ACQ:POIN?")

            data = scope.receive() # In format "<analog_points:int>,<digital_points:int>"
            analog_points = int(data.split(",")[0])
            digital_points = int(data.split(",")[1])
            
            return (analog_points, digital_points)


    class analog:
        """The ANALog Subsystem.
        
        Methods:
            `setBWLimit(channel: int, limit: bool)`:
                Set the internal low pass filter for the specified channel.

            `getBWLimit(channel: int)`:
                Get the state of the internal low pass filter for the specified channel.

            `setCoupling(channel: int, coupling: str)`:
                Set the input coupling for the specified channel.

            `getCoupling(channel: int)`:
                Get the input coupling for the specified channel.

            `setInversion(channel: int, inversion: bool)`:
                Set the inversion for the specified channel.

            `getInversion(channel: int)`:
                Get the inversion for the specified channel.

            `setLabel(channel: int, label: str)`:
                Set the specified analog channel's label to the provided string.

            `getLabel(channel: int)`:
                Get the analog channel label for the specified channel.

            `setOffset(channel: int, offset: float)`:
                Set the voltage that is represented at center screen for the selected channel.

            `getOffset(channel: int)`:
                Get the voltage that is represented at center screen for the selected channel.

            `setProbeMode(chanel: int, mode: str)`:
                Set the probe sense mode for the given channel.

            `getProbeMode(chanel: int)`:
                Get the probe sense mode for the given channel.

            `setProbeAttenuation(channel: int, attenuation: str)`:
                Specify the probe attenuation factor for the selected channel.

            `getProbeAttenuation(channel: int)`:
                Return the current probe attenuation factor for the selected channel.

            `setRange(channel: int, range: float)`:
                Define the full-scale vertical axis of the selected channel.

            `getRange(channel: int)`:
                Get the current full-scale range setting for the specified channel.
        """
        
        def setBWLimit(channel: int, limit: bool):
            """Set the internal low pass filter for the specified channel.
            
            Arguments:
                `channel(int)`: [1 | 2]
                
                `limit(bool)`: [True | False]

            Raises:
                `InputError`: In case channel is invalid.
            """
            
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:BWL {'ON' if limit else 'OFF'}\n")
        
        def getBWLimit(channel: int) -> bool:
            """Get the state of the internal low pass filter for the specified channel.
            
            Arguments:
                `channel(int)`: [1 | 2]

            Returns:
                `bool`: [True | False]

            Raises:
                `InputError`: In case channel is invalid.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:BWL?")
                return (True if scope.receive().find("ON") else False)

        def setCoupling(channel: int, coupling: str):
            """Set the input coupling for the specified channel.
            
            The input coupling can be set to either "AC", "DC", or "GND".

            Aruments:
                `channel(int)`: [1 | 2]

                `coupling(str)`: ["AC" | "DC" | "GND"]

            Raises:
                `InputError`: In case channel is not 1 or 2 or coupling is not "AC", "DC", or "GND".
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(coupling not in {"AC", "DC", "GND"}):
                raise InputError(coupling, "Coupling must be AC, DC or GND!")
            else:
                scope.send(f":ANAL{channel}:COUP {coupling}\n")
        
        def getCoupling(channel: int) -> bool:
            """Get the input coupling for the specified channel.
            
            Arguments:
                `channel(int)`: [1 | 2]

            Returns:
                `bool`: [True | False]
            
            Raises:
                `InputError`: In case the channel is not 1 or 2.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:COUP?")
                return (True if scope.receive().find("ON") else False)
        
        def setInversion(channel: int, inversion: bool):
            """Set the inversion for the specified channel.
            
            Arguments:
                `channel(int)`: [1 | 2]

                `inversion(bool)`: [True | False]

            Raises:
                `InputError`: In case the channel is not 1 or 2.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:INV {'ON' if inversion else 'OFF'}\n")
        
        def getInversion(channel: int) -> bool:
            """Get the inversion for the specified channel.
            
            Arguments:
                `channel(int)`: [1 | 2]

            Returns:
                `bool`: [True | False]
            
            Raises:
                `InputError`: In case the channel is not 1 or 2.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:INV?")
                return (True if scope.receive().find("ON") else False)
        
        def setLabel(channel: int, label: str):
            """Set the specified analog channel's label to the provided string.
            
            Setting a label for a channel will also result in the name being added to the NVRAM label list. The label must be 6 characters or less in ASCII only.
            
            Arguments:
                `channel(int)`: [1 | 2]

                `label(str)`: any str where (len(str) > 6 == false) and (label.isascii() == true).

            Raises:
                `InputError`: In case channel is not 1 or 2, any character in the label is not in the ASCII table, or the label is more than 6 characters long.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(not label.isascii()):
                raise InputError(label, "Label can only contain ASCII characters!")
            elif(len(label) > 6):
                raise InputError(label, "Length must be six characters or less!")
            else:
                scope.send(f":ANAL{channel}:LAB \"{label}\"\n")
        
        def getLabel(channel: int) -> str:
            """Get the analog channel label for the specified channel.
            
            Arguments:
                `channel(int)`: [1 | 2]

            Returns:
                `str`: any str.

            Raises:
                `InputError`: In case channel is not 1 or 2.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:LAB?")
                return scope.receive()
        
        def setOffset(channel: int, offset: float):
            """Set the voltage that is represented at center screen for the selected channel.

            The range of allowed values depends on the values set with the `scope.analog.setRange()` function, but will automatically be set to the nearest allowed value if you go over by the scope.

            Arguments:
                `channel(int)`: [1 | 2]

                `offset(float)`: any float.

            Raises:
                `InputError`: In case the channel is not 1 or 2, or the offset is not a float (or int if python is able to convert it).
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif((not isinstance(offset, float)) and (not isinstance(offset, int))):
                raise InputError(offset, "Offset must be a float (or int if python converts it so)!")
            else:
                scope.send(f":ANAL{channel}:OFFS {offset}\n")
        
        def getOffset(channel: int):
            """Get the voltage that is represented at center screen for the selected channel.
            
            Arugments:
                `channel(int)`: [1 | 2]
            
            Raises:
                `InputError`: In case the channel is not 1 or 2.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:OFFS?")
                return scope.receive()
        
        def setProbeMode(channel: int, mode: str):
            """Set the probe sense mode for the given channel.
            
            "AUT" (auto) turns on automatic probe sense, and "MAN" (manual) turns it off.

            Arguments:
                `channel(int)`: [1 | 2]

                `mode(str)`: ["AUT" | "MAN"]

            Raises:
                `InputError`: In case channel is not 1 or 2, or the mode is not "AUT" or "MAN".
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(mode not in {"AUT", "MAN"}):
                raise InputError(mode, f"Mode must be either AUT (Auto) or MAN (Manual), but was {mode}!")
            else:
                scope.send(f":ANAL{channel}:PMODE {mode}\n")
        
        def getProbeMode(channel: int) -> str:
            """Get the probe sense mode for the given channel.

            Returns either "AUT" or "MAN" meaning automatic probe sensing is enabled or not (respectivley).
            
            Arguments:
                `channel(int)`: [1 | 2]

            Returns:
                `str`: any str.
            
            Raises:
                `InputError`: In case channel is not 1 or 2.
            """
            if(channel is not 1 and channel is not 2):
                raise(InputError(channel, "Channel must be either 1 or 2!"))
            else:
                scope.send(f":ANAL{channel}:PMOD?")  
                return scope.receive()
        
        def setProbeAttenuation(channel: int, attenuation: str):
            """Specify the probe attenuation factor for the selected channel.
            
            The probe's attenuation factor may be 1, 10, 20, or 100. This does not change the actual input sensitivity of the oscilloscope. It changes the reference constants for scaling the display factors, for making automatic measurements, and for setting trigger levels. 
            
            Note: This also turns off the channel's probe sense.

            Arguments:
                `channel(int)`: [1 | 2]

                `attenuation(str)`: ["X1", "X10", "X20", "X100"]

            Raises:
                `InputError`: In case channel is not 1 or 2, or the attenuation is not "X1", "X10", "X20", or "X100".
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(attenuation.upper not in {"X1", "X10", "X20", "X100"}):
                raise InputError(attenuation, f"Attenuation must be X1, X10, X20, X100, but was {attenuation}!")
            else:
                scope.send(f":ANAL{channel}:PROB {attenuation}")

        def getProbeAttenuation(channel: int) -> str:
            """Return the current probe attenuation factor for the selected channel.
            
            This will return "X1", "X10", "X20", or "X100" depending on the current probe attenuation for the specified channel.
            
            Arguments:
                `channel(int)`: [1 | 2]
            
            Returns:
                `str`: any str.
            
            Raises:
                `InputError`: In case channel is not 1 or 2.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:PROB?")
                return scope.receive()

        def setRange(channel: int, range: float):
            """Define the full-scale vertical axis of the selected channel.
            
            The range can be set to any value from 16 mV to 40 V when using 1:1 probe attenuation. If the probe attenuation is changed, the range is multiplied by the probe attenuation factor. 
            
            Note: this function will not send a serial command if the range arugment is outside of the above calculate range.

            Arguments:
                `channel(int)`: [1 | 2]

                `range(float)`: any float specified in volts.

            Raises:
                `InputError`: In case channel is not 1 or 2.
            """

            attenuation = int(re.sub('\D', '', scope.analog.getProbeAttenuation()))
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            
            elif(range < (0.016 * attenuation)  or range > (40 * attenuation)):
                pass
            else:
                scope.send(f":ANAL{channel}:RANG {range}")
        
        def getRange(channel: int) -> float:
            """Get the current full-scale range setting for the specified channel.

            Arguments:
                `channel(int)`: [1 | 2]

            Raises:
                `InputError`: In case the channel is not 1 or 2.
            """

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(f":ANAL{channel}:RANG?")
                return float(scope.receive())


    class calibrate:
        """The CALibrate Subsystem
        
        Methods:
            `setCalibrationLabel(label: str)`:
                Save a string into the scope's non-volatile memory.

            `getCalibrationLabel()`:
                Return the contents of the calibration label string.

            `getCalibrationSwitchState()`:
                Return the protect switch state.
        """

        def setCalibrationLabel(label: str):
            """Save a string into the scope's non-volatile memory.

            The string may be used to record calibration dates or other information as needed. The string must be 32 characters or less in ASCII only.
            
            Arguments:
                `label(str)`: any str where (len(str) > 32 == false) and (label.isascii() == true).

            Raises:
                `InputError`: In case the string is longer than 32 characters or any character in the string is not in the ASCII table.
            """
            if(len(label) > 32):
                length = len(label)
                raise InputError(label, f"Label must not be longer than 32 characters, but was {length} characters long!")
            elif(not label.isascii()):
                raise InputError(label, "Label can only contain ASCII characters!")
            else:
                scope.send(f":CAL:LAB {label}")
        
        def getCalibrationLabel():
            """Return the contents of the calibration label string.
            
            Returns:
                `str`: any str.
            """

            scope.send(":CAL:LAB?")
            return scope.receive()
        
        def getCalibrationSwitchState() -> str:
            """Return the protect switch state.
            
            The value "PROT" indicates calibration is disabled, and "UNPR" indicates calibration is enabled.

            Returns:
                `str`: any str.
            """
            scope.send(":CAL:SWIT?")
            return scope.receive()


    class channel:
        """The CHANnel Subsystem
        
        Methods:
            `clearEdgeVariables()`:
                Clears the cumulative edge variables for the next activity query.
            
            `getActiveEdgesAndLogicLevels()`:
                Return the active edges since the last clear, and returns the current logic levels.

            `setLabel(channel: str, label: str)`:
                Set the label for the specified channel.
            
            `getLabel(channel: str)`:
                Get the label for the specified channel.

            `setMath(mode: str)`:
                Control the add or subtract function on the analog channels.

            `getMath()`:
                Get the add or subtract mode on the analog channels.
            
            `setThreshold(channel_group: int, preset: str, value: str)`:
                Set the threshold for a group of channels.

            `setThreshold(channel_group: int)`:
                Get the threshold for a group of channels.
        """

        def __init__(self) -> None:
            pass

        def clearEdgeVariables():
            """Clears the cumulative edge variables for the next activity query.
            
            Note: Only available on the HP 54645D Mixed-Signal Oscilloscope.
            """
            # @TODO: Pass `:CHAN:ACT` command on non-54645D (HP Mixed-Signal Oscilloscope) models.
            scope.send(":CHAN:ACT\n")

        def getActiveEdgesAndLogicLevels():
            """Return the active edges since the last clear, and returns the current logic levels.
            
            DANGER: This method's return data is not understood ATM. Use at your own risk. (Will return raw serial output.)

            Returns:
                `str`: any str.
            """

            scope.send(":CHAN:ACT?\n")

            # @TODO: Implement response parsing.
            return scope.receive()

        def setLabel(channel: str, label: str):
            """Set the label for the specified channel.
            
            Use `A#` (for analog) or `D#` (for digital) to specify the channel to apply the label to (replacing `#` with 1 or 2 for analog channels, or 0 through 15 for digital channels). The label must not exceed 6 characters and must all be in ASCII.

            Note: Only available on the HP 54645D Mixed-Signal Oscilloscope.

            Arguments:
                `channel(str)`: any str where `/^((A[1-2])|(D[0-9])|(D1[0-5]?))$/g` matches.
                
                `label(str)`: any str where `/^[A-z]{1,6}$/g` matches.
            
            Raises:
                `InputError`: In case the channel or label are not valid.
            """
            # Oh no, everyone run, it's- REGEX!
            if not (re.fullmatch("/^((A[1-2])|(D[0-9])|(D1[0-5]?))$/g", channel)):
                raise InputError(f"Channel is not valid (got \"{channel}\")!")
            elif not (re.fullmatch("/g^[A-z]{1,6}$/g", label) and label.isascii()):
                raise InputError(f"Label is not valid (got \"{label}\")!")
            else:
                chanType = "ANAL" if channel.startswith("A") else "DIG"
                chanNum = int(channel.replace("A", "").replace("D", ""))
                scope.send(f":CHAN:LAB {chanType}{chanNum},\"{label}\"\n")

        def getLabel(channel: str) -> str:
            """Get the label for the specified channel.

            Note: Only available on the HP 54645D Mixed-Signal Oscilloscope.

            Arguments:
                `channel(str)`: any str where `/^((A[1-2])|(D[0-9])|(D1[0-5]?))$/g` matches.
            
            Raises:
                `InputError`: In case the channel is not valid.
            """
            # @ TODO: Check if the query is a HP-54645D-MSO exlcusive, but we're still gonna call it that for safetey.
            # Oh no, everyone run, it's- REGEX, again!
            if not (re.fullmatch("/^((A[1-2])|(D[0-9])|(D1[0-5]?))$/g", channel)):
                raise InputError(f"Channel is not valid (got \"{channel}\")!")
            else:
                chanType = "ANAL" if channel.startswith("A") else "DIG"
                chanNum = int(channel.replace("A", "").replace("D", ""))
                scope.send(f":CHAN:LAB? {chanType}{chanNum}\n")

                return scope.receive()

        def setMath(mode: str):
            """Control the add or subtract function on the analog channels.

            Mode may be either "ADD", "SUBT", or "OFF".

            Arguments:

                `mode(str)`: ["ADD" | "SUBT" | "OFF"]

            Raises:
                `InputError`: In case the mode is not "ADD", "SUBT", or "OFF".
            """

            if (mode not in {}):
                raise InputError(f"Mode must be one of \"ADD\", \"SUBT\", or \"OFF\" (got \"{mode}\")!")
            else:
                scope.send(f":CHAN:MATH {mode}\n")

        def getMath() -> str:
            """Get the add or subtract mode on the analog channels.

            Will return "ADD" (addition), "SUBT" (subtraction), or "OFF".
            
            Returns:
                `str`: any str.
            """

            scope.send(":CHAN:MATH?\n")
            return scope.receive()

        def setThreshold(channel_group: int, preset: str, value: str):
            """Set the threshold for a group of channels.

            The threshold is either set to a predefined value or to a user-defined value. For the predefined value, the value parameter is ignored. Value is a float and a volt type of "V", "mV" (-3), or "uV" (-6). (E.g. `10.2mV`)

            Note: This command is only available on the HP 54645D Mixed-Signal Oscilloscope.

            Arguments:
                `channel_group(int)`: [1 | 2]

                `preset(str)`: ["CMOS" | "ECL" | "TTL" | "USER"]

                `value(str)`: any str where /^[0-9]+(\.[0-9]+)?(V|mV|uV)$/g matches or None if preset is not "USER".

            Raises:
                `InputError`: In case the channel group is not 1 or 2, preset is not "CMOS", "ECL", "TTL", or "USER", or value is invalid.
            """
            # So much regex, and it all works too, hehe.
            
            if (channel_group not in {1, 2}):
                raise InputError(f"Channel group is not 1 or 2 (got {channel_group})!")
            elif (preset not in {"CMOS" | "ECL" | "TTL" | "USER"}):
                raise InputError(f"Preset is not \"CMOS\", \"ECL\", \"TTL\", or \"USER\" (got \"{preset}\")!")
            else:
                needsValue = True if preset is not "User" else False
                scope.send(f":CHAN:THR POD{channel_group},{preset}{f',{value}' if needsValue else ''}\n")
        
        def getThreshold(channel_group: int) -> str:
            """Get the threshold for a group of channels.

            Note: This command is only available on the HP 54645D Mixed-Signal Oscilloscope.

            Warning: Returns raw scope data instead of a true data object. (`[CMOS | ECL | TTL | USERdef],[value if preset was USER]`)

            Arguments:
                `channel_group(int)`: [1 | 2]
            
            Returns:
                `str`: any str.
            
            Raises:
                `InputError`: In case channel group is not 1 or 2.
            """
            # @TODO: Check if this is also an HP-54645D-MSO exlcusive or just lies.

            if (channel_group not in {1,2}):
                raise InputError(f"Channel group must be 1 or 2 (got {channel_group})!")
            else:
                scope.send(f":CHAN:THR? POD{channel_group}\n")
                return scope.receive()


    class system:
        # @TODO: Add channel commands and understand their meaning!
        def getError():
            """Returns error codes from the onboard error memory

            Returns the next error from the 30 entry long error queue, which operates FIFO.

            Returns:
                `str`: any str.
            """
            scope.send(':SYS:ERR?')
            return scope.receive()
  

    class test:
        """
        The TEST subsystem. Allows for a complete self-test of the oscilloscope.

        Methods:
            `getTestAll()`:
                Runs a complete self-test of the oscilloscope

        """
        
        def getTestAll():
            """Runs a self-test on the oscilloscope.

            A non-zero return value indicates a failed test.

            Returns:
                `int`: 16-bit integer
            """
            scope.send(":TEST:ALL?")
            return int(scope.receive())


    class timebase:

        def setDelay(delay: float):
            """Sets the delay from trigger to the reference point on the screen.

            Arguments:
                `delay(float)`: Delay in seconds
            """
            scope.send(f":TIM:DEL {delay}")

        def getDelay():
            """Gets the delay from trigger to the reference point on the screen.

            Returns:
                `float`: delay between trigger and center reference
            """
            scope.send(":TIM:DEL?")
            return float(scope.receive())

        def setMode(mode: str):
            """Sets the timebase mode.

            Sets the time base mode to MAIN, DELayed, XY or ROLL. Only the short forms are used. 

            Arguments:
                `mode(str)`: [MAIN, DEL, XY, ROLL]

            Raises:
                `InputError`: In case the mode is not "MAIN", "DEL", "XY" or "ROLL".
            """
            if(mode not in {'MAIN', 'DEL', 'XY', 'ROLL'}):
                raise InputError(mode, 'Must be "MAIN", "DEL", "XY" or "ROLL"!')
            else:
                #if(scope.system.getError()):
                #@TODO: Add error checking here
                scope.send(f':TIM:MOD {mode}')

        def getMode():
            scope.send(':TIM:MOD?')
            return scope.receive()
        
        def setRange(channel: int, range: float):
            if(range < 0.00000005 or range > 500 ):
                pass
            else:
                scope.send(f":TIM:RANG {range}")
        
        def getRange(channel:int):
            scope.send(":TIM:RANG?")
            return float(scope.receive())

        def setReference(reference: str):
            if(reference not in {'LEFT', 'CENT', 'RIGH'}):
                raise InputError(reference, 'reference must be "LEFT", "CENT" or "RIGH"')
            else:
                scope.send(f':TIM:REF {reference}')
                return scope.receive()
        
        def getReference():
            scope.send(':TIM:REF?')
            return scope.receive()
    

    class trace:
        
        def clearTrace(trace: int):
            if(trace < 1 or trace > 100):
                raise InputError(trace, f'Trace number must be between 1 and 100, but was {trace}!')
            else:
                scope.send(f':TRAC:CLEAR {trace}')
        
        def setTraceData():
            #@TODO: Do this command!
            pass

        def getTraceData():
            #@TODO: Do this command!
            pass

        def setTraceMode(trace: int, mode: str):
            if(trace < 1 or trace > 100):
                raise InputError(trace, f'Trace number must be between 1 and 100, but was {trace}!')
            elif(mode not in {'ON', 'OFF'}):
                raise InputError(mode, f'mode must be "ON" or "OFF", but was {mode}!')
            else:
                scope.send(f':TRAC:MODE {trace} {mode}')
        
        def getTraceMode(trace: int):
            if(trace < 1 or trace > 100):
                raise InputError(trace, f'Trace number must be between 1 and 100, but was {trace}!')
            else:
                scope.send(f':TRAC:MODE? {trace}')
                return scope.receive()
        
        def saveToTrace(trace: int):
            if(trace < 1 or trace > 100):
                raise InputError(trace, f'trace must be between 1 and 100, but was {trace}!')
            else:
                scope.send(f':TRAC:SAVE {trace}')
        
    
    class trigger:

        def setCoupling(coupling: str):
            """
            Sets the current coupling

            Arguments:
                `coupling(str)`: [AC, DC]

            Returns:
                `None`: This function doesn't return anything

            Raises:
                `InputError`: In case `coupling` is invalid, an `InputError` will be raised
            """
            if(coupling not in {'AC', 'DC'}):
                raise InputError(coupling, f'coupling must be "AC" or "DC", but was {coupling}!')
            else:
                scope.send(f":TRIG:COUP {coupling}")
        
        def getCoupling():
            """
            Gets the current coupling

            Arguments:
                `None`: This function doesn't take any arguments

            Returns:
                `coupling(str)`: [AC, DC]

            Raises:
                `None`: This function doesn't raise any errors
            """
            scope.send(':TRIG:COUP?')
            return scope.receive()

        def setHoldoff(holdoff: float):
            """
            Sets the trigger holdoff time

            Arguments:
                `holdoff(float)`: _description_
            """

            scope.send(f":TRIG:HOLD {holdoff}")

        def getHoldoff():
            """
            Gets the trigger holdoff time

            Raises:
                `float`: The trigger holdoff time
            """
