#### C H A N G E L O G ####
#### 04/18/20 | 19:00:00 | Version 1.0.0 finished. | Basics covered, ready to debut on the subreddit.
#### 04/23/20 | 22:30:00 | Version 1.1.0 finished. | Doubled the amount of leaderboards and added additional monthly stats.
#### 04/26/20 | 16:00:00 | Version 1.2.0 finished. | Restructured code so all print calls are class-contained.  Added additional monthly metrics and drastically improved user average data module.
#### 04/30/20 | 15:00:00 | Version 1.2.1 finished. | Updated Monthly Sweet Talker's and Early Bird Clubs to be a top 5 leaderboard instead of a list of qualifying users.
#### 05/05/20 | 16:20:00 | Version 1.2.2 finished. | Updated Early Birds to count any post within the first 24 hours of the thread going live rather than the first hour.
#### 05/13/20 | 21:00:00 | Version 1.3.0 finished. | Added recursive concatenation to a number of post-length related modules, updated BigKid with said functionality and comment depth, and added scaling to user levels.
#### 05/18/20 | 22:42:00 | Version 1.3.1 finished. | Significantly cleaned up most print statements using enumerate() function.
#### 05/27/20 | 19:10:00 | Version 1.3.2 finished. | Added the UpvoteModule that upvotes every parent comment in the thread because you're all beautiful and deserve the best.
#### 05/27/20 | 19:30:00 | Version 1.3.3 finished. | Refactored base loop to use functions so entire modules can be toggled with a single hash sign rather than having to comment out every individual module.
#### 06/02/20 | 12:30:00 | Version 1.3.4 finished. | Did the 1.3.3 to the print functions, and added total average comments vs total parent comments.
#### 06/02/20 | 12:50:00 | Version 1.3.5 finished. | Implemented the PRINT_ALL global variable that changes output to either a set number of list items or 100% of the data.  Added LEADERBOARDS_ON and MONTHLY_ON similarly.
#### 06/02/20 | 12:50:00 | Version 1.3.6 finished. | Added another module to monthly averages, cleaned up formatting; script is ready to debut.
#### 06/03/20 | 15:55:00 | Version 1.3.7 finished. | Fixed Early Birds to accurately track 24 hours after the post is made, rather than only on the same calendar date.
#### 06/11/20 | 21:15:00 | Version 1.3.8 finished. | Added MONTHLY_ and YEARLY_OUTPUT macros to easily control the amount of data printed.
#### 06/22/20 | 17:00:00 | Version 1.3.9 finished. | Updated the average user info for the month to concatenate child replies, and added a new leaderboard Big Kids Club, tracking largest concatenated posts.
#### 08/02/20 | 17:45:00 | Version 1.3.10 finished.| Updated single line statistics section to have many more tracked stats.  Further changes to print formatting will be undocumented.
#### 10/05/20 | 15:30:00 | Version 1.4.2 finished. | Pastebin API, weighted leaderboards, print formatting, Party Goers, Snooze Button, Travelers, Streak bugs.  Very large update.
#### 03/09/21 | 21:00:00 | Version 1.5.0 finished. | New system in place using a template text file and delimiter to format 99% of a reddit post ahead of time - improvements are large.  Snooze is back!
#### 03/10/21 | 11:00:00 | Version 1.5.1 finished. | Added a new submission processing backend to cover for gaps in reddit searches.  Works for now, will move to a more stable backend eventually.

#### Welcome to the WAYR Monthly manager script!  If you've never seen a lick of Python before in your life then it's hard to be able to understand anything by combing through.
#### This script focuses on sending a search query to the /r/visualnovels subreddit and analyzing a host of different datasets off of the weekly recurring WAYR (What Are You Reading?) threads.
#### Things are currently separated between specific, monthly analytics and year-in-total leaderboeards based off of various different criteria.
#### Any and all green text you see will serve to explain what individual blocks of code do.  If you have any other questions, message /u/PHNX_Arcanus on reddit.
#### If you have any ideas for specific analytics to track, feel free to let me know or to modify this script on your own and find what you're looking for.
#### The global macros section contains variables that are used throughout the code for various parameters.  Change them to your liking to see how the data is influenced.
#### This code is my own, written by /u/PHNX_Arcanus.  It is being made publicly available to view or repurpose to your own desires, however please credit me if necessary or recommended.

# # # # Library Imports
import praw
import math
import sys, os
import logging
from pbwrap import Pastebin
from datetime import datetime, date, timedelta
from collections import OrderedDict
from requests import Session

# # # # Global Filter Macros
PRINT_ALL = True
DIET_WAYRSTATS = False

LEADERBOARDS_ON = True
MONTHLY_ON = True
DELTARANK_ON = False

REDDIT_POST = True
PASTE_BIN = False

# # # # Global Constants
YEAR = 2021
MONTH = 10
CALENDAR = { 1 : "Jan" , 2 : "Feb" , 3 : "Mar" , 4 : "Apr" , 5 : "May" , 6 : "Jun" , 7 : "Jul" , 8 : "Aug" , 9 : "Sep" , 10 : "Oct" , 11 : "Nov" , 12 : "Dec" }
POSTS_PER_MONTH = 3
MIN_POST_SIZE = 1
FIRST_THREAD = " Jan 6"
BLABBER_MOUTH = 1500
LVL_EXP = 1000
MONTHLY_OUTPUT = 150
YEARLY_OUTPUT = 300

# # # # Clears the log to write a new one
FILE_NAME = r".\logs\[log] [{}-{}] [{}.{}].txt".format(datetime.now().month, datetime.now().day, datetime.now().hour, datetime.now().minute)
if os.path.isfile(FILE_NAME): os.remove(FILE_NAME)
logging.basicConfig(format = "%(message)s", filename = FILE_NAME, level = logging.INFO)

# # # # Creates a user session for Pastebin, which allows posting full outputs to the website all from this script
myPastebin = Pastebin("!!You will need to obtain an API token from pastebin to use this feature!!")
pbUser = myPastebin.authenticate("Your username here", "Your password here")

# # # # Sends a call to the Reddit API to receive authentication.
Reddit = praw.Reddit(client_id = "your reddit User ID, different from username",
                     client_secret = "obtained from the reddit bot link process",
                     refresh_token = "obtained from the reddit bot link process",
                     user_agent = "The name of this service, can be anything")

########################################################################################################################################
########################################################################################################################################

# # # # Class data structure used to hold info for user averages
# # # # This class is stored in a dictionary in a couple modules below: it allows is the ability to store more than one piece of information in a dictionary key-value pair.
class UserPostInfo:
    def __init__(self):
        self.totalPosts = 0
        self.totalPoints = 0

########################################################################################################################################
########################################################################################################################################

# # # # Class data structure used to hold info for consecutive post streaks.
# # # # Same as above, this allows us to create a dictionary where just one key can access three different pieces of data.
class UserStreakInfo:
    def __init__(self):
        self.streakVal = 0
        self.startThread = 0
        self.endThread = 0

########################################################################################################################################
########################################################################################################################################

# # # # This is the LeaderboardManager class.  It's responsible for getting the analytics of year-long leaderboards.
# # # # Rather than do a lot of hyper-focused monthly analytics, this class focuses solely on year-in-total metrics and generates leaderboards based on certain criteria.
class WAYRLeaderboardManager:

# # # # Default Constructor for initializing private variables.
    def __init__(self):
        self.curStreakContext = {}
        self.streakData = {}
        self.lastThread = 0
        self.userAvgData = {}
        self.partyGoers = {}
        self.sweetTalkers = {}
        self.blabberMouths = {}
        self.bigKids = {}
        self.bigKidConcat = 0
        self.bookWorms = {}
        self.travelPeeps = {}
        
        self.pbString = ""
        self.pString = ""
        self.leadString = ""
        self.rankWeight = 0
        self.lastData = 0

# # # # Generate streak information: this set of functions does a lot.  It keeps a running list of streak data as it crawls through the weekly posts one by one.
# # # # One of three events occur on any given thread: A streak ends, a streak continues, or a streak starts.  Each event has different data associated with it.
# # # # When a streak starts, the user data is added to the database.  When a streak continues it increments their score.  A streak end is written to the database if it's a new record.
# # # # All streaks end on January 1, when the first weekly thread was posted.  Some extraneous actions are handled there.
# # # # Prints the results to the console and log.txt: the bottom function takes the dataset gathered in the first function and displays it in a formatted manner.
# # # # By default a user will need at least 2 consecutive posts to be considered valid, it then sorts by highest streak and outputs the top 10.
    def FindLongestStreak(self, submission):
        threadUsers = [comment.author.name for comment in submission.comments if comment.author]   
        newLosers = [user for user in self.curStreakContext if user not in threadUsers]
        newUsers = [name for name in threadUsers if name not in self.curStreakContext.keys()]    
        newCruisers = [user for user in self.curStreakContext if user in threadUsers]

        for newbie in newUsers:
            tempData = UserStreakInfo()
            tempData.endThread = submission.title.split("-")[1].strip()
            tempData.startThread = submission.title.split("-")[1].strip()
            tempData.streakVal += 1
            self.curStreakContext[newbie] = tempData
            if newbie not in self.streakData.keys(): self.streakData[newbie] = tempData

        for playa in newCruisers:
            self.curStreakContext[playa].streakVal += 1
            if self.curStreakContext[playa].streakVal >= self.streakData[playa].streakVal:
                self.streakData[playa].streakVal = self.curStreakContext[playa].streakVal

        for loser in newLosers:
            self.curStreakContext[loser].startThread = self.lastThread.title.split("-")[1].strip()
            if self.curStreakContext[loser].streakVal >= self.streakData[loser].streakVal:
                self.streakData[loser] = self.curStreakContext[loser]
            del self.curStreakContext[loser]    
        
        if submission.title.split("-")[1] == FIRST_THREAD:
            for edgeCase in newCruisers:
                self.curStreakContext[edgeCase].startThread = submission.title.split("-")[1].strip()
                if self.curStreakContext[edgeCase].streakVal >= self.streakData[edgeCase].streakVal:
                    self.streakData[edgeCase] = self.curStreakContext[edgeCase]
        self.lastThread = submission

    def PrintStreakData(self):
        actualStreaks = {}
        for user in self.streakData:
            if self.streakData[user].streakVal > 1:
                actualStreaks[user] = self.streakData[user].streakVal
        
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "#Year-in-Total Leaderboards\n\n**Leaderboard: Post Streak**"

        for i, user in enumerate(OrderedDict(sorted(actualStreaks.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                if i == 0 or self.lastData != actualStreaks[user]: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}] posts between {} and {}.\n".format(actualStreaks[user], self.streakData[user].startThread, self.streakData[user].endThread)
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}] posts between {} and {}.\n".format(actualStreaks[user], self.streakData[user].startThread, self.streakData[user].endThread)
                self.lastData = actualStreaks[user]

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Post Streak Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # Similar to the monthly analytics below, this concatenates the total character length and total number of posts per user for the year of 2020.
# # # # Taking the data gathered in the first function the parser goes through the results and outputs the data in a formatted manner.
# # # # So long as a user has made at least 4 posts in the entire year, they will be added to the leaderboard.
    def FindAvgPostLengths(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            if comment.author and not comment.author.name in self.userAvgData.keys():
                workingUserData = UserPostInfo()
                workingUserData.totalPoints = len(comment.body)
                workingUserData.totalPosts = 1
                self.userAvgData[comment.author.name] = workingUserData
            elif comment.author:
                self.userAvgData[comment.author.name].totalPoints += len(comment.body)
                self.userAvgData[comment.author.name].totalPosts += 1
            self.RecurseAverages(comment)

    def RecurseAverages(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if comment.author and reply.author:
                    if (comment.author.name == reply.author.name):
                        self.userAvgData[comment.author.name].totalPoints += len(reply.body)
                        #self.userAvgData[comment.author.name].totalPosts += 1
                        if reply.replies._comments.__len__() > 0:
                            self.RecurseAverages(reply)

    def PrintAverages(self):
        postAverages = {}
        for user in self.userAvgData:
            if self.userAvgData[user].totalPosts > 3:
                postAverages[user] = math.floor(self.userAvgData[user].totalPoints / self.userAvgData[user].totalPosts)        
        
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Avg Character Count**"
        for i, user in enumerate(OrderedDict(sorted(postAverages.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                self.pbString += str("    #{}: /u/{}".format(i + 1, user)).ljust(36, ".") + "[{}]\n".format(postAverages[user])
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(i + 1, user)).ljust(36, ".") + "[{}]\n".format(postAverages[user])
        
        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Avg Char Ct Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

        userLevels = {}
        for user in self.userAvgData: 
            lvlUp = LVL_EXP
            expTotal = self.userAvgData[user].totalPoints
            userLevels[user] = 0
            while expTotal > lvlUp:
                expTotal -= lvlUp
                lvlUp *= 1.044
                userLevels[user] += 1
        
        postLengths = {}
        for user in self.userAvgData: postLengths[user] = self.userAvgData[user].totalPoints

        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: User Level** - *Imagine total character count was EXP.*"

        for i, user in enumerate(OrderedDict(sorted(postLengths.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                if userLevels[user] > 0:
                    if i == 0 or self.lastData != userLevels[user]: self.rankWeight = i + 1
                    self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[Level {}] ({})\n".format(userLevels[user], postLengths[user])
                    if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[Level {}] ({})\n".format(userLevels[user], postLengths[user])
                    self.lastData = userLevels[user]

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "User Level Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # The Party Goers Club (formerly Early Birds) essentially tracks the number of days that your posts have seen the light of day.
# # # # The scoring works by subtracting the number of days between your post and the thread creation date from 7, and adding your total for the year/month.
    def FindPartyGoers(self, submission):
        for comment in submission.comments:
            if comment.author:
                userScore = 7 - (datetime.utcfromtimestamp(comment.created_utc) - datetime.utcfromtimestamp(submission.created_utc)).days
                if comment.author.name not in self.partyGoers.keys():
                    temp = UserPostInfo()
                    temp.totalPoints = userScore
                    temp.totalPosts = 1
                    self.partyGoers[comment.author.name] = temp
                else:
                    self.partyGoers[comment.author.name].totalPoints += userScore
                    self.partyGoers[comment.author.name].totalPosts += 1

    def PrintPartyGoers(self):
        orderedScores = {}
        for user in self.partyGoers: orderedScores[user] = self.partyGoers[user].totalPoints

        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Party Goers**"

        for i, user in enumerate(OrderedDict(sorted(orderedScores.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                if i == 0 or self.lastData != self.partyGoers[user].totalPoints: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{} - {}]\n".format(self.partyGoers[user].totalPoints, self.partyGoers[user].totalPosts)
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{} - {}]\n".format(self.partyGoers[user].totalPoints, self.partyGoers[user].totalPosts)
                self.lastData = self.partyGoers[user].totalPoints

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Party Goers Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

    def PrintSnoozers(self):
        orderedScores = {}
        for user in self.partyGoers: 
            #if float(self.partyGoers[user].totalPosts / self.partyGoers[user].totalPoints) > 0.2: 
            if self.partyGoers[user].totalPosts > 1: orderedScores[user] = float((self.partyGoers[user].totalPosts * 7) / self.partyGoers[user].totalPoints)

        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Snoozers Club**"

        for i, user in enumerate(OrderedDict(sorted(orderedScores.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                if i == 0 or self.lastData != self.partyGoers[user].totalPoints: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{:.2f} - {}]\n".format(float(orderedScores[user]), self.partyGoers[user].totalPosts)
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{:.2f} - {}]\n".format(orderedScores[user], self.partyGoers[user].totalPosts)
                self.lastData = self.partyGoers[user].totalPoints

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Snooze Button Monthly", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)


# # # # The Sweet Talker's Club tracks total comment replies for the year.
# # # # AutoModerator is likely to be at the top of this list every time, in which case good for you girl put that hustle in.
    def FindSweetTalkers(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            self.RecurseSweetTalkers(comment)

    def RecurseSweetTalkers(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if reply.replies._comments.__len__() > 0:
                    self.RecurseSweetTalkers(reply)
                if reply.author and reply.author.name not in self.sweetTalkers: 
                    self.sweetTalkers[reply.author.name] = 1
                elif reply.author:
                    self.sweetTalkers[reply.author.name] += 1

    def PrintSweetTalkers(self):
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Sweet Talker's Club**"

        for i, user in enumerate(OrderedDict(sorted(self.sweetTalkers.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:   
                if i == 0 or self.lastData != self.sweetTalkers[user]: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.sweetTalkers[user])
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.sweetTalkers[user])
                self.lastData = self.sweetTalkers[user]

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Sweet Talkers Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # The Blabber Mouth Club tracks users who have posted comments of at least BLABBER_MOUTH characters, defined above.
# # # # BLABBER_MOUTH should be kept more on the lower side of things as higher minimums will result in a leaderboard similar to the character averages.
    def FindBlabberMouths(self, submission):
        for comment in submission.comments:
            if comment.author and len(comment.body) >= BLABBER_MOUTH:
                if comment.author.name not in self.blabberMouths.keys():
                    self.blabberMouths[comment.author.name] = 1
                else:
                    self.blabberMouths[comment.author.name] += 1

    def PrintBlabberMouths(self):
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Blabber Mouth Club** - *Tracks how many posts you've made exceeding 1,500 characters.*"

        for i, user in enumerate(OrderedDict(sorted(self.blabberMouths.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                if i == 0 or self.lastData != self.blabberMouths[user]: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.blabberMouths[user])
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.blabberMouths[user])
                self.lastData = self.blabberMouths[user]

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Blabber Mouth Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # The Big Kids Club tracks the top individual posts with the highest character count for the year.
# # # # Users are able to have multiple entries on this leaderboard as it is about the largest posts, not individual users
    def FindBigKids(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            if comment.author:
                self.bigKidConcat = len(comment.body)
                self.RecurseBigKids(comment)
                self.bigKids[comment.id] = self.bigKidConcat

        for i, comment in enumerate(OrderedDict(sorted(self.bigKids.items(), key = lambda x : -x[1])), 0):
            if i >= 50:
                self.bigKids.pop(comment)

    def RecurseBigKids(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if comment.author and reply.author:
                    if (comment.author.name == reply.author.name):
                        self.bigKidConcat += len(reply.body)
                        if reply.replies._comments.__len__() > 0:
                            self.RecurseBigKids(reply)

    def PrintBigKids(self):
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Big Kids Club**"

        for i, id in enumerate(OrderedDict(sorted(self.bigKids.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                commentInfo = Reddit.comment(id)
                userName = commentInfo.author.name
                postDate = commentInfo.submission.title.split("-")[1].strip()
                self.pbString += str("    #{}: /u/{}".format(i + 1, userName)).ljust(36, ".") + str("[{}]".format(self.bigKids[id]).ljust(10, ".") + "[{}]\n".format(postDate))
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(i + 1, userName)).ljust(36, ".") + str("[{}]".format(self.bigKids[id]).ljust(10, ".") + "[{}]\n".format(postDate))
        
        if PASTE_BIN: self.leadString += " - [Top 50 Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Big Kids Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)


# # # # The Book Worm's club simply tracks the total number of posts you have made for the year.
# # # # I came up with this one when I thought of it being a rework for streaks, but decided to keep both.
    def FindBookWorms(self, submission):
        for comment in submission.comments:
            if comment.author:
                if comment.author.name not in self.bookWorms.keys():
                    self.bookWorms[comment.author.name] = 1
                else:
                    self.bookWorms[comment.author.name] += 1

    def PrintBookWorms(self):
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Book Worms Club** - *Simply tracks your total post number for the year.*"

        for i, user in enumerate(OrderedDict(sorted(self.bookWorms.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:
                if i == 0 or self.lastData != self.bookWorms[user]: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.bookWorms[user])
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.bookWorms[user])
                self.lastData = self.bookWorms[user]
        
        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Book Worm Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)


# # # # The traveler's club tracks all comment replies separate from replies you make to your own post.  
# # # # This is a great way of measuring your interaction with other posts besides your own.
    def FindTravelers(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            if comment.author:
                parent = comment.author.name
                self.RecurseTravelers(comment, parent)

    def RecurseTravelers(self, comment, parent):
        if not comment.stickied:
            for reply in comment.replies:
                if reply.replies._comments.__len__() > 0:
                    self.RecurseTravelers(reply, parent)
                if reply.author and reply.author.name != parent:
                    if reply.author.name not in self.travelPeeps: 
                        self.travelPeeps[reply.author.name] = 1
                    else:
                        self.travelPeeps[reply.author.name] += 1

    def PrintTravelers(self):
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Leaderboard: Travelers Club**"

        for i, user in enumerate(OrderedDict(sorted(self.travelPeeps.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < YEARLY_OUTPUT:   
                if i == 0 or self.lastData != self.travelPeeps[user]: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.travelPeeps[user])
                if i < YEARLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.travelPeeps[user])
                self.lastData = self.travelPeeps[user]

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Travelers Leaderboard", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString + "\n___\n")

########################################################################################################################################
########################################################################################################################################

# # # # This is the MonthlyManager class, split off from the leaderboard class so as to allow for a much larger, more focused level of analytics on any given month's worth of data.
# # # # The class is organized into modules that go through the search results at the bottom of the script and concatenate targeted data based off of various parameters.
class WAYRMonthlyManager:

    # Default Constructor for initializing private variables.
    def __init__(self, minPerMonth, minPostSize):
        self.minPerMonth = minPerMonth
        self.minPostSize = minPostSize
        self.winnerDict = { "PHNX_Arcanus" : 0 }
        self.wayrCandidates = []
        self.timesRun = { "winners" : False, "bigboi" : False , "avgpost" : False , "perfect" : False }
        self.bigKids = {}
        self.bigKidConcat = 0
        self.totalComments = 0
        self.totalCharacters = 0
        self.totalParentComments = 0
        self.totalParentCharacters = 0
        self.monthlyParents = {}
        self.monthlyComments = {}
        self.monthlyCharacters = {}
        self.monthlyParacters = {}
        self.userAvgData = {}
        self.uniqueUsers = 0
        self.totalThreads = 0
        self.partyGoers = {}
        self.sweetTalkers = {}
        self.prettyPeople = []
        self.perfectAttendees = []
        self.travelPeeps = {}
        self.totalUsers = []

        self.pbString = ""
        self.pString = ""
        self.leadString = ""
        self.rankWeight = 0
        self.lastData = 0

# # # # Find valid candidates for the monthly contest: so long as a user has made at least POSTS_PER_MONTH posts in a single month, their name will be added to a list of candidates.
# # # # Manages the data collected in the first function and prints it to the log/console.
    def FindWinCandidates(self, submission):   
        for comment in submission.comments:
            if comment.author:
                OP = str(comment.author)
                #logging.info(OP + " - " + str(len(comment.body)))
                if len(comment.body) >= self.minPostSize:
                    if not self.timesRun["winners"]:
                        self.winnerDict[OP] = 1
                        self.timesRun["winners"] = True
                    else:
                        if OP in self.winnerDict:
                            self.winnerDict[OP] += 1
                        else:
                            self.winnerDict[OP] = 1

    def PrintWinCandidates(self):
        wayrWinners = [] 
        for user in self.winnerDict:
            if self.winnerDict[user] >= self.minPerMonth:
                wayrWinners.append(user)
        self.wayrCandidates = wayrWinners
        
        logging.info("Qualifiers for {} WAYR:\n".format(CALENDAR[MONTH]))
        for winner in self.wayrCandidates:
            logging.info("    /u/" + winner)

# # # # Finds the largest post for the month.
# # # # Currently only counts parent comments, module will likely be updated to concatenate child comments as well.
    def FindBigKids(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            if comment.author:
                self.bigKidConcat = len(comment.body)
                self.RecurseBigKids(comment)
                self.bigKids[comment.id] = self.bigKidConcat

        for i, comment in enumerate(OrderedDict(sorted(self.bigKids.items(), key = lambda x : -x[1])), 0):
            if i >= 25:
                self.bigKids.pop(comment)

    def RecurseBigKids(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if comment.author and reply.author:
                    if (comment.author.name == reply.author.name):
                        self.bigKidConcat += len(reply.body)
                        if reply.replies._comments.__len__() > 0:
                            self.RecurseBigKids(reply)

    def PrintBigKids(self):
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Monthly Big Kids Club:** *Tracks the largest posts for the month/year.*"

        for i, id in enumerate(OrderedDict(sorted(self.bigKids.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < MONTHLY_OUTPUT:
                commentInfo = Reddit.comment(id)
                userName = commentInfo.author.name
                postDate = commentInfo.submission.title.split("-")[1].strip()
                self.pbString += str("    #{}: /u/{}".format(i + 1, userName)).ljust(36, ".") + str("[{}]".format(self.bigKids[id]).ljust(10, ".") + "[{}]\n".format(postDate))
                if i < MONTHLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(i + 1, userName)).ljust(36, ".") + str("[{}]".format(self.bigKids[id]).ljust(10, ".") + "[{}]\n".format(postDate))

        if PASTE_BIN: self.leadString += " - [Top 25 Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Big Kids Monthly", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # Gets the average character count of all posts for the month as well as the average number of characters.   
# # # # Module started out very lightweight but additions over time have made this a robust module worthy of being standalone.
    def FindAvgPostInfo(self, submission):
        curThread = submission.title.split("-")[1].strip()
        submission.comments.replace_more(limit = None)
        self.totalThreads += 1

        self.monthlyParents[curThread] = 0
        self.monthlyComments[curThread] = 0
        self.monthlyCharacters[curThread] = 0
        self.monthlyParacters[curThread] = 0
        
        for comment in submission.comments:
            if comment.author:
                if (comment.author_flair_css_class == None or comment.author_flair_css_class.lower() == "xxxnoflair") and comment.author.name not in self.prettyPeople:
                    self.prettyPeople.append(comment.author.name)
            
                if comment.author.name not in self.totalUsers:
                    self.totalUsers.append(comment.author.name)

                self.totalComments += 1
                self.totalCharacters += len(comment.body)
                self.totalParentComments += 1
                self.totalParentCharacters += len(comment.body)

                self.monthlyParents[curThread] += 1
                self.monthlyComments[curThread] += 1
                self.monthlyCharacters[curThread] += len(comment.body)
                self.monthlyParacters[curThread] += len(comment.body)
                self.RecurseAverages(comment, curThread)

    def RecurseAverages(self, comment, curThread):
        if not comment.stickied:
            for reply in comment.replies:
                if reply.author:
                    if reply.replies._comments.__len__() > 0:
                        self.RecurseAverages(reply, curThread)
                    if reply.author.name not in self.totalUsers:
                        self.totalUsers.append(comment.author.name)
                    self.totalComments += 1
                    self.totalCharacters += len(reply.body)
                    self.monthlyComments[curThread] += 1
                    self.monthlyCharacters[curThread] += len(comment.body)
                    if comment.author.name == reply.author.name:
                        self.totalParentCharacters += len(reply.body)
                        self.monthlyParacters[curThread] += len(comment.body)

    def PrintAvgPostInfo(self):
        prettyPeople = math.floor(((len(self.userAvgData) - len(self.prettyPeople)) / len(self.userAvgData)) * 100)
        logging.info("___\n\n#Single Line Statistics\n\n* The Pretty People Coefficient: Percentage of users who have set custom character flairs: [{}%]".format(prettyPeople))
        logging.info("* A total of [{}] unique users commented on the threads this month.".format(len(self.totalUsers)))
        logging.info("* We had an average of [{}] WAYR posts per thread this month.".format(math.floor(self.totalParentComments / self.totalThreads)))
        logging.info("* We had an average of [{}] total comments per thread this month.".format(math.floor(self.totalComments / self.totalThreads)))
        logging.info("* The average length of WAYR posts for this month is [{}] characters.".format(math.floor(self.totalParentCharacters / self.totalParentComments)))
        logging.info("* The average length of any comment for this month is [{}] characters.".format(math.floor(self.totalCharacters / self.totalComments)))
        logging.info("* There was a total average of [{}] characters per thread this month.".format(math.floor(self.totalCharacters / self.totalThreads)))
        logging.info("* There was a total average of [{}] characters for WAYR posts per thread this month.".format(math.floor(self.totalParentCharacters / self.totalThreads)))
        
        logging.info("\nHere are the totals this month across all threads:\n\n* [{}] characters typed\n* [{}] total WAYR post characters\n* [{}] total comments\n* [{}] total WAYR posts".format(self.totalCharacters, self.totalParentCharacters, self.totalComments, self.totalParentComments))
        logging.info("\nAnd the individual thread breakdowns:\n\n* [Thread] - [total char] | [comments] | [wayr char] | [wayr posts]")
        for thread in self.monthlyCharacters:
            logging.info("* [{}] - [{}] | [{}] | [{}] | [{}]".format(thread, self.monthlyCharacters[thread], self.monthlyComments[thread], self.monthlyParacters[thread], self.monthlyParents[thread]))

# # # # This module covers a lot of different data sets because of how thorough it is with the initial data collection call.
# # # # The number of posts and total character count of all posts for all unique users vising the thread in a month is collected here.
# # # # From there we can take that data and get a bunch of different metrics: total unique users, average character count, user "level" gained for the month, and other small leaderboard stats.
    def FindUserPostInfo(self, submission):
        for comment in submission.comments:
            if comment.author and not comment.author.name in self.userAvgData.keys():
                workingUserData = UserPostInfo()
                workingUserData.totalPoints = len(comment.body)
                workingUserData.totalPosts = 1
                self.userAvgData[comment.author.name] = workingUserData
                self.RecursePostInfo(comment)
            elif comment.author:
                self.userAvgData[comment.author.name].totalPoints += len(comment.body)
                self.userAvgData[comment.author.name].totalPosts += 1
                self.RecursePostInfo(comment)

    def RecursePostInfo(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if comment.author and reply.author and comment.author.name == reply.author.name:
                    self.userAvgData[comment.author.name].totalPoints += len(reply.body)
                    if reply.replies._comments.__len__() > 0:
                        self.RecursePostInfo(reply)

    def PrintUserPostInfo(self):
        logging.info("\n**User Average Data:** *[user] - [char count / # posts = average]*\n")
        printString = ""
        orderedData = {}
        for user in self.userAvgData: orderedData[user] = self.userAvgData[user].totalPoints
        for i, user in enumerate(OrderedDict(sorted(orderedData.items(), key = lambda x : -x[1])), 0):
            userAvg = math.floor(self.userAvgData[user].totalPoints / self.userAvgData[user].totalPosts)
            if i % 2 == 1:
                printString += str("    [{}]".format(user)).ljust(26, ".") + str("[{}/{} = {}]".format(self.userAvgData[user].totalPoints, self.userAvgData[user].totalPosts, userAvg)).rjust(20, ".")
                logging.info(printString)
                printString = ""
            else:
                printString += str("    [{}]".format(user)).ljust(26, ".") + str("[{}/{} = {}]".format(self.userAvgData[user].totalPoints, self.userAvgData[user].totalPosts, userAvg)).rjust(20, ".")
        if printString != "":
            logging.info(printString)
    
    def PrintMonthlyCharCount(self):
        orderedData = {}
        for user in self.userAvgData: orderedData[user] = math.floor(self.userAvgData[user].totalPoints / self.userAvgData[user].totalPosts) if self.userAvgData[user].totalPosts > 1 else 0
        
        self.pbString = ""
        self.pString = ""
        self.leadString = "\n___\n\n#Monthly Leaderboards\n\n**Monthly: Avg Character Count**"

        for i, user in enumerate(OrderedDict(sorted(orderedData.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < MONTHLY_OUTPUT:
                if orderedData[user] > 0:
                    self.pbString += str("    #{}: /u/{}".format(i + 1, user)).ljust(36, ".") + "[{}]\n".format(orderedData[user])
                    if i < MONTHLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(i + 1, user)).ljust(36, ".") + "[{}]\n".format(orderedData[user])

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Monthly Averages", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # The Party Goers Club (formerly Early Birds) essentially tracks the number of days that your posts have seen the light of day.
# # # # The scoring works by subtracting the number of days between your post and the thread creation date from 7, and adding your total for the year/month.
    def FindPartyGoers(self, submission):
        for comment in submission.comments:
            if comment.author:
                userScore = 7 - (datetime.utcfromtimestamp(comment.created_utc) - datetime.utcfromtimestamp(submission.created_utc)).days
                if comment.author.name not in self.partyGoers.keys():
                    temp = UserPostInfo()
                    temp.totalPoints = userScore
                    temp.totalPosts = 1
                    self.partyGoers[comment.author.name] = temp
                else:
                    self.partyGoers[comment.author.name].totalPoints += userScore
                    self.partyGoers[comment.author.name].totalPosts += 1

    def PrintPartyGoers(self):
        orderedScores = {}
        for user in self.partyGoers: orderedScores[user] = self.partyGoers[user].totalPoints
        
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Monthly Party Goers Club:** *Tracks the days your posts have existed in the threads, and your post count.*"

        for i, user in enumerate(OrderedDict(sorted(orderedScores.items(), key = lambda x : -x[1])), 0):
            if (PRINT_ALL or i < MONTHLY_OUTPUT):
                if i == 0 or self.lastData != self.partyGoers[user].totalPoints: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{} - {}]\n".format(self.partyGoers[user].totalPoints, self.partyGoers[user].totalPosts)
                if i < MONTHLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{} - {}]\n".format(self.partyGoers[user].totalPoints, self.partyGoers[user].totalPosts)
                self.lastData = self.partyGoers[user].totalPoints

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Party Goers Monthly", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

    def PrintSnoozers(self):
        orderedScores = {}
        for user in self.partyGoers: 
            #if float(self.partyGoers[user].totalPosts / self.partyGoers[user].totalPoints) > 0.2: 
            if self.partyGoers[user].totalPosts > 1: orderedScores[user] = float((self.partyGoers[user].totalPosts * 7) / self.partyGoers[user].totalPoints)

        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Monthly Snoozers Club:** *Using an algorithm on party-goers we can see some more unsung heroes:*"

        for i, user in enumerate(OrderedDict(sorted(orderedScores.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < MONTHLY_OUTPUT:
                if i == 0 or self.lastData != self.partyGoers[user].totalPoints: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{:.2f} - {}]\n".format(orderedScores[user], self.partyGoers[user].totalPosts)
                if i < MONTHLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{:.2f} - {}]\n".format(orderedScores[user], self.partyGoers[user].totalPosts)
                self.lastData = self.partyGoers[user].totalPoints

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Snooze Button Monthly", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # The Sweet Talker's Club tracks total comment replies.  
# # # # Another leaderboard, the Taveler's club, tracks similar data but with its own twist.
    def FindSweetTalkers(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            self.RecurseSweetTalkers(comment)

    def RecurseSweetTalkers(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if reply.replies._comments.__len__() > 0:
                    self.RecurseSweetTalkers(reply)
                if reply.author and reply.author.name not in self.sweetTalkers: 
                    self.sweetTalkers[reply.author.name] = 1
                elif reply.author:
                    self.sweetTalkers[reply.author.name] += 1

    def PrintSweetTalkers(self):
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Monthly Sweet Talker's Club:** *Tracks total comment replies for the month/year.*"

        for i, user in enumerate(OrderedDict(sorted(self.sweetTalkers.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < MONTHLY_OUTPUT:
                if i == 0 or self.lastData != self.sweetTalkers[user]: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.sweetTalkers[user])
                if i < MONTHLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.sweetTalkers[user])
                self.lastData = self.sweetTalkers[user]

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Sweet Talkers Monthly", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString)

# # # # The Perfect Attendees Club tracks users who have posted in every post for the month.
# # # # Currently this module only tracks parent comments.  Should demand be high enough a module that analyzes child comments can be added.
    def FindPerfectAttendees(self, submission): 
        if not self.timesRun["perfect"]:
            self.timesRun["perfect"] = True
            for comment in submission.comments:
                if comment.author:
                    self.perfectAttendees.append(comment.author.name)
        else:
            threadUsers = [comment.author.name for comment in submission.comments if comment.author]
            self.perfectAttendees = [user for user in threadUsers if user in self.perfectAttendees]

    def PrintPerfectAttendees(self):
        logging.info("___\n\n#User Lists\n\n**The Perfect Attendees:** *Posted in every thread this month.*\n")
        for user in self.perfectAttendees:
            logging.info("    /u/{}".format(user))

# # # # The traveler's club tracks all comment replies separate from replies you make to your own post.  
# # # # This is a great way of measuring your interaction with other posts besides your own.
    def FindTravelers(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            if comment.author:
                parent = comment.author.name
                self.RecurseTravelers(comment, parent)

    def RecurseTravelers(self, comment, parent):
        if not comment.stickied:
            for reply in comment.replies:
                if reply.replies._comments.__len__() > 0:
                    self.RecurseTravelers(reply, parent)
                if reply.author and reply.author.name != parent:
                    if reply.author.name not in self.travelPeeps: 
                        self.travelPeeps[reply.author.name] = 1
                    else:
                        self.travelPeeps[reply.author.name] += 1

    def PrintTravelers(self):
        self.rankWeight = 0
        self.lastData = -1
        self.pbString = ""
        self.pString = ""
        self.leadString = "**Monthly Travelers Club:** *Tracks comment replies __excluding__ replies attached to your own WAYR post.*"

        for i, user in enumerate(OrderedDict(sorted(self.travelPeeps.items(), key = lambda x : -x[1])), 0):
            if PRINT_ALL or i < MONTHLY_OUTPUT:   
                if i == 0 or self.lastData != self.travelPeeps[user]: self.rankWeight = i + 1
                self.pbString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.travelPeeps[user])
                if i < MONTHLY_OUTPUT: self.pString += str("    #{}: /u/{}".format(self.rankWeight, user)).ljust(36, ".") + "[{}]\n".format(self.travelPeeps[user])
                self.lastData = self.travelPeeps[user]

        if PASTE_BIN: self.leadString += " - [Full Output]({})".format(myPastebin.create_paste(api_paste_code = self.pbString, api_paste_private = 0, api_paste_name = "Travelers Monthly", api_paste_expire_date = "N", api_paste_format = "python"))
        logging.info(self.leadString + "\n\n" + self.pString + "\n___")

########################################################################################################################################
########################################################################################################################################

def UpvoteModule(submission):
    for comment in submission.comments:
        if comment.author:
            try: comment.upvote()
            except: temp = 0

def LeaderboardModule(WAYRStats, submission):
    WAYRStats.FindAvgPostLengths(submission)
    if not DIET_WAYRSTATS: WAYRStats.FindBigKids(submission)
    WAYRStats.FindPartyGoers(submission)
    WAYRStats.FindSweetTalkers(submission)
    WAYRStats.FindBlabberMouths(submission)
    WAYRStats.FindBookWorms(submission)
    WAYRStats.FindTravelers(submission)
    if "untranslated" not in submission.title.lower(): WAYRStats.FindLongestStreak(submission)

def MonthlyModule(WAYR, submission):
    WAYR.FindWinCandidates(submission)
    if not DIET_WAYRSTATS: WAYR.FindBigKids(submission)
    WAYR.FindAvgPostInfo(submission)
    WAYR.FindUserPostInfo(submission)
    WAYR.FindPartyGoers(submission)
    WAYR.FindSweetTalkers(submission)
    WAYR.FindTravelers(submission)
    if "untranslated" not in submission.title.lower(): WAYR.FindPerfectAttendees(submission)

def PrintLeaderboards():
    WAYRStats.PrintStreakData()
    if not DIET_WAYRSTATS:WAYRStats.PrintBigKids()
    WAYRStats.PrintAverages()
    WAYRStats.PrintPartyGoers()
    WAYRStats.PrintSnoozers()
    WAYRStats.PrintSweetTalkers()
    WAYRStats.PrintBlabberMouths()
    WAYRStats.PrintBookWorms()
    WAYRStats.PrintTravelers()

def PrintMonthly():
    WAYR.PrintWinCandidates()
    WAYR.PrintPerfectAttendees()
    WAYR.PrintUserPostInfo()
    WAYR.PrintAvgPostInfo()
    WAYR.PrintMonthlyCharCount()
    if not DIET_WAYRSTATS: WAYR.PrintBigKids()
    WAYR.PrintPartyGoers()
    WAYR.PrintSweetTalkers()
    WAYR.PrintSnoozers()
    WAYR.PrintTravelers()

########################################################################################################################################
########################################################################################################################################

visualNovels = Reddit.subreddit("visualnovels")

# # # # Instances of our class structures written above - these instances store all of the relevant data we will access in all the print statements below.
WAYRStats = WAYRLeaderboardManager()
LeaderboardSnapshot = WAYRLeaderboardManager()
WAYR = WAYRMonthlyManager(POSTS_PER_MONTH, MIN_POST_SIZE)
MonthlySnapshot = WAYRMonthlyManager(POSTS_PER_MONTH, MIN_POST_SIZE)

# Must have been an issue with the API not returning these results.
missingPosts = { "Feb 3" : Reddit.submission("lbwscl"), "Jan 27" : Reddit.submission("l6d3fz") }
runMissing = False
lastSubmitted = ""

# # # # This is the official call we are making to the Reddit API.  It sends a search query to the visualnovels subreddit to isolate the WAYR threads, and sets a for loop to iterate through them.
# # # # The for loop is split up into 2 sections, 1 section for yearly analytics and the other for montly.
# # # # This for loop manages all of the modules that we want to process - they can be toggled on and off by simply adding the comment indicator [#] at the start of the line.
# # # # These functions only serve to collect data.  After the for loop finishes we print out the data that's been collected.
# # # # This script analyzes all data from both the regular and untranslated threads however the streak modules break completely when parsing both, and is set to only process the main WAYR threads.
for submission in visualNovels.search("\"What are you reading?\" author:AutoModerator", sort = "new", time_filter = "all"):
    if lastSubmitted != "" and (datetime.utcfromtimestamp(lastSubmitted.created_utc) - datetime.utcfromtimestamp(submission.created_utc)).days > 10:
        for post in missingPosts:
            dateDiff = (datetime.utcfromtimestamp(lastSubmitted.created_utc) - datetime.utcfromtimestamp(missingPosts[post].created_utc)).days
            if dateDiff < 10 and dateDiff > 0:
                curMonth = int(datetime.utcfromtimestamp(missingPosts[post].created_utc).month)
                if curMonth <= MONTH:
                    if int(datetime.utcfromtimestamp(missingPosts[post].created_utc).year) == YEAR:
                        print(missingPosts[post].title)
                        if LEADERBOARDS_ON: LeaderboardModule(WAYRStats, missingPosts[post])
                        if curMonth == MONTH: 
                            if MONTHLY_ON: MonthlyModule(WAYR, missingPosts[post])
                    elif int(datetime.utcfromtimestamp(missingPosts[post].created_utc).year) == YEAR - 1:
                        break
            lastSubmitted = missingPosts[post]
    #UpvoteModule(submission)
    curMonth = int(datetime.utcfromtimestamp(submission.created_utc).month)
    if curMonth <= MONTH:
        if int(datetime.utcfromtimestamp(submission.created_utc).year) == YEAR:
            print(submission.title)
            if LEADERBOARDS_ON: LeaderboardModule(WAYRStats, submission)
            if curMonth == MONTH: 
                if MONTHLY_ON: MonthlyModule(WAYR, submission)
        elif int(datetime.utcfromtimestamp(submission.created_utc).year) == YEAR - 1:
            break
    if DELTARANK_ON and curMonth <= MONTH - 1:
        if int(datetime.utcfromtimestamp(submission.created_utc).year) == YEAR:
            print("Snapshot of " + submission.title)
            if LEADERBOARDS_ON: LeaderboardModule(LeaderboardSnapshot, submission)
            if curMonth == MONTH: 
                if MONTHLY_ON: MonthlyModule(MonthlySnapshot, submission)
    lastSubmitted = submission

# # # # This block of code sets up the debug logger, for outputting info to the console as well as saving the output to a file.
# # # # Gonna be honest I copied this bit straight off of stackOverflow, it works that's all I care about
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

# # # # These functions are for parsing the data that has been gathered in the above for loop.  There's a TON of data to go through so we can't do it on the fly as it's being gathered.
# # # # template.txt is a text file I made as a basic setup to handle as much of the post formatting as possible before I press the submit button.
if REDDIT_POST:
    with open(r".\template.txt", "r") as templateFile:
        curLine = templateFile.readline()
        while curLine:
            if curLine == "|\n":
                if MONTHLY_ON: PrintMonthly()
                if LEADERBOARDS_ON: PrintLeaderboards()
            else:
                logging.info(curLine)
            curLine = templateFile.readline()
else:
    if MONTHLY_ON: PrintMonthly()
    if LEADERBOARDS_ON: PrintLeaderboards()

########################################################################################################################################
########################################################################################################################################
# Leaderboard monthly tracking notes
# Model 1: Create duplicate class structures to create a snapshot of the previous month's data and create a new module to parse data
# Model 2: Adjust current print statements to save to an additional file, develop module that parses file and data