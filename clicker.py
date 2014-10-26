
import sys
import string

import os
import fnmatch
from collections import defaultdict
import csv
import math

from Tkinter import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk

clicks = 0
showed_data = []

rootpath = sys.argv[2]
print 'Using input file:',sys.argv[1],'loading data from: ',rootpath
data = []
with open(sys.argv[1], 'rb') as f:
    reader = csv.reader(f, delimiter=',')
    titles = []
    for i,row in enumerate(reader):
        d = {}
        if i==0:
            for item in row:
                titles.append(item)
        else:
            for j,item in enumerate(row):
                d[titles[j]] = item

            data.append(d)
    #print titles

def clicked_at(x,y):
    global stc, clicks
    global data
    stc = stc+str(x)+' '+str(y)+' '
    if clicks==2:
        #print stc
        #print "poseid:",app.poseid
        #print "individualid:",app.individualid
        q = stc.split(' ')

        (ql,top_left,scale) = showed_data
        changed_str = '%s %s'  % (q[0], q[1])
        q = q[2:]
        for i in range(len(q)/2):
            x = float(q[2*i])
            y = float(q[2*i+1])
            if x>0 and y>0:
                newx = x/scale+top_left[0]
                newy = y/scale+top_left[1]
            else:
                newx = -1
                newy = -1
            changed_str = changed_str + ' %f %f'%(newx,newy)
        #print 'changedstr:',changed_str
        change('landmarks.txt',app.individualid,changed_str)
        app.next()
    else:
        clicks = clicks + 1
        app.update()

    #print "clicks:",clicks

def callback(event):
    canvas = event.widget
    x = canvas.canvasx(event.x)
    y = canvas.canvasx(event.y)
    clicked_at(x,y)
        
def change(file,line,contents):
    contents = contents.strip(' ');
    #print "changing:",file, line,contents
    try:
        f = open(file)
        l = f.readlines()
        f.close()
    except:
        l = []
    f = open(file,'w')
    cnt = 0
    for item in l:
        if cnt == line:
            f.write(contents+"\n")
        else:
            f.write(item)
        cnt = cnt + 1
    if len(l)<=line:
        for i in range(line-(len(l)-1)):
            f.write(contents+"\n")
    f.close()

class App:

    def __init__(self, master):
        
        frame = Frame(master)
        frame.pack()

        self.btn_next = Button(frame, text="Next", command=self.next)
        self.btn_next.pack(side=LEFT)

        self.btn_prev = Button(frame, text="Previous", command=self.previous)
        self.btn_prev.pack(side=LEFT)

        self.btn_next50 = Button(frame, text="+50", command=self.next50)
        self.btn_next50.pack(side=LEFT)

        self.btn_previous50 = Button(frame, text="-50", command=self.previous50)
        self.btn_previous50.pack(side=LEFT)

        self.btn_featnv= Button(frame, text="Feature not visible", command=self.featnv)
        self.btn_featnv.pack(side=LEFT)

        self.btn_exit = Button(frame, text="Exit", fg="red", command=frame.quit)
        self.btn_exit.pack(side=LEFT)

        frame = Frame()
        frame.pack()
        x_size = 1200
        y_size = 800
        self.tamx = x_size
        self.tamy = y_size
        self.poseid = 1
        self.individualid = -1
        # Create a canvas
        self.canvas = Canvas(frame,
                           width = x_size,
                           height = y_size,
                           background = 'white',
                           border = 1
                           )
        self.canvas.bind("<Button-1>", callback)
        self.canvas.pack();
        frame = Frame()
        frame.pack()
        self.label_text = StringVar();
        self.label_result = Label(master,
                                     textvariable=self.label_text)
        self.label_result.pack()
        
    def next50(self):
        self.go_to(50);

    def previous50(self):
        self.go_to(-50);

    def next(self):
        self.go_to(1)

    def featnv(self):
        clicked_at(-1,-1)

    def go_to(self,n):
        global clicks
        global data 
        global stc
        global showed_data
        if clicks == 0 and showed_data:
            (ql,top_left,scale) = showed_data
            changed_str = '%s %s'  % (data[self.individualid]['SUBJECT_ID'],
                    data[self.individualid]['FILE'])
            for (x,y) in ql:
                if x>0 and y>0:
                    newx = x/scale+top_left[0]
                    newy = y/scale+top_left[1]
                else:
                    newx = -1
                    newy = -1
                changed_str = changed_str + ' %f %f'%(newx,newy)
            #print 'changedstr:',changed_str
            change('landmarks.txt',app.individualid,changed_str)

        clicks = 0
        self.individualid = (self.individualid + n) % len(data)
        stc = data[self.individualid]['SUBJECT_ID'] + ' ' + data[self.individualid]['FILE'] + ' ' 
            
        file1 = os.path.join(rootpath,data[self.individualid]['FILE'])
        #print self.individualid
        im = show_points(file1,self.individualid)
        #print 'from next'
        photo = ImageTk.PhotoImage(im)
        item = self.canvas.create_image(0, 0, anchor=NW, image=photo)
        self.canvas.image1 = photo        
        #print "";
        self.update();

    def update(self):
        if clicks == 0:
            location = 'left eye'
        elif clicks == 1:
            location = 'right eye'
        elif clicks == 2:
            location = 'base of nose'

        self.label_text.set("NOW CLICK ON: %s -- Individual: %d/%d"% ( location, 
            self.individualid, len(data)))

    def previous(self):
        self.go_to(-1)

def getint(x):
    return int(round(x))

def draw_cross(im,coord,color):
    (x,y) = coord
    im = im.convert("RGB")
    #for i in range(-3,4,1):
        #try:
            #im.putpixel((getint(x+i),getint(y)),color)
        #except:
            #pass
    #for i in range(-3,4,1):
        #try:
            #im.putpixel((getint(x),getint(y+i)),color)
        #except:
            #pass

    draw = ImageDraw.Draw(im)
    draw.ellipse((x-3, y-3, x+3, y+3),fill=color)
    return im

#This shows the points on a given filename that occurs in order given by iden.
#It loads the landmarks and applies some logic to zoom into the region of
#interest.
def show_points(filename,iden):
    global showed_data
    #print 'in show points'
    im = Image.open(filename)
    
    (x,y) = im.size
    #im = im.resize((int(round(2.0*x)),int(round(2.0*y))),Image.BICUBIC)
    #print 'from show points:'
    ql = read_landmarks(data[iden]['FILE'],data[iden]['SUBJECT_ID'],iden)
    #print ql
    two_points = False
    if ql[0][0]>0 and ql[0][1]>0 and ql[1][0]>0 and ql[1][1]>0:
        p1 = ql[0]
        p2 = ql[1]
        two_points = True
    elif ql[0][0]>0 and ql[0][1]>0 and ql[2][0]>0 and ql[2][1]>0:
        p1 = ql[0]
        p2 = ql[2]
        two_points = True
    elif ql[1][0]>0 and ql[1][1]>0 and ql[2][0]>0 and ql[2][1]>0:
        p1 = ql[1]
        p2 = ql[2]
        two_points = True

    if two_points:
        minx = min(p1[0],p2[0])
        maxx = max(p1[0],p2[0])
        miny = min(p1[1],p2[1])
        maxy = max(p1[1],p2[1])
        d = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        top_left = (int(round(minx-3*d)),int(round(miny-3*d)))
        im = im.crop((top_left[0],top_left[1],int(round(maxx+3*d)),int(round(maxy+3*d))))
        scale = 800.0/max(im.size[0],im.size[1])
        im = im.resize((int(round(scale*im.size[0])),int(round(scale*im.size[1]))),
                Image.BICUBIC)
        ql[0] = (scale*(ql[0][0]-top_left[0]),scale*(ql[0][1]-top_left[1]))
        ql[1] = (scale*(ql[1][0]-top_left[0]),scale*(ql[1][1]-top_left[1]))
        ql[2] = (scale*(ql[2][0]-top_left[0]),scale*(ql[2][1]-top_left[1]))
    else:
        top_left = (0,0)
        scale = 1

    im = draw_cross(im,ql[0],(255,0,0))
    im = draw_cross(im,ql[1],(0,255,0))
    im = draw_cross(im,ql[2],(0,0,255))
    #im = draw_cross(im,ql[3],(0,255,255))
    showed_data = (ql,top_left,scale)
    return im

#Reads the raw (as written in the file) landmarks. First try to read from
#landmarks.txt (which is the results file) if not there load from what we read
#from metadata.csv (from cs0)
def read_landmarks(lookupfile,lookupsubjectid,iden):
    try:
        f = open('landmarks.txt','r')
        ll = f.readlines()
        allcontents = defaultdict(list) 
        for item in ll:
            xx = item.strip()
            xx = xx.strip(' ')
            fields = xx.split(' ')
            ilist = []
            coordinates = fields[2:]
            for i in range(len(coordinates)/2):
                ilist.append((float(coordinates[2*i]),float(coordinates[2*i+1])))
            allcontents[(fields[1],fields[0])] = (ilist)
        datafromfile = allcontents[(lookupfile,lookupsubjectid)]
        rv = [((datafromfile[0][0]),(datafromfile[0][1])),((datafromfile[1][0]),
            (datafromfile[1][1])),((datafromfile[2][0]),(datafromfile[2][1]))]
        #print 'found:',rv
    except:
        #raise
        rv = []
        try:
            x = float(data[iden]['RIGHT_EYE_X'])
            y =  float(data[iden]['RIGHT_EYE_Y'])
            rv.append((x,y))
        except ValueError:
            rv.append((-1,-1))

        try:
            x = float(data[iden]['LEFT_EYE_X'])
            y =  float(data[iden]['LEFT_EYE_Y'])
            rv.append((x,y))
        except ValueError:
            rv.append((-1,-1))

        try:
            x = float(data[iden]['NOSE_BASE_X'])
            y =  float(data[iden]['NOSE_BASE_Y'])
            rv.append((x,y))
        except ValueError:
            rv.append((-1,-1))
    #print 'return value:',rv
    return rv


def main():
    global app
    root = Tk()
    root.title("Clicker")
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()

