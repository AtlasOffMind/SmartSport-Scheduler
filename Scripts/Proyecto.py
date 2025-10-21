#Recursos
resourcers = {
              #Espacios
              "Cancha de Football":              1,
              "Cancha de Tenis":                 1,
              "Cancha de Basket (techada)":      1,
              "Cancha de Basket (aire libre)":   2,
              "Cancha de FootSal":               1,
              "Cancha de Boleyball":             1,
              "Cancha de Badmintong":            1,
              "Cancha de Cancha":                1,
              "Piscina Olimpica":                1,
              "Habitacion para juegos de mesa":  1,
              "Habitacion con Colchon":          1,
              "Pista de Carreras":               1,
              "Biosaludable (techado)":          1,
              "Biosaludable (aire libre)":       1,
              "Estadio de BaseBall":             1,
              
              "Pelota de Football":             15,
              "Pelota de Footsall":             15,
              "Pelota de Tenis":                50,
              "Pelota de Tenis de Mesa":        50,
              "Pelota de Boleyball":            15,
              "Pelota de Basket":               15,
              "Pelota de Cancha":               15,
              "Pelota de Badmintong":           15,
              "Pelota de Baseball":             30,
              
              "Raquetas de Cancha":              6,
              "Raquetas de Badmintong":          6,
              "Raquetas de Tenis":               6,
              "Raquetas de Tenis de Mesa":       6,
              
              "Bates de BaseBall":              30,
              "Guantes de BaseBall":            30,
              
              "Protectores de BaseBall":        30,
              "Cascos de BaseBall":             30,
              "Protectores de Karate":          30,
              "Cascos de Karate":               30,
              "Protectores de Taekwando":       30,
              "Cascos de Taekwando":            30,
              
              "Ned de Boleyball":                4,
              "Ned de Tenis":                    4,
              "Ned de Tenis de Mesa":            4,

              "Porterias (Football)":            6,
              "Porterias (Footsall)":            6,

              "Arbitros":                        5,
              "Personal de primeros auxilios":   5,
              
              "Boyas":                          16,
              "Salva Vidas":                    16,
              
              "Altavoces":                      16,
              "Ambulacia":                       2,
              "Microfonos":                      8,
              "Sacos de Boxeo":                  4,
              "Trampolin":                       3,
              "Estrado de Premiaciones":         4,
              
              }

#Eventos
actual_resource = [
                    ("Cancha de Football", 1),
                    ("Pelota de Football", 3),
                    ("Porterias (Football)", 2),
                    ("Arbitros", 1),
                    ("Personal de primeros auxilios", 2),
                   ]
events = {}

def Add_Events(date, event_name, using_resources):
    
    if  Is_Valid(date,using_resources):
        
        for resource,amount in using_resources:
            resourcers[resource] -= amount  
            
        
        if events.get(event_name):    
            print("This event already exist")
            inpt = input("Do you want to reewrite it, yes/no: ")
            if inpt == "yes":    
                (d,r) = date,using_resources
                events[event_name] = (d,r)   
        else:
            (d,r) = date,using_resources
            events[event_name] = (d,r)
    else:
        print("That's not a valid event")
        
def Remove_Events(event_name):
    if events.get(event_name):
        inpt = input("Do you want to remove this event, yes/no: ")
        if inpt == "yes":
            date,used_resourcers = events[event_name]
            
            for resource,amount in used_resourcers:
                resourcers[resource] += amount 
            
            del events[event_name]
        
            
#TODO crear el metodo este de revision
def Is_Valid(date, using_resources):
    return True


Add_Events("1/2/25", "Partido de Football", actual_resource)
print(events)
for resource,am in actual_resource:
    print(f"{resource} {resourcers[resource]}")
    
print(" ")

Remove_Events("Partido de Football")

print(events)
for resource,am in actual_resource:
    print(f"{resource} {resourcers[resource]}")
