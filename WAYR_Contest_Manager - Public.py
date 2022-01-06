#### C H A N G E L O G ####
#### 04/18/20 | 19:00:00 | Version 1.0 finished.     | Basics covered, ready to debut on the subreddit.
#### 04/23/20 | 22:30:00 | Version 1.1 finished.     | Doubled the amount of leaderboards and added additional monthly stats.
#### 04/26/20 | 16:00:00 | Version 1.2 finished.     | Restructured code so all print calls are class-contained.  Added additional monthly metrics and drastically improved user average data module.
#### 04/30/20 | 15:00:00 | Version 1.2.1 finished.   | Updated Monthly Sweet Talker's and Early Bird Clubs to be a top 5 leaderboard instead of a list of qualifying users.
#### 05/05/20 | 16:20:00 | Version 1.2.2 finished.   | Updated Early Birds to count any post within the first 24 hours of the thread going live rather than the first hour.
#### 05/13/20 | 21:00:00 | Version 1.3 finished.     | Added recursive concatenation to a number of post-length related modules, updated BigBoi with said functionality and comment depth, and added scaling to user levels.
#### 05/18/20 | 22:42:00 | Version 1.3.1 finished.   | Significantly cleaned up most print statements using enumerate() function.
#### 05/27/20 | 19:10:00 | Version 1.3.2 finished.   | Added the UpvoteModule that upvotes every parent comment in the thread because you're all beautiful and deserve the best.
#### 05/27/20 | 19:30:00 | Version 1.3.3 finished.   | Refactored base loop to use functions so entire modules can be toggled with a single hash sign rather than having to comment out every individual module.
#### 06/02/20 | 12:30:00 | Version 1.3.3.1 finished. | Did the 1.3.3 to the print functions, and added total average comments vs total parent comments.
#### 06/02/20 | 12:50:00 | Version 1.3.3.2 finished. | Implemented the PRINT_ALL global variable that changes output to either a set number of list items or 100% of the data.  Added LEADERBOARDS_ON and MONTHLY_ON similarly.
#### 06/02/20 | 12:50:00 | Version 1.3.4 finished.   | Added another module to monthly averages, cleaned up formatting; script is ready to debut.
#### 06/03/20 | 15:55:00 | Version 1.3.4.1 finished. | Fixed Early Birds to accurately track 24 hours after the post is made, rather than only on the same calendar date.

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
from datetime import datetime, date
from collections import OrderedDict
from requests import Session

# # # # Global Filter Macros
PRINT_ALL = True
LEADERBOARDS_ON = True
MONTHLY_ON = False
YEAR = 2020
MONTH = 5
CALENDAR = { 1 : "Jan" , 2 : "Feb" , 3 : "Mar" , 4 : "Apr" , 5 : "May" , 6 : "Jun" , 7 : "Jul" , 8 : "Aug" , 9 : "Sep" , 10 : "Oct" , 11 : "Nov" , 12 : "Dec" }
POSTS_PER_MONTH = 2
MIN_POST_SIZE = 1
FIRST_THREAD = " Jan 1"
BLABBER_MOUTH = 1500
LVL_EXP = 1000

# # # # Clears the log to write a new one
FILE_NAME = r".\logs\[log] [{}-{}] [{}.{}].txt".format(datetime.now().month, datetime.now().day, datetime.now().hour, datetime.now().minute)
if os.path.isfile(FILE_NAME): os.remove(FILE_NAME)
logging.basicConfig(format = "%(message)s", filename = FILE_NAME, level = logging.INFO)

########################################################################################################################################
########################################################################################################################################

# # # # Class data structure used to hold info for user averages
# # # # This class is stored in a dictionary in a couple modules below: it allows is the ability to store more than one piece of information in a dictionary key-value pair.
class UserPostInfo:
    def __init__(self):
        self.totalPosts = 0
        self.totalChar = 0

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
        self.earlyBirds = {}
        self.sweetTalkers = {}
        self.blabberMouths = {}

# # # # Generate streak information: this set of functions does a lot.  It keeps a running list of streak data as it crawls through the weekly posts one by one.
# # # # InitStreakData - the first time through will be assignment, not increment calls, and this manages the first pass.
# # # # One of three events occur on any given thread: A streak ends, a streak continues, or a streak starts.  Each event has different data associated with it.
# # # # When a streak starts, the user data is added to the database.  When a streak continues it increments their score.  A streak end is written to the database if it's a new record.
# # # # All streaks end on January 1, when the first weekly thread was posted.  Some extraneous actions are handled there.
# # # # Prints the results to the console and log.txt: the bottom function takes the dataset gathered in the first function and displays it in a formatted manner.
# # # # By default a user will need at least 2 consecutive posts to be considered valid, it then sorts by highest streak and outputs the top 10.
    def InitStreakData(self, submission):
        self.lastThread = submission
        for comment in submission.comments:
            if comment.author:
                tempData = UserStreakInfo()
                tempData.endThread = submission.title.split("-")[1].strip()
                tempData.startThread = submission.title.split("-")[1].strip()
                tempData.streakVal += 1
                self.curStreakContext[comment.author.name] = tempData
                self.streakData[comment.author.name] = tempData

    def FindLongestStreak(self, submission):
        threadUsers = [comment.author.name for comment in submission.comments if comment.author]   
        newLosers = [user for user in self.curStreakContext if user not in threadUsers]
        newUsers = [name for name in threadUsers if name not in self.streakData.keys()]    
        newCruisers = [user for user in self.curStreakContext if user in threadUsers]

        for newbie in newUsers:
            tempData = UserStreakInfo()
            tempData.endThread = submission.title.split("-")[1].strip()
            tempData.startThread = submission.title.split("-")[1].strip()
            tempData.streakVal += 1
            self.curStreakContext[newbie] = tempData
            self.streakData[newbie] = tempData

        for playa in newCruisers:
            self.curStreakContext[playa].streakVal += 1

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
        
        logging.info("\nLeaderboard stats: Longest Consecutive Post Streak")
        for i, user in enumerate(OrderedDict(reversed(sorted(actualStreaks.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 20:
                logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "[{}] posts between {} and {}.".format(actualStreaks[user], self.streakData[user].startThread, self.streakData[user].endThread))

# # # # Similar to the monthly analytics below, this concatenates the total character length and total number of posts per user for the year of 2020.
# # # # Taking the data gathered in the first function the parser goes through the results and outputs the data in a formatted manner.
# # # # So long as a user has made at least 4 posts in the entire year, they will be added to the leaderboard.
    def FindAvgPostLengths(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            if comment.author and not comment.author.name in self.userAvgData.keys():
                workingUserData = UserPostInfo()
                workingUserData.totalChar = len(comment.body)
                workingUserData.totalPosts = 1
                self.userAvgData[comment.author.name] = workingUserData
            elif comment.author:
                self.userAvgData[comment.author.name].totalChar += len(comment.body)
                self.userAvgData[comment.author.name].totalPosts += 1
            self.RecurseAverages(comment)

    def RecurseAverages(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if comment.author and reply.author:
                    if (comment.author.name == reply.author.name):
                        self.userAvgData[comment.author.name].totalChar += len(comment.body)
                        self.userAvgData[comment.author.name].totalPosts += 1
                        if reply.replies._comments.__len__() > 0:
                            self.RecurseAverages(reply)

    def PrintAverages(self):
        postAverages = {}
        for user in self.userAvgData:
            if self.userAvgData[user].totalPosts > 3:
                postAverages[user] = math.floor(self.userAvgData[user].totalChar / self.userAvgData[user].totalPosts)        
        
        logging.info("\nLeaderboard Stats: Highest Average Character Count")
        for i, user in enumerate(OrderedDict(reversed(sorted(postAverages.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 20:
                logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "[{}]".format(postAverages[user]))
        
        userLevels = {}
        logging.info("\nLeaderboard Stats: User Level")
        for user in self.userAvgData: 
            lvlUp = LVL_EXP
            expTotal = self.userAvgData[user].totalChar
            userLevels[user] = 0
            while expTotal > lvlUp:
                expTotal -= lvlUp
                lvlUp *= 1.044
                userLevels[user] += 1
            
        for i, user in enumerate(OrderedDict(reversed(sorted(userLevels.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 20:
                if userLevels[user] > 0:
                    logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "Level [{}] ({})".format(userLevels[user], self.userAvgData[user].totalChar))


# # # # The Early Bird Club tracks number of times a user has made a post within one hour of the WAYR thread going live.  
# # # # Users will need a minimum of 2 early bird posts to be considered for the leaderboard.
    def FindEarlyBirds(self, submission):
        for comment in submission.comments:
            if comment.author and (datetime.utcfromtimestamp(comment.created_utc) - datetime.utcfromtimestamp(submission.created_utc)).days == 0:
                if comment.author.name not in self.earlyBirds: 
                    self.earlyBirds[comment.author.name] = 1
                else:
                    self.earlyBirds[comment.author.name] += 1

    def PrintEarlyBirds(self):
        logging.info("\nLeaderboard Stats: Early Bird Club")
        for i, user in enumerate(OrderedDict(reversed(sorted(self.earlyBirds.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 20:
                logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "[{}] Early Birds".format(self.earlyBirds[user]))

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
        logging.info("\nLeaderboard Stats: Sweet Talker's Club")
        for i, user in enumerate(OrderedDict(reversed(sorted(self.sweetTalkers.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 20:   
                logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "[{}]".format(self.sweetTalkers[user]))


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
        logging.info("\nLeaderboard Stats: Blabber Mouth Club")
        for i, user in enumerate(OrderedDict(reversed(sorted(self.blabberMouths.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 20:
                logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "[{}]".format(self.blabberMouths[user]))

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
        self.biggestBoiStats = { "name" : "" , "size" : 0, "date" : "" , "concat" : 0 , "depth" : 0 }
        self.bigBoiDepth = 0
        self.totalComments = 0
        self.totalParentComments = 0
        self.totalCharacters = 0
        self.userAvgData = {}
        self.uniqueUsers = 0
        self.totalThreads = 0
        self.earlyBirds = {}
        self.sweetTalkers = {}
        self.prettyPeople = []
        self.perfectAttendees = []

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
        
        logging.info("\nAnd the qualifying winners for the {} WAYR contest are:".format(CALENDAR[MONTH]))
        for winner in self.wayrCandidates:
            logging.info("/u/" + winner)

# # # # Finds the largest post for the month.
# # # # Currently only counts parent comments, module will likely be updated to concatenate child comments as well.
    def FindBigBoi(self, submission):
        submission.comments.replace_more(limit = None)
        for comment in submission.comments:
            self.bigBoiDepth = 1
            self.biggestBoiStats["concat"] = 0
            self.biggestBoiStats["concat"] += len(comment.body)
            self.RecurseBigBoi(comment)
            if self.biggestBoiStats["concat"] > self.biggestBoiStats["size"]:
                self.biggestBoiStats["name"] = comment.author.name
                self.biggestBoiStats["size"] = self.biggestBoiStats["concat"]
                self.biggestBoiStats["date"] = submission.title.split("-")[1].strip()
                self.biggestBoiStats["depth"] = self.bigBoiDepth

    def RecurseBigBoi(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if comment.author and reply.author:
                    if (comment.author.name == reply.author.name):
                        self.bigBoiDepth += 1
                        self.biggestBoiStats["concat"] += len(reply.body)
                        if reply.replies._comments.__len__() > 0:
                            self.RecurseBigBoi(reply)

    def PrintBigBoi(self):
        logging.info("\nThe longest post in {} was written by [{}] on [{}] and had a length of [{}] characters.".format(CALENDAR[MONTH], self.biggestBoiStats["name"], self.biggestBoiStats["date"], self.biggestBoiStats["size"]))

# # # # Gets the average character count of all posts for the month as well as the average number of characters.   
# # # # Module started out very lightweight but additions over time have made this a robust module worthy of being standalone.
    def FindAvgPostInfo(self, submission):
        submission.comments.replace_more(limit = None)
        self.totalThreads += 1
        for comment in submission.comments:
            self.totalComments += 1
            self.totalParentComments += 1
            self.totalCharacters += len(comment.body)
            self.RecurseAverages(comment)

    def RecurseAverages(self, comment):
        if not comment.stickied:
            for reply in comment.replies:
                if reply.replies._comments.__len__() > 0:
                    self.RecurseAverages(reply)
                self.totalComments += 1
                if comment.author and reply.author and comment.author.name == reply.author.name:
                    self.totalCharacters += len(comment.body)
                       

    def PrintAvgPostInfo(self):
        logging.info("\nWe had an average of [{}] WAYR posts per thread this month.".format(math.floor(self.totalParentComments / self.totalThreads)))
        logging.info("We had an average of [{}] total comments per thread this month.".format(math.floor(self.totalComments / self.totalThreads)))
        logging.info("The average length of WAYR posts for this month is [{}] characters.".format(math.floor(self.totalCharacters / self.totalParentComments)))
        logging.info("The average length of any comment for this month is [{}] characters.".format(math.floor(self.totalCharacters / self.totalComments)))

# # # # This module covers a lot of different data sets because of how thorough it is with the initial data collection call.
# # # # The number of posts and total character count of all posts for all unique users vising the thread in a month is collected here.
# # # # From there we can take that data and get a bunch of different metrics: total unique users, average character count, user "level" gained for the month, and other small leaderboard stats.
    def FindUserPostInfo(self, submission):
        for comment in submission.comments:
            if comment.author and not comment.author.name in self.userAvgData.keys():
                workingUserData = UserPostInfo()
                workingUserData.totalChar = len(comment.body)
                workingUserData.totalPosts = 1
                self.userAvgData[comment.author.name] = workingUserData
            elif comment.author:
                self.userAvgData[comment.author.name].totalChar += len(comment.body)
                self.userAvgData[comment.author.name].totalPosts += 1

    def PrintUserPostInfo(self):
        logging.info("\nA total of {} unique users commented on the threads this month.".format(len(self.userAvgData)))
        logging.info("\nAverage user data: [user] - [total character count / number of posts = average character count]")

        printString = ""
        orderedData = {}
        for user in self.userAvgData: orderedData[user] = self.userAvgData[user].totalChar
        for i, user in enumerate(OrderedDict(reversed(sorted(orderedData.items(), key = lambda x : x[1]))), 0):
            userAvg = math.floor(self.userAvgData[user].totalChar / self.userAvgData[user].totalPosts)
            if i % 2 == 1:
                printString += str("[{}]".format(user)).ljust(22, ".") + str("[{}/{} = {}]    ".format(self.userAvgData[user].totalChar, self.userAvgData[user].totalPosts, userAvg)).rjust(22, ".")
                logging.info(printString)
                printString = ""
            else:
                printString += str("[{}]".format(user)).ljust(22, ".") + str("[{}/{} = {}]    ".format(self.userAvgData[user].totalChar, self.userAvgData[user].totalPosts, userAvg)).rjust(22, ".")
        if printString != "":
            logging.info(printString)
        
        for user in self.userAvgData: orderedData[user] = math.floor(self.userAvgData[user].totalChar / self.userAvgData[user].totalPosts) if self.userAvgData[user].totalPosts > 1 else 0
        logging.info("\nAverages: Top 5 for the month")
        for i, user in enumerate(OrderedDict(reversed(sorted(orderedData.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 10:
                if orderedData[user] > 0:
                    logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "[{}]".format(orderedData[user]))

# # # # The Early Bird Club is for any user who has posted within the first hour of the weekly thread going live.
# # # # Considering adding an additional module that checks if a comment was added on the last day before a new thread goes live
    def FindEarlyBirds(self, submission):
        for comment in submission.comments:
            if comment.author and (datetime.utcfromtimestamp(comment.created_utc) - datetime.utcfromtimestamp(submission.created_utc)).days == 0:
                if comment.author.name not in self.earlyBirds: 
                    self.earlyBirds[comment.author.name] = 1
                else:
                    self.earlyBirds[comment.author.name] += 1

    def PrintEarlyBirds(self):
        logging.info("\nThe Early Bird Club: Posting within 24 hours of a weekly thread going live at least twice.")
        for user in OrderedDict(reversed(sorted(self.earlyBirds.items(), key = lambda x : x[1]))):
            if self.earlyBirds[user] > 1:
                logging.info(str("/u/{}".format(user)).ljust(24, ".") + "[{}]".format(self.earlyBirds[user]))

# # # # The Sweet Talker's Club tracks total comment replies.  
# # # # If a user has at least 2 replies for the month they qualify.
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
        logging.info("\nThe Sweet Talker's Club: Tracks total comment replies for the month.")
        for i, user in enumerate(OrderedDict(reversed(sorted(self.sweetTalkers.items(), key = lambda x : x[1]))), 0):
            if PRINT_ALL or i < 10:
                logging.info(str("#{}: /u/{}".format(i + 1, user)).ljust(30, ".") + "[{}]".format(self.sweetTalkers[user]))

# # # # The Pretty People Coefficient tracks the percentage of the users who posted who have set character flairs.
# # # # This number is expected to stay pretty low as a large portion of subreddit visitors do not have old reddit CSS enabled.
    def FindPrettyPeople(self, submission):
        for comment in submission.comments:
            if comment.author and (comment.author_flair_css_class == None or comment.author_flair_css_class.lower() == "xxxnoflair") and comment.author.name not in self.prettyPeople:
                self.prettyPeople.append(comment.author.name)
    
    def PrintPrettyPeople(self):
        prettyPeople = math.floor(((len(self.userAvgData) - len(self.prettyPeople)) / len(self.userAvgData)) * 100)
        logging.info("\nThe Pretty People Coefficient: Percentage of users who have set custom character flairs: [{}%]".format(prettyPeople))

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
        logging.info("\nThe Perfect Attendance Club: Users who posted in every thread for the month.")
        for user in self.perfectAttendees:
            logging.info("/u/{}".format(user))

########################################################################################################################################
########################################################################################################################################

# # # # Upvote Module
def UpvoteModule(submission):
    for comment in submission.comments:
        if comment.author:
            comment.upvote()

# # # # This is the WAYR Leaderboard Module - Each individual module for year-in-total leaderboards is contained in this function, and called below in the main loop.
def LeaderboardModule(WAYRStats, submission):
    WAYRStats.FindAvgPostLengths(submission)
    WAYRStats.FindEarlyBirds(submission)
    WAYRStats.FindSweetTalkers(submission)
    WAYRStats.FindBlabberMouths(submission)
    if "untranslated" not in submission.title.lower():
        WAYRStats.InitStreakData(submission) if WAYRStats.streakData.__len__ == 0 else WAYRStats.FindLongestStreak(submission)

# # # # This is the WAYR Monthly Module - Each individual module for monthly analytics is contained in this function, and called below in the main loop.
def MonthlyModule(WAYR, submission):
    WAYR.FindWinCandidates(submission)
    WAYR.FindBigBoi(submission)
    WAYR.FindAvgPostInfo(submission)
    WAYR.FindUserPostInfo(submission)
    WAYR.FindEarlyBirds(submission)
    WAYR.FindSweetTalkers(submission)
    WAYR.FindPrettyPeople(submission)
    if "untranslated" not in submission.title.lower():
        WAYR.FindPerfectAttendees(submission)

def PrintLeaderboards():
    WAYRStats.PrintStreakData()
    WAYRStats.PrintAverages()
    WAYRStats.PrintEarlyBirds()
    WAYRStats.PrintSweetTalkers()
    WAYRStats.PrintBlabberMouths()

def PrintMonthly():
    WAYR.PrintWinCandidates()
    WAYR.PrintBigBoi()
    try:
        WAYR.PrintAvgPostInfo()
        WAYR.PrintPrettyPeople()
    except:
        logging.info("Average post length error: API sucks\n")
    WAYR.PrintPerfectAttendees()
    WAYR.PrintUserPostInfo()
    WAYR.PrintEarlyBirds()
    WAYR.PrintSweetTalkers()

########################################################################################################################################
########################################################################################################################################

# # # # Sends a call to the Reddit API to receive authentication.
Reddit = praw.Reddit(client_id = "-h3fHcyk8774Ww",
                     client_secret = "",
                     refresh_token = "",
                     user_agent = "Arc's WAYR Contest Bot")
visualNovels = Reddit.subreddit("visualnovels")

# # # # Instances of our class structures written above - these instances store all of the relevant data we will access in all the print statements below.
WAYRStats = WAYRLeaderboardManager()
WAYR = WAYRMonthlyManager(POSTS_PER_MONTH, MIN_POST_SIZE)

# # # # This is the official call we are making to the Reddit API.  It sends a search query to the visualnovels subreddit to isolate the WAYR threads, and sets a for loop to iterate through them.
# # # # The for loop is split up into 2 sections, 1 section for yearly analytics and the other for montly.
# # # # This for loop manages all of the modules that we want to process - they can be toggled on and off by simply adding the comment indicator [#] at the start of the line.
# # # # These functions only serve to collect data.  After the for loop finishes we print out the data that's been collected.
# # # # This script analyzes all data from both the regular and untranslated threads however the streak modules break completely when parsing both, and is set to only process the main WAYR threads.
for submission in visualNovels.search("\"What are you reading?\" author:AutoModerator", sort = "new", time_filter = "all"):
    #UpvoteModule(submission)
    if int(datetime.utcfromtimestamp(submission.created_utc).year) == YEAR:
        print(submission.title)
        if LEADERBOARDS_ON: LeaderboardModule(WAYRStats, submission)
        if int(datetime.utcfromtimestamp(submission.created_utc).month) == MONTH: 
            if MONTHLY_ON: MonthlyModule(WAYR, submission)
    else:
        break

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
if MONTHLY_ON: PrintMonthly()
if LEADERBOARDS_ON: PrintLeaderboards()

########################################################################################################################################
########################################################################################################################################