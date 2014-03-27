import quixote
from quixote.directory import Directory, export, subdir
from quixote.util import StaticFile
import os.path

from . import html, image

class RootDirectory(Directory):
    _q_exports = []

    @export(name='')                    # this makes it public.
    def index(self):
        return html.render('index.html')

    @export(name='jquery')
    def jquery(self):
        return open('jquery-1.3.2.min.js').read()

    @export(name='upload')
    def upload(self):
        return html.render('upload.html')

    @export(name='upload_receive')
    def upload_receive(self):
        request = quixote.get_request()
        print request.form.keys()

        the_file = request.form['file']
        print dir(the_file)
        print 'received file with name:', the_file.base_filename
        data = the_file.read(int(1e9))

        image.add_image(data)

        return quixote.redirect('./')

    @export(name='upload2')
    def upload2(self):
        return html.render('upload2.html')

    @export(name='upload2_receive')
    def upload2_receive(self):
        request = quixote.get_request()
        print request.form.keys()

        the_file = request.form['file']
        print dir(the_file)
        print 'received file with name:', the_file.base_filename
        data = the_file.read(int(1e9))

        image.add_image(data)

        return html.render('upload2_received.html')

    @export(name='image')
    def image(self):
        return html.render('image.html')

    @export(name='image_raw')
    def image_raw(self):
        response = quixote.get_response()
        response.set_content_type('image/png')
        img = image.get_latest_image()
        return img
