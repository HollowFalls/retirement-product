import customtkinter as tk
import xlsxwriter
import json
import os
class MyDb:
    def __init__(self, dbName):
        self.fileName = dbName + ".json"
        self.json = self.loadDatabase()
        self.collection = ""
    def loadDatabase(self):
        with open(self.fileName) as file:
            return json.load(file)

    def saveDatabase(self):
        with open(self.fileName, "w") as file:
           file.write(json.dumps(self.json, indent=4)) 

    def changeCollection(self, nameOfCol):
        try:
            self.json[nameOfCol]
        except KeyError:
            print("This collection is not in database, preparing collection.")
            self.json[nameOfCol] = []
        
        self.collection = nameOfCol
    def getAll(self):
        return self.json[self.collection]
    def find(self, query):
        key = list(query.keys())[0]
        for obj in self.json[self.collection]:
            if obj[key] == query[key]:
                return obj

    def create(self, obj):
        highestId = 0
        for user in self.json[self.collection]:
            if user["id"] >= highestId:
                highestId = user["id"] 
        highestId += 1
        obj["id"] = highestId
        self.json[self.collection].append(obj)
        self.saveDatabase()
        return obj
    
    def delete(self, query):
        key = list(query.keys())[0]
        for obj in self.json[self.collection]:
           if obj[key] == query[key]:
                self.json[self.collection].remove(obj)
                self.saveDatabase()
                return True 
        return False

    def update(self, query, updateObj):
        queryKey = list(query.keys())[0]
        updateKey = list(updateObj.keys())[0]
        for obj in self.json[self.collection]:
            if obj[queryKey] == query[queryKey]:
                obj[updateKey] == updateObj[updateKey]
                self.saveDatabase()
                return obj 
        return False

patra = []
tk.set_appearance_mode("dark")
tk.set_default_color_theme("dark-blue")
master = tk.CTk()
database = MyDb("users")

class Floor:
        def __init__(self, name):
                self.name = name
                patra.append(self)
                self.id = patra.index(self)

        def getWidth(self):
            maxWidth = 0
            for userName in [user["name"] for user in self.listUsers()]:
                currLen = len(userName)
                if currLen > maxWidth:
                    maxWidth = currLen
                 
            return maxWidth

        def getDiaperWidth(self, userId):
            maxWidth = 0
            for diaper in self.listDiapers(userId):
                currLen = len(diaper)
                if currLen > maxWidth:
                    maxWidth = currLen
            return maxWidth

        def listUsers(self):
            database.changeCollection(self.name)
            return database.getAll()
            
        def addUser(self, name):
            database.changeCollection(self.name)
            if name not in [user["name"] for user in database.getAll()]:
                if len(name) != 0: 
                    user = database.create({"name": name, "diapers": []})

        def removeUser(self, userId):
            database.changeCollection(self.name)
            userIdBools = [user["id"] == userId for user in database.getAll()]
            if True in userIdBools:
                database.delete({"id": userId})

        def addDiaper(self, userId, nameOfDiaper):
            database.changeCollection(self.name)
            userIdBools = [user["id"] == userId for user in database.getAll()]
            if True in userIdBools:
                user = database.getAll()
                user = user[userIdBools.index(True)]
                diapers = user["diapers"]
                if not nameOfDiaper in diapers:
                    diapers.append(nameOfDiaper)
                    database.update({"id": userId}, {"diapers": diapers}) 
        
        def removeDiaper(self, userId, nameOfDiaper):
            database.changeCollection(self.name)
            userIdBools = [user["id"] == userId for user in database.getAll()]
            if True in userIdBools:
                user = database.getAll()
                user = user[userIdBools.index(True)]
                diapers = user["diapers"]
                diapers.remove(nameOfDiaper)
                database.update({"id": userId}, {"diapers": diapers}) 
        
        def listDiapers(self, userId):
            database.changeCollection(self.name)
            userIdBools = [user["id"] == userId for user in database.getAll()] 
            diapers = []
            if True in userIdBools:
                user = database.getAll()
                user = user[userIdBools.index(True)]
                diapers = user["diapers"]
            return diapers

prizemi = Floor("Přízemí")
prvni = Floor("První Patro")
druhe = Floor("Druhé Patro")

def generateExcel(button):
    workbook = xlsxwriter.Workbook("Fasování.xlsx")
    worksheet = workbook.add_worksheet()
    floorFormat = workbook.add_format({"bold": True})
    floorFormat.set_align("vcenter")
    floorFormat.set_align("center")
    otherCellFormat = workbook.add_format()
    otherCellFormat.set_align("vcenter")
    otherCellFormat.set_align("center")

    row = 0
    col = 0
    worksheet.write(row, col, "Jméno", otherCellFormat)
    worksheet.write(row, col+1, "Název pleny", otherCellFormat)
    worksheet.write(row, col+2, "Počet", otherCellFormat)
    row += 1
    maxWidthUsers = 0
    maxWidthDiapers = 0
    for floor in patra:
        worksheet.write(row, col, floor.name, floorFormat)
        row += 1
        for user in floor.listUsers():
            currUserWidth = len(user["name"])
            if maxWidthUsers < currUserWidth:
                maxWidthUsers = currUserWidth
            worksheet.write(row, col, user["name"], otherCellFormat)
            for diaper in floor.listDiapers(user["id"]):
                currDLen = len(diaper)
                if currDLen > maxWidthDiapers:
                    maxWidthDiapers = currDLen
                worksheet.write(row, col+1, diaper, otherCellFormat)
                row += 1
            row += 1
    worksheet.set_column(0, 0, maxWidthUsers)
    worksheet.set_column(1, 1, maxWidthDiapers)
    workbook.close()

def removeDiaperCallback(nameOfDiaper, user, floor, userWindow):
    floor.removeDiaper(user["id"], nameOfDiaper)
    userWindow.destroy()
    showUserDiapers(user, floor)

def addDiaperButton(user, floor, nameOfDiaper, userWindow, addDiaperWindow):
    floor.addDiaper(user["id"], nameOfDiaper.get())
    addDiaperWindow.destroy()
    userWindow.destroy()
    showUserDiapers(user, floor)

def addDiaperCallback(user, floor, userWindow):
    addDiaperWindow = tk.CTkToplevel(master)
    addDiaperWindow.geometry("300x200")
    addDiaperWindow.title("Přidat plenu")
    addDiaperFrame = tk.CTkFrame(master=addDiaperWindow)
    addDiaperFrame.pack(pady=20, padx=60, fill="both", expand=True)
    diaperEntry = tk.CTkEntry(master=addDiaperFrame, placeholder_text="Název")
    diaperEntry.pack(pady=12, padx=10)
    addButton = tk.CTkButton(addDiaperFrame, text = "Přidat", height=2, width=5, command = lambda user = user, floor = floor, diaperEntry = diaperEntry, userWindow = userWindow, addDiaperWindow = addDiaperWindow : addDiaperButton(user, floor, diaperEntry, userWindow, addDiaperWindow))
    addButton.pack(pady=12, padx=10)
    
def addUserButton(name, floorNum, usersWindow, addUserWindow):
    patra[floorNum].addUser(name.get())
    addUserWindow.destroy()
    usersWindow.destroy()
    showUsers(floorNum)

def showUserDiapers(user, patro):
    userWindow = tk.CTkToplevel(master)
    userWindow.geometry("400x400")
    userWindow.title(user["name"])
    userFrame = tk.CTkFrame(master=userWindow)
    userFrame.pack(pady=20, padx=60, fill="both", expand=True)
    diapers = patro.listDiapers(user["id"])
    width = patro.getDiaperWidth(user["id"])
    if width < 10:
        width = 10
    num = 0
    for num, diaper in enumerate(diapers):
        l1 = tk.CTkLabel(userFrame, text = diaper, height=2, width=width)
        l1.grid(row=num, column=0, pady=5, padx=3)
        delete = tk.CTkButton(userFrame, text = "Odstranit", height=2, command = lambda user = user, nameOfDiaper = diaper, patro = patro, userWindow = userWindow : removeDiaperCallback(nameOfDiaper, user, patro, userWindow))
        delete.grid(row=num, column=1, pady=5, padx=3)
    addDiaperButt = tk.CTkButton(userFrame, text = "Přidat plenu", height=2, width=width, command= lambda user = user, floor = patro, userWindow = userWindow : addDiaperCallback(user, floor, userWindow))
    addDiaperButt.grid(row=num+1, column=1, pady=5, padx=3)

def deleteUserCallback(userId, floorNum, usersWindow):
    patra[floorNum].removeUser(userId)
    usersWindow.destroy()
    showUsers(floorNum)

def addUserCallback(number, usersWindow):
    patro = patra[number]
    addUserWindow = tk.CTkToplevel(master)
    addUserWindow.geometry("300x200")
    addUserWindow.title("Přidat uživatele")
    addUserFrame = tk.CTkFrame(master=addUserWindow)
    addUserFrame.pack(pady=20, padx=60, fill="both", expand=True)
    userName = tk.CTkEntry(addUserFrame)
    userName.pack(pady=12, padx=10)
    add = tk.CTkButton(addUserFrame, height=1, width=4, text="Přidat", command = lambda name = userName, floorNum = number, usersWindow = usersWindow, addUserWindow = addUserWindow : addUserButton(name, floorNum, usersWindow, addUserWindow))
    add.pack(pady=12, padx=10)

def showUsers(number):
    patro = patra[number]
    usersWindow = tk.CTkToplevel(master)
    usersWindow.geometry("400x400")
    usersWindow.title(patro.name)
    frame = tk.CTkFrame(master=usersWindow)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    width = patro.getWidth() + 2
    if width < 16:
        width = 16
    for num, user in enumerate(patro.listUsers()):
        userBut = tk.CTkButton(frame, height=2, width=width, text=user["name"], command = lambda user = user, floor = patro : showUserDiapers(user, floor))
        userBut.grid(row=num, column=0, pady=5, padx=3)
        userDel = tk.CTkButton(frame, height=2, text = "Odstranit", command = lambda userId = user["id"], floorNum = number, usersWindow = usersWindow : deleteUserCallback(userId, floorNum, usersWindow))
        userDel.grid(row=num, column=1, pady=5, padx=3)
    num = len(patro.listUsers())
    addUs = tk.CTkButton(frame, height=2, width=width, text="Přidat uživatele", command = lambda x = number, usersWindow = usersWindow : addUserCallback(x, usersWindow))
    addUs.grid(row=num+1, column=1, pady=5, padx=3)

def writeFloors(window):
    frame = tk.CTkFrame(master=window)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    for num, floor in enumerate(patra):
        floorBut = tk.CTkButton(frame, height=3, width=16, text = floor.name, command = lambda num = num : showUsers(num))
        floorBut.pack(pady=5, padx=3)
    button = tk.CTkButton(frame, height=2, width=16, text = "Extrahovat do excelu")
    button.configure(command = lambda button = button : generateExcel(button))
    button.pack(pady=12, padx=10)
    
def main():
    master.title("Fasování")
    master.geometry("400x400")
    writeFloors(master)
    master.mainloop()


if __name__ == "__main__":
    main()
