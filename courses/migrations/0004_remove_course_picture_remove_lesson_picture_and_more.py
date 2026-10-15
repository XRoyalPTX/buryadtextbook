from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_alter_course_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='picture',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=models.TextField(),
        ),
    ]
