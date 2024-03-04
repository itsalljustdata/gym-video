import moviepy.editor as mp
from pathlib import Path
import json

# from moviepy.config import change_settings
# change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})


BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH.joinpath('data')
DEFAULT_JSON = BASE_PATH.joinpath('videos.json')

def do_it (videoFile : str, textList : list):

# Python program to write 
# text on video     

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
        # print (type(txt_col))
        txt_mov = txt_col.set_pos( lambda t: (max(w/40,int(w-0.5*w*t))
                                             ,max(vPos*h/6,int(100*t))
                                            #  ,((vPos*h)/6)
                                             )
                                )
        # print (type(txt_mov))
        # # print (txt_mov.__dict__.keys())
        # print (f"start        : {txt_mov.start}")
        # print (f"end          : {txt_mov.end}")
        # print (f"duration     : {txt_mov.duration}")
        # print (f"pos          : {txt_mov.pos}")
        # print (f"relative_pos : {txt_mov.relative_pos}")
        # print (f"size         : {txt_mov.size}")
        return txt_mov
    
    txtLift = doText (theText)
    final = mp.CompositeVideoClip([my_video,txtLift])
    final.set_duration(my_video.duration)
    outFile = inFile.with_suffix(f".combined{inFile.suffix}")
    final.subclip(0,my_video.duration).write_videofile(str(outFile),fps=my_video.fps,codec='libx264')
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
            v["repText"] = f"{ix+1}/{len(vids)}"
            
            
    theParms['vids'] =   [dict  (videoFile = v['videoFile']
                    ,textList  = [t for t in [v.get('liftText',None),v.get('repText',None),v.get('RPE',None),v.get('commentText',None)] if t]
                    )
              for v in theParms['vids']
             ]
        
    print("videos")
    videoFiles = [do_it(**v) for v in theParms['vids']]
    print (videoFiles)
    print("concat")
    videos = [mp.VideoFileClip(str(v), audio=True) for v in videoFiles]
    final_clip = mp.concatenate_videoclips(videos)
    print("write")
    outPath = DATA_PATH.joinpath(theParms['vids'][0]['videoFile'])
    outPath = outPath.with_suffix(f".{theParms.get('liftType',None)}{outPath.suffix}")
    final_clip.write_videofile(str(outPath))
    print("done")
    _ = [v.unlink() for v in videoFiles] 
    return outPath


if __name__ == '__main__':
    outPath = processJSON()