from django.db import models

# Create your models here.
class Image(models.Model):
    """
        This class will represent one image within the database. It will be
        automatically instantiated whenever a user uploads an image.
    """
    name = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='images/%Y/%m/%d', max_length=100)

    def save(self, *args, **kwargs):
        """
            Overrides the base save method. Checks to see if the user
            specified the name for the image. If they did not, use the
            name from the image file.
        """
        if not self.name:
            self.name = self.image.name

        super(Image, self).save(*args, **kwargs)
