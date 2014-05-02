# __init__.py is the top level file in a Python package.
import os
import sqlite3

from quixote.publish import Publisher

# this imports the class RootDirectory from the file 'root.py'
from .root import RootDirectory
from . import html, image

IMAGE_DB_FILE = 'images.sqlite'

def create_publisher():
     p = Publisher(RootDirectory(), display_exceptions='plain')
     p.is_thread_safe = True
     return p
 
def setup():                            # stuff that should be run once.
    html.init_templates()

    if not os.path.exists(IMAGE_DB_FILE):
        create_database()

    #retrieve_all_images()

def teardown():                         # stuff that should be run once.
    pass

def create_database():
    print 'creating database'
    db = sqlite3.connect('images.sqlite')
    db.execute('CREATE TABLE image_store (i INTEGER PRIMARY KEY, filename VARCHAR(255), \
        owner VARCHAR(30), score INTEGER, image BLOB, \
        FOREIGN KEY (owner) REFERENCES user(username))');
    db.execute('CREATE TABLE image_comments (i INTEGER PRIMARY KEY, imageId INTEGER, \
     comment TEXT, FOREIGN KEY (imageId) REFERENCES image_store(i))');
    db.execute('CREATE TABLE user (username VARCHAR(30) PRIMARY KEY, \
        password VARCHAR(30))');
    db.commit()
    db.close()

def retrieve_all_images():
    # connect to database
    db = sqlite3.connect('images.sqlite')
    
    # configure to retrieve bytes, not text
    db.text_factory = bytes

    # get a query handle (or "cursor")
    c = db.cursor()

    # select all of the images
    for row in c.execute('SELECT * FROM image_store ORDER BY i DESC'):
        open(row[1], 'w').write(row[2])