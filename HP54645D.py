import re
import string
import time
from enum import Enum

import serial
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE


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

    def __init__(self, port: str, model, baudrate: int) -> None:
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
        """
        The ACQuire subsystem.
        
        Methods:
            `setCompletionCriteria(int)`:
                Sets the criteria for how much information needs 
                to be captured to complete an acquisition.
        
            `getCompletionCriteria(NONE)`:
                Returns the current completion criteria.
            
            `setCount(int)`:
                Sets the numbers of samples to be used in averaging mode.
            
            `getCount`:
                Returns the current number of samples to be used in averaging mode.
        """

        def __init__(self) -> None:
            pass

        def setCompletionCriteria(criteria: int):
            """
            Sets completion criteria for acquisitions.

            Sets how full acquisition memory needs to be for an acquisition to be completed.
            

            Arguments:
                `criteria(int)`: An integer between 0 and 100, which describes how full acquisition memory needs to be to complete one acquisition
            
            Returns:
                `None`: This function doesn't return anything

            Raises:
                `InputError`: In case `criteria` is invalid, an `InputError` exception will be raised.
            """
            if(criteria < 0 or criteria > 100):
                raise InputError(criteria, 'Must be an int between 0 and 100.')
            else:
                scope.send(":ACQ:COMP {criteria}\n")

        def getCompletionCriteria():
            """
            Gets the current completion criteria set in the scope.

            Gets the information how full acquisition memory needs to be for an acquisition to be completed

            Arguments:
                `None`: This function doesn't take any arguments

            Returns:
                `int`: Integer from 0 to 100 that describes how full acquisition memory needs to be to complete one acquisition.
            """

            scope.send(":ACQ:COMP?")
            return int(scope.receive())
        
        def setCount(count: int):
            """Sets the amount of samples to average per time bucket in averaging mode.

            The number must be a power of 2, with the exponent ranging from 0 to 8 

            Arguments:
                `count(int)`: [1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256]

            Returns:
                `None`: This function doesn't return anything.
            
            Raises:
                `InputError`: In case `count` is invalid, an `InputError` exception will be raised.
            """
            if(count not in {1, 2, 4, 8, 16, 32, 64, 128, 256}):
                raise InputError(count, 'Must be a power of 2 with an exponent between 0 and 8!')
            else:
                scope.send(":ACQ:COUN {count}\n")
        
        def getCount():
            """Gets the current number of samples to average per time bucket in averaging mode.

            The number will be a power of 2, with the exponent ranging from 0 to 8.

            Returns:
                `int`: [1, 2, 4, 8, 16, 32, 64, 128, 256]
            """
            scope.send(":ACQ:COUN?")
            return int(scope.receive())

        def setDither(dither: str):
            """
            Dis- or enables dithering

            For slow sweep speeds, a small random time offset is added to the sampling clock to avoid aliasing. Dithering is turned on by default, however, some functions, such as FFT, require dithering to be disabled.

            Arguments:
                `dither(str)`: [ON | OFF]

            Returns:
                `None`: This function doesn't return anything.

            Raises:
                `InputError`: In case `dither` is neither "ON" nor "OFF", an `InputError` exception will be raised.
            """

            if(dither is not "OFF" or dither is not "ON"):
                raise InputError(dither, 'Must be either "ON" to turn dithering on, or "OFF" to turn dithering off!')
            scope.send(":ACQ:DITH {dither}\n")

        def getDither():
            """
            Checks whether dithering is dis- or enabled.

            Returns "ON" if dithering is on, and "OFF" if dithering is off.

            Arguments:
                `None`: This function does not take any arguments.

            Returns:
                `String`: [ON | OFF]
            """

            scope.send(":ACQ:DITH?")
            return scope.receive()

        def setType(type: str):
            """
            Sets the type of acquisition

            Selects between the four modes that there are: NORMal, AVERage, PEAK and REALtime. Only the short forms are used. In AVERage, the count number is set by the `setCount()` command.

            Arguments:
                `type(str)`: [NORM | AVER | PEAK | REAL]

            Returns:
                `None`: This function doesn't return anything.

            Raises:
                `InputError`: In case `type` is not "NORM", "AVER", "PEAK" or "REAL" an InputError will be raised
            """

            if(type not in {'NORM', 'AVER', 'PEAK', 'REAL'}):
                raise InputError(type, 'Must be "NORM", "AVER", "PEAK" or "REAL"!')
            else:
                scope.send(":ACQ:TYPE {type}\n")


    class analog:
        
        def setBWLimit(channel: int, limit: str):
            
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(limit not in {"ON", "OFF"}):
                raise InputError(limit, 'limitOn must be either "ON" or "OFF"!')
            else:
                scope.send(":ANAL{channel}:BWL {limitOn}\n")
        
        def getBWLimit(channel: int):

            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(":ANAL{channel}:BWL?")
                return scope.receive()

        def setCoupling(channel: int, coupling: str):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(coupling not in {"AC", "DC", "GND"}):
                raise InputError(coupling, "Coupling must be AC, DC or GND!")
            else:
                scope.send(":ANAL{channel}:COUP {coupling}\n")
        
        def getCoupling(channel: int):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(":ANAL{channel}:COUP?")
                return scope.receive()
        
        def setInversion(channel: int, inversion: str):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(inversion not in {"ON", "OFF"}):
                raise InputError(inversion, "inversion must be either ON or OFF!")
            else:
                scope.send(":ANAL{channel}:INV {inversion}\n")
        
        def getInversion(channel: int):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(":ANAL{channel}:INV?")
                return scope.receive()
        
        def setLabel(channel: int, label: str):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(not label.isascii()):
                raise InputError(label, "Label can only contain ASCII characters!")
            elif(len(label) > 6):
                raise InputError(label, "Length must be six characters or less!")
            else:
                scope.send(":ANAL{channel}:LAB \"{label}\"\n")
        
        def getLabel(channel: int):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(":ANAL{channel}:LAB?")
                return scope.receive()
        
        def setOffset(channel: int, offset: float):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif((not isinstance(offset, float)) and (not isinstance(offset, int))):
                raise InputError(offset, "Offset must be a float (or int if python converts it so)!")
            else:
                scope.send(":ANAL{channel}:OFFS {offset}\n")
        
        def getOffset(channel: int):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(":ANAL{channel}:OFFS?")
                return scope.receive()
        
        def setProbeMode(channel: int, mode: str):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(mode not in {"AUT", "MAN"}):
                raise InputError(mode, "Mode must be either AUT (Auto) or MAN (Manual), but was {mode}!")
            else:
                scope.send(":ANAL{channel}:PMODE {mode}\n")
        
        def getProbeMode(channel: int):
            if(channel is not 1 and channel is not 2):
                raise(InputError(channel, "Channel must be either 1 or 2!"))
            else:
                scope.send(":ANAL{channel}:PMOD?")  
                return scope.receive()
        
        def setProbeAttenuation(channel: int, attenuation: str):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            elif(attenuation.upper not in {"X1", "X10", "X20", "X100"}):
                raise InputError(attenuation, "Attenuation must be X1, X10, X20, X100, but was {attenuation}!")
            else:
                scope.send(":ANAL{channel}:PROB {attenuation}")

        def getProbeAttenuation(channel: int):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(":ANAL{channel}:PROB?")
                return scope.receive()

        def setRange(channel: int, range: float):
            attenuation = re.sub('\D', '', scope.analog.getProbeAttenuation())
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            
            elif(range < (0.016 * attenuation)  or range > (40 * attenuation)):
                pass
            else:
                scope.send(":ANAL{channel}:RANG {range}")
        
        def getRange(channel:int):
            if(channel is not 1 and channel is not 2):
                raise InputError(channel, "Channel must be either 1 or 2!")
            else:
                scope.send(":ANAL{channel}:RANG?")
                return float(scope.receive())


    class calibrate:

        def setCalibrationLabel(label: str):
            if(len(label) > 32):
                length = len(label)
                raise InputError(label, "Label must not be longer than 32 characters, but was {length} characters long!")
            elif(not label.isascii()):
                raise InputError(label, "Label can only contain ASCII characters!")
            else:
                scope.send(":CAL:LAB {label}")
        
        def getCalibrationLabel():
            scope.send(":CAL:LAB?")
            return scope.receive()
        
        def getCalibrationSwitchState():
            scope.send(":CAL:SWIT?")
            return scope.receive()


    class channel:
        # @TODO: Add channel commands and understand their meaning!
        pass


    class system:
      # @TODO: Add channel commands and understand their meaning!
        def getError():
            """
            Returns error codes from the onboard error memory

            Returns the next error from the 30 entry long error queue, which operates FIFO.

            Arguments:

            Returns:
                ``: _description_
            """
            scope.send(':SYS:ERR?')
            return scope.receive()
  

    class test:
        """
        The TEST subsystem. Allows for a complete self-test of the oscilloscope.

        Methods:
            `getTestAll(NONE)`:
                Runs a complete self-test of the oscilloscope

        """
        
        def getTestAll():
            """
            Runs a self-test on the oscilloscope.

            A non-zero return value indicates a failed test.

            Arguments:
                `None`: This function doesn't require any arguments.

            Returns:
                `int`: 16-bit integer
            
            Raises:
                `None`: This function doesn't raise any errors.
            """
            scope.send(":TEST:ALL?")
            return int(scope.receive())


    class timebase:

        def setDelay(delay: float):
            """
            Sets the delay from trigger to the reference point on the screen

            Arguments:
                `delay(float)`: Delay in seconds

            Returns:
                `None`: This function doesn't return anything

            Raises:
                `None`: This function doesn't raise any errors.
            """
            scope.send(":TIM:DEL {delay}")

        def getDelay():
            """
            Gets the delay from trigger to the reference point on the screen

            Arguments:
                `None`: This function doesn't require any arguments

            Returns:
                `float`: delay between trigger and center reference

            Raises:
                `None`: This function doesn't raise any errors.
            """
            scope.send(":TIM:DEL?")
            return float(scope.receive())

        def setMode(mode: str):
            """
            Sets the timebase mode

            Sets the time base mode to MAIN, DELayed, XY or ROLL. Only the short forms are used. 

            Arguments:
                `mode(str)`: [MAIN, DEL, XY, ROLL]

            Returns:
                `None`: This function doesn't return anything

            Raises:
                `InputError`: _description_
            """
            if(mode not in {'MAIN', 'DEL', 'XY', 'ROLL'}):
                raise InputError(mode, 'Must be "MAIN", "DEL", "XY" or "ROLL"!')
            else:
                #if(scope.system.getError()):
                #@TODO: Add error checking here
                scope.send(':TIM:MOD {mode}')

        def getMode():
            scope.send(':TIM:MOD?')
            return scope.receive()
        
        def setRange(channel: int, range: float):
            if(range < 0.00000005 or range > 500 ):
                pass
            else:
                scope.send(":TIM:RANG {range}")
        
        def getRange(channel:int):
            scope.send(":TIM:RANG?")
            return float(scope.receive())

        def setReference(reference: str):
            if(reference not in {'LEFT', 'CENT', 'RIGH'}):
                raise InputError(reference, 'reference must be "LEFT", "CENT" or "RIGH"')
            else:
                scope.send(':TIM:REF {reference}')
                return scope.receive()
        
        def getReference():
            scope.send(':TIM:REF?')
            return scope.receive()
    

    class trace:
        
        def clearTrace(trace: int):
            if(trace < 1 or trace > 100):
                raise InputError(trace, 'Trace number must be between 1 and 100, but was {trace}!')
            else:
                scope.send(':TRAC:CLEAR {trace}')
        
        def setTraceData():
            #@TODO: Do this command!
            pass

        def getTraceData():
            #@TODO: Do this command!
            pass

        def setTraceMode(trace: int, mode: str):
            if(trace < 1 or trace > 100):
                raise InputError(trace, 'Trace number must be between 1 and 100, but was {trace}!')
            elif(mode not in {'ON', 'OFF'}):
                raise InputError(mode, 'mode must be "ON" or "OFF", but was {mode}!')
            else:
                scope.send(':TRAC:MODE {trace} {mode}')
        
        def getTraceMode(trace: int):
            if(trace < 1 or trace > 100):
                raise InputError(trace, 'Trace number must be between 1 and 100, but was {trace}!')
            else:
                scope.send(':TRAC:MODE? {trace}')
                return scope.receive()
        
        def saveToTrace(trace: int):
            if(trace < 1 or trace > 100):
                raise InputError(trace, 'trace must be between 1 and 100, but was {trace}!')
            else:
                scope.send(':TRAC:SAVE {trace}')
        
    
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
                raise InputError(coupling, 'coupling must be "AC" or "DC", but was {coupling}!')
            else:
                scope.send(':TRIG:COUP {coupling}')
        
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

            Returns:
                `None`: This function doesn't return anything

            Raises:
                `None`: This function doesn't raise any errors.
            """
            scope.send(":TRIG:HOLD {holdoff}")

        def getHoldoff():
            """
            Gets the trigger holdoff time

        Arguments:
            `None`: This function doesn't take any arguments

        Returns:
            `None`: This function doesn't return anything

        Raises:
            `float`: The trigger holdoff time
            """