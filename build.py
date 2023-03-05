import pathlib
import json
import subprocess
# this is https://github.com/nurse/nkf/tree/master/NKF.python3
import nkf

full = []
for jf in pathlib.Path("hashes").glob("*.json"):
    txt = jf.read_text()
    full += json.loads(txt)
print(len(full), "loaded!")

def tja2mongo(x,text):
  title = None
  subtitle = None
  levels = ["easy", "normal", "hard", "oni", "ura"]
  course_index = None
  courses = [None]*5
  music_type = None
  preview=None

  for line in text.splitlines():
    if line.startswith("TITLE:"):
      title = line.split(":")[1].strip()
    elif line.startswith("SUBTITLE:"):
      subtitle = line.split(":")[1].strip().lstrip("-")
    elif line.startswith("WAVE:"):
      wave = line.split(":")[1].strip()
      music_type = wave.split('.')[-1]
    elif line.startswith("DEMOSTART:"):
      preview = float(line.split(":")[1].strip() or 0)
    elif line.startswith("COURSE:"):
      course_str = line.split(":")[1].strip().lower()
      if course_str.isdigit():
        course_index = int(course_str)
      elif course_str in levels:
        course_index = levels.index(course_str)
      elif course_str == "edit":
        course_index = levels.index("oni")
    elif line.startswith("LEVEL:"):
      if course_index == None and not any(courses):
        course_index = levels.index("oni")
      stars = int(line.split(":")[1].strip() or 0)
      courses[course_index] = {"stars":stars,"branch":False}

  return {
    "title_lang": {
      "ja": title,
      "en": None,
      "cn": None,
      "tw": None,
      "ko": None
    },
    "subtitle_lang": {
      "ja": subtitle,
      "en": None,
      "cn": None,
      "tw":None,
      "ko":None
    },
    "courses": {level: courses[index] for index, level in enumerate(levels)},
    "enabled": True,
    "title":title,
    "subtitle":subtitle,
    "category_id":None,
    "type":"tja",
    "music_type":music_type,
    "offset":-0.01,
    "skin_id":None,
    "preview":preview,
    "volume":1,
    "maker_id":None,
    "lyrics": False,
    "hash":"",
    "id":x,
    "order":x
  }

db = []
song_dir = pathlib.Path("songs")
for x,th,sh in [(1+i,*e) for i, e in enumerate(full)]:
    tb = subprocess.run(['ipfs', 'cat', th], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    tt = nkf.nkf('-w', tb).decode('utf-8')
    item = tja2mongo(x,tt)
    db += [item]
    print(item["id"],'is',item["title"])

    tp = song_dir / str(item["id"]) / "main.tja"
    sp = song_dir / str(item["id"]) / str("main." + item["music_type"])
    tp.parent.mkdir(parents=True,exist_ok=True)
    sp.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ipfs', 'get', '-o',tp,th])
    subprocess.run(['ipfs', 'get', '-o',sp,sh])
    print(item["title"], "saved!")
pathlib.Path("db.json").write_text(json.dumps(db,indent=4))
