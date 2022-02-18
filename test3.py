import pandas as pd

data = pd.read_csv('static/uploads/sample.csv')
data.head()
i = 0
for col in data.columns:
    i += 1
print(i)

class vehiclelist:
    def __init__(self, vehicleno, holdername, holdertype, carmake, company):
        self.vehicleno = vehicleno
        self.holdername = holdername
        self.holdertype = holdertype
        self.carmake = carmake
        self.company = company

vehiclein = []

if i == 5:


    for i, row in data.iterrows():
        if "," in str(row[0]):
            data2 = row[0].split(",")
            data2.pop(1)
            if "nan" in str(row[3]):
                row[3] = "No Model Found"
            if "nan" in str(row[4]):
                row[4] = "No Company Found"
            if "/" in str(row[3]):
                data3 = row[3].split(" / ")
                data3.pop(1)
                vehiclein.append(vehiclelist(data2[0], row[1],row[2],data3[0],row[4]))

    for i, row in data.iterrows():
        if "," in str(row[0]):
            data2 = row[0].split(",")
            data2.pop(0)
            if "nan" in str(row[3]):
                row[3] = "No Model Found"
            if "nan" in str(row[4]):
                row[4] = "No Company Found"
            if(data2[0] != ""):
                if "/" in str(row[3]):
                    data3 = row[3].split(" / ")
                    data3.pop(0)
                    vehiclein.append(vehiclelist(data2[0], row[1],row[2],data3[0],row[4]))




    for i, row in data.iterrows():
        flag = 0
        if "," in str(row[0]) or "nan" in str(row[0]):
            flag = 1
        if "nan" in str(row[3]):
            row[3] = "No Model Found"
        if "nan" in str(row[4]):
            row[4] = "No Company Found"
        if not flag:
            vehiclein.append(vehiclelist(row[0], row[1],row[2],row[3],row[4]))


    for row in vehiclein:
        print(row.vehicleno, row.carmake)

else:
    print("Your total excel columns should only have 5")
