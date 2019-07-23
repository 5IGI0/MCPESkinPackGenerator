# Author : 5IGI0
# Github : https://github.com/5IGI0
import json
import uuid
import tempfile
import random
import os.path
import shutil
import requests
import base64
from zipfile import ZipFile

def copy(filePath, targetPath):
    with open(filePath, "rb") as fp:
        with open(targetPath, "wb") as fpp:
            while True:
                byte = fp.read(1)
                if byte == b"":
                    break
                fpp.write(byte)

def download_file(url, local_file):
    r = requests.get(url, stream=True)
    with open(local_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: 
                f.write(chunk)

def getMCPCSkin(username):
    tmp = requests.post("https://api.mojang.com/profiles/minecraft", data=json.dumps([username]), headers={"Content-Type":"application/json"}).json()
    if len(tmp) != 1:
        return None
    tmp = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{tmp[0]['id']}").json()
    tmp = json.loads(base64.b64decode(tmp["properties"][0]["value"]))["textures"]["SKIN"]["url"]
    download_file(tmp, "cache.png")
    return "cache.png"

manifest = {
    "header": {
        "version": [
            1,0,0
        ],
        "uuid": str(uuid.uuid4())
    },
    "modules": [
        {
            "version": [
                1,0,0
            ],
            "type": "skin_pack",
            "uuid": str(uuid.uuid4())
        }
    ],
    "format_version": 1
}

manifest["header"]["name"] = input("Pack Name : ")
manifest["header"]["description"] = input("Pack Description : ")
print()

tmpDir = f"{tempfile.gettempdir()}/MCPESkinPack-{random.randint(0, 10000)}/"

os.mkdir(tmpDir)

with open(f"{tmpDir}manifest.json", "w") as fp:
    json.dump(manifest, fp, indent=4)

tmp = "".join(random.choices("azertyuiopqsdfghjklmwxcvbn", k=25))

skins = {
  "skins": [],
  "serialize_name": tmp,
  "localization_name": tmp
}

texts = {
    f"skinpack.{tmp}":manifest["header"]["name"]
}

while True:
    skinFile = input("skin file : ")
    if not skinFile.find("mcpc:"):
        skinFile = getMCPCSkin(skinFile.replace("mcpc:",""))
        if skinFile is None:
            print("ERROR : this player does not exist")
            continue
    elif not os.path.isfile(skinFile):
        print("ERROR : this file does not exist")
        continue
    skinName = input("skin name : ")
    tmp = "".join(random.choices("azertyuiopqsdfghjklmwxcvbn", k=25))
    copy(skinFile, f"{tmpDir}{tmp}.png")
    skins["skins"].append({
        "localization_name": tmp,
        "texture": f"{tmp}.png",
        "type": "free"
    })
    texts[f"skin.{skins['serialize_name']}.{tmp}"] = skinName
    while True:
        tmp = input("continue ? [ yes / no ] : ")
        if not tmp.lower() in ["yes", "no"]:
            print("YES OR NO !")
        else:
            break
    if tmp.lower() == "no":
        break
    print()


with open(f"{tmpDir}skins.json", "w") as fp:
    json.dump(skins, fp, indent=4)

os.mkdir(f"{tmpDir}texts")

with open("languagesList") as fp:
    languagesList = fp.read().split("\n")

for language in languagesList:
    with open(f"{tmpDir}texts/{language}", "w") as fp:
        for item in texts.items():
            fp.write(f"{item[0]}={item[1]}\n")

zipObj = ZipFile('output.mcpack', 'w')

for folderName, subfolders, filenames in os.walk(tmpDir):
    for filename in filenames:
        filePath = os.path.join(folderName, filename)
        zipObj.write(filePath, arcname=filePath.replace(tmpDir, ""))

shutil.rmtree(tmpDir)