from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from image.models import Image
from image.forms import ImageUploadForm
import images
# Create your views here.

def index(request):
	context = {}
	try:
		latest_image = Image.objects.latest('id')
	except:
		pass
	else:
	    context['latest'] = latest_image

	return render(request, 'index.html', context)

def upload(request):
	return render(request, 'upload.html')

def upload_receive(request):
	if request.method == 'POST':
		form = ImageUploadForm(request.POST, request.FILES)

		if form.is_valid():
			the_file = request.FILES['image']
			image = Image()
			if form.cleaned_data['name']:
				image.name = form.cleaned_data['name']
			image.image = the_file
			image.save()

			return HttpResponseRedirect('/')
		else:
			raise Exception("not valid")

		return HttpResponseRedirect('/upload/')

def image(request):
	return render(request, 'image.html')

def image_raw(request):
	img = images.get_latest_image()
	return HttpResponse(img, content_type='image/png')