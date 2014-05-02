# image handling API
import sqlite3
import sys

class Image:
    filename = ''
    data = ''
    score = 0
    def __init__(self, filename, data, score):
        self.filename = filename
        self.data = data
        self.score = score

images = {}

def add_image(filename, username, data):
    # insert to database
    insert_image(filename, username, data)

def get_image(num):
    return retrieve_image(num)

def get_latest_image():
    return retrieve_image(-1)

def insert_image(filename, username, data):
    # connect to the already existing database
    db = sqlite3.connect('images.sqlite')

    # configure to allow binary insertions
    db.text_factory = bytes

    # grab whatever it is you want to put in the database
    print username
    # insert!
    db.execute('INSERT INTO image_store (filename, owner, score, image) \
        VALUES (?,?,?,?)', (filename, username, 1, data))
    db.commit()

# retrieve an image from the database.
def retrieve_image(i):
    # connect to database
    db = sqlite3.connect('images.sqlite')
    
    # configure to retrieve bytes, not text
    db.text_factory = bytes

    # get a query handle (or "cursor")
    c = db.cursor()

    # select all of the images
    if i >= 0:
        c.execute('SELECT i, filename, score, image FROM image_store where i=(?)', (i,))
    else:
        c.execute('SELECT i, filename, score, image FROM image_store ORDER BY i DESC LIMIT 1')

    # grab the first result (this will fail if no results!)
    try:
        i, filename, score, image = c.fetchone()

        return Image(filename, image, score)
    except:
        pass

def add_comment(i, comment):
    db = sqlite3.connect('images.sqlite')
   
    if i == -1:
        c = db.cursor()

        # Latest image
        c.execute('SELECT i FROM image_store ORDER BY i DESC LIMIT 1')
        try:
            i = c.fetchone()[0]
        except:
            return

    db.execute('INSERT INTO image_comments (imageId, comment) VALUES (?,?)', (i, comment))
    db.commit()

def get_comments(i):
    comments = []
    db = sqlite3.connect('images.sqlite')

    # Get all the comments for this image
    c = db.cursor()
    if i == -1:
        # Latest image
        c.execute('SELECT i FROM image_store ORDER BY i DESC LIMIT 1')
        try:
            i = c.fetchone()[0]
        except:
            return

    c.execute('SELECT i, comment FROM image_comments WHERE imageId=(?) ORDER BY i DESC', (i,))
    for row in c:
        comments.append(row[1])

    return comments

def get_owner(i):
    # connect to database
    db = sqlite3.connect('images.sqlite')

    # get a query handle (or "cursor")
    c = db.cursor()

    # select all of the images
    if i >= 0:
        c.execute('SELECT owner FROM image_store where i=(?)', (i,))
    else:
        c.execute('SELECT owner FROM image_store ORDER BY i DESC LIMIT 1')

    return c.fetchone()[0]

def get_image_score(i):
    # connect to database
    db = sqlite3.connect('images.sqlite')

    # get a query handle (or "cursor")
    c = db.cursor()

    # select all of the images
    if i >= 0:
        c.execute('SELECT score FROM image_store where i=(?)', (i,))
    else:
        c.execute('SELECT score FROM image_store ORDER BY i DESC LIMIT 1')

    val = int(c.fetchone()[0])
    return val

def increment_image_score(i):
# connect to database
    db = sqlite3.connect('images.sqlite')

    if i < 0:
        i = get_num_images()

    db.execute('UPDATE image_store SET score = score + 1 where i=(?)', (i,))
    db.commit()

def decrement_image_score(i):
# connect to database
    db = sqlite3.connect('images.sqlite')

    if i < 0:
        i = get_num_images()

    db.execute('UPDATE image_store SET score = score - 1 where i=(?)', (i,))
    db.commit()

def get_image_numbers():
    db = sqlite3.connect('images.sqlite')
    c = db.cursor()
    c.execute('SELECT i FROM image_store ORDER BY i')
    nums = []

    for num in c.fetchall():
        nums.append(num[0])

    print nums
    return nums

def delete_image(i):
    db = sqlite3.connect('images.sqlite')
    print(i)
    db.execute('DELETE FROM image_store WHERE i=(?)', (i,))
    db.commit()