#!/usr/bin/python
"""

makeScene

Take a scene file and break it into little markup text files
If the file exists and is identical, leave it alone
If it is different, replace it
rebuild xml & wav for any file that is changed (ala make)
combine wavs into master wav

"""
import sys, os, time
from collections import OrderedDict
from findPy import *
from kbhit_safe import *

BUILDPARTS = False
BUILDJUST = None
BUILDDIR = "build"

ORIGDIR = os.path.abspath(".")

def main(scene):
    f = open(scene)
    lines = f.readlines()
    f.close()
    scene = scene[:-4]
    index = 0
    actors = {}
    blends = {}
    blended = {}
    files = OrderedDict()
    os.chdir(BUILDDIR)

    i = 0
    lastName = None
    while i < len(lines):
        line = lines[i]
        line = line.strip()
        if line == "":
            i += 1
            continue

        if ":" in line and "{" in line:        
            if line.find(":") < line.find("{"):                     #inline actor definition
                actor, parameters = line.split(":")
                actors[actor.strip()] = parameters.strip()
            else:                                                   #include file
                a, fn = line.split(":")
                f = open("../" + fn.strip().replace("}",""))
                for ln in f.readlines():
                    lines.insert(i + 1, ln)
                f.close()
            i += 1
            continue

        actor = None
        blend = None
        if "{" in line:
            extra = ""
            temp = line[1:].replace("}", "")
            if ";" in temp:                                         #extra parameters for these lines (until next actor spec)
                extra = temp[temp.find(";") + 1:]
                temp = temp[:temp.find(";")]
            if temp in actors:
                actor = temp
                line = actors[actor]
                if extra:
                    line = line.replace("}","") + ";" + extra + "}"
                    params = extra.split(";")
                    for param in params:
                        key, val = param.split("=")
                        if key.lower() == "blend":
                            blend = float(val)
                name = scene + "_" + str(index) + "_" + actor + ".txt"
                if blend:
                    blends[name] = (lastName, blend)
                    blended[lastName] = name
                    print "BLEND", lastName, "with", name, "*", blend
                index += 1
                files[name] = ""
        files[name] += line + "\n"
        i += 1
        lastName = name

    print "blends:", blends
    buildMaster = False
    errors = 0
    index = -1
    rewritten = {}
    for fil in files:
        index += 1
        if kbhit():
            print "******************************** USER BREAK ************************************"
            break
    ##    print "-----------------------", fil
    ##    print files[fil],
        rewrite = False
        if os.path.exists(fil):
            f = open(fil)
            s = f.read()
            f.close()
            if s != files[fil]:
                rewrite = True
        else:
            rewrite = True

        if BUILDJUST != None:
            if type(BUILDJUST) == type(0):
                rewrite = BUILDJUST == index
            else:
                rewrite = BUILDJUST == fil

        if fil in blended:
            fil2 = blended[fil]
            if os.path.exists(fil2):
                f = open(fil2)
                s = f.read()
                f.close()
                if s != files[fil2]:
                    rewrite = True
            else:
                rewrite = True

        if fil in blends and blends[fil][0] in rewritten:
            rewrite = True

        if rewrite:
            rewritten[fil] = True
            buildMaster = True
            print "-------->", fil, "is new or has changed -- writing to disk:"
            print files[fil]
            f = open(fil, "w")
            f.write(files[fil])
            f.close()
            print "   rebuilding wav file"
            wav = fil[:-4] + ".wav"
            cmd = "rm " + wav
            print cmd
            os.system(cmd)
            cmd = text2vox + " " + fil + " " + wav + " >> " + scene + ".log"
            print cmd
            os.system(cmd)
            if not os.path.exists(wav):
                print "***ERROR*** failed to build", wav, "-- renaming to force rebuild"
                cmd = "mv " + fil + " " + fil[:-4] + "_error.txt"
                print cmd
                os.system(cmd)
                errors += 1
            else:
                if fil in blends:
                    print "XXXXXXXXxx I think I'm supposed to blend here:", blends[fil]
                    fil2, blend = blends[fil]
                    cmd = "mv " + fil2[:-4] + ".wav temp.wav"
                    print cmd
                    os.system(cmd)  
                    cmd = "sox -D -m -v " + str(1.0 - blend) + " temp.wav -v " + str(blend) + " " + fil[:-4] + ".wav " + fil2[:-4] + ".wav"
                    print cmd
                    os.system(cmd)  
                if CHANGES and fil not in blended:
                    f = fil
                    if fil in blends:
                        f = fil2
                    cmd = "mplayer " + (("-af pan=2:0.5:0.5 -ao " + MPDRIVER) if MPDRIVER else "") + " " + f[:-4] + ".wav"
                    print cmd
                    os.system(cmd)
        else:
            if (not NOBUILD) and (BUILDJUST == None):
                print "++++++++>", fil, "is unchanged"

    if BUILD or ((not NOBUILD) and (BUILDJUST == None) and (buildMaster and errors == 0)):
        print "Building master wav file"
        if PAD:
            cmd = "sox -n -r 44100 pad.wav trim 0 " + str(PAD)
            print cmd
            os.system(cmd)
        cmd = "sox "
        for fil in files:
            if fil in blends:
                continue
            print fil
            cmd += fil[:-4] + ".wav "
            if PAD:
                cmd += "pad.wav "
        cmd += scene + ".wav"
        print cmd
        os.system(cmd)

        if BUILDPARTS:
            print "Building parts for each actor"
            partfiles = []
            for actor in actors:
                someAudio = False
                cmd = "sox "
                for fil in files:
                    if fil in blends:
                        continue
                    if not "_" + actor + ".txt" in fil:
                        cmd += "-v 0 "
                    else:
                        someAudio = True
                    cmd += fil[:-4] + ".wav "
                    if PAD:
                        cmd += "pad.wav "
                cmd += scene + "_" + actor + ".wav"
                if someAudio:
                    partfiles.append(scene + "_" + actor + ".wav")
                    print cmd
                    os.system(cmd)
            cmd = "sox -D -M "
            for p in partfiles:
                cmd += p + " "
            cmd += scene + "_" + "merge.wav"
            print cmd
            os.system(cmd)

    if errors:
        print errors, "errors encountered -- will not rebuild master"
    else:
        if PLAY:
            cmd = "mplayer " + (("-af pan=2:0.5:0.5 -ao " + MPDRIVER) if MPDRIVER else "") + " " + scene + ".wav"
            if type(PLAY) == type(0):
                cmd += " -ss " + str(PLAY)
            print cmd
            os.system(cmd)
    os.chdir(ORIGDIR)
#end main

if not os.path.exists(BUILDDIR):
    cmd = "mkdir " + BUILDDIR
    print cmd
    os.system(cmd)

if len(sys.argv) < 2:
    print "makeScene.py scenefile.txt [changes]"
    print 'specify "changes" as last option to play modified files'
    exit()

text2vox = findPy("text2vox.py")
print "text2vox:", text2vox

CHANGES = False
PLAY = False
WATCH = False
BUILD = False
NOBUILD = False
MPDRIVER = False
PAD = 0

for e in sys.argv[1:]:
    if e[:2] == "--":
        try:
            opt, val = e.split("=")
            try:
                val = int(val)
            except:
                pass
        except:
            opt = e
            val = True
        if opt == "--force":
            BUILDJUST = val
        else:
            globals()[opt[2:].upper()] = val
    else:
        scene = e
print "BUILDJUST:", BUILDJUST, "CHANGES:", CHANGES, "PLAY:", PLAY, "WATCH:", WATCH, "MPDRIVER:", MPDRIVER

if WATCH:
    t = time.time()
    print "waiting for changes to", scene
    while not kbhit():
        if os.stat(scene).st_mtime > t:
            t = time.time()
            main(scene)
            print "waiting for changes to", scene
        time.sleep(0.5)
else:
    main(scene)

