import json

# entire database class with all the functions
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

def main():
    db = MyDb("users")
    db.changeCollection("prizemi")
    name = input("Name: ")
    print(db.getAll())
    user = db.create({"name": name})
    print(db.getAll())

if __name__ == '__main__':
   main() 
