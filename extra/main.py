import pymongo

if __name__ == "__main__":
    print("Using Pymongo to connect MongoDB")
    client = pymongo.MongoClient("mongodb://localhost:27017")     #client = MongoClient('mongodb://username:password@localhost:27017/')
    print(client)

    db = client['Company']        #database
    collection = db['Branch']     #collection

    # CREATE
    dictionary = {'Location': "Delhi", 'Head': "Sumit"}       #document
    collection.insert_one(dictionary)
    dict2 = {'Location': "Kolkata", 'Head': "Anil", 'Members': 50}
    collection.insert_one(dict2)


    # READ
    docs = collection.find_one({'Head': 'Sumit'})
    print(docs)
    all_docs = collection.find({'Head': 'Sumit'}, {'_id': 0, 'Head': 1})     # 1 - will be shown and 0 - will not be shown.
    for item in all_docs:
        print(item)


    # UPDATE
    condition = {"Head": "Anil"}
    change = {"$set": {"Location": "Bangalore"}}
    collection.update_one(condition, change)    #use update_many for more than one values

    # DELETE
    collection.delete_one({"Head": "Anil"})

    print(collection.count_documents({}))  #give count of all the documents

 # ODM - object Document Mapper
