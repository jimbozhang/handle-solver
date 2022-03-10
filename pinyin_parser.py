import re


class PinyinParser:
    def __call__(self, pinyin):
        c, vt = self.split_cv(pinyin)
        v, t = self.split_vt(vt)
        return [c, v, t]
    
    def split_cv(self, pinyin):
        c = ''
        for x in self.c_list:
            if pinyin.startswith(x):
                c = x
                break
        v = pinyin[len(c):]
        return c, v
    
    def split_vt(self, v):
        if 'ā' in v or 'ē' in v or 'ī' in v or 'ō' in v or 'ū' in v or 'ǖ' in v:
            t = '1'
        elif 'á' in v or 'é' in v or 'í' in v or 'ó' in v or 'ú' in v or 'ǘ' in v:
            t = '2'
        elif 'ǎ' in v or 'ě' in v or 'ǐ' in v or 'ǒ' in v or 'ǔ' in v or 'ǚ' in v:
            t = '3'
        elif 'à' in v or 'è' in v or 'ì' in v or 'ò' in v or 'ù' in v or 'ǜ' in v:
            t = '4'
        else:
            t = '0'
        
        v = re.sub(r'[āáǎà]', 'a', v)
        v = re.sub(r'[ēéěè]', 'e', v)
        v = re.sub(r'[īíǐì]', 'i', v)
        v = re.sub(r'[ōóǒò]', 'o', v)
        v = re.sub(r'[ūúǔù]', 'u', v)
        v = re.sub(r'[ǖǘǚǜü]', 'v', v)

        assert v in self.v_list
        return v, t

    def __init__(self):
        self.c_list = [
            'zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j','q',
            'r', 'x', 'w', 'y', 'z', 'c', 's'
        ]
        self.v_list = [
            'a', 'ai', 'an', 'ang', 'ao', 'e', 'ei', 'en', 'eng', 'er', 'i',
            'ia', 'ian', 'iang', 'iao', 'ie', 'in', 'ing', 'io', 'iong', 'iu',
            'o', 'ong', 'ou', 'u', 'ua', 'uai', 'uan', 'uang', 'ue', 'ui',
            'un', 'uo', 'v', 'van', 've', 'vn'
        ]