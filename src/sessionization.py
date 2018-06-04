import sys
import csv
from datetime import datetime, timedelta

def endSession(user):
    ip = user['ip']
    curr_time = datetime.strptime(user['date']+' '+user['time'], TIME_FORMAT)
    end_time = curr_time + timedelta(seconds=int(inactivity_time)+1)
    if end_time not in track_session.keys(): ##create a new key (time, ip)
        track_session[end_time] = [ip]   
    else:
        if ip not in track_session[end_time]: ##treat ip as value
            track_session[end_time].append(ip)
    return ip, curr_time, end_time

def trackSession(ip, curr_time):
    if ip not in session:
        session[ip] = {'start':curr_time, 'end':curr_time, 'dur':1, 'req':1}
    else:
        session[ip]['end'] = curr_time
        session[ip]['dur'] = int((session[ip]['end'] - session[ip]['start']).total_seconds()) + 1
        session[ip]['req'] += 1

def updateSession():
    update = []
    for ips in track_session.values():
        for ip in ips:
            if ip not in update:
                logOutput(session, ip)
                update.append(ip)

def logOutput(session, ip):
    info = session[ip]
    with open(output_file_name, 'a') as final:
                    writer = csv.writer(final)
                    output = [ip, 
                              info['start'].strftime(TIME_FORMAT),
                              info['end'].strftime(TIME_FORMAT),
                              info['dur'], info['req']]
                    writer.writerow(output)
                    
#log_file_name = '/Users/Admin/Desktop/edgar-analytics-master/input/log.csv'
#inactivity_file_name = '/Users/Admin/Desktop/edgar-analytics-master/input/#inactivity_period.txt'
#output_file_name = '/Users/Admin/Desktop/edgar-analytics-master/output/sessionization.txt'

log_file_name =  sys.argv[1]
inactivity_file_name =  sys.argv[2]
output_file_name = sys.argv[3]
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

with open(inactivity_file_name) as a:
    inactivity_time = a.readlines()[0] #file contains a single integer value denoting the period of inactivity (in seconds) 

session = dict()
track_session = dict()
open(output_file_name, 'w').close()

try:
    with open(log_file_name) as b:
        log = csv.DictReader(b)
        for user in log:
            tip, now, end = endSession(user)
            if now in track_session.keys(): ##curr_time == end_session time
                temp = track_session[now]
                for ip in temp:
                    if session[ip]['end'] == now - timedelta(seconds=int(inactivity_time)+1):
                        logOutput(session, ip) ##output it             
                        track_session[now].remove(ip) ##remove it
                        del session[ip] #remove it
            trackSession(tip, now)
        updateSession()
except IOError as e:
    print('Operation failed: %s') % e.strerror