from ctypes import Structure, c_ubyte, c_ushort, c_uint, c_char


class CommandHeader(Structure):
    #print "commands.py:CommandHeader"
    _fields_ = [('command', c_ubyte),
                ('subcommand', c_ubyte),
                ('reserved_1', c_ubyte),
                ('reserved_2', c_ubyte)]


class ResponseHeader(Structure):
    #print "commands.py:ResponseHeader"
    _fields_ = [('command', c_ubyte),
                ('status', c_ubyte),
                ('subcommand', c_ubyte),
                ('reserved', c_ubyte)]


class Response(Structure):
    #print "commands.py:Response"
    pass


class EmptyResponse(Response):
    #print "commands.py:EmptyResponse"
    _anonymous_ = ['header']
    _fields_ = [('header', ResponseHeader)]


class Command(Structure):
    #print "commands.py:Command"
    def __init__(self, *args, **kwargs):
        #print "commands.py:Command:__init__"
        super(Command, self).__init__((self.COMMAND, self.SUBCOMMAND, 0x00, 0x00), *args, **kwargs)


class SetBootSettingsCommand(Command):
    #print "commands.py:SetBootSettingsCommand"
    COMMAND = 0x60
    RESPONSE = EmptyResponse


class ChipSettings(Structure):
    #print "commands.py:ChipSettings"
    _fields_ = [('pin_designations', c_ubyte * 9),
                ('gpio_outputs', c_ushort),
                ('gpio_directions', c_ushort),
                ('other_settings', c_ubyte),
                ('access_control', c_ubyte),
                ('new_password', c_char * 8)]


class SetBootChipSettingsCommand(SetBootSettingsCommand):
    #print "commands.py:SetBootChipSettingsCommand"
    SUBCOMMAND = 0x20
    _fields_ = [('header', CommandHeader),
                ('settings', ChipSettings)]


class SPISettings(Structure):
    #print "commands.py:SPISettings"
    _fields_ = [('bit_rate', c_uint),
                ('idle_cs', c_ushort),
                ('active_cs', c_ushort),
                ('cs_data_delay', c_ushort),
                ('lb_cs_delay', c_ushort),
                ('interbyte_delay', c_ushort),
                ('spi_tx_size', c_ushort),
                ('spi_mode', c_ubyte)]


class SetBootSPISettingsCommand(SetBootSettingsCommand):
    #print "commands.py:SetBoot:SPISettingsCommand"
    SUBCOMMAND = 0x10
    _fields_ = [('header', CommandHeader),
                ('settings', SPISettings)]


class USBSettings(Structure):
    #print "commands.py:USBSettings"
    _fields_ = [('vid', c_ushort),
                ('pid', c_ushort),
                ('power_option', c_ubyte),
                ('current_request', c_ubyte)]


class SetBootUSBSettingsCommand(SetBootSettingsCommand):
    #print "commands.py:SetBootUSBSettingsCommand"
    SUBCOMMAND = 0x30
    _fields_ = [('header', CommandHeader),
                ('settings', USBSettings)]


class SetUSBStringCommand(SetBootSettingsCommand):
    #print "commands.py:SetUSBStringCommand"
    _fields_ = [('header', CommandHeader),
                ('str_len', c_ubyte),
                ('descriptor_id', c_ubyte),
                ('str', c_ubyte * 58)]

    def __init__(self, s):
        #print "commands.py:SetUSBStringCommand:__init__"
        super(SetUSBStringCommand, self).__init__()
        self.descriptor_id = 0x03
        self.string = s

    @property
    def string(self):
        #print "commands.py:SetUSBStringCommand:string(@property)"
        return ''.join(chr(x) for x in self.str[:self.str_len - 2]).decode('utf16')

    @string.setter
    def string(self, value):
        #print "commands.py:SetUSBStringCommand:string(@string.setter)"
        for i, x in enumerate((value + '\0').encode('utf16')):
            self.str[i] = ord(x)
        self.str_len = len(value) * 2 + 4


class SetUSBManufacturerCommand(SetUSBStringCommand):
    #print "commands.py:SetUSBManufacturerCommand"
    SUBCOMMAND = 0x50


class SetUSBProductCommand(SetUSBStringCommand):
    #print "commands.py:SetUSBProductCommand"
    SUBCOMMAND = 0x40


class GetBootSettingsCommand(Command):
    #print "commands.py:GetBootSettingsCommand"
    COMMAND = 0x61


class GetChipSettingsResponse(Response):
    #print "commands.py:GetChipSettingsResponse"
    _anonymous_ = ['header']
    _fields_ = [('header', ResponseHeader),
                ('settings', ChipSettings)]


class GetBootChipSettingsCommand(GetBootSettingsCommand):
    #print "commands.py:GetBootChipSettingsCommand"
    SUBCOMMAND = 0x20
    RESPONSE = GetChipSettingsResponse
    _fields_ = [('header', CommandHeader)]


class GetSPISettingsResponse(Response):
    #print "commands.py:GetSPISettingsResponse"
    _anonymous_ = ['header']
    _fields_ = [('header', ResponseHeader),
                ('settings', SPISettings)]


class GetBootSPISettingsCommand(GetBootSettingsCommand):
    #print "commands.py:GetBootSPISettingsCommand"
    SUBCOMMAND = 0x10
    RESPONSE = GetSPISettingsResponse
    _fields_ = [('header', CommandHeader)]


class GetUSBSettingsResponse(Response):
    #print "commands.py:GetUSBSettingsResponse"
    _anonymous_ = ['header']
    _fields_ = [('header', ResponseHeader),
                ('reserved', c_ubyte * 8),
                ('vid', c_ushort),
                ('pid', c_ushort),
                ('reserved_2', c_ubyte * 13),
                ('power_option', c_ubyte),
                ('current_request', c_ubyte)]

    @property
    def settings(self):
        #print "commands.py:GetUSBSettingsResponse:settings(@property)"
        return USBSettings(self.vid, self.pid, self.power_option, self.current_request)


class GetBootUSBSettingsCommand(GetBootSettingsCommand):
    #print "commands.py:GetBootUSBSettingsCommand"
    SUBCOMMAND = 0x30
    RESPONSE = GetUSBSettingsResponse
    _fields_ = [('header', CommandHeader)]


class GetUSBStringResponse(Response):
    #print "commands.py:GetUSBStringResponse"
    _anonymous_ = ['header']
    _fields_ = [('header', ResponseHeader),
                ('str_len', c_ubyte),
                ('descriptor_id', c_ubyte),
                ('str', c_ubyte * 58)]

    @property
    def string(self):
        #print "commands.py:GetUSBStringResponse:string(@property)"
        return ''.join(chr(x) for x in self.str[:self.str_len - 2]).decode('utf16')


class GetUSBProductCommand(GetBootSettingsCommand):
    #print "commands.py:GetUSBProductCommand"
    SUBCOMMAND = 0x40
    RESPONSE = GetUSBStringResponse
    _fields_ = [('header', CommandHeader)]


class GetUSBManufacturerCommand(GetBootSettingsCommand):
    #print "commands.py:GetUSBManufacturerCommand"
    SUBCOMMAND = 0x50
    RESPONSE = GetUSBStringResponse
    _fields_ = [('header', CommandHeader)]


class SendPasswordCommand(Command):
    #print "commands.py:SendPasswordCommand"
    COMMAND = 0x70
    SUBCOMMAND = 0x00
    RESPONSE = EmptyResponse
    _fields_ = [('header', CommandHeader),
                ('password', c_char * 8)]


class GetSPISettingsCommand(Command):
    #print "commands.py:GetSPISettingsCommand"
    COMMAND = 0x41
    SUBCOMMAND = 0x00
    RESPONSE = GetSPISettingsResponse
    _fields_ = [('header', CommandHeader)]


class SetSPISettingsCommand(Command):
    #print "commands.py:SetSPISettingsCommand"
    COMMAND = 0x40
    SUBCOMMAND = 0x00
    RESPONSE = EmptyResponse
    _fields_ = [('header', CommandHeader),
                ('settings', SPISettings)]


class GetChipSettingsCommand(Command):
    #print "commands.py:GetChipSettingsCommand"
    COMMAND = 0x20
    SUBCOMMAND = 0x00
    RESPONSE = GetChipSettingsResponse
    _fields_ = [('header', CommandHeader)]


class SetChipSettingsCommand(Command):
    #print "commands.py:SetChipSettingsCommand"
    COMMAND = 0x21
    SUBCOMMAND = 0x00
    RESPONSE = EmptyResponse
    _fields_ = [('header', CommandHeader),
                ('settings', ChipSettings)]


class GetGPIOResponse(Response):
    #print "commands.py:GetGPIOResponse"
    _anonymous_ = ['header']
    _fields_ = [('header', ResponseHeader),
                ('gpio', c_ushort)]


class GetGPIOCommand(Command):
    #print "commands.py:GetGPIOCommand"
    SUBCOMMAND = 0x00
    RESPONSE = GetGPIOResponse
    _fields_ = [('header', CommandHeader)]


class GetGPIODirectionCommand(GetGPIOCommand):
    #print "commands.py:GetGPIODirectionCommand"
    COMMAND = 0x33


class SetGPIOCommand(Command):
    #print "commands.py:SetGPIOCommand"
    SUBCOMMAND = 0x00
    RESPONSE = EmptyResponse
    _fields_ = [('header', CommandHeader),
                ('gpio', c_ushort)]


class SetGPIODirectionCommand(SetGPIOCommand):
    #print "commands.py:SetGPIODirectionCommand"
    COMMAND = 0x32


class GetGPIOValueCommand(GetGPIOCommand):
    #print "commands.py:GetGPIOValueCommand"
    COMMAND = 0x31


class SetGPIOValueCommand(SetGPIOCommand):
    #print "commands.py:SetGPIOValueCommand"
    COMMAND = 0x30


class ReadEEPROMResponse(Structure):
    #print "commands.py:ReadEEPROMResponse"
    _fields_ = [('command', c_ubyte),
                ('status', c_ubyte),
                ('address', c_ubyte),
                ('data', c_ubyte)]


class ReadEEPROMCommand(Structure):
    #print "commands.py:ReadEEPROMCommand"
    COMMAND = 0x50
    RESPONSE = ReadEEPROMResponse
    _fields_ = [('command', c_ubyte),
                ('address', c_ubyte),
                ('reserved', c_ubyte)]

    def __init__(self, address):
        #print "commands.py:ReadEEPROMCommand:__init__"
        super(ReadEEPROMCommand, self).__init__(self.COMMAND, address, 0x00)


class WriteEEPROMCommand(Structure):
    #print "commands.py:WriteEEPROMCommand"
    COMMAND = 0x51
    RESPONSE = EmptyResponse
    _fields_ = [('command', c_ubyte),
                ('address', c_ubyte),
                ('value', c_ubyte)]

    def __init__(self, address, value):
        #print "commands.py:WriteEEPROMCommand:__init__"
        super(WriteEEPROMCommand, self).__init__(self.COMMAND, address, value)


SPIBuffer = c_ubyte * 60


class SPITransferResponse(Structure):
    #print "commands.py:SPITransferResponse"
    _fields_ = [('command', c_ubyte),
                ('status', c_ubyte),
                ('length', c_ubyte),
                ('engine_status', c_ubyte),
                ('_data', SPIBuffer)]

    @property
    def data(self):
        #print "commands.py:SPITransferResponse:data(@property)"
        return ''.join(chr(x) for x in self._data[:self.length])


class SPITransferCommand(Structure):
    #print "commands.py:SPITransferCommand"
    COMMAND = 0x42
    RESPONSE = SPITransferResponse
    _fields_ = [('command', c_ubyte),
                ('length', c_ubyte),
                ('reserved', c_ushort),
                ('data', SPIBuffer)]

    def __init__(self, data):
        #print "commands.py:SPITransferCommand:__init__"
        data = SPIBuffer(*(ord(x) for x in data))
        super(SPITransferCommand, self).__init__(self.COMMAND, len(data), 0x0000, data)


class DeviceStatusResponse(Response):
    #print "commands.py:DeviceStatusResponse"
    _fields_ = [('command', c_ubyte),
                ('status', c_ubyte),
                ('bus_release_status', c_ubyte),
                ('bus_owner', c_ubyte),
                ('password_attempts', c_ubyte),
                ('password_guessed', c_ubyte)]


class CancelTransferCommand(Command):
    #print "commands.py:CancelTransferCommand"
    COMMAND = 0x11
    SUBCOMMAND = 0x00
    RESPONSE = DeviceStatusResponse
    _fields_ = [('header', CommandHeader)]
