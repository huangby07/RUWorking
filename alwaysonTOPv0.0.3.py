#!/usr/bin/env python

from Tkinter import *
#from ttk import *
import win32ui, win32con, win32gui
from sys import maxint
import datetime
import random
import time
import os.path

class study_Timer(Frame):
    #All the members:
    #usableW: max width of the window
    #usableH: max height of the window
    #master:the window
    #fS: file system, write and read files, calculate study time
    #studying: the study status
    #checkflag: whether it is checking status
    #checktime: the beginning of checking

    ################################
    ############Constant############
    ################################
    #STARTROW: use for grid
    #STARTCOL: use for grid

    ################################
    ############Widget##############
    ################################

    #STUDY: start study button
    #END: end study button
    #CHECKTXT: check study status text
    #TIMELAPSE: text box showing the time elapse
    #CHECK: button to confirm studying status
    #TOTALTIME:total study time

    ########################################################################
    ########################################################################
    ########################################################################
    ####################Start definition of class###########################
    ########################################################################
    ########################################################################
    ########################################################################

    ########################################
    #Function controling behavior of window#
    ########################################
    
    def display(self, update=0):
        for wN, wV in self.wVisible.items():
            wS=self.wShow[wN]#whether the widget should be shown at this time(although visible when mouse move over the window)
            if update==1:
                self.widget[wN].grid(row=self.wRow[wN]+self.STARTROW,column=self.wCol[wN]+self.STARTCOL, columnspan=self.wColSpan.get(wN,1),rowspan=self.wRowSpan.get(wN,1))
            if wV*wS==1:
                self.widget[wN].grid()
            else:
                self.widget[wN].grid_remove()    

    def pose(self, corner="SW"):
        sW=self.usableW
        sH=self.usableH
        wW=self.master.winfo_width()
        wH=self.master.winfo_height()
        if corner=="SW":
            X=sW-wW
            Y=sH-wH
            self.master.geometry('+%d+%d' % (X,Y))
        elif corner=="MID":
            X=(sW-wW)//2
            Y=(sH-wH)//2
            self.master.geometry('+%d+%d' % (X,Y))
        self.display(1)

    def update(self, studyState=1, checkState=1):#studyState means whether updates studyState, checkState means whether updates checkState
        #output=self.NORMALT
        posCorner="SW"
        if studyState==1:
            if self.studying==1:#if in study session
                self.updateLapse()
                #output=self.NORMALT
        if checkState==1:
            if self.checkflag!=0 and self.studying==0:#if the study state is return to 0
                self.response()
                #output=self.IMT
            elif self.checkflag==0 and self.studying!=0:#need to generate random number for checking study status
                if random.random()<self.checkProb:#if invoke
                    self.checkStudy()
                    posCorner="MID"
                    #output=self.IMT
            elif self.checkflag==1:#checkUpdate
                self.checkUpdate()
                posCorner="MID"
                #output=self.IMT
        self.pose(posCorner)
        #return output

    def changeDay(self):#when the date is changed
        flag=0
        if self.studying==1:
            flag=1
            self.endStudy()
        self.fS.newDay()
        self.startStudy()
        if flag!=1:
            self.endStudy()

    def terminate(self):#when the program is terminated
        self.fS.endDay()

    def exitProgram(self):#terminate the program
        self.terminate()
        self.master.destroy()
        
    def updateSettings(self,*arg):
        if len(arg)==1:
            self.curAct=arg[0]
        self.checktimeout=self.act.getActTimeout(self.curAct) #time out after 20 seconds
        if self.act.getActCheck(self.curAct)==0:
            self.checkProb=-1
        else:
            self.checkProb=self.act.getActFrequency(self.curAct)#approximate 1/1800, every half hour

    ###############################################
    #########                           ###########
    ######### Define behavior of window ###########
    #########                           ###########
    ###############################################

    #When mouse enter the body, need to change the display
    #Everything is available
    def enterBody(self,event=None):
        for wN in self.wShow:
            if wN=='TIMELAPSEMINI':
                self.wShow[wN]=0
            else:
                self.wShow[wN]=1
        #self.wShow={'TOTALTIME':1,'TIMESPAN':1,'TIMELAPSE':1,'TIMELAPSEMINI':0,'CHECKTXT':1,'END':1,'STUDY':1,'CHECK':1,'EXIT':1}#a dictionary saving the visibility of widgets(when mouse moving)
        self.update()
		
    #When mouse leave the body, only show the check-related and the time
    def leaveBody(self,event=None):
        for wN in self.wShow:
            if wN in ['TIMELAPSEMINI','CHECKTXT','CHECK']:
                self.wShow[wN]=1
            else:
                self.wShow[wN]=0
        #self.wShow={'TOTALTIME':0,'TIMESPAN':0,'TIMELAPSE':0,'TIMELAPSEMINI':1,'CHECKTXT':1,'END':0,'STUDY':0,'CHECK':1,'EXIT':0}#a dictionary saving the visibility of widgets(when mouse moving)
        self.update()
    
 
    ########################################
    ########Define behavior of widget#######
    ########################################

            
    #Behavior of button start(STUDY)
    def startStudy(self):
        self.wVisible["STUDY"]=0
        #self.STUDY.grid_remove()
        self.wVisible["END"]=1
        #self.END.grid()
        self.starttime=datetime.datetime.now().replace(microsecond=0)
        self.studying=1
        self.updateLapse()
        self.checkflag=0
        self.wVisible["CHECKTXT"]=0
        self.SELECTACT.config(state=DISABLED)
        #self.CHECKTXT.grid_remove()

    #Behavior of button END
    def endStudy(self):
        self.wVisible["END"]=0
        #self.END.grid_remove()
        self.wVisible["STUDY"]=1
        #self.STUDY.grid()
        self.endtime=datetime.datetime.now().replace(microsecond=0)
        self.studying=0
        self.fS.updateTime(self.curAct,self.endtime-self.starttime)
        self.fS.writeDay()
        self.updateSpan()
        self.updateTotal()
        self.updateAct()
        self.SELECTACT.config(state=NORMAL)
        #self.response()

    #Behavior of label TIMELAPSE
    def updateLapse(self):
        self.TIMELAPSE["text"]="You have studied: "
        if self.studying==1:
            systemTime=datetime.datetime.now().replace(microsecond=0)
            self.TIMELAPSE["text"]+=str(systemTime-self.starttime)
        else:
            self.TIMELAPSE["text"]+=str(self.starttime-self.starttime)
        self.updateMini()#let update of lapse and lapse mini simultaneous

    #Behavior of label TIMELAPSEMINI
    def updateMini(self):
        self.TIMELAPSEMINI["text"]=""
        if self.studying==1:
            systemTime=datetime.datetime.now().replace(microsecond=0)
            self.TIMELAPSEMINI["text"]+=str(systemTime-self.starttime)
        else:
            self.TIMELAPSEMINI["text"]+=str(self.starttime-self.starttime)

    #Behavior of lable TIMESPAN
    def updateSpan(self):
        self.TIMESPAN["text"]="Past session length: "
        self.TIMESPAN["text"]+=str(self.fS.getSegTime(self.curAct))
        # if self.studying==1:
            # systemTime=datetime.datetime.now().replace(microsecond=0)
            # self.TIMESPAN["text"]+=str(self.endtime-self.starttime)
        # else:
            # self.TIMESPAN["text"]+=str(self.starttime-self.starttime)

    #Behavior of checking study status CHECKTXT, CHECK
    def checkStudy(self):
        self.wVisible["CHECKTXT"]=1
        #self.CHECKTXT.grid()
        self.wVisible["CHECK"]=1
        #self.CHECK.grid()
        self.checkflag=1
        self.checktime=datetime.datetime.now()

    def checkUpdate(self):#update the check box to check whether user is studying
        systemTime=datetime.datetime.now()
        checkTimeLapse=(systemTime-self.checktime).total_seconds()
        self.CHECKTXT["text"]="Are you still working? Confirm in " +str(self.checktimeout - int(checkTimeLapse)) +" seconds or your session will end!"
        if self.checktimeout - int(checkTimeLapse)<0:
            self.checkTimeout()

    def checkTimeout(self):
        self.checkflag=2
        self.endStudy()
        self.CHECKTXT["text"]="Study check time out. Session ended. Please start a new session!"
        self.wVisible["CHECK"]=0
        #self.CHECK.grid_remove()

    def response(self):#user response before timeout
        self.checkflag=0
        self.wVisible["CHECKTXT"]=0
        #self.CHECKTXT.grid_remove()
        self.wVisible["CHECK"]=0
        #self.CHECK.grid_remove()

    def updateTotal(self):#update TOTALTIME's text
        self.TOTALTIME["text"]="Today's total time:"
        self.TOTALTIME["text"]+=str(self.fS.getTotalTime())
        
    def updateAct(self):#update TIMEACT's text
        self.TIMEACT["text"]=self.curAct + " total time:" + str(self.fS.getActTime(self.curAct))
        
    def selectAct(self,*arg):
        if self.studying==0:
            self.updateSettings(self.act.getActList()[map(int,self.SELECTACT.curselection())[0]])
            self.updateSpan()
            self.updateAct()
    
    ###################################################            
    ################Initialize widgets#################
    ###################################################
        
    def createWidgets(self):
        self.TIMELAPSE=Label(self)#currently studying time
        self.TIMELAPSEMINI=Label(self)#currently studying time in mini version
        self.TIMESPAN=Label(self)#last time study time
        self.TIMEACT=Label(self)#the total time of current activity
        #in ttk could not use fg
        self.TIMELAPSEMINI["fg"]   = "red"
        #self.TIMELAPSEMINI.configure(style="Red.TLabel")
        
        
        self.STUDY = Button(self)
        self.STUDY["text"] = "Start"
        
        self.STUDY["command"] =  self.startStudy

        

        self.TOTALTIME=Label(self) #today's total study time
        self.updateTotal()#update TOTALTIME's text
        
        
        self.END = Button(self)
        self.END["text"] = "End"
        #in ttk could not use fg
        self.STUDY["fg"]   = "red"
        #self.STUDY.configure(style="Red.TButton")
        self.END["command"] = self.endStudy

        

        self.CHECKTXT=Label(self,text="Hey! Are you still working?",wraplength=180)
        
        
        self.CHECK=Button(self)
        self.CHECK["text"]="Check"
        self.CHECK["command"]=self.response
        

        self.EXIT=Button(self)
        self.EXIT["text"]="x"
        self.EXIT["command"]=self.exitProgram
        #self.EXIT.configure(padding=0)
        
        self.SELECTACT=Listbox(self)
        actList=self.act.getActList()
        for item in actList:
            self.SELECTACT.insert(END,item)
        self.SELECTACT.bind("<ButtonRelease-1>",self.selectAct)

        ######################################
        ########                       #######
        ######## update all the labels #######
        ########                       #######
        ######################################
        self.updateLapse()
        self.updateSpan()
        self.updateMini()
        self.updateAct()
        
        #set the position of widget
        self.widget={'TOTALTIME':self.TOTALTIME,'TIMESPAN':self.TIMESPAN,'TIMELAPSE':self.TIMELAPSE,'TIMELAPSEMINI':self.TIMELAPSEMINI,'CHECKTXT':self.CHECKTXT,'END':self.END,\
                         'STUDY':self.STUDY,'CHECK':self.CHECK,'EXIT':self.EXIT,'SELECTACT': self.SELECTACT, 'TIMEACT': self.TIMEACT}#The map between name and object
        self.wVisible={'TOTALTIME':1,'TIMESPAN':1,'TIMELAPSE':1,'TIMELAPSEMINI':1,'CHECKTXT':0,'END':0,'STUDY':1,'CHECK':0,\
                        'EXIT':1, 'SELECTACT':1,'TIMEACT':1}#a dictionary saving the visibility of widgets
        self.wShow={'TOTALTIME':1,'TIMESPAN':1,'TIMELAPSE':1,'TIMELAPSEMINI':0,'CHECKTXT':1,'END':1,'STUDY':1,\
                    'CHECK':1,'EXIT':1, 'SELECTACT':1,'TIMEACT':1}#a dictionary saving the visibility of widgets(when mouse moving)
        self.wRow={'TOTALTIME':-2,'TIMEACT':-1,'TIMESPAN':0,'TIMELAPSE':1,'TIMELAPSEMINI':1,'CHECKTXT':4,'END':2,'STUDY':2,\
                    'CHECK':4, 'EXIT':-3,'SELECTACT':-2}#a dictionary saving the row of widgets
        self.wCol={'TOTALTIME':0,'TIMEACT':0,'TIMESPAN':0,'TIMELAPSE':0,'TIMELAPSEMINI':0,'CHECKTXT':0,'END':1,'STUDY':0,\
                    'CHECK':1, 'EXIT':4,'SELECTACT':-2}#a dictionary saving the column of widgets
        self.wRowSpan={'SELECTACT': 5}
        self.wColSpan={}
        self.display(1)#update the widget display
        #self.TOTALTIME.grid(row=self.STARTROW-1)
        #self.TIMESPAN.grid(row=self.STARTROW)
        #self.TIMELAPSE.grid(row=self.STARTROW+1)
        #self.CHECKTXT.grid(row=self.STARTROW+4)
        #self.END.grid(row=self.STARTROW+2,column=self.STARTCOL+1)
        #self.END.grid_remove()
        #self.STUDY.grid(row=self.STARTROW+2)
        #self.EXIT.grid(row=self.STARTROW-2,column=self.STARTCOL+4,sticky=E)
        #self.CHECK.grid(row=4,column=1)
        #self.CHECKTXT.grid_remove()
        #self.CHECK.grid_remove()

        
    ####################################
    ##########                ##########
    ########## Initialization ##########
    ##########                ##########
    ####################################
    def __init__(self, master=None):
        #studytime=[]
        Frame.__init__(self, master)
        self.endtime=datetime.datetime.now().replace(microsecond=0)
        self.starttime=self.endtime
        self.studying=0#0 denote idle, 1 denote study
        self.checkflag=0#whether we are checking the user is staying focused
        #check=1 means we are checking the user
        #check=2 means response timeout
        self.checktime=self.endtime
        
        random.seed()
        self.act=activity()#initialize the activity dictionary of settings
        #self.curAct=self.act.getActList()[0] #This is initiated after the list
        self.updateSettings(self.act.getActList()[0])
        self.fS=timeSystem(self.act.getActList())#initialize the file system to save files
        self.grid()
        self.STARTROW=7# use in grid
        self.STARTCOL=7#use in grid
        
        self.IMT=1 #immediate refresh time
        self.NORMALT=1000 #normal refresh rate =1000ms


        
        #################################
        ############Attention############
        #################################
        ##create widgets
        ##As python is a script language
        ##all the definition of member should be done before this point
        #################################
        self.createWidgets()
        #self.sysTime=datetime.datetime.now().replace(microsecond=0)

        
        ############################################################
        ###############Get the usable screen size###################
        ############################################################
        root.overrideredirect(0)#do not let the window overrided
        self.master.attributes("-alpha",0)#let all the changes invisible
        self.master.state("zoomed")#The screen will only expaned to the area without task bar
        self.master.update()#do
        self.usableW=self.master.winfo_width()#get the screen size
        self.usableH=self.master.winfo_height()
        self.master.state("normal")#return to normal
        self.master.update()#do
        self.master.attributes("-alpha",1)#make the screen visible again
        root.overrideredirect(1)#enable override

        ############################################################
        ######################Define behavior#######################
        ############################################################
        self.bind('<Enter>', self.enterBody)#The mouse enters the body of windows
        self.bind('<Leave>', self.leaveBody)#The mouse leaves the body of windows
        self.leaveBody()#let the window refresh

class activity:
    DEFAULT_CHECK=1 #whether check working status of one activity
    DEFAULT_CHECK_FREQUENCY=20 #the number of minutes of one check
    DEFAULT_WAITING_TIME=20 #the number of seconds before one check is time out
    DEFAULT_ACTIVITY="Default Activity"
    #Input: filename-the file name of the setting file
    #Output:nothing
    #Action:Initialize the activity class (including activity name, the specific settings)
    #Change:Create several variables including name list and specific settings
    def __init__(self, filename="Settings.txt"):
        self.filename=filename
        self.activities={}
        if os.path.isfile(self.filename):
            with open(self.filename,'a+') as f:
                N=int(f.readline())
                for _ in range(N):
                    name=f.readline().replace('\n','')#remove all the '\n'
                    check=int(f.readline().split(' ')[1])
                    timebase=float(f.readline().split(' ')[1])*60
                    freq=1/timebase if timebase>0 else 1
                    timeout=int(f.readline().split(' ')[1])
                    self.activities[name]=(check,freq,timeout)
                    
        else:
            self.activity[DEFAULT_ACTIVITY]=(DEFAULT_CHECK,1/(DEFAULT_CHECK_FREQUENCY*60),DEFAULT_WAITING_TIME)
            self.updateActivityFile()
            
    #Input: nothing
    #Output:nothing
    #Action:write the "Settings.txt"(specified in self.filename) with the dictionary of self.activities
    #Change:the disk file saving all the possible settings
    def updateActivityFile(self):
        N=len(self.activities)
        with open(self.filename,'w') as f:
            f.write(str(N)+'\n')
            for name in self.activities:
                f.write(name+'\n')
                f.write('CHECK '+str(self.activities[name][0]))
                f.write('CHECK_FREQUENCY '+str(int(1/self.activities[name][1]/60)))
                f.write('WAITING_TIME ' + str(self.activities[name][2]))
    
    #input: nothing
    #output:the key of self.activities
    def getActList(self):
        return self.activities.keys()

    #input: name-activity name
    #output:whether activity needs check
    def getActCheck(self,name):
        return self.activities[name][0]

    #input: activity name
    #output:the waiting time before timeout
    def getActTimeout(self,name):
        return self.activities[name][2]

    #input: activity name
    #output:the checking probability (if rnd number< probability then check)
    def getActFrequency(self,name):
        return self.activities[name][1]

   
class timeSystem:
##############################################
############File System Members###############
##############################################
#filename: the name of the file\
#totalTime: the total study time of the day (including all activities, dictionary, with a total denotes the total time of all activities) plus the time length of different study segment
    TOTAL="Total"
    def __init__(self, activityList=[TOTAL]):#call when program starts
        self.filename=self.getFileName()
        self.activityList=activityList
        self.initTotalTime()
        self.readFile()
        # self.fileHandle=open(self.filename,'w')
        # if self.totalTime!=datetime.timedelta(0):#if there is already data inside
            # posE=inputline.find('=')#find if there is total time save
            # if posE!=-1:#if there is total time
                # self.fileHandle.write(inputline[:posE-1])#only preserve the non-total part (delete the part after" = ")
            # else:#if there is no total time
                # self.fileHandle.write(inputline)#directly write
    
    #input: nothing
    #output:nothing
    #action:initialize an empty self.totalTime according to self.activityList(the activity class that specifies the name of activites)
    #change:the self.totalTime is created
    def initTotalTime(self):
        temp=self.activityList[:]#copy the activity list
        temp.insert(0,self.TOTAL)#insert a token 'total' at the beginning of the list
        self.totalTime=dict(zip(temp,[[datetime.timedelta(0)] for _ in temp]))#generate the dictionary where the totalTime is a dictionary from activity name to total time and time segments of activity
    
    #Input: nothing
    #output: nothing
    #Action: directly taking self.fileHandle and self.totalTime to read line
    #Change: self.totalTime is changed by the file content (total time of each activity
    #self.fileHandle reaches the end
    def readFile(self):
        with open(self.filename,'a+') as f:
            for inputline in f:
                if inputline.startswith(self.TOTAL):
                    continue
                self.parseTime(inputline)

    #Input: nothing
    #Output: the filename for today's use
    #Action: get today's date and return it with a suffix of '.txt'
    #Change: nothing
    def getFileName(self):
        return time.strftime("%Y%m%d")+".txt"
    
    #Input: nothing
    #Output: nothing
    #Action: end the counting of previous day and re-initialize all the variables include: total time, filename and fileHandle
    #Change: self.totalTime, self.filename, self.fileHandle, all changed to the new date.
    #Note: only call when the date changes
    def newDay(self):
        self.endDay()
        #self.totalTime=dict.fromkeys(self.totalTime,[datetime.timedelta(0)])#update the total time all as 0
        self.initTotalTime()
        self.filename=self.getFileName()
        #self.fileHandle=open(self.filename,'w')
        #self.fileHandle.seek(0)
        #inputline=self.fileHandle.readline()
        #self.totalTime=parseTime(inputline)
    
    #Input: nothing
    #Output:nothing
    #Action:Write all the data to file and exit
    #Change:disk file
    #Note:  only called at the end of day
    def endDay(self):
        self.writeDay()
    
    #Input: nothing
    #Output:nothing
    #Action:open local file with self.filename and write to it
    #Change:the diskfile is rewrited according to the totalTime
    def writeDay(self):
        
        #input: actName-activity name, timeS-the list of activity time segment(with total time at the beginning)
        #output:a string that will be written in the disk file end with '\n'
        #action:
        #change:nothing
        def writeDayHelper(actName,timeS):
            ret=actName+ ' '
            timeS=timeS[:]#use the copy of timeS list to prevent the mutable data being changed
            totalT=timeS.pop(0)#the first element of timeS is the total time, this should be recorded at the end of the string
            for _t in timeS:
                hours,minutes=timedelta2int(_t)
                ret+=str(hours) +'h'+str(minutes)+'min + '
            hours,minutes=timedelta2int(totalT)
            ret=ret[:-2] if len(timeS)!=0 else ret
            ret=ret + '= '+str(hours)+'h'+str(minutes)+'min\n'
            return ret
        
        #end of writeDayHelper
        
        with open(self.filename,'w') as f:
            retString=writeDayHelper(self.TOTAL,self.totalTime[self.TOTAL][:])#for safety reasons, pass the argument as copy
            f.write(retString)
            for a in self.totalTime:
                if a==self.TOTAL:
                    continue
                f.write(writeDayHelper(a,self.totalTime[a][:]))
    
    #input: activity-the name token of activity, *arg-could have single/two variables. Single variable specifies the sTime, the segment time in time delta. 
            #Two-variable case specifies the hours and minutes, the segment time in hour and minute.
    #output:nothing
    #action:test the number of variable in arg, then calculate the timedelta of the segment. update both the activity time(total,segment) and the total time(total, segment)
    def updateTime(self, activity, *arg):
        if len(arg)==1:
            sTime=arg[0]
        else:
            sTime=datetime.timedelta((float(arg[0])*3600+float(arg[1])*60)/3600/24)
        self.totalTime[activity][0]+=sTime
        self.totalTime[activity].append(sTime)
        self.totalTime[self.TOTAL][0]+=sTime
        self.totalTime[self.TOTAL].append(sTime)
    
    #input: inputString-raw string input from disk file with format:"%a %dh%dmin + %dh%dmin = %dh%dmin", first space is required and the function will ignore all other space. 
            #self.totalTime-the dictionary that saves all the total study time and study time segment
    #output:if the inputString is empty, return 0
    #action:parsing the inputString. convert it to timedelta datatype and save it into totalTime
    #change:self.totalTime is changed. The format is totalTime[name]=[total study time, segment 1, segment 2, segment 3,...]
    def parseTime(self, inputString):
        #input: iS-the string in form"%dh%dmin", where %d denotes an int number
        #output:a tuple of hours and minutes, in int
        #action:parsing the substring and return a tuple
        #change:nothing
        def parseTimeHelper(iS):
            hourS,minuteS=iS.split('h')
            minuteS=minuteS.split('m')[0]
            return (hourS,minuteS)
            
        #end of parseTimeHelper
        if inputString=="":
            return 0
        parselist=inputString.split(' ')
        name=parselist[0]
        timeString=''.join(parselist[1:])
        segmentTime,totalTime=timeString.split('=')
        # totalTime[name]=[]
        # totalTime[name].append(datetime.timedelta((float(hourS)*3600+float(minuteS)*60)/3600/24)))#Notice that the time delta of a day is less than 1
        if len(segmentTime)>0:#it is possible that there is not activity
            segmentList=segmentTime.split('+')
            for _s in segmentList:
                hourS, minuteS=parseTimeHelper(_s)
                self.updateTime(name,hourS,minuteS)
            # totalTime[name].append((datetime.timedelta((float(hourS)*3600+float(minuteS)*60)/3600/24)))
        # """
        
        # posE=inputString.find('=')
        # if posH==-1:#there is no time
            # return datetime.timedelta(0)
        # if posE!=-1:#there is a total time
            # return parseTime(inputString[posE+2:])
        # return 
        # """
    def getSegTime(self,act,seg=-1):
        return self.totalTime[act][seg] if len(self.totalTime[act])>1 else datetime.timedelta(0)
    
    def getActTime(self,act):
        return self.totalTime[act][0]
        
    def getTotalTime(self):
        return self.totalTime[self.TOTAL][0]

def timedelta2int(timeSpan):
    day=timeSpan.days #Notice that the total seconds of a day in the argument of datetime.timedelta() should be less than 1
    hours, remainder=divmod(timeSpan.seconds,3600)
    minutes, seconds=divmod(remainder, 60)
    return hours, minutes



def dlHandler():
    global root
    global app
    app.terminate()
    root.destroy()

#############################################################################################################################################################################
#############################################################################################################################################################################
    
######################################
#####The program starts from here#####
######################################

####################################
#########                  #########
######### ttk style update #########
#########                  #########
####################################
#Style().configure("Flat.TButton", padding=6, relief="flat", background="#ccc")
#Style().configure("Red.TButton", foreground="red", padding=6, relief="flat", background="#ccc")
#Style().configure("Red.TLabel", foreground="red")



refreshRate=100
root = Tk()
#root.title("Good good study and day day up")
#root.overrideredirect(1)
#root.
#root.minsize(270, 10)  #minimum size, do not want, because it will not let the close button appear at the corner.
#root.resizable(width=FALSE, height=TRUE)
#sysTime=Label(root,text=time.strftime("%Y%m%d%H%M%S"))
#sysTime.pack()
root.protocol("WM_DELETE_WINDOW",dlHandler)
reps = 0
sysDay=datetime.datetime.now().day

app=study_Timer(master=root)
app.update()



def show():
    hwnd = int(eval(root.wm_frame()))
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

#def show():
    # try everything to keep this window on top
#    root.lift()
#    root.focus_force()
#    hwnd = int(eval(root.wm_frame()))
#    pycwnd = win32ui.CreateWindowFromHandle(hwnd)
#    pycwnd.ShowWindow(win32con.SW_RESTORE)
#    pycwnd.BringWindowToTop()    
#    win32gui.SetFocus(hwnd)
#    win32gui.BringWindowToTop(hwnd)
#    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0, 0x0001)

def reshow(times=maxint,to=500):
    global reps
    global sysDay
    #global sysTime
    #sysTime["text"]=time.strftime("%Y%m%d%H%M%S")
    app.update()
    if datetime.datetime.now().day!=sysDay:
        app.changeDay()
        sysDay=datetime.datetime.now().day
        reps=0
    reps += 1
    #print 'reshow(%d)' % (reps)
    show()
    if reps < times:
        root.after(to, reshow)
    else:
        root.destroy()



#root.config(width=400, height=400)
show()
root.after(refreshRate, reshow)
root.mainloop()
