"""최소 HWPX(OWPML) 작성기.

한글 2022(12.x)가 저장한 파일 구조를 기준으로 header.xml / sectionN.xml /
content.hpf 등을 직접 생성한다. 문단 줄 배치(lineseg)는 비워 두어
한글이 열 때 다시 조판하도록 한다.
"""
import io
import zipfile
from xml.sax.saxutils import escape

NS = (
    'xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
    'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" '
    'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
    'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
    'xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" '
    'xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" '
    'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:opf="http://www.idpf.org/2007/opf/" '
    'xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" '
    'xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" '
    'xmlns:epub="http://www.idpf.org/2007/ops" '
    'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"'
)
XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
LANGS = ["HANGUL", "LATIN", "HANJA", "JAPANESE", "OTHER", "SYMBOL", "USER"]
LANG_ATTR = ["hangul", "latin", "hanja", "japanese", "other", "symbol", "user"]
import os as _os
EMPTY_LINESEG = '' if _os.environ.get('NO_LINESEG') else ('<hp:linesegarray><hp:lineseg textpos="0" vertpos="0" vertsize="0" '
                 'textheight="0" baseline="0" spacing="0" horzpos="0" horzsize="0" '
                 'flags="393216"/></hp:linesegarray>')


def mm(v):
    return int(round(v * 7200 / 25.4))


def pt(v):
    return int(round(v * 100))


def x(s):
    return escape(str(s), {'"': "&quot;"})


class Header:
    """글꼴 · 테두리/배경 · 글자 모양 · 문단 모양 · 스타일 레지스트리."""

    def __init__(self):
        self.fonts = []          # face names (모든 언어 공통 목록)
        self.border_fills = []   # xml strings (id = index+1)
        self._bf_keys = {}
        self.char_prs = []
        self._cp_keys = {}
        self.para_prs = []
        self._pp_keys = {}
        self.tab_prs = ['<hh:tabPr id="0" autoTabLeft="0" autoTabRight="0"/>',
                        '<hh:tabPr id="1" autoTabLeft="1" autoTabRight="0"/>',
                        '<hh:tabPr id="2" autoTabLeft="0" autoTabRight="1"/>']
        self._tab_keys = {}
        self.styles = []
        self.cp_meta = {}
        self.pp_meta = {}
        # 1: 쪽 테두리용(없음), 2: 글자 기본(없음)
        self.border_fill()
        self.border_fill(fill="none")

    # ---- fonts
    def font(self, face):
        if face not in self.fonts:
            self.fonts.append(face)
        return self.fonts.index(face)

    # ---- border / fill
    def border_fill(self, left=None, right=None, top=None, bottom=None, fill=None):
        """각 변: None 또는 (type, width_mm_str, color). fill: '#RRGGBB' | 'none' | None"""
        key = (left, right, top, bottom, fill)
        if key in self._bf_keys:
            return self._bf_keys[key]
        bid = len(self.border_fills) + 1

        def side(tag, v):
            if v is None:
                return f'<hh:{tag} type="NONE" width="0.1 mm" color="#000000"/>'
            t, w, c = v
            return f'<hh:{tag} type="{t}" width="{w}" color="{c}"/>'

        s = (f'<hh:borderFill id="{bid}" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
             '<hh:slash type="NONE" Crooked="0" isCounter="0"/>'
             '<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
             + side("leftBorder", left) + side("rightBorder", right)
             + side("topBorder", top) + side("bottomBorder", bottom)
             + '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>')
        if fill is not None:
            s += (f'<hc:fillBrush><hc:winBrush faceColor="{fill}" hatchColor="#999999" alpha="0"/>'
                  '</hc:fillBrush>')
        s += '</hh:borderFill>'
        self.border_fills.append(s)
        self._bf_keys[key] = bid
        return bid

    # ---- char shape
    def char(self, size=10, color="#1F1F1F", font="Pretendard", latin=None, bold=False,
             italic=False, sup=False, sub=False, underline=None, shade="none",
             spacing=0, ratio=100, offset=0):
        key = (size, color, font, latin, bold, italic, sup, sub, underline, shade, spacing, ratio, offset)
        if key in self._cp_keys:
            return self._cp_keys[key]
        cid = len(self.char_prs)
        f = self.font(font)
        lf = self.font(latin) if latin else f
        refs = [f, lf, f, f, f, lf, f]
        fr = " ".join(f'{a}="{r}"' for a, r in zip(LANG_ATTR, refs))
        allv = lambda v: " ".join(f'{a}="{v}"' for a in LANG_ATTR)
        s = (f'<hh:charPr id="{cid}" height="{pt(size)}" textColor="{color}" shadeColor="{shade}" '
             f'useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="2">'
             f'<hh:fontRef {fr}/><hh:ratio {allv(ratio)}/><hh:spacing {allv(spacing)}/>'
             f'<hh:relSz {allv(100)}/><hh:offset {allv(offset)}/>')
        if italic:
            s += '<hh:italic/>'
        if bold:
            s += '<hh:bold/>'
        if underline:
            s += f'<hh:underline type="BOTTOM" shape="SOLID" color="{underline}"/>'
        else:
            s += '<hh:underline type="NONE" shape="SOLID" color="#000000"/>'
        s += ('<hh:strikeout shape="NONE" color="#000000"/><hh:outline type="NONE"/>'
              '<hh:shadow type="NONE" color="#C0C0C0" offsetX="10" offsetY="10"/>')
        if sup:
            s += '<hh:supscript/>'
        if sub:
            s += '<hh:subscript/>'
        s += '</hh:charPr>'
        self.char_prs.append(s)
        self._cp_keys[key] = cid
        self.cp_meta[cid] = (pt(size), font, bold)
        return cid

    # ---- tab
    def tab_right(self, pos):
        if pos in self._tab_keys:
            return self._tab_keys[pos]
        tid = len(self.tab_prs)
        self.tab_prs.append(
            f'<hh:tabPr id="{tid}" autoTabLeft="0" autoTabRight="0"><hp:switch>'
            f'<hp:case hp:required-namespace="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar">'
            f'<hh:tabItem pos="{pos}" type="RIGHT" leader="NONE" unit="HWPUNIT"/></hp:case>'
            f'<hp:default><hh:tabItem pos="{pos * 2}" type="RIGHT" leader="NONE"/></hp:default>'
            f'</hp:switch></hh:tabPr>')
        self._tab_keys[pos] = tid
        return tid

    # ---- para shape
    def para(self, align="JUSTIFY", left=0, right=0, indent=0, prev=0, next=0, line=160,
             line_type="PERCENT", keep_next=False, keep_lines=False, border=2, tab=0,
             word_break=True, border_offset=(0, 0, 0, 0), vert="BASELINE"):
        key = (align, left, right, indent, prev, next, line, line_type, keep_next, keep_lines,
               border, tab, word_break, border_offset, vert)
        if key in self._pp_keys:
            return self._pp_keys[key]
        pid = len(self.para_prs)
        # OWPML: KEEP_WORD=글자 단위, BREAK_WORD=어절 단위(한글 실동작 기준)
        bnl = "BREAK_WORD" if word_break else "KEEP_WORD"

        def margin(scale):
            return (f'<hh:margin><hc:intent value="{indent * scale}" unit="HWPUNIT"/>'
                    f'<hc:left value="{left * scale}" unit="HWPUNIT"/>'
                    f'<hc:right value="{right * scale}" unit="HWPUNIT"/>'
                    f'<hc:prev value="{prev * scale}" unit="HWPUNIT"/>'
                    f'<hc:next value="{next * scale}" unit="HWPUNIT"/></hh:margin>'
                    f'<hh:lineSpacing type="{line_type}" value="{line}" unit="HWPUNIT"/>')

        ol, orr, ot, ob = border_offset
        s = (f'<hh:paraPr id="{pid}" tabPrIDRef="{tab}" condense="0" fontLineHeight="0" '
             f'snapToGrid="0" suppressLineNumbers="0" checked="0" textDir="LTR">'
             f'<hh:align horizontal="{align}" vertical="{vert}"/>'
             '<hh:heading type="NONE" idRef="0" level="0"/>'
             f'<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="{bnl}" '
             f'widowOrphan="0" keepWithNext="{int(keep_next)}" keepLines="{int(keep_lines)}" '
             'pageBreakBefore="0" lineWrap="BREAK"/>'
             '<hh:autoSpacing eAsianEng="0" eAsianNum="0"/>'
             '<hp:switch><hp:case hp:required-namespace="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar">'
             + margin(1) + '</hp:case><hp:default>' + margin(2) + '</hp:default></hp:switch>'
             f'<hh:border borderFillIDRef="{border}" offsetLeft="{ol}" offsetRight="{orr}" '
             f'offsetTop="{ot}" offsetBottom="{ob}" connect="0" ignoreMargin="0"/></hh:paraPr>')
        self.para_prs.append(s)
        self._pp_keys[key] = pid
        self.pp_meta[pid] = dict(left=left, right=right, indent=indent, prev=prev, next=next, line=line)
        return pid

    def style(self, name, eng, para, char, kind="PARA"):
        sid = len(self.styles)
        self.styles.append((sid, kind, name, eng, para, char))
        return sid

    def xml(self, sec_cnt):
        fonts = ""
        for lang in LANGS:
            items = ""
            for i, face in enumerate(self.fonts):
                subst = ""
                if face.startswith("Pretendard"):
                    subst = '<hh:substFont face="맑은 고딕" type="TTF" isEmbedded="0" binaryItemIDRef=""/>'
                items += (f'<hh:font id="{i}" face="{x(face)}" type="TTF" isEmbedded="0">{subst}'
                          '<hh:typeInfo familyType="FCAT_GOTHIC" weight="6" proportion="4" contrast="0" '
                          'strokeVariation="1" armStyle="1" letterform="1" midline="1" xHeight="1"/></hh:font>')
            fonts += f'<hh:fontface lang="{lang}" fontCnt="{len(self.fonts)}">{items}</hh:fontface>'
        styles = "".join(
            f'<hh:style id="{sid}" type="{kind}" name="{x(n)}" engName="{x(e)}" paraPrIDRef="{p}" '
            f'charPrIDRef="{c}" nextStyleIDRef="{sid if kind == "PARA" else 0}" langID="1042" lockForm="0"/>'
            for sid, kind, n, e, p, c in self.styles)
        numbering = ('<hh:numberings itemCnt="1"><hh:numbering id="1" start="0">'
                     + "".join(
                         f'<hh:paraHead start="1" level="{lv}" align="LEFT" useInstWidth="1" autoIndent="1" '
                         f'widthAdjust="0" textOffsetType="PERCENT" textOffset="50" numFormat="DIGIT" '
                         f'charPrIDRef="4294967295" checkable="0">^{lv}.</hh:paraHead>'
                         for lv in range(1, 8))
                     + '</hh:numbering></hh:numberings>')
        return (XML_DECL + f'<hh:head {NS} version="1.5" secCnt="{sec_cnt}">'
                '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>'
                '<hh:refList>'
                f'<hh:fontfaces itemCnt="7">{fonts}</hh:fontfaces>'
                f'<hh:borderFills itemCnt="{len(self.border_fills)}">{"".join(self.border_fills)}</hh:borderFills>'
                f'<hh:charProperties itemCnt="{len(self.char_prs)}">{"".join(self.char_prs)}</hh:charProperties>'
                f'<hh:tabProperties itemCnt="{len(self.tab_prs)}">{"".join(self.tab_prs)}</hh:tabProperties>'
                + numbering +
                f'<hh:paraProperties itemCnt="{len(self.para_prs)}">{"".join(self.para_prs)}</hh:paraProperties>'
                f'<hh:styles itemCnt="{len(self.styles)}">{styles}</hh:styles>'
                '<hh:memoProperties itemCnt="1"><hh:memoPr id="1" width="15591" lineWidth="1" lineType="SOLID" '
                'lineColor="#B6D7AE" fillColor="#F0FFE9" activeColor="#CFF1C7" memoType="NOMAL"/></hh:memoProperties>'
                '</hh:refList>'
                '<hh:compatibleDocument targetProgram="HWP201X"><hh:layoutCompatibility/></hh:compatibleDocument>'
                '<hh:docOption><hh:linkinfo path="" pageInherit="0" footnoteInherit="0"/></hh:docOption>'
                '<hh:trackchageConfig flags="56"/></hh:head>')


class IdGen:
    def __init__(self):
        self.n = 1000

    def __call__(self):
        self.n += 1
        return self.n


ids = IdGen()
_z = [0]


def zorder():
    _z[0] += 1
    return _z[0]


# ---------------------------------------------------------------- inline pieces
def t(cp, text):
    """텍스트 런. text 안의 '\t' 는 탭, '\n' 은 줄바꿈으로 변환."""
    parts = []
    for i, seg in enumerate(str(text).split("\t")):
        if i:
            parts.append('<hp:tab width="4000" leader="0" type="1"/>')
        lines = seg.split("\n")
        for j, ln in enumerate(lines):
            if j:
                parts.append('<hp:lineBreak/>')
            parts.append(x(ln))
    return f'<hp:run charPrIDRef="{cp}"><hp:t>{"".join(parts)}</hp:t></hp:run>'


def obj(cp, xml):
    return f'<hp:run charPrIDRef="{cp}">{xml}<hp:t/></hp:run>'


def para(pp, runs, style=0, page_break=False, col_break=False, pid="0"):
    body = "".join(runs) if runs else ''
    if not runs:
        body = '<hp:run charPrIDRef="0"/>'
    return (f'<hp:p id="{pid}" paraPrIDRef="{pp}" styleIDRef="{style}" pageBreak="{int(page_break)}" '
            f'columnBreak="{int(col_break)}" merged="0">{body}{EMPTY_LINESEG}</hp:p>')


def sublist(paras, vert="TOP", width=0, height=0):
    return (f'<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="{vert}" '
            f'linkListIDRef="0" linkListNextIDRef="0" textWidth="{width}" textHeight="{height}" '
            f'hasTextRef="0" hasNumRef="0">{"".join(paras)}</hp:subList>')


def pos_inline():
    return ('<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" '
            'holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" '
            'vertOffset="0" horzOffset="0"/>')


def pos_paper(xo, yo):
    return ('<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="0" allowOverlap="1" '
            'holdAnchorAndSO="0" vertRelTo="PAPER" horzRelTo="PAPER" vertAlign="TOP" horzAlign="LEFT" '
            f'vertOffset="{yo}" horzOffset="{xo}"/>')


IDENT = ('<hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
         '<hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
         '<hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo>')


def _shape_head(w, h):
    return (f'<hp:offset x="0" y="0"/><hp:orgSz width="{w}" height="{h}"/>'
            f'<hp:curSz width="{w}" height="{h}"/><hp:flip horizontal="0" vertical="0"/>'
            f'<hp:rotationInfo angle="0" centerX="{w // 2}" centerY="{h // 2}" rotateimage="1"/>' + IDENT)


def _line_shape(color="#000000", width=0, style="NONE"):
    return (f'<hp:lineShape color="{color}" width="{width}" style="{style}" endCap="FLAT" '
            'headStyle="NORMAL" tailStyle="NORMAL" headfill="1" tailfill="1" headSz="MEDIUM_MEDIUM" '
            'tailSz="MEDIUM_MEDIUM" outlineStyle="NORMAL" alpha="0"/>')


def _fill(color):
    if not color:
        return ""
    return f'<hc:fillBrush><hc:winBrush faceColor="{color}" hatchColor="#000000" alpha="0"/></hc:fillBrush>'


SHADOW = '<hp:shadow type="NONE" color="#B2B2B2" offsetX="0" offsetY="0" alpha="0"/>'


def polygon(points, fill, xo=0, yo=0, wrap="BEHIND_TEXT"):
    """points: 종이 기준 절대 좌표(HWPUNIT) 목록"""
    minx = min(p[0] for p in points)
    miny = min(p[1] for p in points)
    maxx = max(p[0] for p in points)
    maxy = max(p[1] for p in points)
    w, h = maxx - minx, maxy - miny
    pts = "".join(f'<hc:pt x="{px - minx}" y="{py - miny}"/>' for px, py in points + [points[0]])
    return (f'<hp:polygon id="{ids()}" zOrder="{zorder()}" numberingType="PICTURE" textWrap="{wrap}" '
            'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" '
            f'instid="{ids()}">' + _shape_head(w, h) + _line_shape() + _fill(fill) + SHADOW + pts
            + f'<hp:sz width="{w}" widthRelTo="ABSOLUTE" height="{h}" heightRelTo="ABSOLUTE" protect="0"/>'
            + pos_paper(minx, miny) + '<hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:polygon>')


def textbox(xo, yo, w, h, paras, fill=None, vert="TOP", wrap="IN_FRONT_OF_TEXT", margin=0):
    dt = (f'<hp:drawText lastWidth="{w}" name="" editable="0">' + sublist(paras, vert)
          + f'<hp:textMargin left="{margin}" right="{margin}" top="{margin}" bottom="{margin}"/></hp:drawText>')
    return (f'<hp:rect id="{ids()}" zOrder="{zorder()}" numberingType="PICTURE" textWrap="{wrap}" '
            'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" '
            f'instid="{ids()}" ratio="0">' + _shape_head(w, h) + _line_shape() + _fill(fill) + SHADOW + dt
            + f'<hc:pt0 x="0" y="0"/><hc:pt1 x="{w}" y="0"/><hc:pt2 x="{w}" y="{h}"/><hc:pt3 x="0" y="{h}"/>'
            + f'<hp:sz width="{w}" widthRelTo="ABSOLUTE" height="{h}" heightRelTo="ABSOLUTE" protect="0"/>'
            + pos_paper(xo, yo) + '<hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:rect>')


def picture(bin_id, px_w, px_h, w, h=None, comment="그림입니다."):
    if h is None:
        h = int(round(w * px_h / px_w))
    dw, dh = px_w * 75, px_h * 75
    return (f'<hp:pic id="{ids()}" zOrder="{zorder()}" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" '
            'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" '
            f'instid="{ids()}" reverse="0">'
            f'<hp:offset x="0" y="0"/><hp:orgSz width="{w}" height="{h}"/><hp:curSz width="{w}" height="{h}"/>'
            f'<hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="{w // 2}" '
            f'centerY="{h // 2}" rotateimage="1"/>' + IDENT
            + f'<hc:img binaryItemIDRef="{bin_id}" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
            f'<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{w}" y="0"/><hc:pt2 x="{w}" y="{h}"/>'
            f'<hc:pt3 x="0" y="{h}"/></hp:imgRect>'
            f'<hp:imgClip left="0" right="{dw}" top="0" bottom="{dh}"/>'
            '<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
            f'<hp:imgDim dimwidth="{dw}" dimheight="{dh}"/><hp:effects/>'
            f'<hp:sz width="{w}" widthRelTo="ABSOLUTE" height="{h}" heightRelTo="ABSOLUTE" protect="0"/>'
            + pos_inline() + '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
            f'<hp:shapeComment>{x(comment)}</hp:shapeComment></hp:pic>')


def equation(script, w, h, base=1000, color="#1F1F1F", baseline=85):
    return (f'<hp:equation id="{ids()}" zOrder="{zorder()}" numberingType="EQUATION" textWrap="TOP_AND_BOTTOM" '
            'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" version="Equation Version 60" '
            f'baseLine="{baseline}" textColor="{color}" baseUnit="{base}" lineMode="CHAR" font="HYhwpEQ">'
            f'<hp:sz width="{w}" widthRelTo="ABSOLUTE" height="{h}" heightRelTo="ABSOLUTE" protect="0"/>'
            + pos_inline() + '<hp:outMargin left="56" right="56" top="0" bottom="0"/>'
            f'<hp:shapeComment>수식입니다.</hp:shapeComment><hp:script>{x(script)}</hp:script></hp:equation>')


AUTO_HEADER = [None]


def table(rows, col_widths, border_fill, cell_margin=(510, 510, 280, 280), row_heights=None):
    """rows: [[cell,...],...]; cell = dict(paras=[...], bf=id, span=(c,r), vert='CENTER')
    colspan 으로 덮이는 칸은 None."""
    nrows, ncols = len(rows), len(col_widths)
    row_heights = list(row_heights or [1000] * nrows)
    hdr = AUTO_HEADER[0]
    if hdr is not None:
        for r, row in enumerate(rows):
            c = 0
            for cell in row:
                if cell is None:
                    c += 1
                    continue
                cs, rs = cell.get("span", (1, 1))
                ml, mr, mt, mb = cell.get("margin", cell_margin)
                if rs == 1:
                    need = estimate_height(hdr, cell["paras"], sum(col_widths[c:c + cs]) - ml - mr) + mt + mb
                    row_heights[r] = max(row_heights[r], need)
                c += cs
    trs = ""
    for r, row in enumerate(rows):
        tcs = ""
        c = 0
        for cell in row:
            if cell is None:
                c += 1
                continue
            cs, rs = cell.get("span", (1, 1))
            w = sum(col_widths[c:c + cs])
            h = sum(row_heights[r:r + rs])
            ml, mr, mt, mb = cell.get("margin", cell_margin)
            tcs += (f'<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" '
                    f'borderFillIDRef="{cell.get("bf", border_fill)}">'
                    + sublist(cell["paras"], cell.get("vert", "CENTER"))
                    + f'<hp:cellAddr colAddr="{c}" rowAddr="{r}"/><hp:cellSpan colSpan="{cs}" rowSpan="{rs}"/>'
                    f'<hp:cellSz width="{w}" height="{h}"/>'
                    f'<hp:cellMargin left="{ml}" right="{mr}" top="{mt}" bottom="{mb}"/></hp:tc>')
            c += cs
        trs += f'<hp:tr>{tcs}</hp:tr>'
    tw, th = sum(col_widths), sum(row_heights)
    return (f'<hp:tbl id="{ids()}" zOrder="{zorder()}" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" '
            'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="0" '
            f'rowCnt="{nrows}" colCnt="{ncols}" cellSpacing="0" borderFillIDRef="{border_fill}" noAdjust="0">'
            f'<hp:sz width="{tw}" widthRelTo="ABSOLUTE" height="{th}" heightRelTo="ABSOLUTE" protect="0"/>'
            + pos_inline() + '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
            '<hp:inMargin left="510" right="510" top="141" bottom="141"/>' + trs + '</hp:tbl>')


def page_num_ctrl():
    return ('<hp:ctrl><hp:autoNum num="1" numType="PAGE"><hp:autoNumFormat type="DIGIT" userChar="" '
            'prefixChar="" suffixChar="" supscript="0"/></hp:autoNum></hp:ctrl>')


def sec_pr(page_w, page_h, margins, cols=1, col_gap=0, col_line=None, header_footer="",
           hide_first=False, start_page=0):
    left, right, top, bottom, header, footer = margins
    vis = int(hide_first)
    line = ""
    if col_line:
        line = f'<hp:colLine type="SOLID" width="{col_line[0]}" color="{col_line[1]}"/>'
    return (
        '<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" '
        'tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">'
        '<hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/>'
        f'<hp:startNum pageStartsOn="BOTH" page="{start_page}" pic="0" tbl="0" equation="0"/>'
        f'<hp:visibility hideFirstHeader="{vis}" hideFirstFooter="{vis}" hideFirstMasterPage="{vis}" '
        'border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>'
        '<hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/>'
        f'<hp:pagePr landscape="WIDELY" width="{page_w}" height="{page_h}" gutterType="LEFT_ONLY">'
        f'<hp:margin header="{header}" footer="{footer}" gutter="0" left="{left}" right="{right}" '
        f'top="{top}" bottom="{bottom}"/></hp:pagePr>'
        '<hp:footNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
        '<hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/>'
        '<hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/>'
        '<hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="EACH_COLUMN" beneathText="0"/>'
        '</hp:footNotePr>'
        '<hp:endNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
        '<hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/>'
        '<hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/>'
        '<hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="END_OF_DOCUMENT" beneathText="0"/>'
        '</hp:endNotePr>'
        + "".join(
            f'<hp:pageBorderFill type="{tp}" borderFillIDRef="1" textBorder="PAPER" headerInside="0" '
            'footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/>'
            '</hp:pageBorderFill>' for tp in ("BOTH", "EVEN", "ODD"))
        + '</hp:secPr>'
        f'<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="{cols}" sameSz="1" '
        f'sameGap="{col_gap}">{line}</hp:colPr></hp:ctrl>' + header_footer)


def header_ctrl(kind, paras, width, height, vert):
    tag = "header" if kind == "header" else "footer"
    return (f'<hp:ctrl><hp:{tag} id="{ids()}" applyPageType="BOTH">'
            + sublist(paras, vert, width, height) + f'</hp:{tag}></hp:ctrl>')


def section_xml(paras):
    return XML_DECL + f'<hs:sec {NS}>' + "".join(paras) + '</hs:sec>'


def write_package(path, header_xml, sections, images, title="", preview_text=""):
    """images: list of (bin_id, filename_in_BinData, bytes, media_type)"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/hwp+zip", compress_type=zipfile.ZIP_STORED)

        def w(name, data, stored=False):
            z.writestr(name, data, compress_type=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)

        w("version.xml", XML_DECL + '<hv:HCFVersion xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version" '
          'tagetApplication="WORDPROCESSOR" major="5" minor="1" micro="1" buildNumber="0" os="1" '
          'xmlVersion="1.5" application="Hancom Office Hangul" appVersion="12, 0, 0, 535 WIN32LEWindows_10"/>',
          True)
        w("Contents/header.xml", header_xml)
        for i, s in enumerate(sections):
            w(f"Contents/section{i}.xml", s)
        for bin_id, fname, data, _ in images:
            w(f"BinData/{fname}", data, True)
        w("settings.xml", XML_DECL + '<ha:HWPApplicationSetting xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
          'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0">'
          '<ha:CaretPosition listIDRef="0" paraIDRef="0" pos="0"/></ha:HWPApplicationSetting>')
        items = '<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>'
        items += "".join(f'<opf:item id="{b}" href="BinData/{f}" media-type="{m}" isEmbeded="1"/>'
                         for b, f, _, m in images)
        items += "".join(f'<opf:item id="section{i}" href="Contents/section{i}.xml" media-type="application/xml"/>'
                         for i in range(len(sections)))
        items += '<opf:item id="settings" href="settings.xml" media-type="application/xml"/>'
        spine = '<opf:itemref idref="header" linear="yes"/>' + "".join(
            f'<opf:itemref idref="section{i}" linear="yes"/>' for i in range(len(sections)))
        w("Contents/content.hpf", XML_DECL + f'<opf:package {NS} version="" unique-identifier="" id="">'
          f'<opf:metadata><opf:title>{x(title)}</opf:title><opf:language>ko</opf:language>'
          '<opf:meta name="creator" content="text"/><opf:meta name="subject" content="text"/>'
          '<opf:meta name="description" content="text"/><opf:meta name="lastsaveby" content="text"/>'
          '<opf:meta name="CreatedDate" content="text">2026-09-29T00:00:00Z</opf:meta>'
          '<opf:meta name="ModifiedDate" content="text">2026-09-29T00:00:00Z</opf:meta>'
          '<opf:meta name="date" content="text"/><opf:meta name="keyword" content="text"/></opf:metadata>'
          f'<opf:manifest>{items}</opf:manifest><opf:spine>{spine}</opf:spine></opf:package>')
        w("Preview/PrvText.txt", preview_text or title)
        w("META-INF/container.xml", XML_DECL + '<ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container" '
          'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf"><ocf:rootfiles>'
          '<ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>'
          '<ocf:rootfile full-path="Preview/PrvText.txt" media-type="text/plain"/>'
          '<ocf:rootfile full-path="META-INF/container.rdf" media-type="application/rdf+xml"/>'
          '</ocf:rootfiles></ocf:container>')
        w("META-INF/manifest.xml", XML_DECL + '<odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"/>')
        rdf = ('<rdf:Description rdf:about=""><ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#" '
               'rdf:resource="Contents/header.xml"/></rdf:Description><rdf:Description rdf:about="Contents/header.xml">'
               '<rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#HeaderFile"/></rdf:Description>')
        for i in range(len(sections)):
            rdf += (f'<rdf:Description rdf:about=""><ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#" '
                    f'rdf:resource="Contents/section{i}.xml"/></rdf:Description>'
                    f'<rdf:Description rdf:about="Contents/section{i}.xml"><rdf:type '
                    'rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#SectionFile"/></rdf:Description>')
        rdf += ('<rdf:Description rdf:about=""><rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#Document"/>'
                '</rdf:Description>')
        w("META-INF/container.rdf", XML_DECL + '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
          + rdf + '</rdf:RDF>')
    with open(path, "wb") as f:
        f.write(buf.getvalue())


# ---------------------------------------------------------------- 높이 추정(표 행 높이용)
import re as _re
from html import unescape as _unescape
_FONT_FILES = {}
_FONT_DIR = _os.path.expanduser("~/.local/share/fonts/pretendard")


def _font(face, bold, size_hu):
    from PIL import ImageFont
    name = {"Pretendard Black": "Black", "Pretendard SemiBold": "SemiBold", "Pretendard Medium": "Medium"}.get(face)
    if name is None:
        name = "Bold" if bold else "Regular"
    key = (name, size_hu)
    if key not in _FONT_FILES:
        _FONT_FILES[key] = ImageFont.truetype(f"{_FONT_DIR}/Pretendard-{name}.ttf", max(1, size_hu // 10))
    return _FONT_FILES[key]


_P_RE = _re.compile(r'<hp:p id="[^"]*" paraPrIDRef="(\d+)"[^>]*>(.*?)</hp:p>(?=<hp:p |$)', _re.S)
_RUN_RE = _re.compile(r'<hp:run charPrIDRef="(\d+)"(?:/>|>(.*?)</hp:run>)', _re.S)


def estimate_para(header, pp_id, inner, width):
    m = header.pp_meta.get(int(pp_id), dict(left=0, right=0, indent=0, prev=0, next=0, line=160))
    avail = max(1000, width - m["left"] - m["right"])
    items = []  # (width, height, is_break, base_size)
    for cp, body in _RUN_RE.findall(inner):
        size, face, bold = header.cp_meta.get(int(cp), (1000, "Pretendard", False))
        body = body or ""
        for om in _re.finditer(r'<hp:(equation|pic|tbl|rect|polygon) .*?<hp:sz width="(\d+)"[^>]*height="(\d+)"', body, _re.S):
            items.append((int(om.group(2)), int(om.group(3)), False, size))
        for tm in _re.findall(r'<hp:t>(.*?)</hp:t>', body, _re.S):
            tm = tm.replace('<hp:lineBreak/>', '\n')
            tm = _re.sub(r'<hp:tab[^>]*/>', '    ', tm)
            tm = _unescape(_re.sub(r'<[^>]+>', '', tm))
            f = _font(face, bold, size)
            for k, line in enumerate(tm.split('\n')):
                if k:
                    items.append((0, 0, True, size))
                for word in _re.split(r'(?<= )', line):
                    if word:
                        items.append((int(f.getlength(word) * 10), size, False, size))
    lines = []
    cur_w, cur = 0, []
    for w, h, br, sz in items:
        if br or (cur and cur_w + w > avail):
            lines.append(cur)
            cur, cur_w = [], 0
        if not br:
            cur.append((w, h, sz))
            cur_w += w
    lines.append(cur)
    total = m["prev"] + m["next"]
    for ln in lines:
        if not ln:
            total += int(1000 * m["line"] / 100)
            continue
        text_sz = max(sz for _, _, sz in ln)
        obj_h = max(h for _, h, _ in ln)
        total += max(obj_h, text_sz) + int(text_sz * (m["line"] - 100) / 100)
    return total


def estimate_height(header, paras, width):
    total = 0
    for pxml in paras:
        for pp_id, inner in _P_RE.findall(pxml):
            total += estimate_para(header, pp_id, inner, width)
    return total
