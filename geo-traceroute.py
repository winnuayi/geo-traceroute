import os
import subprocess
import sys

import GeoIP

# enum for normalized hops
HOP_IP = 1
COUNTRY = 3
CITY = 4
LON = 5
LAT = 6

PASSWORD = 'liverpool'

def read_dump(target):
    """DEPRECATED"""
    """Return a list of hops from previous dump."""
    f = open(target)
    hops = []
    for line in f:
        hops.append(line)
    f.close()
    return hops


def execute_traceroute(target):
    """Return a list of hops from traceroute command."""
    p = subprocess.Popen(
            ['sudo', 'paris-traceroute', target], 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            shell=False)
    text, _ = p.communicate(PASSWORD)
    hops = text.split('\n')
    return hops


def normalize(list_hops):
    """Extract information from traceroute line per line."""
    # get geoip instance
    gi = GeoIP.open('data/GeoLiteCity.dat', GeoIP.GEOIP_STANDARD)

    normalized_hops = []
    for hop in list_hops:
        # filer out if an empty line
        if len(hop) is 0:
            continue

        # clean information from unnecessary information
        hop = remove_chars(hop)

        # split them by space
        token = hop.split()

        # filter out
        if len(token) < 2:
            continue

        # filter out if the first element is not the order of number
        # and if the order of number does not exist (because of multiple hops)
        try:
            if not isinstance(int(token[0]), int): continue
        except TypeError:
            continue
        except ValueError:
            continue

        # remove number of order at the first element of token
        token.pop(0)

        # remove strip from '(ip)'
        token[1] = token[1].strip('()')

        # calculate average duration
        avg_duration = calculate_avg_duration(token)

        # extract information from traceroute
        hop_ip = token[HOP_IP]
        info = get_information(hop_ip, gi)
        
        # create a normalized hop
        if info is not None:
            token = token[0:2] + \
                        [avg_duration, info['country_name'], info['city'], 
                         info['longitude'], info['latitude']]
        else:
            token = token[0:2] + [avg_duration, None, None, None, None]

        # collect all normalized hops
        normalized_hops.append(token)
    return normalized_hops


def get_information(hop_ip, lib):
    """Return a complete information about an IP address using MaxMind Geolocation API."""
    return lib.record_by_addr(hop_ip)


def calculate_avg_duration(token):
    """Return average duration. Number of durations varies for each hop."""
    durations = token[2:]
    durations = [float(d) for d in durations]
    avg_duration = sum(durations) / len(durations)
    return avg_duration


def display(normalized_hops):
    """"""
    for hop in normalized_hops:
        server = hop[0]
        hop_ip = ""
        avg_duration = hop[2]
        country = ""
        city = ""
        lon = ""
        lat = ""

        #print hop
        if hop[HOP_IP] is not None: hop_ip = hop[HOP_IP]
        if hop[COUNTRY] is not None: country = hop[COUNTRY]
        if hop[CITY] is not None: city = hop[CITY]
        if hop[LON] is not None and hop[LAT] is not None: 
            lon = str(hop[LON])
            lat = str(hop[LAT])
            text = "%15s | %55s | %8.3f ms | %20s | %20s | %15s | %15s"
        else:
            text = "%15s | %55s | %8.3f ms | %20s | %20s | %15s | %15s"

        print text % (hop_ip, server, avg_duration, country, city, lon, lat)


def remove_chars(hop):
    """Remove unnecessary characters."""
    hop = hop.replace('*', '')
    hop = hop.replace('ms', '')
    hop = hop.replace('!X', '')
    hop = hop.replace('!T0', '')
    hop = hop.replace('!T1', '')
    hop = hop.replace('!T2', '')
    hop = hop.replace('!T3', '')
    hop = hop.replace('!T4', '')
    hop = hop.replace('!T5', '')
    hop = hop.replace('!T6', '')
    hop = hop.replace('!T7', '')
    hop = hop.replace('!T8', '')
    hop = hop.replace('!T9', '')
    hop = hop.replace('!T10', '')
    hop = hop.replace('!A', '')
    return hop


### MAIN PROGRAM ###
if __name__ == '__main__':
    # get target server
    target = sys.argv[1]

    list_hops = execute_traceroute(target)

    # remove clutters
    normalized_hops = normalize(list_hops)

    # show result on screen
    display(normalized_hops)
