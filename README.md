# snake-game
Python snake game using pygame. Just learnning python

## Important notes
* tile coordinates start from bottom left
* tile coordinate are different from real (pixel) coordinates
* If you convert tile coordinates to real (pixel) coordinates (1,1) it'll be (tileSize - 1, tileSize - 1). While with negatives (0 is considered positive) (-1,-1) will be in real coords (-tileSize, -tileSize)

## Known bugs and limitations
* Fruit never spawns at first or last columns or rows
* There is a bug where you can go 1 tile to the side of a fruit if they are on the top or 2nd top? row 
* Doesn't display stats on game end screen
* No retry button on game end screen
* Maybe bug: Can't turn snake when it is on a first or last column, it is like instant death. **Or I'm just bad at my own game**