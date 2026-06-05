#!/usr/bin/env python3
"""
Bluetooth pairing helper for ELM327
Uses D-Bus BlueZ API to pair and connect
"""
import dbus
import dbus.exceptions
import dbus.service
import dbus.mainloop.glib
import time
import subprocess
import sys
from gi.repository import GLib

OBD_MAC = "A2:2A:19:04:00:00"

BUS_NAME = "org.bluez"
AGENT_PATH = "/test/agent"
AGENT_INTERFACE = "org.bluez.Agent1"

class Agent(dbus.service.Object):
    def __init__(self, bus, path):
        self.exit_on_release = True
        dbus.service.Object.__init__(self, bus, path)

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print(f"RequestPinCode ({device}) -> 0000")
        return "0000"

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print(f"RequestPasskey ({device}) -> 0000")
        return dbus.UInt32(0)

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print(f"DisplayPasskey ({device}): {passkey:06d} entered {entered}")

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print(f"DisplayPinCode ({device}): {pincode}")

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print(f"RequestConfirmation ({device}): {passkey:06d}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print(f"RequestAuthorization ({device})")

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print(f"AuthorizeService ({device}, {uuid})")
        return

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Get BlueZ object manager
    obj_manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                 "org.freedesktop.DBus.ObjectManager")

    # Find the adapter
    objects = obj_manager.GetManagedObjects()
    adapter_path = None
    for path, ifaces in objects.items():
        if "org.bluez.Adapter1" in ifaces:
            adapter_path = path
            break

    if not adapter_path:
        print("No Bluetooth adapter found")
        sys.exit(1)

    print(f"Adapter: {adapter_path}")

    # Get device object path
    device_path = None
    for path, ifaces in objects.items():
        if "org.bluez.Device1" in ifaces:
            props = ifaces["org.bluez.Device1"]
            if props.get("Address") == OBD_MAC:
                device_path = path
                break

    if not device_path:
        print(f"Device {OBD_MAC} not found, need to scan...")
        # Remove device first if exists
        subprocess.run(["bluetoothctl", "remove", OBD_MAC], capture_output=True)
        # Scan
        subprocess.run(["bluetoothctl", "--timeout", "5", "scan", "on"], capture_output=True, timeout=10)
        # Re-check
        objects = obj_manager.GetManagedObjects()
        for path, ifaces in objects.items():
            if "org.bluez.Device1" in ifaces:
                props = ifaces["org.bluez.Device1"]
                if props.get("Address") == OBD_MAC:
                    device_path = path
                    break
        if not device_path:
            print(f"Device {OBD_MAC} not found after scan. Is it powered on?")
            sys.exit(1)

    print(f"Device path: {device_path}")

    # Trust
    dev_props = dbus.Interface(bus.get_object("org.bluez", device_path),
                               "org.freedesktop.DBus.Properties")
    dev_props.Set("org.bluez.Device1", "Trusted", dbus.Boolean(True))

    # Register agent
    agent = Agent(bus, AGENT_PATH)
    agent_manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"),
                                   "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    agent_manager.RequestDefaultAgent(AGENT_PATH)
    print("Agent registered")

    # Pair
    device = dbus.Interface(bus.get_object("org.bluez", device_path),
                             "org.bluez.Device1")
    print("Pairing...")
    try:
        device.Pair()
        print("Pairing initiated, waiting...")
    except dbus.exceptions.DBusException as e:
        if "AlreadyExists" in str(e):
            print("Already paired")
        else:
            print(f"Pair error: {e}")

    time.sleep(3)

    # Check status
    props = dev_props.GetAll("org.bluez.Device1")
    print(f"Paired: {props.get('Paired')}")
    print(f"Connected: {props.get('Connected')}")

    if not props.get('Paired'):
        print("Not paired, trying connect...")
        try:
            device.Connect()
        except dbus.exceptions.DBusException as e:
            print(f"Connect error: {e}")

    time.sleep(2)
    props = dev_props.GetAll("org.bluez.Device1")
    print(f"After connect - Paired: {props.get('Paired')}, Connected: {props.get('Connected')}")

    # Cleanup
    agent_manager.UnregisterAgent(AGENT_PATH)

if __name__ == "__main__":
    main()
