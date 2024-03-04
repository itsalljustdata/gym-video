import moviepy.editor as mp
from pathlib import Path
import json

# from moviepy.config import change_settings
# change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})


BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH.joinpath('data')
DEFAULT_JSON = BASE_PATH.joinpath('videos.json')

def do_it (videoFile : str, textList : list):

    if isinstance(textList,str):
        textList = [textList,]
        
    theText = ' - '.join(textList)
  
    inFile = DATA_PATH.joinpath(videoFile)
    my_video = mp.VideoFileClip(str(inFile), audio=True)
    w,h = my_video.size
    
    def doText (theText: str,vPos = 5):
        my_text = mp.TextClip   (txt = theText
                                ,font="Amiri-regular"
                                ,color="white"
                                ,fontsize=34
                                )
        txt_col = my_text.on_color  (size=(w + my_text.w, my_text.h+5)
                                    ,color=(0,0,0)
                                    ,pos=(6,"center")
                                    ,col_opacity=0.6
                                    )
        txt_mov = txt_col.set_pos( lambda t: (max(w/40,int(w-0.5*w*t))
                                             ,max(vPos*h/6,int(100*t))
                                            #  ,((vPos*h)/6)
                                             )
                                )
        return txt_mov
    
    txtLift = doText (theText)
    final = mp.CompositeVideoClip([my_video,txtLift])
    final.set_duration(my_video.duration)
    outFile = inFile.with_suffix(f".combined{inFile.suffix}")
    final.subclip(0,my_video.duration).write_videofile(filename =   str(outFile)
                                                      ,fps      =   my_video.fps
                                                      ,codec    =   'libx264'
                                                      ,threads  =   4
                                                      ,logger   =   None
                                                      )
    return outFile

def processJSON (theFile : Path = DEFAULT_JSON):
    theParms = json.loads(theFile.read_text())
   
    liftTextLast = None
    for ix,v in enumerate(theParms['vids']):
        if "liftText" not in v:
            if not liftTextLast:
                raise Exception
            v["liftText"] = liftTextLast
        else:
            liftTextLast = v["liftText"]
        if "repText" not in v:
            v["repText"] = f"{ix+1}/{len(theParms['vids'])}"
            
            
    theParms['vids'] =   [dict  (videoFile = v['videoFile']
                    ,textList  = [t for t in [v.get('liftText',None),v.get('repText',None),v.get('RPE',None),v.get('commentText',None)] if t]
                    )
              for v in theParms['vids']
             ]
        
    videoFiles = [do_it(**v) for v in theParms['vids']]
    final_clip = mp.concatenate_videoclips([mp.VideoFileClip(str(v), audio=True) for v in videoFiles])
    outPath = DATA_PATH.joinpath(theParms['vids'][0]['videoFile'])
    outPath = outPath.with_suffix(f".{theParms.get('liftType',None)}{outPath.suffix}")
    final_clip.write_videofile(str(outPath))
    theParms['videoFile'] = str(outPath)
    _ = [v.unlink() for v in videoFiles] 
    theFile.write_text(json.dumps(theParms,indent=2))
    # print("done")
    return outPath


if __name__ == '__main__':
    print (processJSON())