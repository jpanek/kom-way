
# read last 100 lines from log 

sudo tail -n 100 -f /var/log/nginx/kom-way_access.log | python3 -c '
import sys
for line in sys.stdin:
    if "garmin-weather" in line:
        clean = line.replace("\\x0A", " ").replace("\\x22", "\"")
        print(clean, end="")
'


#check unique IPs in current log file:
awk '{print $1}' /var/log/nginx/kom-way_access.log | sort | uniq | wc -l

awk '{print $1}' /var/log/nginx/kom-way_access.log | sort | uniq -c | sort -nr

#check counts of errors in log
grep "garmin-weather" /var/log/nginx/kom-way_access.log | awk -F'"' '{print $3}' | awk '{print $1}' | sort | uniq -c