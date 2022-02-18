# pyplayonwm
python package to remove the playon watermark with handbrake

## remove watermark plus a little to wait for buffering
`HandBrakeCLI -i /share/tvshows/tvshow_files/The_Office/Season_3/E02_The_Convention_S03E02.mp4 -o/tvoutput/E02_The_Convention_S03E02.mp4 --turbo --two-pass --start-at seconds:7 --stop-at seconds:1292.42 --quality 22.0 --aencoder flac24 --gain 5`

## remove only water mark
`HandBrakeCLI -i /share/tvshows/tvshow_files/The_Office/Season_3/E02_The_Convention_S03E02.mp4 -o /tvoutput/E02_The_Convention_S03E02.mp4 --turbo --two-pass --start-at seconds:5 --stop-at seconds:1294.42 --quality 22.0 --aencoder flac24 --gain 5`
