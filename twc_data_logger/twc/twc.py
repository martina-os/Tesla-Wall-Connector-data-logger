import json
import requests
import certifi

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

#Token input
token_text = open("token.txt", "r")
token_s = token_text.read().replace('\n', '').replace(' ','')

if (token_s == ""):
    token_i = input("Enter the Token:")
    
    token_text= open("token.txt", "w")
    t_write = token_text.write(token_i)
    token_text.close()
    
    token_text2 = open('token.txt', 'r')
    token_s = token_text2.read().replace('\n', '').replace(' ','')
    print("Token: " + token_s)
    token_text2.close()
else:
    print("Token: " + token_s)
    token_text.close()

#Org input
org_text = open("org.txt", "r")
org_s = org_text.read().replace('\n', '').replace(' ','')

if (org_s == ""):
    org_i = input("Enter the org:")
    
    org_text= open("org.txt", "w")
    t_write = org_text.write(org_i)
    org_text.close()
    
    org_text2 = open('org.txt', 'r')
    org_s = org_text2.read().replace('\n', '').replace(' ','')
    print("Org: " + org_s)
    org_text2.close()
else:
    print("Org: " + org_s)
    org_text.close()

#URL input
url_text = open("url.txt", "r")
url_s = url_text.read().replace('\n', '').replace(' ','')

if (url_s == ""):
    url_i = input("Enter the url:")
    
    url_text= open("url.txt", "w")
    t_write = url_text.write(url_i)
    url_text.close()
    
    url_text2 = open('url.txt', 'r')
    url_s = url_text2.read().replace('\n', '').replace(' ','')
    print("URL: " + url_s)
    url_text2.close()
else:
    print("URL: " + url_s)
    url_text.close()

#InfluxDB authorization to the database
token = str(token_s)
org = str(org_s)
url = str(url_s)
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, ssl_ca_cert=certifi.where())


#InfluxDB bucket creating and sending data to database
bucket="baza"

#IP address input
text = open("ip_address.txt", "r")
ip = text.read().replace('\n', '').replace(' ','')

if (ip == ""):
    ip_adr = input("Enter the IP address:")
    
    text= open("ip_address.txt", "w")
    write = text.write(ip_adr)
    text.close()
    
    text2 = open('ip_address.txt', 'r')
    ip = text2.read().replace('\n', '').replace(' ','')
    print("IP address: " + ip )
    text2.close()
else:
    print("IP address: " + ip )
    text.close()



#vitals
api_url = 'http://' + str(ip) + '/api/1/vitals'
print(api_url)
#lifetime
api_liftime_url = 'http://' + str(ip) + '/api/1/lifetime'
print(api_liftime_url)
#wifi_status
api_wifi_url = 'http://' + str(ip) + '/api/1/wifi_status'
print(api_wifi_url)


while (True):
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while (True):
        try:
            objava = json.loads(requests.get(api_url, timeout=5).content.decode('UTF-8'))
            objava_liftime = json.loads(requests.get(api_liftime_url, timeout=5).content.decode('UTF-8'))
            objava_wifi = json.loads(requests.get(api_wifi_url, timeout=5).content.decode('UTF-8'))
            print("Data fetched")
            break
        except:
            print("No connection to TWC!")
            time.sleep(5)

    #---------
    #api vitals

    currentA_a = objava['currentA_a']
    currentB_a = objava['currentB_a']
    currentC_a = objava['currentC_a']
    currentN_a = objava['currentN_a']
    vehicle_current_a = objava['vehicle_current_a']

    voltageA_v = objava['voltageA_v']
    voltageB_v = objava['voltageB_v']
    voltageC_v = objava['voltageC_v']
    relay_coil_v = objava['relay_coil_v']
    grid_v = objava['grid_v']
    grid_hz = objava['grid_hz']

    pilot_high_v = objava['pilot_high_v']
    pilot_low_v = objava['pilot_low_v']
    prox_v = objava['prox_v']
    config_status = objava['config_status']
    evse_state = objava['evse_state']

    pcba_temp_c = objava['pcba_temp_c']
    handle_temp_c = objava['handle_temp_c']
    mcu_temp_c = objava['mcu_temp_c']

    input_thermopile_uv = objava['input_thermopile_uv']


    #contactor closed? returns string bcs boolean can't be shown in InfluxDB
    contactor_closed = objava['contactor_closed']
    def bool_str(bool_var):
        if(bool_var == True):
            return "True"
        else:
            return "False"
    contactor_closed_str = bool_str(contactor_closed)
    #vehicle connected? returns string bcs boolean can't be shown
    vehicle_connected = objava['vehicle_connected']
    def if_connected(bool_var):
        if(bool_var == True):
            return "Vehicle is connected."
        else:
            return "Vehicle is not connected."

    vozilo_spojeno = if_connected(vehicle_connected)

    #time in hours, minutes and seconds
    session_s = objava['session_s']
    import datetime
    def sec_to_hours(sec):
        return str(datetime.timedelta(seconds=sec))
    session = sec_to_hours(session_s)

    #wh to kWh
    session_energy_wh= objava['session_energy_wh']
    def kWh(n):
        return float(n/1000)
    session_energy_kwh = kWh(session_energy_wh)

    #price
    def price(x):
        return float(((x/1000)*0.312)/7.52)
    cijena = price(session_energy_wh)

    #power
    def power(a,b):
        return float((a*b)/1000)
    powerA_kw= power(currentA_a, voltageA_v)
    powerB_kw = power(currentB_a, voltageB_v)
    powerC_kw = power(currentC_a, voltageC_v)

    #total_charging_power
    def total_charg_pw(a,b,c):
        return float(a+b+c)
    total_charging_power = total_charg_pw(powerA_kw, powerB_kw, powerC_kw)


    #--------------------------------
    #liftime

    charging_time_s = objava_liftime['charging_time_s']
    charging_time_h = sec_to_hours(charging_time_s)

    energy_wh = objava_liftime['energy_wh']
    energy_kwh = kWh(energy_wh)

    #total_electricity_cost
    total_electricity_cost = price(energy_wh)

    #uptime
    uptime_s = objava_liftime['uptime_s']
    uptime_h = sec_to_hours(uptime_s)

    #----------------------------------
    #wifi_status

    wifi_signal_strength = objava_wifi['wifi_signal_strength']

    wifi_connected = objava_wifi['wifi_connected']
    wifi_connected_str = bool_str(wifi_connected)

    #--------------------------------
    point = (
        Point("objava")
        #vitals
        .field("session", session)
        .field("contactor_closed_str", contactor_closed_str)
        .field("vehicle_connected", vozilo_spojeno)

        .field("currentA_a", currentA_a)
        .field("currentB_a", currentB_a)
        .field("currentC_a", currentC_a)
        .field("currentN_a", currentN_a)
        .field("vehicle_current_a", vehicle_current_a)

        .field("voltageA_v", voltageA_v)
        .field("voltageB_v", voltageB_v)
        .field("voltageC_v", voltageC_v)
        .field("relay_coil_v", relay_coil_v)
        .field("grid_hz", grid_hz)
        .field("grid_v", grid_v)

        .field("pilot_high_v", pilot_high_v)
        .field("pilot_low_v", pilot_low_v)
        .field("prox_v", prox_v)
        .field("config_status", config_status)
        .field("evse_state", evse_state)


        .field("pcba_temp_c", pcba_temp_c)
        .field("handle_temp_c", handle_temp_c)
        .field("mcu_temp_c", mcu_temp_c)

        .field("input_thermopile_uv", input_thermopile_uv)

        .field("session_energy_kwh", session_energy_kwh)
        .field("session_energy_wh", session_energy_wh)

        .field("electricity_cost", cijena)

        .field("powerA_kw", powerA_kw)
        .field("powerB_kw", powerB_kw)
        .field("powerC_kw", powerC_kw)
        .field("total_charging_power_kw", total_charging_power)

        #liftime
        .field("charging_time_h", charging_time_h)
        .field("energy_kwh", energy_kwh)
        .field("total_electricity_cost", total_electricity_cost)
        .field("uptime_h", uptime_h)
        
        #wifi_status
        .field("wifi_signal_strength", wifi_signal_strength)
        .field("wifi_connected_str", wifi_connected_str)
        
    )

    while (True):
        try:
            write_api.write(bucket=bucket, org= str(org_s), record=point)
            print("Data sent")
            break
        except:
            print("No connection to InfluxDB!")
            time.sleep(5)
    
    time.sleep(30) # separate points