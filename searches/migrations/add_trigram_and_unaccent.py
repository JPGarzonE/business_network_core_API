from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension, TrigramExtension

class Migration(migrations.Migration):

    initial = True

    operations = [
        UnaccentExtension(),
        TrigramExtension()
    ]