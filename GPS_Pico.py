from machine import UART, Pin
import io

adaGPS = UART(0, 9600)
adaGPS.write(b'$PMTK314,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1*34\r\n')

nmea_list = ['$GPGGA', '$GPGSA', '$GPRMC', '$GPZDA']

def speedCalc(data, u):
    #converts speed to user required units
    if u == 1:
        d = round((float(data) * 1.150779448),1)
        return '{} MPH'.format(d) 
    elif u == 2:
        d = round((float(data) * 1.852),1)
        return '{} KM/H'.format(d)
    elif u == 3:
        d = round((float(data) * 1.943844),1)
        return '{} m/s'.format(d)
    else:
        d = round(float(data),1)
        return '{} kn'.format(d)

def coordDecode(data, b):
    #decodes lat and lon co-ordinates from GPS NMEA
    sec = round((60*float("0.{}".format(data.split('.')[1]))),4)
    return '{}{} {}m {}s'.format(data.split('.')[0][0:-2],b, data.split('.')[0][-2:],sec)


def nmeaDecode(data):
    #create dictionary to put data into
    nmea_dict = {}
    
    # for each NMEA sentence, extract the data required
    # and add it to the dictionary
    for x in data:
        if x[0] == '$GPGGA':
            nmea_dict['satelites'] = int(x[7])
            nmea_dict['altitude'] = '{} {}'.format(x[9], x[10])

        elif x[0] == '$GPGSA':
            nmea_dict['fix'] = True if int(x[2]) > 1 else False
            nmea_dict['fix_type'] = '{}D'.format(x[2]) if int(x[2]) > 1 else 'N/A'
        
        elif x[0] == '$GPRMC':
            #decodes lat and lon to degrees and mins
            nmea_dict['latitude'] = coordDecode(x[3], x[4])
            nmea_dict['longitude'] = coordDecode(x[5], x[6])
        
            # for speed, it can be calculated in MPH, KM/H, m/s Knots
            # 1 = MPH | 2 = KM/H | 3 = m/s | any other no. for knots
            nmea_dict['speed'] = speedCalc(x[7], 1)
        elif x[0] == '$GPZDA':
            # gets the date and time from GPS
            nmea_dict['date_time'] = '{}/{}/{} {}:{}:{}'.format(x[2], x[3], x[4][-2:],x[1][0:2], x[1][2:4], x[1][4:6])
    return nmea_dict

while 1:

    # create a list for NMEA sentences
    l=[]
    # Get NMEA sentence
    s = adaGPS.readline().decode('utf-8').strip().split(',')
    if s[0] == '$GPGGA':
        for x in nmea_list:
            l.append(s)
            s = adaGPS.readline().decode('utf-8').strip().split(',')
        data = nmeaDecode(l)
        fix = '{}, {}, {}'.format('Yes' if data['fix'] else 'No', data['fix_type'], data['satelites'])
        print('''
            Lat :  {}\tSpeed    : {}
            Lon : {}\tAltitude : {}
            UTC : {}\tFix      : {} Sats
            '''.format(data['latitude'],data['speed'], data['longitude'], data['altitude'], data['date_time'], fix))