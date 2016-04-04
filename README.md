# COCoNotes is a video annotation platform #

It is primarily aimed at publishing enriched educational or research
content. However, it can be used for any type of video content.

This project has been funded by a French government support granted to
the COMIN Labs excellence laboratory, managed by the National Research
Agency in the 'Investing for the Future' program under reference
ANR-JO-LABX-07-0J, and by French Région Pays de la Loire.

## Install ##

- Configure project/local_settings.py (copy and customize local_settings-example.py)

- Create a database
For mysql backend, specify utf8 as character set:
  create database michaux DEFAULT CHARACTER SET utf8;

- Create tables
  ./manage.py migrate

- Create initial data

There is a `cocoadmin` management command that allows quick creation
of content from the command line. For instance, to quickly integrate
new videos, use the following command:

  ./manage.py cocoadmin publish [channel_title] [video_url] [video_title]

