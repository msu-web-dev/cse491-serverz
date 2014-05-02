# insert an image into the database.

import sqlite3

# connect to the already existing database
db = sqlite3.connect('images.sqlite')

# configure to allow binary insertions
db.text_factory = bytes

# grab whatever it is you want to put in the database
r = open('../imageapp/dice.png', 'rb').read()

# insert!
db.execute('INSERT INTO image_store (image) VALUES (?)', (r,))
db.commit()
