# pyplayonwm
python package to remove the playon watermark with handbrake

## remove water plus a litte to wait for buffering
`sudo HandBrakeCLI -i /home/jasschul/share/tvshows/tvshow_files/The_Office/Season_3/E02_The_Convention_S03E02.mp4 -o /home/jasschul/tvoutput/E02_The_Convention_S03E02.mp4 --turbo --two-pass --start-at frames:200`

## remove only water mark
`sudo HandBrakeCLI -i /home/jasschul/share/tvshows/tvshow_files/The_Office/Season_3/E02_The_Convention_S03E02.mp4 -o /home/jasschul/tvoutput/E02_The_Convention_S03E02.mp4 --turbo --two-pass --start-at frames:140`