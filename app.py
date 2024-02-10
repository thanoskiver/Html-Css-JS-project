# BEGIN CODE HERE
from flask import Flask,request,jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from pymongo import TEXT

import numpy as np


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# END CODE HERE

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/pspi"
CORS(app)
mongo = PyMongo(app)


# flask - -app main run - -debugger --> terminal --> Activating a connection via Flask with interactive


mongo.db.products.create_index([("name", TEXT)])
#endpoint search δέχεται μια παραμέτρο την name ειναι το ονομα του προϊοντος που ψαχνουμε στην βαση

@app.route("/search", methods=["GET"])
def search():
    # BEGIN CODE HERE
    
    name = request.args.get("name")#μεθοδος για να παρουμε την τιμη της παραμέτρου απο το request




    

    
    json=mongo.db.products.find({"$text":{"$search":f"\"{name}\""}}).sort("price",-1)#εδω πραγματοποιειται η αναζητηση στην βαση συμφωνα με την τιμη της παραμέτρου
    #επιστρεφει το αντικειμενο cursor που περιλαμβανει το σύνολο των εγγραφων που ικανοποίουν την συνθηκη κατα φθινουσα σειρα
    
    if json is None: #σε περιπτωση που ο cursor ειναι κενος γυρναει αδεια λιστα
        json=[]
        return json
    
    
    finale=[]
    #σε αντιθετη περιπτωση επιστρεψε μια λιστα απο json αρχεια/εγγραφες 
    for j in json:
        finale.append({'name':j['name'],
                       'id':str(j["_id"]),
                       'production_year':j['production_year'],
                       'price':j['price'],
                       'color':j['color'],
                       'size':j['size']  
                       })


        
        
    
    return jsonify(finale)
    
    # END CODE HERE


#end point add-product δεχεται ενα json αρχειο και ελεγχει αν υπαρχει αυτη η εγγραφη στην βαση.Αν υπαρχει την ενημερωνει ,αντιθετα την προσθετει 



@app.route("/add-product", methods=["POST"])
def add_product():
    # BEGIN CODE HERE
  
    new=request.json #παιρνω  το json αρχειο του request
 

    #elegxos eisodou
  
    if  type(new["color"])==type(None):
        return "\"Color\" field must be an integer"
    elif type(new["size"])==type(None):
        return " \"Size\" field must be an integer"
    elif type(new["production_year"])==type(None):
        return "\"Production year\" field must be an integer"
    elif type(new["price"])==type(None):
        return "\"Price\" field must be an integer"

    if (new["color"]>3 or new["color"]<1):
        return "The available colors options are 1,2,3"
    elif(new["size"]<1 or new['size']>4):
        return "The available size options are 1,2,3,4"

    
    name=new["name"] 
    old=mongo.db.products.find_one({"name":name }) #psaxno tin pleiada me to akribes onoma 
    

    if old is None :#an den brika kamia prostheto to json arxeio opws to pira apo to request 
        mongo.db.products.insert_one(new)
        return"added new product"
    elif old is not None: #alliws enimerwno thn eggrafi ths basis
       mongo.db.products.update_one({"name":new["name"]},{"$set":{"price":new["price"],"production_year":new["production_year"],"color":new["color"],"size":new["size"]}})
       return "Product updated"
    
    return "addition is complete"
   
    # END CODE HERE


#end point content-based-filtering δεχεται ενα json αρχειο και επιστρεφει τα ονοματα των εγγραφων που ταιριαζουν με αυτην κατα 70 τοις εκατο και πανω

@app.route("/content-based-filtering", methods=["POST"])
def content_based_filtering():
    # BEGIN CODE HERE
     input=request.json#παιρνω το json apo to request

     allMyProducts=mongo.db.products.find()#γυρναω όλες τις εγγραφες της βασης (φαση select *)
     inputArray= [input["production_year"],  input['price'],input['color'], input['size']]#παιρνω τα χαρακτηριστικα που θα χρησιμοποιησω ως κριτηρια ομοιοτητας
     inputArray=np.array(inputArray)#1 by 4 array
                      
   


     theListOfAllMyProducts=[]
     paralerArray=[]


     for j in allMyProducts: #καθε πλειαδα που επιστεψε το find την κανω λιστα και την προσθετω σε μια αλλη λιστα (δημιουργω μια δισδιαστατη λιστα)
           #παραλληλα κανω και μια εξτρα λιστα παραλληλη που κραταει τα ονοματα της δισδιαστατης λιστας
           paralerArray.append(j["name"])
           theListOfAllMyProducts.append([
                       j["production_year"],
                       j['price'],
                       j['color'],
                       j['size']  
                       ]   )

     NameArray=np.array(paralerArray)#n by 1
     
     ProductsArray=np.array(theListOfAllMyProducts) #n by 4
     

         
     

         
    

     
     
    #διαδικασία κανονικοποίησης
     debug=[]

    
    
     for i in range(0,4):
         max=np.max(ProductsArray[:,i])
         if (max<inputArray[i]):
            max=inputArray[i]

          

         for j in range(0,np.shape(ProductsArray)[0]):
             ProductsArray[j][i]=ProductsArray[j][i]/max
             
              
            
        
         x=inputArray[i]/max
         inputArray[i]=x
         debug.append(x)
           
              

     inputArray=np.array(debug)
     above=np.dot(ProductsArray,inputArray.T) #παραγει εναν πινακα n by 1 ειναι τα n εσωτερικα γινόμενα των διανυσματων 

    #υπολογίζω τα μετρα των διανυσματων και το γινομενο τους
     magnitudeOfA=np.sqrt(np.sum(np.square(ProductsArray),axis=1))
     magnitudeOfB=np.sqrt(np.sum(np.square(inputArray)))
     
    

     below=magnitudeOfA*magnitudeOfB




     resultArray=above/below



    
     #resultArray=np.concatenate((resultArray, NameArray), axis=0)
     
     #κολλαω τους δυο παραλληλους πινακες (τα ονοματα και τα αντιστοιχα ποσοστα ομοιοτητας)
     resultArray = np.column_stack((resultArray, NameArray))


     #εδω αποθηκευω τα ονοματα που ικανοποιουν την συνθηκη
     listOfReturnedNames=[]


     
     for i in resultArray:
         if float(i[0])>0.70:
             listOfReturnedNames.append(i[1])






     resultArray=list(resultArray)

     
     
     



     return (listOfReturnedNames)
    # END CODE HERE


@app.route("/crawler", methods=["GET"])
def crawler():
    # BEGIN CODE HERE

     try:
        semester=request.args.get("semester")
        url="https://qa.auth.gr/el/x/studyguide/600000438/current"
        options=Options()
        options.headless=True

        driver = webdriver.Chrome(options=options)
        
        driver.get(url)
        courses = driver.find_elements(By.XPATH,"//table[@id='exam{}']/tbody/tr".format(semester))
        result=[]
        for course in courses:
            c=course.get_attribute("coursetitle")
            result.append(c)
        
        return jsonify(result)

     except Exception as e:
         return str(e)
         return "BAD REQUEST", 400
     
     app.run
    # END CODE HERE
