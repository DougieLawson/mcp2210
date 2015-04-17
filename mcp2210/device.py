import hid
from mcp2210 import commands
import time


class CommandException(Exception):
    #print "device.py:CommandException"
    """Thrown when the MCP2210 returns an error status code."""

    def __init__(self, code):
        #print "device.py:CommandException:__init__"
        super(CommandException, self).__init__("Got error code from device: 0x%.2x" % code)


class GPIOSettings(object):
    #print "device.py:GPIOSettings"
    """Encapsulates settings for GPIO pins - direction or status."""

    def __init__(self, device, get_command, set_command):
        #print "device.py:GPIOSettings:__init__"
        self._device = device
        self._get_command = get_command
        self._set_command = set_command
        self._value = None

    @property
    def raw(self):
        #print "device.py:GPIOSettings:raw(@property)"
        if self._value is None:
            self._value = self._device.sendCommand(self._get_command()).gpio
        return self._value

    @raw.setter
    def raw(self, value):
        #print "device.py:GPIOSettings:raw(@raw.setter)"
        self._value = value
        self._device.sendCommand(self._set_command(value))

    def __getitem__(self, i):
        #print "device.py:GPIOSettings:__getitem__"
        return (self.raw >> i) & 1

    def __setitem__(self, i, value):
        #print "device.py:GPIOSettings:__setitem__"
        if value:
            self.raw |= 1 << i
        else:
            self.raw &= ~(1 << i)


def remote_property(name, get_command, set_command, field_name, doc=None):
    #print "device.py:remote_property"
    """Property decorator that facilitates writing properties for values from a remote device.

    Arguments:
      name: The field name to use on the local object to store the cached property.
      get_command: A function that returns the remote value of the property.
      set_command: A function that accepts a new value for the property and sets it remotely.
      field_name: The name of the field to retrieve from the response message to get operations.
    """

    def getter(self):
        #print "device.py:remote_property:getter"
        try:
            return getattr(self, name)
        except AttributeError:
            value = getattr(self.sendCommand(get_command()), field_name)
            setattr(self, name, value)
            return value

    def setter(self, value):
        #print "device.py:remote_property:setter"
        setattr(self, name, value)
        self.sendCommand(set_command(value))

    return property(getter, setter, doc=doc)


class EEPROMData(object):
    #print "device.py:EEPROMData"
    """Represents data stored in the MCP2210 EEPROM."""

    def __init__(self, device):
        #print "device.py:EEPROMData:__init__"
        self._device = device

    def __getitem__(self, key):
        #print "device.py:EEPROMData:__getitem__"
        if isinstance(key, slice):
            return ''.join(self[i] for i in range(*key.indices(255)))
        else:
            return chr(self._device.sendCommand(commands.ReadEEPROMCommand(key)).header.reserved)

    def __setitem__(self, key, value):
        #print "device.py:EEPROMData:__setitem__"
        if isinstance(key, slice):
            for i, j in enumerate(range(*key.indices(255))):
                self[j] = value[i]
        else:
            self._device.sendCommand(commands.WriteEEPROMCommand(key, ord(value)))


class MCP2210(object):
    #print "device.py:MCP2210"
    """MCP2210 device interface.

    Usage:
        >>> dev = MCP2210(my_vid, my_pid)
        >>> dev.transfer("data")

    Advanced usage:
        >>> dev.manufacturer_name = "Foobar Industries Ltd"
        >>> #print dev.manufacturer_name
        Foobar Industries Ltd

        >>> dev.product_name = "Foobinator 1.0"
        >>> #print dev.product_name
        Foobinator 1.0

        >>> settings = dev.boot_chip_settings
        >>> settings.pin_designations[0] = 0x01  # GPIO 0 to chip select
        >>> dev.boot_chip_settings = settings  # Settings are updated on property assignment

    See the MCP2210 datasheet (http://ww1.microchip.com/downloads/en/DeviceDoc/22288A.pdf) for full details
    on available commands and arguments.
    """
    def __init__(self, vid, pid):
        #print "device.py:MCP2210:__init__"
        """Constructor.

        Arguments:
          vid: Vendor ID
          pid: Product ID
        """
        self.hid = hid.device()
        self.hid.open(vid, pid)
        self.gpio_direction = GPIOSettings(self, commands.GetGPIODirectionCommand, commands.SetGPIODirectionCommand)
        self.gpio = GPIOSettings(self, commands.GetGPIOValueCommand, commands.SetGPIOValueCommand)
        self.eeprom = EEPROMData(self)
        self.cancel_transfer()

    def sendCommand(self, command):
        #print "device.py:MCP2210:sendCommand"
        """Sends a Command object to the MCP2210 and returns its response.

        Arguments:
            A commands.Command instance

        Returns:
            A commands.Response instance, or raises a CommandException on error.
        """
        command_data = [ord(x) for x in buffer(command)]
	bits = dict()
	for i in range(0,8):
		bits[i] = ""
	printall = False
	for x in buffer(command)[2:]:
		for i in range(0,8):
			if ((ord(x) & 1 << i)) == 0:
				bits[i] = bits[i] + " "
			else:
				bits[i] = bits[i] + "X"
				printall = True
	l = max(len(bits[0].strip()), len(bits[1].strip()), len(bits[2].strip()), len(bits[3].strip()), len(bits[4].strip()), len(bits[5].strip()), len(bits[6].strip()), len(bits[7].strip()))
	if l > 2:
		for i in range(0,62):
			print bits[7][i], bits[6][i], bits[5][i], bits[4][i], bits[3][i], bits[2][i], bits[1][i], bits[0][i]
	elif l == 0:
		print
	else:
		print bits[7][2], bits[6][2], bits[5][2], bits[4][2], bits[3][2], bits[2][2], bits[1][2], bits[0][2]
        self.hid.write(command_data)
        response_data = ''.join(chr(x) for x in self.hid.read(64))
        response = command.RESPONSE.from_buffer_copy(response_data)
        response.command = 66
        engine_status = 16
        response.length = 64
	response.status = 0
	
        #response_data = ''.join(chr(x) for x in mock_data)
#        if response.status != 0:
#            raise CommandException(response.status)
        return response


#    manufacturer_name = remote_property(
#        '_manufacturer_name',
#        commands.GetUSBManufacturerCommand,
#        commands.SetUSBManufacturerCommand,
#        'string',
#        doc="Sets and gets the MCP2210 USB manufacturer name")

#    product_name = remote_property(
#        '_product_name',
#        commands.GetUSBProductCommand,
#        commands.SetUSBProductCommand,
#        'string',
#        doc="Sets and gets the MCP2210 USB product name")

#    boot_chip_settings = remote_property(
#        '_boot_chip_settings',
#        commands.GetBootChipSettingsCommand,
#        commands.SetBootChipSettingsCommand,
#        'settings',
#        doc="Sets and gets boot time chip settings such as GPIO assignments")

#    chip_settings = remote_property(
#        '_chip_settings',
#        commands.GetChipSettingsCommand,
#        commands.SetChipSettingsCommand,
#        'settings',
#        doc="Sets and gets current chip settings such as GPIO assignments")

#    boot_transfer_settings = remote_property(
#        '_boot_transfer_settings',
#        commands.GetBootSPISettingsCommand,
#        commands.SetBootSPISettingsCommand,
#        'settings',
#        doc="Sets and gets boot time transfer settings such as data rate")

#    transfer_settings = remote_property(
#        '_transfer_settings',
#        commands.GetSPISettingsCommand,
#        commands.SetSPISettingsCommand,
#        'settings',
#        doc="Sets and gets current transfer settings such as data rate")

#    boot_usb_settings = remote_property(
#        '_boot_usb_settings',
#        commands.GetBootUSBSettingsCommand,
#        commands.SetBootUSBSettingsCommand,
#        'settings',
#        doc="Sets and gets boot time USB settings such as VID and PID")

    def authenticate(self, password):
        #print "device.py:MCP2210:authenticate"
        """Authenticates against a password-protected MCP2210.

        Arguments:
            password: The password to use.
        """
        self.sendCommand(commands.SendPasswordCommand(password))

    def transfer(self, data):
        #print "device.py:MCP2210:transfer"
        """Transfers data over SPI.

        Arguments:
            data: The data to transfer.

        Returns:
            The data returned by the SPI device.
        """
#       settings = self.transfer_settings
#       settings.spi_tx_size = len(data)
#       self.transfer_settings = settings

        response = ''
        for i in range(0, len(data), 60):
            response += self.sendCommand(commands.SPITransferCommand(data[i:i + 60])).data
            time.sleep(0.01)

        while len(response) < len(data):
            response += self.sendCommand(commands.SPITransferCommand('')).data

        return ''.join(response)

    def cancel_transfer(self):
        #print "device.py:MCP2210:cancel_transfer"
        """Cancels any ongoing transfers."""
        self.sendCommand(commands.CancelTransferCommand())
