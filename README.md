# boincAutoDischarger
Use BOINC to artificially increase the number of battery cycles in your Mac.

# Installation requirements
- BOINC (of course);
- `boinccmd` (the CLI manager for BOINC), make sure that is is in your PATH;
- Python3 (`brew install python3`);
- [terminal-notifier](https://github.com/julienXX/terminal-notifier), for notifications;
- [iStats](https://github.com/Chris911/iStats) (optional), for integrated nice stats.

# Usage
- `./autodischarger.py` runs with a default refresh timeout of 10 seconds and no iStats;
- `./autodischarger.py [timeout] stats` runs with a refresh timeout of `[timeout]` seconds and iStats.

# Why?
My university provides all students with Macbooks with a free of charge (other than the tuition fee) lease. Since 
if you have [AppleCare](https://www.apple.com/support/products/mac/) you are entitled to a free battery replacement when 
your it reaches 80% of the original factory capacity, I have created this tool to moderately degrade the battery on my Mac
in order to get a free replacement just about when the AppleCare coverage will end.

If you have AppleCare and for some reason you too want to get a "free" battery, this is the tool for you.

# What
This is a ~200 line Python 3 script that uses `boinccmd` in order to change automatically the settings of BOINC in order to 
maximize resource usage (and thus battery consumption) while your Mac is using battery power. BOINC will run with a 80% CPU
limit when your Macbook is on battery power with at least a 20% charge. Once the charge runs out, BOINC will slow down to 10% CPU usage and the script will send a notification telling you to plug the charger. Once you are charging, the script will start waiting for the battery to be at least 90% charged, and then will prompt you to disconnect the charger and the cycle will start again.

My setup uses a power strip to turn the charger manually on and off. I think the process can be entirely automated by using a smartplug and automating its activation from this script (e.g the TP-LINK HS100 has [this](https://github.com/GadgetReactor/pyHS100) open source python control library), but unfortunately I am currently not able to buy such a product both in a physical store or online and therefore I am tediously switching on and off the charger myself every hour (_I know_)

# This is not a finished product
Please feel free the hardcoded constant values for the charging thresholds and various BOINC config files. I have created this 
script for personal use and I am just sharing it here for someone that is curious enough to hack it to their needs.

Another quick note: my AppleCare expiration date is hardcoded as well, feel free to change that.

I might be able polish this script in the following days, but I have a quite busy class schedule (albeit remote). So, if you 
want, just create a pull request to tidy up this mess and I will accept it.

# Use at your own risk 
I am not responsible if your Mac will be damaged in any way by using this script. Please be careful since this is a fairly 
resource intensive setup and Macbooks are not exactly known for their amazing cooling system. Use at your own risk 

