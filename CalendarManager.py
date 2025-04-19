import textwrap 
from icalevents.icalevents import events
import ColorUtils
import json
class assignment():
    def __init__(self, name, subject,DueDate):
        self.name = name
        self.subject = subject
        self.dueDate = DueDate
        self.subjectColors = [ 
                                ColorUtils.DynamicColor().__class__(),
                                ColorUtils.DynamicColor().__class__(),
                                ColorUtils.DynamicColor().__class__(),
                                ColorUtils.DynamicColor().__class__(),
                                ColorUtils.DynamicColor().__class__()
                            ]
        

    def setName(self, name):
        self.name = name
    def setStartDate(self, StartDate):
        self.startDate = StartDate
    def setDueDate(self, DueDate):
        self.endDate = DueDate
    def setSubjectColor(self,index,color=None, orginalTargetColor = None, targetColor=None,orginalBlendFactor=None, blendFactor=None):
        if color != None:
            self.subjectColors[index].setColor(color)
        if targetColor != None:
            self.subjectColors[index].setTargetColor(targetColor)
        if orginalTargetColor != None:
            self.subjectColors[index].setOrginalTargetColor(orginalTargetColor)
        if orginalBlendFactor !=None:
            self.subjectColors[index].setOrginalBlendFactor(orginalBlendFactor)
        if blendFactor != None:
            self.subjectColors[index].setBlendFactor(blendFactor)
        self.subjectColors[index].Reset()
        

    def setSubject(self, subject):
        self.subject = subject
    def getName(self):
        return(self.name)
    def getSubject(self):
        return(self.subject)
    def getDueDate(self):
        return(self.DueDate)
    def getSubjectColors(self):
        return(self.subjectColors)

    def getInfo(self,p=""):
        print(f"    name: {self.name}")
        print(f"    subject: {self.subject}")
        print(f"    dueDate: {self.dueDate}")
        
        for c in range(5):
            print(f"    subjectColors({c}):")
            self.subjectColors[c].printInfo(f"  {p}")    

def fetchCalData():
    output=[]
    Calevents = []
    with open("/home/carl/.CodeProjects/python/AlarmClock/ENV.json", "r") as f:
        calData = json.load(f)
        for item in calData["Calender"]:
            print(item)
            Calevents += events(url = calData["Calender"][item]["URL"], fix_apple= calData["Calender"][item]["FixApple"])
    # Parse the data
    for i in range(len(Calevents)):
        e = Calevents[i]
        output.append(
            assignment(
                textwrap.shorten(e.summary.split("[")[0].strip().capitalize(),28,placeholder=" [...]"),
                e.summary.split("[")[1].split("-")[0].strip().capitalize(),
                e.end.date()
                )
            )
        
        SubjectColor = (30, 30, 30)

        match output[i].subject:
            case "Graphic design 1":
                SubjectColor = (61, 133, 61)
            case "12 career comm & composition b":
                output[i].setSubject("Career & Communications")
                SubjectColor = (63, 77, 131)
            case "Digital electronics b":
                output[i].setSubject("Digital electronics")
                SubjectColor = (112, 63, 132)
            case "Ap comp sci a (sem 2)":
                output[i].setSubject("AP Computer Science")
                SubjectColor = (131, 90, 63)
        # 0 == text one
        # 1 == text two
        # 2 == text three
        # 3 == Backgrounc
        # 4 == Bat
        output[i].setSubjectColor(0, color = (0,0,0), targetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 70/100  ), orginalTargetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 70/100  ), orginalBlendFactor = -abs((1 / 5 * 2.5 ) + i / 50), blendFactor = -abs((1 / 5 * 2.5 ) + i / 50))
        output[i].setSubjectColor(1, color = (0,0,0), targetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 60/100  ), orginalTargetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 60/100  ), orginalBlendFactor = -abs((1 / 5 * 2.0 ) + i / 50), blendFactor = -abs((1 / 5 * 2.0 ) + i / 50))
        output[i].setSubjectColor(2, color = (0,0,0), targetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 50/100  ), orginalTargetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 50/100  ), orginalBlendFactor = -abs((1 / 5 * 1.5 ) + i / 50), blendFactor = -abs((1 / 5 * 1.5 ) + i / 50))
        output[i].setSubjectColor(3, color = (0,0,0), targetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 90/100  ), orginalTargetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 90/100  ), orginalBlendFactor = -abs((1 / 5 * 1.0 ) + i / 50), blendFactor = -abs((1 / 5 * 1.0 ) + i / 50))
        output[i].setSubjectColor(4, color = (0,0,0), targetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 75/100  ), orginalTargetColor = ColorUtils.blendColors((255, 255, 255), SubjectColor, 75/100  ), orginalBlendFactor = -abs((1 / 5 * 0.5 ) + i / 50), blendFactor = -abs((1 / 5 * 0.5 ) + i / 50))
    return(output)

if __name__ =="__main__":
    calData = fetchCalData()
    
    for i in range(len(calData)):
        for c in calData[i].getSubjectColors():
            c.Update(1.0)
        print(calData[0].getInfo("    "))