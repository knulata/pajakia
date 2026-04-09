Place icon-16.png, icon-48.png, and icon-128.png here.

Until you generate proper icons, Chrome will use a default icon. To create
quick placeholders, run:

    convert -size 128x128 xc:#1a56db -fill white -gravity center \
        -font Arial -pointsize 64 -annotate 0 'P' icon-128.png
    convert icon-128.png -resize 48x48 icon-48.png
    convert icon-128.png -resize 16x16 icon-16.png

Or use any 128x128 PNG with the Pajakia logo.
