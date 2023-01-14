from netmiko import ConnectHandler
from tabulate import tabulate
import json
from getpass import getpass
import os
import pyfiglet

neighbor_data = [
    {"device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "cisco",
    "password": "cisco"}]

##################################################################################################################################################

def find_mac():

    print("\n-----| DATOS DE BUSQUEDA MAC |-----\n")

    target = input("Ingrese la mac del dispositivo: ")
    target = (target.replace("-","")).lower()

    target = list(target)
    target.insert(4,".")
    target.insert(9,".")
    target = "".join(target)

    print("\n-----| DATOS DEL PRIMER SWITCH |-----\n")

    c_ipsw = input("Ingrese la ip: ")
    c_user = input("Ingrese el usuario ssh: ")
    c_pass = getpass("Ingrese la contraseña ssh: ")
    c_enap = getpass("Ingrese la enable password: ")

    print("")

    c_data = {
    "host": c_ipsw,
    "username": c_user,
    "password": c_pass,
    "device_type": "cisco_ios",
    "secret": c_enap,}

    Connect_Device = ConnectHandler(**c_data)
    Connect_Device.enable()

    while ciclo == 1: 
        command_mac = Connect_Device.send_command("show mac address-table",use_textfsm = True)
        command_mac = json.loads(command_mac)

        command_cdp = Connect_Device.send_command("show cdp neighbors detail",use_textfsm = True)
        command_cdp = json.loads(command_cdp)

        command_run = Connect_Device.send_command("show run | include hostname")

        try:
            for device  in range(len(command_cdp)):
                puertov = (command_cdp[device]["local_port"])

            if "Gigabit" in puertov:
                puertov = (puertov[0:2]) + (puertov[15:])
            elif "Fastet" in puertov:
                puertov = (puertov[0:2]) + (puertov[12:])
            else:
                puertov = ("No hay puerto")
            (command_cdp[device]["local_port"]) = puertov

        except:
            pass

        try:
            for mac in range(len(command_mac)):
                if target == (command_mac[mac]['destination_address']):
                    puerto_mac = (command_mac[mac]['destination_port'][0])
                else: pass
            
            for vecino in range(len(command_cdp)):
                puerto_v = (command_cdp[vecino]["local_port"])
                ip_ssh = (command_cdp[vecino]["management_ip"])

                neighbor_data.append[{"device_type": "cisco_ios","host": ip_ssh,"username": "cisco","password": "cisco",}]

                try:
                    if puerto_v == puerto_mac:
                        c_data["host"]=ip_ssh
                        Connect_Device.enable()
                    else:
                        print(f'''
                        Mac objetivo: {target}
                        Estatus de busqueda: "Exitosa"
                        Puerto conectado: {puerto_mac}
                        Nombre del switch: {command_run}
                        ''')

                        ciclo = 0
                        Connect_Device.disconnect()
                        break

                except:
                    print(f'''
                    Mac objetivo: {target}
                    Estatus de busqueda: "Fallida"
                    Lamac objetivo no fue encontrada
                    ''')

                    ciclo = 0
                    Connect_Device.disconnect()
                    break

        except:
            pass

###########################################################################################################################################

def save_config():
    host = input("Enter device hostname or IP: ")
    username = input("Enter your username: ")
    password = getpass()

    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**device) as ssh:
        output = ssh.send_command("show run")

        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, 'Desktop', 'configs')
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, f"{host}_config.txt")
        with open(config_file, "w") as f:
            f.write(output)

    print(f"Configuration saved to {config_file}")

##########################################################################################################################################

def get_neighbors(device):
    neighbors = []
    with ConnectHandler(**device) as ssh:
        output = ssh.send_command("show cdp neighbors")
        for line in output.splitlines():
            if "Eth" in line:
                fields = line.split()
                neighbors.append(
                    {
                        "hostname": fields[0],
                        "interface": fields[1],
                        "local_interface": fields[-2],
                    })

    return neighbors

def build_topology(devices):
    topology = {}
    for device in devices:
        neighbors = get_neighbors(device)
        topology[device["host"]] = neighbors
    return topology

def knowed_topology():
    topology = build_topology(neighbor_data)

    headers = ["Device", "Neighbor", "Interface", "Neighbor Interface"]
    table = []
    for sw, neighbors in topology.items():
        for neighbor in neighbors:
            table.append([sw, neighbor["hostname"], neighbor["local_interface"], neighbor["interface"]])
    print(tabulate(table, headers=headers))

###################################################################################################################################

def banner():
    print("\n-----| Ingrese los datos del dispositivo donde quiere establecer el banner |-----\n")

    b_ipsw = input("Ingrese la ip: ")
    b_user = input("Ingrese el usuario ssh: ")
    b_pass = getpass("Ingrese la contraseña ssh: ")
    b_enap = getpass("Ingrese la enable password: ")

    c_data = {
    "host": b_ipsw,
    "username": b_user,
    "password": b_pass,
    "device_type": "cisco_ios",
    "secret": b_enap,}

    Connect_Device = ConnectHandler(**c_data)
    Connect_Device.enable()

    text = input("Enter text for the banner: ")

    # Use pyfiglet to convert text to ASCII art
    ascii_banner = pyfiglet.figlet_format(text)

    # Print the banner
    print("El banner a establecer sera:\n",ascii_banner)

    Connect_Device.send_command(f"banner motd ${ascii_banner}$")

############################################################################################################################################
def menu():
    print("""
                        -----| MENU |-----
    ^-------------------------------------------------------^
    FUNCIONES DEL PROGRAMA:

    1) - BUSQUEDA DE DISPOSITIVOS VIA MAC

    2) - TOPOLOGIA CONOCIDA (SE AMPLIA CON BUSQUEDAS DE MAC)

    3) - ALMACENAMIENTO DE CONFIGURACIONES EN UN TXT

    4) - ESTABLECER UN BANNER PERSONALIZADO
    ^-------------------------------------------------------^

    """)

    choice = input("QUE FUNCION QUIERE EJECUTAR: ")

    if choice == "1":
        os.system("cls")
        print("-----| BUSQUEDA DE DISPOSITIVOS VIA MAC |-----")
        find_mac()

    elif choice == "2":
        os.system("cls")
        print("-----| TOPOLOGIA CONOCIDA |-----")
        knowed_topology()

    elif choice == "3":
        os.system("cls")
        print("-----| ALMACENAMIENTO DE CONFIGURACIONES EN UN TXT |-----")
        save_config()

    elif choice == "4":
        os.system("cls")
        print("-----| ESTABLECER UN BANNER PERSONALIZADO |-----")
        banner()

    else:
        os.system("cls")
        print("Error en la entrada, ingrese un numero de la opcion")
        menu()

menu()