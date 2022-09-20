import os
import psycopg
import argparse

class Schemaverse(object):
    def __enter__(self):
        username = os.environ.get("SHIP_USERNAME")
        password = os.environ.get("SHIP_PASSWORD")
        self.connection = psycopg.connect(host='db.schemaverse.com', dbname='schemaverse', user=username, password=password)
        self.connection.autocommit = True
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type != None:
            print("exc_type: ", exc_type)
            print("exc_value: ", exc_value)
            print("exc_traceback: ", exc_traceback)
            return True #suppress exceptions for now
        self.connection.close()

    def GetCursor(self):
        return self.connection.cursor()


def GetPlayerId():
    with Schemaverse() as s:
        cursor = s.GetCursor()
        cursor.execute("SELECT id FROM my_player;")
        results = cursor.fetchone()
        s.connection.commit()
        return results[0]


def basic_player_info():
    print("getting basic player info: { balance, fuel_reserve }")
    with Schemaverse() as s:
        cursor = s.GetCursor()
        cursor.execute("SELECT id, username, balance, fuel_reserve FROM my_player;")
        results = cursor.fetchone()
        print(results)
        s.connection.commit()

def name_planet(planet_id, planet_name):
    print(f'renaming planet: {planet_id} to {planet_name}')
    with Schemaverse() as s:
        cursor = s.GetCursor()
        cursor.execute("SELECT id from my_player;")
        result = cursor.fetchone()
        user_id = result[0]
        print(user_id)
        updater = "UPDATE planets SET name=%s WHERE conqueror_id=%s;"
        cursor.execute(updater, (planet_name, user_id))
        s.connection.commit()

class Commander(object):
    def __init__(self):
        self.id = GetPlayerId()

    def list_ships(self):
        with Schemaverse() as s:
            cursor = s.GetCursor()
            cursor.execute("SELECT * from my_ships;")
            results = cursor.fetchall()
            for result in results:
                print(result)
            s.connection.commit()

    def list_planets(self):
        with Schemaverse() as s:
            cursor = s.GetCursor()
            cursor.execute("SELECT u.id, p.id, p.name, p.location FROM my_player as u JOIN planets as p ON p.conqueror_id=u.id;")
            results = cursor.fetchone()
            s.connection.commit()
            print(results)
            if cursor.rowcount > 0:
                list = cursor.fetchall()
                print(*list, sep="\n")
            else:
                print("no planets currently conquerered by this player")

class Shipyard(object):
    def build_fighter(self, name, location):
        self.build_ship(name, 10, 10, 0, 0, location)
    
    def build_engineer(self, name, location):
        self.build_ship(name, 0, 0, 10, 10, location)

    def build_ship(self, name, attack, defense, engineering, mining, location):
        print(f'Creating ship {name} at ({location[0]},{location[1]}')
        with Schemaverse() as s:
            cursor = s.GetCursor()
            inserter = """INSERT INTO my_ships(name, attack, defense, engineering, prospecting, location) VALUES (%s, %s, %s, %s, %s, POINT(%s, %s)) RETURNING *"""
            cursor.execute(inserter, (name, attack, defense, engineering, mining, location[0], location[1]))
            results = cursor.fetchall()
            for result in results:
                print(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-ships', help='Lists your ships', action='store_true', default=False)
    parser.add_argument('--list-planets', help='Lists your planets id, name, and location', action='store_true', default=False)
    args = parser.parse_args()
    print(args)

    c = Commander()

    if args.list_ships:
        print('Listing all ships...')
        c.list_ships()
    
    if args.list_planets:
        print('Listing all planets...')
        c.list_planets()