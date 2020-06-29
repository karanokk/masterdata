import json


def flatten(li):
    return [item for sub_list in li for item in sub_list]


def read_master_js_id(file):
    with open(file) as f:
        ver = json.load(f)
    return ver["master_js_id"]


def write_new_master_js_id(file, j_id):
    with open(file, 'r+') as f:
        ver = json.load(f)
        f.seek(0)
        f.truncate()
        ver["master_js_id"] = j_id
        json.dump(ver, f)


class Mst:
    """Table names"""
    Svt = 'mstSvt'
    Cv = 'mstCv'
    Illustrator = 'mstIllustrator'
    TreasureDevice = 'mstTreasureDevice'
    TreasureDeviceDetail = 'mstTreasureDeviceDetail'
    Skill = 'mstSkill'
    SkillDetail = 'mstSkillDetail'
    Item = 'mstItem'
    SvtComment = 'mstSvtComment'
    Quest = 'mstQuest'
    Spot = 'mstSpot'
    War = 'mstWar'
