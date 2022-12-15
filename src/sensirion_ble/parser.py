from __future__ import annotations

import logging
import struct

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, Units

from .const import COMPANY_IDENTIFIER

_LOGGER = logging.getLogger(__name__)


def _convert_advertisement(
    raw_data: bytes,
) -> tuple[str | None, dict[tuple[DeviceClass, Units], float]] | None:
    """
    Convert a Sensirion advertisement to a device name and a dictionary of sensor values.
    """
    if raw_data[0] == b"\x00":
        samples = _parse_data_type(int(raw_data[1]), raw_data[4:])
        if not samples:
            return None
        return raw_data[2:4].hex().upper(), samples
    _LOGGER.debug("Data format not supported: %s", raw_data)
    return None


'''
Functions beneath are adjusted copies from: custom_components/ble_monitor/ble_parser/sensirion.py

The following functions are based on Sensirion_GadgetBle_Lib.cpp from  https://github.com/Sensirion/arduino-ble-gadget/
support from other devices should be easily added by looking at GadgetBle::setDataType and updating _parse_data_type 
accordingly. Note that the device name also has to be added to the SENSIRION_DEVICES list.
'''


def _parse_data_type(advSampleType, byte_data) -> dict[tuple[DeviceClass, Units], float]:
    if advSampleType == 3:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[4:6])
        }
    elif advSampleType == 4:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4])
        }
    elif advSampleType == 6:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV2(byte_data[2:4])
        }
    elif advSampleType == 8:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[4:6])
        }
    elif advSampleType == 10:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[4:6])
        }
    elif advSampleType == 12:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[4:6]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V1(byte_data[6:8])
        }
    elif advSampleType == 14:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            # 'hcho': _decodeHCHOV1(byte_data[4:6]) # device class not available in home assistant
        }
    elif advSampleType == 16:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[4:6]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V1(byte_data[6:8])
        }
    elif advSampleType == 20:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[4:6]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[6:8]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V1(byte_data[8:10]),
            # 'hcho': _decodeHCHOV1(byte_data[10:12]) # device class not available in home assistant
        }
    elif advSampleType == 22:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[4:6]),
            (DeviceClass.NITROUS_OXIDE, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[6:8])
        }
    elif advSampleType == 24:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[4:6]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V2(byte_data[8:10])
        }
    elif advSampleType == 26:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[4:6]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[6:8]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V2(byte_data[10:12])
        }
    elif advSampleType == 28:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[4:6]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V2(byte_data[6:8])
        }
    elif advSampleType == 30:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[4:6]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V2(byte_data[6:8])
        }
    elif advSampleType == 32:
        return {
            (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): _decodeTemperatureV1(byte_data[0:2]),
            (DeviceClass.HUMIDITY, Units.PERCENTAGE): _decodeHumidityV1(byte_data[2:4]),
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[4:6]),
            (DeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[6:8]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodePM2p5V2(byte_data[8:10]),
            # 'hcho': _decodeHCHOV1(byte_data[10:12]) # device class not available in home assistant
        }
    elif advSampleType == 32:
        return {
            (DeviceClass.PM1, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[0:2]),
            (DeviceClass.PM25, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[2:4]),
            # 'pm4': _decodeSimple(byte_data[4:6]), # device class not available in home assistant
            (DeviceClass.PM10, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER): _decodeSimple(byte_data[6:8]),
        }
    elif advSampleType == 34:
        return {
            (DeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION): _decodeSimple(byte_data[0:2])
        }
    else:
        _LOGGER.debug("Advertisement SampleType %s not supported", advSampleType)


def _decodeSimple(byte_data):
    # GadgetBle::_convertSimple - return static_cast<uint16_t>(value + 0.5f);
    return int.from_bytes(byte_data, byteorder='little')


def _decodeTemperatureV1(byte_data):
    # GadgetBle::_convertTemperatureV1 - return static_cast<uint16_t>((((value + 45) / 175) * 65535) + 0.5f);
    return round((int.from_bytes(byte_data, byteorder='little') / 65535) * 175 - 45, 2)


def _decodeHumidityV1(byte_data):
    # GadgetBle::_convertHumidityV1 - return static_cast<uint16_t>(((value / 100) * 65535) + 0.5f);
    return round((int.from_bytes(byte_data, byteorder='little') / 65535) * 100, 2)


def _decodeHumidityV2(byte_data):
    # GadgetBle::_convertHumidityV2 - return static_cast<uint16_t>((((value + 6.0) * 65535) / 125.0) + 0.5f);
    return round(((int.from_bytes(byte_data, byteorder='little') * 125 / 65535) - 6), 2)


def _decodePM2p5V1(byte_data):
    # GadgetBle::_convertPM2p5V1 - return static_cast<uint16_t>(((value / 1000) * 65535) + 0.5f);
    return round((int.from_bytes(byte_data, byteorder='little') / 65535) * 1000, 2)


def _decodePM2p5V2(byte_data):
    # GadgetBle::_convertPM2p5V2 - return static_cast<uint16_t>((value * 10) + 0.5f);
    return round(int.from_bytes(byte_data, byteorder='little') / 10, 2)


def _decodeHCHOV1(byte_data):
    # GadgetBle::_convertHCHOV1 - return static_cast<uint16_t>((value * 5) + 0.5f);
    return round(int.from_bytes(byte_data, byteorder='little') / 5, 2)


class SensirionBluetoothDeviceData(BluetoothData):
    """Data for Sensirion BLE sensors."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        try:
            raw_data = service_info.manufacturer_data[COMPANY_IDENTIFIER]
        except (KeyError, IndexError):
            _LOGGER.debug("Manufacturer ID not found in data")
            return None

        result = _convert_advertisement(raw_data)
        if result is None:
            return
        identifier, data = result
        self.set_device_type(f"Sensirion {service_info.name}")
        self.set_device_manufacturer("Sensirion AG")
        identifier = identifier or short_address(service_info.address)
        self.set_device_name(f"{service_info.name} {identifier}")
        for (device_class, unit), value in data.items():
            self.update_sensor(
                key=device_class,
                device_class=device_class,
                native_unit_of_measurement=unit,
                native_value=value,
            )
