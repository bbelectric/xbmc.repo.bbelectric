
import xbmc, xbmcaddon, xbmcgui, xbmcvfs

# xbmc hooks
settings = xbmcaddon.Addon(id='script.absolutetv.updater')
plugin = settings.getAddonInfo('name')+"-"+settings.getAddonInfo('version')

def log(message):
    print "[%s] %s" % (plugin, message)

if (__name__ == "__main__" ):
    print plugin + " ARGV: " + repr(sys.argv)

    dialog=xbmcgui.Dialog()
    if dialog.yesno(plugin,"Would you like %s to "%plugin," reset your addons selections and XBMC settings? "," "):

        keypass = dialog.input("Please provide the password", type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        if keypass <> '123456' : raise Exception("Wrong password")

        import shutil, os, zipfile, re
        from t0mm0_common_net import Net
        net=Net()

        #### lines should be modified when file is changed
        fileurl  = "https://drive.google.com/file/d/0B1Q9WJpTJdJldE16UXVGSDIzWXc/view?usp=sharing"
        filename = "comeon.zip"
        ######################################################

        #fileurl  = "https://drive.google.com/file/d/0B1Q9WJpTJdJldE16UXVGSDIzWXc/view?usp=sharing"
        #filename = "comeon.zip"
        fileurl = "https://docs.google.com/uc?export=download&id="+re.search('https://drive.google.com/file/d/(.*)/', fileurl).group(1)
        log("URL :"+fileurl);

        tempfile = os.path.join(xbmc.translatePath("special://temp"),filename)
        log("File to download: "+tempfile)

        #result = urllib.urlopen(fileurl).read()
        result = net.http_GET(fileurl).content
        #print repr(result)

        #PATTERN = re.compile('export=download.*confirm=(.*)&amp;id=')
        m = re.search('export=download.*confirm=(.*)&amp;id=', result)
        print m.group(0)

        fileurl = fileurl + '&confirm=' + m.group(1)

        #for f in os.listdir(xbmc.translatePath(os.path.join("special://home","addons"))):
        #    if f.startswith('repository.'): print f

        try: os.remove(tempfile)
        except: pass

        dp = xbmcgui.DialogProgress();
        dp.create(plugin,"Downloading ",'','Please Wait')
        net.http_DL(fileurl, tempfile, dp)

        #dp.update(0,"Testing Zip")
        #zipfile.ZipFile(tempfile, "r").testzip()

        dp.update(0,"Preparing folders")

        home = xbmc.translatePath("special://home")
        profile = xbmc.translatePath("special://masterprofile")

        try: shutil.rmtree(os.path.join(home,"addons1"))
        except Exception as e: log("ERROR1:"+repr(e))
        try: shutil.rmtree(os.path.join(profile,"addon_data1"))
        except Exception as e: log("ERROR2:"+repr(e))
        try: os.remove(os.path.join(profile,"guisettings1.xml"))
        except Exception as e: log("ERROR3:"+repr(e))

        exclude = [settings.getAddonInfo('id'), xbmc.getSkinDir(), 'packages']

        for f in os.listdir(os.path.join(home,"addons")):
            log(f)
            #log(os.path.join(home,"addons",f))
            if f not in exclude and not f.startswith('repository.'):
                xbmc.executebuiltin('StopScript(%s)' % f)
                try: os.renames(os.path.join(home,"addons",f),os.path.join(home,"addons1",f))
                except Exception as e: log("ERROR4:"+repr(e))

        #os.rename(os.path.join(home,"addons"),os.path.join(home,"addons1"))
        try: os.rename(os.path.join(profile,"addon_data"),os.path.join(profile,"addon_data1"))
        except Exception as e: log("ERROR5:"+repr(e))
        try: os.rename(os.path.join(profile,"guisettings.xml"),os.path.join(profile,"guisettings1.xml"))
        except Exception as e: log("ERROR6:"+repr(e))
        try: os.renames(os.path.join(profile,"addon_data1",settings.getAddonInfo('id')),os.path.join(profile,"addon_data",settings.getAddonInfo('id')))
        except Exception as e: log("ERROR7:"+repr(e))

        #os.renames(os.path.join(home,"addons1",settings.getAddonInfo('id')),os.path.join(home,"addons",settings.getAddonInfo('id')))
        #for f in os.listdir(os.path.join(home,"addons1")):
        #    if f.startswith('repository.'):
        #        os.renames(os.path.join(home,"addons1",f),os.path.join(home,"addons",f))

        #dp = xbmcgui.DialogProgress();
        #dp.create(plugin,"Extracting Zip",'','Please Wait')
        dp.update(0,"Extracting Zip","This may take a few minutes to complete")

        log("Will unzip file "+tempfile)
        #with zipfile.ZipFile(tempfile, "r") as z:
        #    z.extractall(home,pwd=password)
        fh = open(tempfile, 'rb')
        z = zipfile.ZipFile(fh)
        total = len(z.namelist())
        count = 0
        for name in z.namelist():
            z.extract(name, home)
            count = count+1
            dp.update(int(count*100/total))
        log("unzip done")

        file=open(os.path.join(profile,"guisettings.xml"),'r')
        contents=file.read()
        file.close()

        shorts=re.compile('(HomeVideosButton.)">(.*)<').findall(contents)
        for shortname in shorts:
            log(repr(shortname))
            xbmc.executebuiltin('Skin.SetString(%s,%s)'% (shortname[0],shortname[1]))
        shorts=re.compile('(HomeMusicButton.)">(.*)<').findall(contents)
        for shortname in shorts:
            log(repr(shortname))
            xbmc.executebuiltin('Skin.SetString(%s,%s)'% (shortname[0],shortname[1]))
        shorts=re.compile('(HomePictureButton.)">(.*)<').findall(contents)
        for shortname in shorts:
            log(repr(shortname))
            xbmc.executebuiltin('Skin.SetString(%s,%s)'% (shortname[0],shortname[1]))
        shorts=re.compile('(HomeProgramButton.)">(.*)<').findall(contents)
        for shortname in shorts:
            log(repr(shortname))
            xbmc.executebuiltin('Skin.SetString(%s,%s)'% (shortname[0],shortname[1]))

        proname=xbmc.getInfoLabel("System.ProfileName")
        xbmc.executebuiltin("LoadProfile(%s)" % proname)
        xbmc.executebuiltin('ReloadSkin()')
        xbmc.executebuiltin("UpdateAddonRepos()")
        xbmc.executebuiltin("UpdateLocalAddons()")

        try: shutil.rmtree(os.path.join(home,"addons1"))
        except: pass
        try: shutil.rmtree(os.path.join(profile,"addon_data1"))
        except: pass
        try: os.remove(os.path.join(profile,"guisettings1.xml"))
        except: pass

        try: os.remove(tempfile)
        except: pass

        dialog.ok("Success","Installation Complete","")

    log("Finish")
