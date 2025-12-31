from backend import Resource, Planner


"""Utilidades del sistema"""

def create_planner():
        """Crea un planificador con todos los recursos predefinidos"""
        raw_global_resources = {
            #                               Espacios
            "Cancha de Football": Resource("Cancha de Football", 1),
            "Cancha de Tenis": Resource("Cancha de Tenis", 1),
            "Cancha de Basket (techada)": Resource("Cancha de Basket (techada)", 1),
            "Cancha de Basket (aire libre)": Resource(
                "Cancha de Basket (aire libre)", 1
            ),
            "Cancha de FootSal": Resource("Cancha de FootSal", 1),
            "Cancha de Boleyball": Resource("Cancha de Boleyball", 1),
            "Cancha de Badmintong": Resource("Cancha de Badmintong", 1),
            "Cancha de Cancha": Resource("Cancha de Cancha", 1),
            "Piscina Olimpica": Resource("Piscina Olimpica", 1),
            "Habitacion para juegos de mesa": Resource(
                "Habitacion para juegos de mesa", 1
            ),
            "Habitacion con Colchon": Resource("Habitacion con Colchon", 1),
            "Pista de Carreras": Resource("Pista de Carreras", 1),
            "Biosaludable (techado)": Resource("Biosaludable (techado)", 1),
            "Biosaludable (aire libre)": Resource("Biosaludable (aire libre)", 1),
            "Estadio de BaseBall": Resource("Estadio de BaseBall", 1),
            "Ring de boxeo": Resource("Estadio de BaseBall", 1),
            #                             Implementos
            "Pelota de Football": Resource("Pelota de Football", 15),
            "Pelota de Footsal": Resource("Pelota de Footsal", 15),
            "Pelota de Tenis": Resource("Pelota de Tenis", 50),
            "Pelota de Tenis de Mesa": Resource("Pelota de Tenis de Mesa", 50),
            "Pelota de Boleyball": Resource("Pelota de Boleyball", 15),
            "Pelota de Basket": Resource("Pelota de Basket", 15),
            "Pelota de Cancha": Resource("Pelota de Cancha", 15),
            "Pelota de Badmintong": Resource("Pelota de Badmintong", 15),
            "Pelota de Baseball": Resource("Pelota de Baseball", 30),
            "Raquetas de Cancha": Resource("Raquetas de Cancha", 6),
            "Raquetas de Badmintong": Resource("Raquetas de Badmintong", 6),
            "Raquetas de Tenis": Resource("Raquetas de Tenis", 6),
            "Raquetas de Tenis de Mesa": Resource("Raquetas de Tenis de Mesa", 6),
            "Bates de BaseBall": Resource("Bates de BaseBall", 30),
            "Guantes de BaseBall": Resource("Guantes de BaseBall", 30),
            "Guantes de Boxeo": Resource("Guantes de Boxeo", 30),
            "Protectores de BaseBall": Resource("Protectores de BaseBall", 30),
            "Cascos de BaseBall": Resource("Cascos de BaseBall", 30),
            "Cascos de Boxeo": Resource("Cascos de Boxeo", 30),
            "Protectores de Karate": Resource("Protectores de Karate", 30),
            "Cascos de Karate": Resource("Cascos de Karate", 30),
            "Protectores de Taekwando": Resource("Protectores de Taekwando", 30),
            "Cascos de Taekwando": Resource("Cascos de Taekwando", 30),
            "Boyas": Resource("Boyas", 16),
            "Sacos de Boxeo": Resource("Sacos de Boxeo", 4),
            "Estrado de Premiaciones": Resource("Estrado de Premiaciones", 4),
            "Altavoces": Resource("Altavoces", 16),
            "Microfonos": Resource("Microfonos", 8),
            "Mesa de PingPong": Resource("Mesa de PingPong", 8),
            "Tablero de ajedrez": Resource("Tablero de ajedrez", 8),
            #                               Personal
            "Arbitro": Resource("Arbitro", 5),
            "Personal de primeros auxilios": Resource(
                "Personal de primeros auxilios", 5
            ),
            "Salva Vidas": Resource("Salva Vidas", 16),
            "Ambulacia": Resource("Ambulacia", 2),
            "Comentaristas": Resource("Comentaristas", 6),
        }
        return Planner(raw_global_resources, {})
