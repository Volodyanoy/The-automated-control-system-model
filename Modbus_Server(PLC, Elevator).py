import asyncio
import logging
import time
import tkinter as tk
import helper
import threading
import elevator_app
from tkinter import Label
#from elevator import ElevatorSimulator  # Импортируем класс ElevatorSimulator
from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer

_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)

current_floor = 1

def setup_server(description=None, context=None, cmdline=None):
    """Run server setup."""
    args = helper.get_commandline(server=True, description=description, cmdline=cmdline)
    if context:
        args.context = context
    if not args.context:
        _logger.info("### Create datastore")
        if args.store == "sequential":
            datablock = ModbusSequentialDataBlock(0x00, [1] * 100)
        elif args.store == "sparse":
            datablock = ModbusSparseDataBlock({0x00: 0, 0x05: 1})
        elif args.store == "factory":
            datablock = ModbusSequentialDataBlock.create()

        if args.slaves:
            context = {
                0x01: ModbusSlaveContext(
                    di=datablock,
                    co=datablock,
                    hr=datablock,
                    ir=datablock,
                ),
                0x02: ModbusSlaveContext(
                    di=datablock,
                    co=datablock,
                    hr=datablock,
                    ir=datablock,
                ),
                0x03: ModbusSlaveContext(
                    di=datablock,
                    co=datablock,
                    hr=datablock,
                    ir=datablock,
                    zero_mode=True,
                ),
            }
            single = False
        else:
            context = ModbusSlaveContext(
                di=datablock, co=datablock, hr=datablock, ir=datablock
            )
            single = True

        # Build data storage
        args.context = ModbusServerContext(slaves=context, single=single)

    args.identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": pymodbus_version,
        }
    )
    return args

async def run_async_server(args):
    """Run server."""
    txt = f"### start ASYNC server, listening on {args.port} - {args.comm}"
    _logger.info(txt)
    if args.comm == "tcp":
        address = (args.host if args.host else "", args.port if args.port else None)
        server = await StartAsyncTcpServer(
            context=args.context,  # Data storage
            identity=args.identity,  # server identify
            address=address,  # listen address
        )
    return server

async def check_registers(args):
    while True:
        values = args.context[0x00].getValues(3, 0x00, count=6)
        #print("Values:", values)
        global current_floor
        current_floor = int(values[0])
        print("Номер этажа в регистре ПЛК:", current_floor)
        await asyncio.sleep(7)


class ElevatorSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Модуль \"Лифт\" ")

        self.canvas = tk.Canvas(root, width=150, height=300)
        self.canvas.pack()

        # Рисуем лифтовую шахту
        self.canvas.create_line(75, 0, 75, 300, fill="#CCCCCC", width=50)

        self.elevator = self.canvas.create_rectangle(60, 270, 90, 290, fill="#555555")
        self.floor_height = 30

        self.current_floor = 1
        self.target_floor = 1
        self.is_moving = False

        self.floor_label = tk.Label(root, text=f"Текущий этаж: {self.current_floor}")
        self.floor_label.pack()

    def move_elevator_forever(self, my_time):
        while True:
            time.sleep(my_time)
            self.move_elevator(current_floor)

    def move_elevator(self, target_floor):
        if not self.is_moving:
            try:
                self.target_floor = target_floor
                if self.target_floor < 1:
                    print("Этаж не может быть меньше 1.")
                elif self.target_floor > 20:
                    print("Максимальный этаж - 10.")
                elif self.target_floor == self.current_floor:
                    print("Лифт находится на этаже:", self.target_floor)
                else:
                    self.is_moving = True
                    # Добавляем задержку перед началом движения
                    self.root.after(1000, self.move)

            except ValueError:
                print("Введите корректный этаж.")

    def move(self):
        if self.current_floor < self.target_floor:
            self.current_floor += 1
        elif self.current_floor > self.target_floor:
            self.current_floor -= 1

        self.floor_label["text"] = f"Текущий этаж: {self.current_floor}"
        self.update_elevator_position()

        if self.current_floor != self.target_floor:
            self.root.after(1000, self.move)
        else:
            self.is_moving = False

    def update_elevator_position(self):
        elevator_y = 270 - (self.current_floor - 1) * self.floor_height
        self.canvas.coords(self.elevator, 60, elevator_y, 90, elevator_y + 20)


def start_app():
    root = tk.Tk()
    app = ElevatorSimulator(root)
    thr = threading.Thread(target=app.move_elevator_forever, args=(6,))
    thr.daemon = True
    thr.start()
    root.mainloop()

async def async_helper():
    """Combine setup and run."""
    _logger.info("Starting...")
    run_args = setup_server(description="Run asynchronous server")
    server_task = run_async_server(run_args)
    check_registers_task = check_registers(run_args)

    # Запуск GUI в отдельном потоке

    gui_thread = threading.Thread(target=start_app)
    gui_thread.daemon = True
    gui_thread.start()

    await asyncio.gather(server_task, check_registers_task)


if __name__ == "__main__":
    asyncio.run(async_helper(), debug=True)

