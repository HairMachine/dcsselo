# DCSS Elo calculator

## Overview

This attempts to calculate an Elo value for all DCSS players, based on server log files. It outputs CSV files for importing to databases, google sheets etc.

As well as a numerical Elo value it also assigns each player a 'rank', which is designated as follows:

- 2000-??: Grand Master
- 1800-1999: Master
- 1600-1699: Diamond
- 1400-1499: Platinum
- 1200-1299: Gold
- 1000-1199: Silver
- 0-1000: Bronze

This is purely for fun and it's unlikely that it's reasonable to represent a player's skill at this game in a single integer, given the game's complexity and just how many possible things you can try and do in it, but it was interesting as an exercise and should provide a better overall read than any existing single metric.

There is a public Google sheet which has the current scores avaiable here: https://docs.google.com/spreadsheets/d/1tVaSG7su418qObhVhNqzHadGMZon0eJzDycdczgqzCQ/edit#gid=1453132958 

## Usage

To gather the logs, run

``python download.py``

This will then download all logs into the logs folder, which can take some time as some are rather large. Subsequent runs of this file should only download files if they have been update on the server (note: the underhound.eu server at least does not output date modified headers, so logs from this server always be updated whether they have changed or not).

To calculate Elos from the downloaded logs, run:

``python main.py``

This takes about 9-10 minutes to run through all of the games downloaded and calculate a score for everyone. CSV files are written to the outputs folder containing the results of the analysis.

If you have not previously downloaded the logs, you will probably get empty files. Or your computer may catch fire and explode, who knows?

## Method

This uses the standard '400' Elo formula to calculate Elos. As DCSS is a single player game, what happens is that the system assumes a player is playing against the computer, and the computer's 'skill' is calculated based upon the character and the number of runes that were acquired.

More exactly, what this does is model the player's game as 18 simultaneous games, each with their own binary win/loss score: one for species, one for background, one for combo, and one for each of the runes. Each of these seperate 'factors' maintains their own Elo score. K values (which determine how much each score will move each time) are set independently for each factor - the rune values are set to a significantly lower K to the other metrics, which means they should affect the overall Elo change less.

The games are evaluated in chronological order, and the time a game happens does matter; Elos are used as they were at the time the game was played.

The computer was set at a starting Elo of 3000, the players 1000. This is mostly to reflect the high difficulty of the game and not unduly punish the first ever players. It seems nice to reward the pioneers.

## Flaws

The calculated Elos for players come out quite consistent across all the factors, which suggests the factors are correlated, and maybe even that we are indeed measuring something of crawl 'skill'. Despite this there are some clear flaws:

- Unpopular or underplayed combos are worth a lot of points, which means people who happen to go with weird combos probably have their rating inflated. I thought this better than having it deflated instead.
- Easy combos are often played by inexperienced players. This means things like Minotaur Berserker will win Elo points by defeating novices, and thus rise above some other, probably more challenging, combos.
- High score and speed runs likely have the effect of deflating Elo substantially, as the player doing them will record many losses. At the moment there is no compensation based on score to offset this.
- The crawl account system is rather permissive and it is very possible for bad players to sign up with a good player's name; in this system they would then be conflated together. I tried splitting by server, which would eliminate this, but some players (particularly 6-time Tournament winner Yermak) lose out as they tend to use many different servers to play on, so I removed that tweak. As far as I could tell there isn't any really obvious case of name squatting having a big effect.
- The time-dependent nature of the analysis makes complete sense for games with two human players whose skills constantly change over time, but is not as obviously sensible for a computer. However, crawl code changes do occur quite frequently and this likely affects the difficulty of the game, so on reflection it seems reasonable, if an approximation.

This isn't an exhaustive list - there are likely many more, too.

Enjoy!