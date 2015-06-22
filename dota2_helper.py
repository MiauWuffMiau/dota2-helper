#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

###########################################
#                                         #
# Feel free to use and edit this script,  #
# but be so fair and let this signature   #
# appear in this script.                  #
#                                         #
# miau@server-plant.de                    #
# 22-11-2014 v4.0                         #
# Published under GNU License v2          #
#                                         #
# Script written by Marcel 'miau' Kassuhn #
#                                         #
###########################################


from BeautifulSoup import BeautifulSoup
import urllib, urllib2, cookielib
import array
import os, time, sys
import getopt

global heroes_dotahut
heroes_dotahut = []
global heroes_dota2com
heroes_dota2com = []
global imgs_dota2com
imgs_dota2com = []
global opts_state_against
opts_state_against = []
global skill_plus_description
skill_plus_description = []

# Has to be edited manually, if a new hero is added by Valve
global not_supported_dotahut_heroes
not_supported_dotahut_heroes = ["Techies", "Oracle"]

global opts_state
opts_state = ""
global opts_hero
opts_hero = ""

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

def getopts():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dh:ls:u", ["download", "hero=", "list", "state=", "usage"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o in ("-u", "usage"):
            usage()
            sys.exit()
        elif o in ("-d", "--download"):
            downloading_imgs_from_dota2com()
        elif o in ("-h", "--hero"):
            global opts_hero
            opts_hero = a
        elif o in ("-l", "--list"):
            print("\nPossible heroes:\n")
            list_heroes()
            sys.exit(4)
        elif o in ("-s", "--state"):
            global opts_state
            opts_state = a
        else:
            assert False, "unhandled option"

def usage():
        getting_dota2com_heroes()
        if opts_hero not in (heroes_dota2com) or opts_state not in ("weak", "strong"):
                print("\nUsage:\n\n./dota2_helper.py -h \"Abaddon\" -s \"weak\"")
                print("\nThis will show you the best counter heroes against Abaddon!"
                        "(Abaddon is weak against)\n")
                print("Possible options:\n\n-h or --hero= :\n\tSpecifying the hero\n")
                print("-s or --state= :\n\tSpecifying the state"
                        "\n\tAllowed values: \"strong\" or \"weak\"\n")
                print("-l or --list :\n\tWill show all possible heroes\n")
                print("-d or --download :\n\tWill download all Dota " 
                    "hero pictures into a subfolder.\n\tThere will be a two seconds delay "
                    "due to otherwise\n\tdota2.com said 'connection refused'.\n")
                print("-u or --usage :\n\tIf you want to see this usage.\n\t"
                        "Otherwise just execute the script without params\n")
                sys.exit(3)

def matching_dota2com_dotahut(hero):
        getting_dotahut_heroes()
        heroes_dotahut.append("oracle N/A")
        heroes_dotahut.append("techies N/A")
        heroes_dotahut.sort()
        heroes_dota2com.sort()
        index_of_hero = heroes_dota2com.index(hero)
        return heroes_dotahut[index_of_hero]

def list_heroes():
        getting_dota2com_heroes()
        heroes_dota2com.sort()
        for hero in heroes_dota2com:
                print(hero)
        print("")

def open_site(site):
        answer = opener.open(site)
        output = BeautifulSoup(answer.read())
        return output

def downloading_imgs_from_dota2com():
        output = open_site("http://www.dota2.com/heroes/")
        last = output.findAll('img', {'class':'heroHoverLarge'})

        for l in last:
                imgs_dota2com.append(str(l['src']).replace("hphover", "full"))

        imgs = str(os.getcwd()) + "/heroes_img"

        if not os.path.exists(imgs):
                os.makedirs(imgs)

        os.chdir(imgs)

        for img in imgs_dota2com:
                dl_string = img
                file_name = dl_string.split("/")[7]
                print("Downloading image (%s)..." % file_name)
                urllib.urlretrieve(dl_string, file_name)
                time.sleep(2) # due to received a 'connection refused' from dota2.com

        os.chdir(os.path.abspath(os.path.join(imgs, os.pardir)))

def getting_dotahut_heroes():
        # pattern: http://www.dotahut.com/heroes/abbadon
        output = open_site("http://www.dotahut.com/heroes")
        last = output.findAll('div', {'class':'left champ-img'})
        for l in last:
                heroes_dotahut.append(str(l).split("\"")[1])

def getting_dota2com_heroes():
        # pattern: http://www.dota2.com/hero/Anti-Mage/?l=english
        output = open_site("http://www.dota2.com/heroes/")
        last = output.findAll('a', {'class':'heroPickerIconLink'})
        for l in last:
                heroes_dota2com.append(str(l['href']).split("/")[4])

def getting_dota2com_bio_stats(hero):
        bio_stats = ""
        output = open_site("http://www.dota2.com/hero/%s/?l=english" % str(hero))

        last = output.findAll('span', {'class':'bioTextAttack'})
        for l in last:
                bio_stats += l.string

        last = output.findAll('p', {'id':'heroBioRoles'})
        for l in last:
                bio_stats += str(l).split("</span>")[1].replace("</p>", "")
        return bio_stats

def getting_weak_or_strong(hero, state):
        getting_dotahut_heroes()

        #hero = "abbadon"
        output = open_site("http://www.dotahut.com/heroes/%s/%s" % (str(hero), state))
        hero = str(hero).replace("_", " ").title()

        last = output.findAll('div', {'class':'name'})
        for l in last:
                if hero != l.string:
                        opts_state_against.append(l.string)

        champions = output.findAll('div', {'class':'champ-block left'})
        help = 0
        for champ in champions:
                if "lane tag_countersinteamfights" in str(champ):
                        opts_state_against[help] = "%s:\n\tCounters in Team Fights" % opts_state_against[help]
                elif "lane tag_countersinlane" in str(champ):
                        opts_state_against[help] = "%s:\n\tCounters in Lane" % opts_state_against[help]
                help += 1

        infos = output.findAll('div', {'class':'uvote tag_green'})
        help = 0
        for info in infos:
                yes_votes = str(info).split(">")[2].replace("</div", "")
                opts_state_against[help] = "%s\n\tYes votes: %s" % (opts_state_against[help], yes_votes)
                help += 1

        infos = output.findAll('div', {'class':'dvote tag_red'})
        help = 0
        for info in infos:
                no_votes = str(info).split(">")[2].replace("</div", "")
                opts_state_against[help] = "%s\n\tNo votes: %s" % (opts_state_against[help], no_votes)
                #print(opts_state_against[help] + "\n")
                help += 1

def get_skills_descriptions(hero):
    output = open_site("http://www.dota2.com/hero/%s/?l=english" % str(hero))
    skills = output.findAll('h2')

    help = 0
    for skill in skills:
        if help == len(skills)/2:
            break
        else:
            help += 1
            skill_plus_description.append(skill.string)


    skills_description = output.findAll('div', {'class':'abilityHeaderRowDescription'})

    help = 0
    for sd in skills_description:
        description = str(sd).split("<p>")[1].replace("</p>", "").replace("</div>", "")
        skill_plus_description[help] = "\n%s:\n%s" % (str(skill_plus_description[help]), description)
        help += 1

    for skill in skill_plus_description:
        print(skill)
    print("\n")

getopts()

usage()

bio_stats_of_opts_hero = getting_dota2com_bio_stats(opts_hero)
print("\n%s:\n\t%s\n" % (opts_hero, bio_stats_of_opts_hero))

get_skills_descriptions(opts_hero)


if opts_hero not in not_supported_dotahut_heroes:
        print("%s is %s against (ordered by most efficient):\n\n" % (opts_hero, opts_state))

        dotahut_hero = matching_dota2com_dotahut(opts_hero)

        getting_weak_or_strong(dotahut_hero, opts_state)

        for hero in opts_state_against:
                print("%s\n" % hero)
        print("")
else:
        print("%s is not supported by dotahut.com. Sorry!\n" % opts_hero)

#print("Data provided by dota2.com and dotahut.com")
