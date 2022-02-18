from datetime import datetime


startdate = datetime(2021, 6, 21, 18, 25, 30)
enddate = datetime(2021, 7, 21, 18, 25, 30)

teststart = "10/12/2021T10:10:10"
testend = "10/12/2021T11:10:10"

now = datetime.now()
datetimeformat = datetime.strftime(now,"%d-%m-%Y %H:%M:%S")

start = datetime.strptime(teststart, "%d/%m/%YT%H:%M:%S")
end = datetime.strptime(testend, "%d/%m/%YT%H:%M:%S")

datediff = (end-start)
sec = datediff.total_seconds()
diff = sec/60

print(datetimeformat)