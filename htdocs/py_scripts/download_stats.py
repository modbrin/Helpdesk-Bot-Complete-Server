#!python.exe
import cgi
import user_activation_dates
import sys
import datetime

now = datetime.datetime.now()


today = "%s.%s.%s"%(now.day,now.month,now.year)

filename = "user_stats_" + today + ".xls"
user_activation_dates.update()
print("Content-type: application/octet-stream")
print("Content-Disposition: attachment; filename=%s" %(filename))
print("Location:/py_scripts/user_statistics/actual_data.xls\r\n")

