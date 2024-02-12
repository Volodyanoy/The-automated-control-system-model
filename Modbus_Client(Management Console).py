#!/usr/bin/env python3

from pymodbus.client import ModbusTcpClient
from pymodbus.datastore import ModbusSimulatorContext


def my_client_run():
    """Combine setup and run."""
    client = ModbusTcpClient(host='192.168.0.104', port=502)  # Create client object
    client.connect()  # connect to device, reconnect automatically

    '''
    client.write_coil(1, False, slave=1)  # set information in device
    result_coil = client.read_coils(1, 8, slave=1)  # get information from device
    print(result_coil.bits)  # use information
    '''

    client.write_register(0, 4, slave=1)
    # client.write_register(2, 14, slave=1)
    # slave = modbus slave id
    # rr = client.read_holding_registers(0, 1, slave=1)
    #print(rr.registers)  # use information
    client.close()  # Disconnect device


if __name__ == "__main__":
    my_client_run()  # pragma: no cover


# master -  client
# slave  -  server

#  Таблица	                                Тип элемента	    Тип доступа
#  Регистры флагов (Coils)	                один бит	        чтение и запись
#  Дискретные входы (Discrete Inputs)	    один бит	        только чтение
#  Регистры ввода (Input Registers)	        16-битное слово	    только чтение
#  Регистры хранения (Holding Registers)    16-битное слово	    чтение и запись

# value = ModbusSimulatorContext.build_value_from_registers(rr.registers, True)
# print(value)

#  assuming all sizes are set to 10, the addresses for configuration are as follows:
# • coils have addresses 0-9,
# • discrete_inputs have addresses 10-19,
# • input_registers have addresses 20-29,
# • holding_registers have addresses 30-39



