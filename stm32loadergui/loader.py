import getopt
import os
import sys

from stm32loader import bootloader
from stm32loader.uart import SerialConnection


class LoaderConfig:
    def __init__(self, port=None, parity="E", baud=115200, family=None, address=0x08000000, erase=False, unprotect=False, swap_rts_dtr=False, reset_active_high=False, boot0_active_low=False):
        self.port = port
        self.parity = parity
        self.baud = baud
        self.family = family
        self.address = address
        self.erase = erase
        self.unprotect = unprotect
        self.swap_rts_dtr = swap_rts_dtr
        self.reset_active_high = reset_active_high
        self.boot0_active_low = boot0_active_low



class Stm32Loader:
    def __init__(self, config : LoaderConfig):
        self.config = config


    def connect(self):
        """Connect to the RS-232 serial port."""
        serial_connection = SerialConnection(
            self.config.port, self.config.baud, self.config.parity
        )
        try:
            serial_connection.connect()
        except IOError as e:
            return False

        serial_connection.swap_rts_dtr = self.config.swap_rts_dtr
        serial_connection.reset_active_high = self.config.reset_active_high
        serial_connection.boot0_active_low = self.config.boot0_active_low

        #show_progress = self._get_progress_bar(self.configuration["hide_progress_bar"])

        self.stm32 = bootloader.Stm32Bootloader(
            serial_connection, show_progress=show_progress
        )

        try:
            self.stm32.reset_from_system_memory()
            return True
        except bootloader.CommandError:
            self.stm32.reset_from_flash()
            return False

    def perform_commands(self):
        """Run all operations as defined by the configuration."""
        # pylint: disable=too-many-branches
        binary_data = None
        if self.configuration["write"] or self.configuration["verify"]:
            with open(self.configuration["data_file"], "rb") as read_file:
                binary_data = bytearray(read_file.read())
        if self.configuration["unprotect"]:
            try:
                self.stm32.readout_unprotect()
            except bootloader.CommandError:
                # may be caused by readout protection
                self.debug(0, "Erase failed -- probably due to readout protection")
                self.debug(0, "Quit")
                self.stm32.reset_from_flash()
                sys.exit(1)
        if self.configuration["erase"]:
            try:
                self.stm32.erase_memory()
            except bootloader.CommandError:
                # may be caused by readout protection
                self.debug(
                    0,
                    "Erase failed -- probably due to readout protection\n"
                    "consider using the -u (unprotect) option.",
                )
                self.stm32.reset_from_flash()
                sys.exit(1)
        if self.configuration["write"]:
            self.stm32.write_memory_data(self.configuration["address"], binary_data)
        if self.configuration["verify"]:
            read_data = self.stm32.read_memory_data(
                self.configuration["address"], len(binary_data)
            )
            try:
                bootloader.Stm32Bootloader.verify_data(read_data, binary_data)
                print("Verification OK")
            except bootloader.DataMismatchError as e:
                print("Verification FAILED: %s" % e, file=sys.stdout)
                sys.exit(1)
        if not self.configuration["write"] and self.configuration["read"]:
            read_data = self.stm32.read_memory_data(
                self.configuration["address"], self.configuration["length"]
            )
            with open(self.configuration["data_file"], "wb") as out_file:
                out_file.write(read_data)
        if self.configuration["go_address"] != -1:
            self.stm32.go(self.configuration["go_address"])

    def reset(self):
        """Reset the microcontroller."""
        self.stm32.reset_from_flash()

    def read_device_id(self):
        """Show chip ID and bootloader version."""
        boot_version = self.stm32.get()
        self.debug(0, "Bootloader version: 0x%X" % boot_version)
        device_id = self.stm32.get_id()
        self.debug(
            0, "Chip id: 0x%X (%s)" % (device_id, bootloader.CHIP_IDS.get(device_id, "Unknown"))
        )

    def read_device_uid(self):
        """Show chip UID and flash size."""
        family = self.family
        if not family:
            return

        try:
            if family != "F4":
                flash_size = self.stm32.get_flash_size(family)
                device_uid = self.stm32.get_uid(family)
            else:
                # special fix for F4 devices
                flash_size, device_uid = self.stm32.get_flash_size_and_uid_f4()
        except bootloader.CommandError as e:
            self.debug(
                0, "Something was wrong with reading chip family data: " + str(e),
            )
            return

        device_uid_string = self.stm32.format_uid(device_uid)
        return (device_uid_string, flash_size)
