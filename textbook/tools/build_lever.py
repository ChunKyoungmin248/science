"""통합과학 WEEK2 「평형과 안정성」 LEVER 교재 HWPX 빌드 스크립트.

사용: python3 build_lever.py <그림 폴더> <출력.hwpx>
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import hwpx
import layout
from hwpx import (Header, mm, t, obj, para, polygon, textbox, picture, equation, table,
                  page_num_ctrl, sec_pr, header_ctrl, section_xml, write_package)

FIG = sys.argv[1] if len(sys.argv) > 1 else "fig"
OUT = sys.argv[2] if len(sys.argv) > 2 else "LEVER_통합과학_WEEK2.hwpx"
EQSIZE = os.environ.get("EQSIZE_BIN")  # rhwp 수식 크기 계산기(선택)

BURG = "#903031"
INK = "#1F1F1F"
GRAY = "#6E6E6E"
LIGHT = "#F7F7F7"
TINT = "#F5EDED"
LINE = "#D6D6D6"
WHITE = "#FFFFFF"

PAGE_W, PAGE_H = 59528, 84188
ML, MR = mm(16), mm(16)
BODY_W = PAGE_W - ML - MR
COL_GAP = mm(8)
COL_W = (BODY_W - COL_GAP) // 2

H = Header()
hwpx.AUTO_HEADER[0] = H

# ------------------------------------------------------------------ 글자 모양
F_REG, F_MED, F_SEMI, F_BOLD, F_BLACK = ("Pretendard", "Pretendard Medium", "Pretendard SemiBold",
                                         "Pretendard", "Pretendard Black")
TIMES = "Times New Roman"
CP = {}
CP["base"] = H.char(10, INK, F_REG)                     # 0 : 바탕글
CP["body"] = H.char(9.5, INK, F_REG)
CP["bodyb"] = H.char(9.5, INK, F_BOLD, bold=True)
CP["key"] = H.char(9.5, BURG, F_BOLD, bold=True)
CP["var"] = H.char(10, INK, F_REG, latin=TIMES, italic=True)
CP["note"] = H.char(8.5, GRAY, F_REG)
CP["noteb"] = H.char(8.5, BURG, F_SEMI)
CP["cap"] = H.char(8, GRAY, F_REG)
CP["h1num"] = H.char(26, BURG, F_BLACK, spacing=-3)
CP["h1"] = H.char(19, INK, F_BLACK, spacing=-2)
CP["h1eng"] = H.char(8, GRAY, F_SEMI, spacing=6)
CP["h2num"] = H.char(11.5, BURG, F_BLACK)
CP["h2"] = H.char(11.5, INK, F_SEMI, spacing=-2)
CP["h3"] = H.char(10, INK, F_SEMI, spacing=-2)
CP["h3m"] = H.char(10, BURG, F_SEMI)
CP["chip"] = H.char(8.5, WHITE, F_SEMI, shade=BURG)
CP["chipk"] = H.char(8.5, WHITE, F_SEMI, shade=INK)
CP["blank"] = H.char(9.5, INK, F_REG, underline=INK)
CP["hdr"] = H.char(8, GRAY, F_MED)
CP["hdrb"] = H.char(8, INK, F_SEMI)
CP["hdrlogo"] = H.char(10, BURG, F_BLACK, spacing=3)
CP["pnum"] = H.char(9, BURG, F_BLACK)
CP["tbl"] = H.char(8.5, INK, F_REG)
CP["tblb"] = H.char(8.5, INK, F_SEMI)
CP["tblw"] = H.char(8.5, WHITE, F_SEMI)
CP["qnum"] = H.char(17, BURG, F_BLACK, spacing=-3)
CP["prob"] = H.char(9.3, INK, F_REG, spacing=-2)
CP["tip"] = H.char(12, WHITE, F_BLACK, spacing=4)
CP["tiptitle"] = H.char(10, WHITE, F_SEMI)
CP["kicker"] = H.char(8, BURG, F_SEMI, spacing=3)
EQ_BASE = 950

# ------------------------------------------------------------------ 테두리/배경
BF_NONE = 2
S = lambda w, c: ("SOLID", w, c)
BF_H1 = H.border_fill(bottom=S("0.5 mm", INK))
BF_H2 = H.border_fill(bottom=S("0.12 mm", LINE))
BF_HDR = H.border_fill(bottom=S("0.12 mm", LINE))
BF_FTR = H.border_fill(top=S("0.12 mm", LINE))
BF_KEYBOX = H.border_fill(left=S("1.0 mm", BURG), fill=TINT)
BF_TBL = H.border_fill(S("0.12 mm", LINE), S("0.12 mm", LINE), S("0.12 mm", LINE), S("0.12 mm", LINE))
BF_TBL_HEAD = H.border_fill(S("0.12 mm", LINE), S("0.12 mm", LINE), S("0.12 mm", LINE), S("0.12 mm", LINE),
                            fill=BURG)
BF_TBL_SIDE = H.border_fill(S("0.12 mm", LINE), S("0.12 mm", LINE), S("0.12 mm", LINE), S("0.12 mm", LINE),
                            fill=TINT)
BF_BOGI = H.border_fill(S("0.12 mm", "#9A9A9A"), S("0.12 mm", "#9A9A9A"), S("0.12 mm", "#9A9A9A"),
                        S("0.12 mm", "#9A9A9A"))
BF_TIPHEAD = H.border_fill(fill=INK)
BF_TIPBODY = H.border_fill(S("0.12 mm", INK), S("0.12 mm", INK), None, S("0.12 mm", INK))
BF_QBOX = H.border_fill(top=S("0.4 mm", BURG), bottom=S("0.12 mm", LINE), fill="#FBFAFA")
BF_ANS = H.border_fill(top=S("0.12 mm", LINE), bottom=S("0.12 mm", LINE))
BF_OPEN = H.border_fill(fill=BURG)

# ------------------------------------------------------------------ 문단 모양
PP = {}
PP["base"] = H.para()                                               # 0
PP["body"] = H.para(left=mm(3), line=155, next=mm(0.6))
PP["body0"] = H.para(line=165, next=mm(0.8))
PP["bodyi"] = H.para(left=mm(6), line=155, next=mm(0.5))
PP["bul"] = H.para(left=mm(6.2), indent=-mm(3), line=160, next=mm(0.6))
PP["bul2"] = H.para(left=mm(9.2), indent=-mm(3), line=160, next=mm(0.6))
PP["h1"] = H.para(align="LEFT", line=110, prev=0, next=mm(3), border=BF_H1, keep_next=True,
                  border_offset=(0, 0, 0, mm(1.4)))
PP["kicker"] = H.para(align="LEFT", line=100, next=mm(1), keep_next=True)
PP["h2"] = H.para(align="LEFT", line=130, prev=mm(3.6), next=mm(1.8), border=BF_H2, keep_next=True,
                  border_offset=(0, 0, 0, mm(0.8)))
PP["h3"] = H.para(align="LEFT", left=mm(1.5), line=150, prev=mm(1.8), next=mm(0.8), keep_next=True)
PP["fig"] = H.para(align="CENTER", line=100, prev=mm(1.2), next=mm(1.2), keep_next=False)
PP["figk"] = H.para(align="CENTER", line=100, prev=mm(1.2), next=mm(0.6), keep_next=True)
PP["cap"] = H.para(align="CENTER", line=140, next=mm(1.6))
PP["center"] = H.para(align="CENTER", line=160, prev=mm(0.6), next=mm(1.2))
PP["cell"] = H.para(align="LEFT", line=150)
PP["cellc"] = H.para(align="CENTER", line=140)
PP["cellj"] = H.para(align="JUSTIFY", line=150)
PP["tbl"] = H.para(align="CENTER", line=100, prev=mm(1.2), next=mm(2))
PP["tblL"] = H.para(align="LEFT", line=100, prev=mm(1.2), next=mm(2))
PP["tblK"] = H.para(align="LEFT", line=100, prev=mm(1.2), next=mm(1.2), keep_next=True)
PP["prob"] = H.para(align="JUSTIFY", line=165, next=mm(1), indent=0)
PP["hdr"] = H.para(align="LEFT", line=100, tab=H.tab_right(BODY_W), border=BF_HDR,
                   border_offset=(0, 0, 0, mm(1.6)))
PP["ftr"] = H.para(align="LEFT", line=100, tab=H.tab_right(BODY_W), border=BF_FTR,
                   border_offset=(0, 0, mm(1.6), 0))
PP["cov"] = H.para(align="LEFT", line=100)
PP["covR"] = H.para(align="RIGHT", line=100)
PP["covD"] = H.para(align="DISTRIBUTE_SPACE", line=150)
PP["covC"] = H.para(align="CENTER", line=100)
PP["gap"] = H.para(line=100)

# ------------------------------------------------------------------ 스타일
ST = {}
ST["바탕글"] = H.style("바탕글", "Normal", PP["base"], CP["base"])
ST["본문"] = H.style("본문", "Body", PP["body"], CP["body"])
ST["대단원"] = H.style("LEVER 대단원", "LEVER Chapter", PP["h1"], CP["h1"])
ST["중단원"] = H.style("LEVER 중단원", "LEVER Section", PP["h2"], CP["h2"])
ST["소단원"] = H.style("LEVER 소단원", "LEVER Subsection", PP["h3"], CP["h3"])
ST["글머리"] = H.style("LEVER 글머리", "LEVER Bullet", PP["bul"], CP["body"])
ST["캡션"] = H.style("캡션", "Caption", PP["cap"], CP["cap"])
ST["머리말"] = H.style("머리말", "Header", PP["hdr"], CP["hdr"])
ST["쪽 번호"] = H.style("쪽 번호", "Page Number", PP["base"], CP["pnum"], kind="CHAR")

# ------------------------------------------------------------------ 이미지
IMAGES = []
_img_ids = {}


def img(name, width_mm):
    path = os.path.join(FIG, name)
    if name not in _img_ids:
        bid = f"image{len(IMAGES) + 1}"
        with open(path, "rb") as f:
            data = f.read()
        ext = os.path.splitext(name)[1].lower()
        media = "image/png" if ext == ".png" else "image/jpg"
        IMAGES.append((bid, f"{bid}{ext}", data, media))
        _img_ids[name] = bid
    im = Image.open(path)
    return picture(_img_ids[name], im.width, im.height, mm(width_mm), comment=f"그림입니다.\n원본 그림의 이름: {name}")


# ------------------------------------------------------------------ 수식 크기
_eq_cache = {}


def eq_sizes(scripts):
    todo = [s for s in scripts if s not in _eq_cache]
    if not todo:
        return
    if EQSIZE and os.path.exists(EQSIZE):
        inp = "".join(f"{EQ_BASE}\t{s}\n" for s in todo)
        out = subprocess.run([EQSIZE], input=inp, capture_output=True, text=True, check=True).stdout
        for s, line in zip(todo, out.strip().split("\n")):
            w, h = map(int, line.split("\t"))
            _eq_cache[s] = (w, h)
    else:
        for s in todo:
            n = len(re.sub(r"\s|[{}]", "", s))
            frac = " over " in s
            _eq_cache[s] = (int(n * EQ_BASE * 0.55), int(EQ_BASE * (2.3 if frac else 1.15)))


def M(script):
    eq_sizes([script])
    w, h = _eq_cache[script]
    base_line = 66 if " over " in script else 86
    return obj(CP["body"], equation(script, w, h, base=EQ_BASE, baseline=base_line))


# ------------------------------------------------------------------ 인라인 마크업
TOKEN = re.compile(r"(\*\*.+?\*\*|__.+?__|\$.+?\$|\[\[\d+\]\]|\{c:[a-z0-9]+\|.+?\})")


def rich(text, base="body"):
    """**핵심**, __굵게__, $수식$, [[n]] 빈칸, {c:스타일|텍스트}"""
    runs = []
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("**"):
            runs.append(t(CP["key"], tok[2:-2]))
        elif tok.startswith("__"):
            runs.append(t(CP["bodyb"], tok[2:-2]))
        elif tok.startswith("$"):
            runs.append(M(tok[1:-1]))
        elif tok.startswith("[["):
            n = int(tok[2:-2])
            runs.append(t(CP["blank"], " " * n))
        elif tok.startswith("{c:"):
            st, txt = tok[3:-1].split("|", 1)
            runs.append(t(CP[st], txt))
        else:
            runs.append(t(CP[base], tok))
    return runs


def P(text, pp="body", base="body", style="본문", **kw):
    return para(PP[pp], rich(text, base), style=ST[style], **kw)


def h1(num, title, eng, col_break=False, page_break=False):
    return [
        para(PP["h1"], [t(CP["h1num"], num), t(CP["h1"], "  " + title), t(CP["h1eng"], "   " + eng)],
             style=ST["대단원"], col_break=col_break, page_break=page_break),
    ]


def h2(num, title, **kw):
    return para(PP["h2"], [t(CP["h2num"], num + "  "), *rich(title, "h2")], style=ST["중단원"], **kw)


def h3(mark, title):
    return para(PP["h3"], [t(CP["h3m"], mark + " "), *rich(title, "h3")], style=ST["소단원"])


def bul(text, level=1):
    return para(PP["bul" if level == 1 else "bul2"], [t(CP["key"] if level == 1 else CP["body"], "·" if level == 1 else "–"),
                                                        t(CP["body"], "  "), *rich(text)], style=ST["글머리"])


def fig(name, width_mm, cap=None, keep=False):
    out = [para(PP["figk" if (cap or keep) else "fig"], [obj(CP["body"], img(name, width_mm))])]
    if cap:
        out.append(para(PP["cap"], rich(cap, "cap"), style=ST["캡션"]))
    return out


def cell(paras, bf=None, span=(1, 1), vert="CENTER", margin=None):
    c = {"paras": paras, "span": span, "vert": vert}
    if bf:
        c["bf"] = bf
    if margin:
        c["margin"] = margin
    return c


def keybox(lines, width=None, align="center"):
    """핵심 공식 상자"""
    width = width or COL_W - mm(4)
    pp = PP["cellc"] if align == "center" else PP["cell"]
    ps = [para(pp, rich(l)) for l in lines]
    return para(PP["tbl"], [obj(CP["body"], table([[cell(ps, BF_KEYBOX, margin=(mm(3), mm(3), mm(2), mm(2)))]],
                                                    [width], BF_KEYBOX))])


def chip(label, text, dark=False):
    return para(PP["body"], [t(CP["chipk" if dark else "chip"], f" {label} "), t(CP["body"], "  "), *rich(text)])


def qbox(title, lines, width=None):
    """생각해 보기(Q) 상자"""
    width = width or COL_W
    ps = [para(PP["cell"], [t(CP["chip"], " Q "), t(CP["body"], "  "), *rich(title, "bodyb")])]
    ps += [para(PP["cell"], rich(l)) for l in lines]
    return para(PP["tblK"], [obj(CP["body"], table([[cell(ps, BF_QBOX, vert="TOP",
                                                            margin=(mm(2.5), mm(2.5), mm(2), mm(2)))]],
                                                     [width], BF_QBOX))])


def gap(h_mm=2):
    return para(H.para(line=100, next=0, prev=0), [t(H.char(max(1, h_mm * 2.2)), "")])


# ================================================================== 표지
def cover():
    s = 210 / 467.0          # 원본 시안(467px 폭) → A4 mm

    def P_(px, py):
        return (mm(px * s), mm(py * s))

    shapes = []
    # 배경
    shapes.append(textbox(0, 0, PAGE_W, PAGE_H, [para(PP["cov"], [])], fill=LIGHT, wrap="BEHIND_TEXT"))
    # 위: 45° 사선 띠 + 오른쪽 기둥
    shapes.append(polygon([P_(238, 0), P_(362, 0), P_(92, 270), P_(30, 208)], BURG))
    shapes.append(polygon([P_(365, 0), P_(452, 0), P_(452, 212), P_(365, 212)], BURG))
    # 아래: 가로 띠 + 오른쪽 기둥 + 사선 띠
    shapes.append(polygon([P_(85, 330), P_(452, 330), P_(452, 415), P_(85, 415)], BURG))
    shapes.append(polygon([P_(365, 330), P_(452, 330), P_(452, 660), P_(365, 660)], BURG))
    shapes.append(polygon([P_(307, 415), P_(430, 415), P_(185, 660), P_(62, 660)], BURG))

    c_title = H.char(27, INK, F_BLACK, spacing=-4)
    c_week = H.char(14, INK, F_SEMI, spacing=2)
    c_logo = H.char(17, LIGHT, F_BLACK, spacing=4)
    c_school = H.char(22, LIGHT, F_BLACK, spacing=-3)
    c_grade = H.char(15, LIGHT, F_SEMI)
    c_tag = H.char(10, INK, F_MED)
    c_lever = H.char(158, INK, F_BLACK, spacing=-6)
    c_foot = H.char(10.5, INK, F_SEMI, spacing=-2)
    c_foot2 = H.char(10.5, LIGHT, F_SEMI, spacing=-2)
    c_unit = H.char(9, INK, F_MED, spacing=3)
    c_unitv = H.char(13, INK, F_BLACK, spacing=-2)

    def tb(x0, y0, w, h, paras, **kw):
        return textbox(mm(x0), mm(y0), mm(w), mm(h), paras, **kw)

    shapes.append(tb(13.5, 12, 80, 16, [para(PP["cov"], [t(c_title, "통합과학")])]))
    shapes.append(tb(13.5, 26.5, 80, 9, [para(PP["cov"], [t(c_week, "(WEEK 2)")])]))
    shapes.append(tb(94, 13, 24, 10, [para(PP["covC"], [t(c_logo, "KΛ")])]))
    shapes.append(tb(150, 12, 50.5, 12, [para(PP["covR"], [t(c_school, "부산외고")])]))
    shapes.append(tb(150, 24.5, 50.5, 9, [para(PP["covR"], [t(c_grade, "1학년")])]))
    # 단원 표시
    shapes.append(tb(13.5, 128, 90, 7, [para(PP["cov"], [t(c_unit, "UNIT  ·  평형과 안정성")])]))
    shapes.append(tb(13.5, 134.5, 120, 10, [para(PP["cov"], [t(c_unitv, "힘 · 돌림힘 · 물체의 평형 · 구조물의 안정성")])]))
    # 영문 태그라인
    shapes.append(tb(13.5, 192, 185, 26, [
        para(PP["covD"], [t(c_tag, "Every step forward begins with understanding.")]),
        para(PP["covD"], [t(c_tag, "Let each concept become a point of leverage")]),
        para(PP["covD"], [t(c_tag, "to lift your skills and reach new heights.")]),
    ]))
    shapes.append(tb(8, 212, 200, 62, [para(PP["cov"], [t(c_lever, "LEVER")])]))
    shapes.append(tb(13.5, 280, 80, 8, [para(PP["cov"], [t(c_foot, "성적 상승의 지렛대")])]))
    shapes.append(tb(80, 280, 81, 8, [para(PP["covR"], [t(c_foot, "정확한 개념 / 이해하는 과학")])]))

    first = para(PP["cov"], [
        f'<hp:run charPrIDRef="{CP["base"]}">'
        + sec_pr(PAGE_W, PAGE_H, (0, 0, 0, 0, 0, 0)) + "</hp:run>",
        *[obj(CP["base"], s_) for s_ in shapes],
    ])
    return section_xml([first])


# ================================================================== 머리말/꼬리말
def header_footer():
    half = BODY_W // 2
    pl, pr = H.para(align="LEFT", line=100), H.para(align="RIGHT", line=100)
    m0 = (0, 0, mm(0.5), mm(1.5))
    hdr_tbl = table([[cell([para(pl, [t(CP["hdrb"], "통합과학  WEEK 2"), t(CP["hdr"], "   |   평형과 안정성")])],
                            BF_HDR, vert="BOTTOM", margin=m0),
                       cell([para(pr, [t(CP["hdrlogo"], "LEVER")])], BF_HDR, vert="BOTTOM", margin=m0)]],
                    [half, BODY_W - half], BF_HDR)
    m1 = (0, 0, mm(1.5), 0)
    ftr_tbl = table([[cell([para(pl, [t(CP["hdr"], "부산외고 1학년  ·  정확한 개념 / 이해하는 과학")])], BF_FTR,
                            vert="TOP", margin=m1),
                       cell([para(pr, [f'<hp:run charPrIDRef="{CP["pnum"]}">{page_num_ctrl()}<hp:t/></hp:run>'])],
                            BF_FTR, vert="TOP", margin=m1)]],
                    [half, BODY_W - half], BF_FTR)
    hdr = para(H.para(align="LEFT", line=100), [obj(CP["hdr"], hdr_tbl)], style=ST["머리말"])
    ftr = para(H.para(align="LEFT", line=100), [obj(CP["hdr"], ftr_tbl)])
    return (header_ctrl("header", [hdr], BODY_W, mm(11), "TOP")
            + header_ctrl("footer", [ftr], BODY_W, mm(10), "TOP"))


# ================================================================== 본문
def body():
    B = []

    # ---------------------------------------------------------------- 01 힘
    B.append(para(PP["kicker"], [t(CP["kicker"], "WEEK 2  ·  평형과 안정성")]))
    B += h1("01", "힘", "FORCE")
    B.append(h2("(1)", "힘의 정의"))
    B.append(P("물체의 **모양**이나 **운동 상태**를 변화시키는 원인"))
    B.append(P("예) 중력, 마찰력, 부력, 전기력, 자기력", "bodyi", "note"))
    B.append(h3("①", "힘의 단위"))
    B.append(P("$rm N$ (뉴턴)  =  $rm kg CDOT m/s ^{2}$", "bodyi"))
    B.append(h3("②", "힘의 3요소 : 크기 · 방향 · 작용점"))
    B += fig("p1_x13.png", 42, "힘의 크기는 화살표의 **길이**, 방향은 화살표의 방향,\n작용점은 화살표의 시작점으로 나타낸다.")

    B.append(h2("(2)", "알짜힘 (합력)"))
    B.append(P("한 물체에 여러 힘이 동시에 작용할 때 **모든 힘의 벡터합**"))
    B.append(P("→ 실제로 물체에 작용하는 힘", "bodyi", "noteb"))
    B.append(h3("①", "힘의 합성 (알짜힘 구하기)"))
    B.append(chip("부호", "오른쪽 방향 **＋**,  왼쪽 방향 **－** 로 정한다."))
    B.append(bul("같은 방향의 두 힘 ($F_1 ,~ F_2$) → 두 힘의 **합**"))
    B += fig("p1_x10.png", 38)
    B.append(bul("반대 방향, 크기가 다른 두 힘 → **큰 값 － 작은 값**, 방향은 큰 힘의 방향"))
    B += fig("p1_x11.png", 38)
    B.append(bul("반대 방향, 크기가 같은 두 힘 → 알짜힘 0 (**힘의 평형**)"))
    B += fig("p1_x12.png", 32)
    B.append(bul("셋 이상의 힘 → 같은 방법으로 차례로 합성"))
    B += fig("p1_x14.png", 38, keep=True)
    B.append(para(PP["center"], [M("F = (F_1 - F_2 ) + F_3")]))

    B.append(h3("②", "알짜힘과 운동 상태"))
    B.append(P("알짜힘 = 0 → 운동 상태 **유지** (정지, 등속도 운동)", "bodyi"))
    B.append(P("알짜힘 ≠ 0 → 운동 상태 **변화**", "bodyi"))
    B.append(net_force_table())
    B.append(keybox(["$vec F = m vec a$ ,     $vec a = {Δ vec v} over {Δ t} = {v_t - v_0} over {Δ t}$",
                     "$therefore ~ v_t = v_0 + at$"]))
    B.append(P("힘의 방향 = **가속도의 방향**  ≠  운동 방향($v$의 방향)"))
    B.append(qbox("운동 방향과 반대로 힘이 작용할 때", [
        "질량 2 kg인 물체가 오른쪽으로 5 m/s로 운동하는 중에 왼쪽으로 2 N의 힘을 2초 동안 받았다.",
    ]))
    B += fig("draw_box2kg.png", 50, keep=True)
    B.append(P("가속도  $a = {F} over {m} = {-2 rm N} over {2 rm kg} = -1 rm m/s ^{2}$", "bodyi"))
    B.append(P("속도 : 처음  +5 m/s  →  2초 후  [[14]] m/s", "bodyi"))

    B.append(h3("③", "알짜힘과 물체의 운동"))
    B.append(P("1) 알짜힘 $= 0$ → 정지 상태 유지 또는 등속도 운동", "bodyi"))
    B.append(P("2) 크기가 같고 방향이 반대인 두 힘은 작용점이 달라도 알짜힘 $= 0$", "bodyi"))
    B.append(P("   **but** 두 힘이 같은 직선 위에 있지 않으면 → 물체가 **회전**한다.", "bodyi"))
    B += fig("p1_x17.png", 36, "$F_1 = -F_2$ 일 때 알짜힘은 0이지만 물체는 회전한다.")

    # ---------------------------------------------------------------- 02 돌림힘
    B += h1("02", "돌림힘", "TORQUE", page_break=True)
    B.append(h2("(1)", "돌림힘의 정의"))
    B.append(P("물체에 힘이 작용할 때 **회전 운동의 원인**이 되는 물리량"))
    B += fig("p2_x76.png", 27)
    B.append(bul("**회전축** : 물체가 회전할 때 중심이 되는 직선 (움직이지 않는다)"))
    B.append(bul("**회전 팔** : 회전축에서 힘의 작용점까지의 거리 벡터"))
    B.append(P("방향 : 회전축 → 힘의 작용점,   길이 : 회전축 ~ 작용점 사이의 거리", "bul2", "note"))

    B.append(h2("(2)", "돌림힘의 크기"))
    B.append(keybox(["$tau = rF sin theta$      (단위 : $rm N CDOT m$)"]))
    B.append(chip("주의", "일 $W = F TIMES s$ 도 단위가 $rm N CDOT m$ (= J)이지만 **다른 물리량**이다."))
    B.append(h3("①", "$F$ 와 $r$ 가 수직일 때 :  $tau = rF$"))
    B += fig("p2_x77.png", 50)
    B.append(h3("②", "$F$ 와 $r$ 가 수직이 아닐 때 :  $tau = rF sin theta$"))
    B += fig("p2_x78.png", 36, "회전 팔에 수직인 성분 $F sin theta$ 만 회전에 기여한다.")
    B.append(P("돌림힘의 크기를 결정하는 요인 : **회전 팔의 길이** $r$,  **수직 성분의 힘** $F sin theta$", "body"))
    B.append(qbox("회전 팔의 길이 $r$ 의 영향 (수직 성분 $F$ 동일)", []))
    B.append(para(PP["fig"], [obj(CP["body"], img("p2_x79.png", 30)), t(CP["body"], "     "),
                              obj(CP["body"], img("p2_x80.png", 36))]))
    B.append(P("회전 팔의 길이  $r_1 < r_2$   →   돌림힘  $tau _1$ [[6]] $tau _2$", "bodyi"))
    B.append(qbox("힘의 방향 $theta$ 의 영향 ($r$, $F$ 동일,  $0 DEG < theta < 90 DEG$)", []))
    B.append(para(PP["fig"], [obj(CP["body"], img("p2_x81.png", 22)), t(CP["body"], "  "),
                              obj(CP["body"], img("p2_x82.png", 22)), t(CP["body"], "  "),
                              obj(CP["body"], img("p2_x83.png", 21))]))
    B.append(P("수직 성분의 힘   $0 < F sin theta < F$   →   돌림힘 [[26]]", "bodyi"))
    B.append(sin_table())
    B.append(h2("(3)", "돌림힘의 방향"))
    B.append(P("**시계 방향**과 **시계 반대 방향** 두 가지 → 부호( ＋ / － )로 구분한다."))

    B.append(h2("(4)", "돌림힘의 이용"))
    B.append(h3("①", "지레"))
    B += fig("draw_lever.png", 60, keep=True)
    B.append(keybox(["$tau _F = aF$ ,      $tau _w = bw = bmg$",
                     "$tau _F = tau _w$ 일 때 물체를 들어 올릴 수 있다."]))
    B.append(P("질량 $m$ 인 물체를 들어 올리는 데 필요한 힘  $F = {bw} over {a}$", "bodyi"))
    B.append(P("$a : b = w : F$      ($F ∝ {1} over {r}$)", "bodyi"))
    B.append(qbox("작은 힘으로 쉽게 들어 올리려면?", ["길이 조건 :  $a$ [[6]] $b$"]))
    B.append(P("예) 지렛대, 병따개, 장도리, 스패너, 뼈와 근육", "bodyi", "note"))
    B.append(h3("②", "축바퀴"))
    B += fig("p3_x152.png", 44, "작은 축바퀴(반지름 $b$)와 큰 축바퀴(반지름 $a$)가 함께 회전한다.\n예) 자동차 운전대, 드라이버, 자전거 기어")

    # ---------------------------------------------------------------- 03 물체의 평형
    B += h1("03", "물체의 평형", "EQUILIBRIUM", page_break=True)
    B.append(eq_table())
    B.append(chip("주의", "힘의 평형 ≠ 돌림힘의 평형  →  두 조건을 **각각** 확인해야 한다."))
    B.append(h2("(1)", "돌림힘의 평형 : 모든 $tau$ 의 합 $= 0$"))
    B.append(P("회전축을 중심으로 시계 방향 돌림힘과 시계 반대 방향 돌림힘의 **크기가 같고 방향이 반대**"))
    B.append(keybox(["$tau _T = tau _A + tau _B = 0$     $therefore ~ tau _A = -tau _B$",
                     "$F_A r_A = -F_B r_B$"]))
    B.append(qbox("시소의 평형 (단, $g = 10 rm m/s ^{2}$)", []))
    B += fig("p3_x153.png", 52, keep=True)
    B.append(seesaw_table())

    B.append(h2("(2)", "역학적 평형 조건"))
    B.append(keybox(["**힘의 평형**  &  **돌림힘의 평형**"]))
    B.append(P("why? 힘의 작용선이 서로 다르면 알짜힘이 0이어도 물체가 **회전**하기 때문!"))
    B.append(h3("ex 1", "두 힘이 같은 작용선 위에 있는 경우"))
    B += fig("p4_x223.png", 36)
    B += fig("draw_same_line.png", 38, keep=True)
    B.append(P("$F_1 = -F_2$ ,  $r = 0$ (같은 작용선)   $therefore ~ tau _A = tau _B = 0$  → 회전하지 않는다.", "bodyi"))
    B.append(h3("ex 2", "두 힘의 작용선이 다른 경우"))
    B += fig("p4_x224.png", 54)
    B += fig("draw_diff_line.png", 30, keep=True)
    B.append(P("$F_1 = -F_2$ ,   $tau _1 = F_1 TIMES r_1$ ,   $tau _2 = F_2 TIMES r_2$", "bodyi"))
    B.append(P("$tau _T = tau _1 + tau _2 ≠ 0$  → 두 돌림힘이 모두 **시계 반대 방향**이므로 회전한다.", "bodyi"))

    B.append(qbox("타워 크레인의 역학적 평형", []))
    B += fig("p4_x225.png", 42, "받침점을 회전축으로, 짐($M$)과 균형추($m$)의 무게가 각각 돌림힘을 만든다.")
    B.append(P("① 힘의 평형 :  $F_M + F_m - N = 0$  ($N$ : 받침점에서의 수직 항력)", "bodyi"))
    B.append(P("② 돌림힘의 평형 :  $tau _A = -tau _B$", "bodyi"))
    B.append(P("$tau _A =$ [[18]]      $tau _B =$ [[18]]", "bodyi"))
    B.append(h3("＊", "수직 항력 : 접촉면에 수직인 방향으로 물체를 떠받치는 힘"))
    B += fig("draw_normal.png", 62, "수평면에서는 $N = mg$, 빗면에서는 $N = mg cos theta$ 이다.")

    # ---------------------------------------------------------------- 문제 풀이
    B += h1("TIP", "문제 풀이 전략", "STRATEGY", page_break=True)
    B.append(symbol_table())
    B.append(tip_box())
    B.append(problem08())
    B.append(problem09())

    # ---------------------------------------------------------------- 04 구조물의 안정성
    B += h1("04", "구조물의 안정성", "STABILITY", page_break=True)
    B.append(h2("(1)", "무게 중심"))
    B.append(P("물체의 각 부분에 작용하는 **중력의 합력의 작용점** — 물체에 작용하는 중력의 효과가 모두 모여 있다고 여겨지는 한 점"))
    B.append(para(PP["figk"], [obj(CP["body"], img("cg_sym.png", 34)), t(CP["body"], "   "),
                               obj(CP["body"], img("cg_bat.png", 40))]))
    B.append(para(PP["cap"], rich("대칭인 물체 : 물체의 **중앙**          모양이 불규칙한 물체 : 질량이 많이 분포한 쪽", "cap"), style=ST["캡션"]))
    B.append(chip("주의", "무게 중심 ≠ 질량 중심(질량 분포의 중심점) → 중력의 차이로 두 지점이 달라질 수 있다."))
    B.append(h2("(2)", "구조물의 안정성"))
    B.append(P("① 역학적 평형 상태를 유지한다.", "bodyi"))
    B.append(P("② 역학적 평형에서 벗어나도 **돌림힘**에 의해 원래 상태로 되돌아온다.", "bodyi"))
    B.append(P("   조건 : 무게 중심을 지나는 중력의 작용선이 **바닥면 안**에 있을 것", "bodyi", "noteb"))
    B.append(stability_table())
    B += fig("p6_x333.png", 78, keep=True)
    B.append(P("$theta _1 < theta _2 < theta _3$  → (다)가 가장 안정하다.  **무게 중심이 낮고, 바닥면이 넓을수록** 안정하다.", "body"))
    B.append(example_table())
    B.append(h2("(3)", "복원력"))
    B.append(P("평형 상태에서 벗어난 물체를 **원래 위치로 되돌리려는 힘**"))
    B.append(restore_table())
    B.append(qbox("배의 복원력과 안정성", []))
    B.append(ship_table())

    # ---------------------------------------------------------------- 정답
    B += h1("ANS", "정답과 해설", "ANSWERS", page_break=True)
    B += answers()
    return B


# ------------------------------------------------------------------ 표/상자 구성 요소
def net_force_table():
    w0 = mm(15)
    wc = (COL_W - w0) // 4
    cws = [w0] + [wc] * 4
    head = [cell([para(PP["cellc"], [t(CP["tblw"], "관계")])], BF_TBL_HEAD)]
    pics = ["net1.png", "net2.png", "net3.png", "net4.png"]
    for p in pics:
        head.append(cell([para(PP["cellc"], [obj(CP["tbl"], img(p, 14.5))])], margin=(mm(0.8), mm(0.8), mm(1), mm(1))))
    texts = ["운동 방향과 같은 방향 → 속력 **증가**", "운동 방향과 반대 방향 → 속력 **감소**",
             "운동 방향에 수직 → 속력 일정, **방향만 변화**", "알짜힘 0 → 운동 상태 **유지**"]
    row2 = [cell([para(PP["cellc"], [t(CP["tblw"], "운동")])], BF_TBL_HEAD)]
    row2 += [cell([para(PP["cellc"], rich(x_, "tbl"))], margin=(mm(1), mm(1), mm(1.2), mm(1.2))) for x_ in texts]
    signs = ["$+v ,~ +F$", "$+v ,~ -F$", "$v perp F$ (원운동)\n예) 쥐불놀이", "$F = 0 rarrow a = 0$"]
    row3 = [cell([para(PP["cellc"], [t(CP["tblw"], "부호")])], BF_TBL_HEAD)]
    for s_ in signs:
        ps = [para(PP["cellc"], rich(ln, "tbl")) for ln in s_.split("\n")]
        row3.append(cell(ps, BF_TBL_SIDE, margin=(mm(0.6), mm(0.6), mm(1), mm(1))))
    return para(PP["tbl"], [obj(CP["tbl"], table([head, row2, row3], cws, BF_TBL, row_heights=[mm(12), mm(10), mm(8)]))])


def sin_table():
    angles = ["$0 DEG$", "$30 DEG$", "$45 DEG$", "$60 DEG$", "$90 DEG$"]
    vals = ["$0$", "${1} over {2}$", "${sqrt {2}} over {2}$", "${sqrt {3}} over {2}$", "$1$"]
    w0 = mm(16)
    wc = (COL_W - mm(6) - w0) // 5
    rows = [[cell([para(PP["cellc"], rich("$theta$", "tblw"))], BF_TBL_HEAD)]
            + [cell([para(PP["cellc"], rich(a, "tbl"))], BF_TBL_SIDE) for a in angles],
            [cell([para(PP["cellc"], rich("$sin theta$", "tblw"))], BF_TBL_HEAD)]
            + [cell([para(PP["cellc"], rich(v, "tbl"))]) for v in vals]]
    return para(PP["tbl"], [obj(CP["tbl"], table(rows, [w0] + [wc] * 5, BF_TBL, row_heights=[mm(7), mm(10)]))])


def eq_table():
    w0 = mm(26)
    w1 = COL_W - w0 - mm(2)
    rows = [
        [cell([para(PP["cellc"], [t(CP["tblw"], "힘의 평형")])], BF_TBL_HEAD),
         cell([para(PP["cell"], rich("알짜힘 $= 0$       $F_A = -F_B$", "tbl"))])],
        [cell([para(PP["cellc"], [t(CP["tblw"], "돌림힘의 평형")])], BF_TBL_HEAD),
         cell([para(PP["cell"], rich("모든 돌림힘의 합 $= 0$       $tau _A = -tau _B$", "tbl"))])],
    ]
    return para(PP["tbl"], [obj(CP["tbl"], table(rows, [w0, w1], BF_TBL, row_heights=[mm(9), mm(9)]))])


def seesaw_table():
    w = (COL_W - mm(2)) // 2
    L = lambda s_: cell([para(PP["cell"], rich(s_, "body"))], margin=(mm(2), mm(1), mm(1.3), mm(1.3)))
    rows = [
        [L("$m_A =$ [[12]]"), L("$m_B =$ [[12]]")],
        [L("$F_A =$ [[12]]"), L("$F_B =$ [[12]]")],
        [cell([para(PP["cell"], rich("( $because ~ F =$ [[10]] ,  단위 $rm N = kg CDOT m/s ^{2}$ )", "body"))],
              span=(2, 1), margin=(mm(2), mm(1), mm(1.3), mm(1.3))), None],
        [L("$r_A =$ [[12]]"), L("$r_B =$ [[12]]")],
        [L("$rarrow ~ tau _A =$ [[12]]"), L("$tau _B =$ [[12]]")],
    ]
    return para(PP["tblL"], [obj(CP["body"], table(rows, [w, w], BF_ANS, row_heights=[mm(8)] * 5))])


def symbol_table():
    ws = [mm(20), mm(14), mm(30)]
    hd = lambda s_: cell([para(PP["cellc"], [t(CP["tblw"], s_)])], BF_TBL_HEAD)
    c_ = lambda s_: cell([para(PP["cellc"], rich(s_, "tbl"))])
    rows = [[hd("물리량"), hd("기호"), hd("단위")],
            [c_("힘"), c_("$F$"), c_("$rm N$  ($rm kg CDOT m/s ^{2}$)")],
            [c_("거리"), c_("$r$"), c_("$rm m$")],
            [c_("질량"), c_("$m$"), c_("$rm kg$")]]
    return (para(PP["tblK"], [t(CP["noteb"], "기호와 단위를 구분하자!")])
            + para(PP["tblL"], [obj(CP["tbl"], table(rows, ws, BF_TBL, row_heights=[mm(6.5)] * 4))]))


def tip_box():
    w = COL_W
    body_ps = [
        para(PP["cell"], rich("**역학적 평형** = 알짜힘 $= 0$  그리고  돌림힘의 합 $= 0$")),
        para(PP["cell"], rich("__① 막대에 작용하는 힘 찾기 (알짜힘 = 0)__")),
        para(PP["bul"], rich("아래 방향 힘 = 중력의 크기 = 무게 = $mg$  (무게 중심에서 연직 아래 방향)")),
        para(PP["bul"], rich("물체의 무게(N) = 질량(kg) × 중력 가속도($g$ = 10 m/s²)   ($F = ma$)")),
        para(PP["bul"], rich("위 방향 힘 = 수직 항력 또는 장력")),
        para(PP["cell"], [t(CP["bodyb"], "② 막대에 작용하는 돌림힘 찾기 ("), M("tau _T = 0"), t(CP["bodyb"], ")")]),
        para(PP["bul"], rich("**기준점(회전축)을 잡고** 그 점을 기준으로 계산한다. (받침대나 줄로 지탱하는 점)")),
        para(PP["bul"], rich("시계 방향 $tau = rF$ 의 합 = 시계 반대 방향 $tau = rF$ 의 합")),
        para(PP["bul"], rich("기준점에 작용하는 힘은 $r = 0$ 이므로 $tau = 0$ → 식에서 **제외**")),
        para(PP["bul"], rich("기준점이 달라지면 $r$ 이 달라진다!")),
    ]
    rows = [[cell([para(PP["cell"], [t(CP["tip"], "TIP"), t(CP["tiptitle"], "   역학적 평형 문제 풀이 순서")])],
                  BF_TIPHEAD, margin=(mm(3), mm(3), mm(1.6), mm(1.6)))],
            [cell(body_ps, BF_TIPBODY, vert="TOP", margin=(mm(3), mm(3), mm(2.5), mm(2.5)))]]
    return para(PP["tblL"], [obj(CP["body"], table(rows, [w], BF_TIPBODY, row_heights=[mm(9), mm(40)]))])


def bogi(items, width):
    ps = [para(PP["cell"], [t(CP["noteb"], "보기")])]
    for k, s_ in items:
        ps.append(para(H.para(align="JUSTIFY", left=mm(4.5), indent=-mm(4.5), line=160), [t(CP["prob"], k + "  "), *rich(s_, "prob")]))
    return obj(CP["body"], table([[cell(ps, BF_BOGI, vert="TOP", margin=(mm(3), mm(3), mm(2), mm(2)))]],
                                 [width], BF_BOGI))


def problem08():
    return "".join([
        para(PP["prob"], [t(CP["qnum"], "08  "), *rich(
            "그림은 한쪽 끝에 질량이 3 kg인 물체가 매달린 막대가 받침대 위에서 수평을 유지하고 있는 모습을 나타낸 것이다. "
            "막대의 질량은 $m$이고 길이는 3 m이며, 물체가 매달린 지점과 받침대까지의 거리는 1 m이다.", "prob")],
             pid="0"),
        para(PP["fig"], [obj(CP["body"], img("q08.png", 56))]),
        para(PP["prob"], rich("받침대를 회전축으로 할 때에 대한 설명으로 옳은 것만을 [보기]에서 있는 대로 고른 것은? "
                              "(단, 중력 가속도는 10 m/s²이고 막대의 밀도는 균일하며, 막대의 두께와 폭은 무시한다.)", "prob")),
        para(PP["tblL"], [bogi([("ㄱ.", "물체에 작용하는 중력에 의한 돌림힘의 크기는 30 N·m이다."),
                                ("ㄴ.", "시계 방향 돌림힘의 크기는 (2 × $m$ × 10) N·m이다."),
                                ("ㄷ.", "$m$ = 3 kg이다.")], COL_W)]),
        para(PP["body0"], rich("__풀이__   ① 힘 : 아래 방향 = 물체 [[8]] N + 막대 [[8]] N,   위 방향 = [[10]] N", "body")),
        para(PP["body0"], rich("② $tau$ (받침대 기준) : 시계 방향 [[12]] N·m  =  시계 반대 방향 [[12]] N·m", "body")),
        para(PP["body0"], rich("$therefore ~ m =$ [[8]] kg", "body")),
    ])


def problem09():
    return "".join([
        para(H.para(align="JUSTIFY", line=165, prev=mm(4), next=mm(1)), [t(CP["qnum"], "09  "), *rich(
            "그림과 같이 물체의 무게를 측정하는 손저울이 수평을 유지하고 있다. 저울은 길이 60 cm, 질량 0.5 kg인 원통형 막대와 "
            "질량 1 kg인 추로 구성되어 있다. 추는 막대의 중심에서 10 cm만큼 떨어져 있고, 손으로 잡은 줄과 물체가 매달린 "
            "지점 사이의 거리는 10 cm이다.", "prob")]),
        para(PP["fig"], [obj(CP["body"], img("q09.png", 74))]),
        para(PP["prob"], rich("이에 대한 설명으로 옳은 것만을 [보기]에서 있는 대로 고른 것은? (단, 중력 가속도는 10 m/s²이다.)", "prob")),
        para(PP["tblL"], [bogi([("ㄱ.", "물체의 무게는 40 N이다."),
                                ("ㄴ.", "줄이 막대를 당기는 힘의 크기는 60 N이다."),
                                ("ㄷ.", "막대의 중심을 회전축으로 할 때 추의 무게에 의한 돌림힘과 물체의 무게에 의한 돌림힘이 평형을 이룬다.")],
                               COL_W)]),
        para(PP["body0"], rich("__풀이__   ① 힘 : 아래 방향 = 추 [[6]] N + 막대 [[6]] N + 물체 [[6]] N,  위 방향 = 줄의 장력", "body")),
        para(PP["body0"], rich("② $tau$  기준 1) 막대 중심 → 막대의 돌림힘 제외!", "body")),
        para(PP["bodyi"], rich("시계 방향 : 물체 $0.3 TIMES 10m$ ,   시계 반대 방향 : 추 $0.1 TIMES 10$ + 줄 $0.2 (15 + 10m)$", "body")),
        para(PP["bodyi"], rich("$therefore ~ 3m = 1 + 3 + 2m$ ,   $m =$ [[8]] kg", "body")),
        para(PP["body0"], rich("기준 2) 줄 → 줄의 돌림힘 제외!", "body")),
        para(PP["bodyi"], rich("시계 방향 : [[30]]", "body")),
        para(PP["bodyi"], rich("시계 반대 방향 : [[26]]", "body")),
    ])


def stability_table():
    w = COL_W // 2
    hd = lambda s_: cell([para(PP["cellc"], [t(CP["tblw"], s_)])], BF_TBL_HEAD, margin=(mm(1), mm(1), mm(1), mm(1)))
    rows = [[hd("❶ 무게 중심이 낮고 바닥이 넓은 경우"), hd("❷ 무게 중심이 높고 바닥이 좁은 경우")],
            [cell([para(PP["cellc"], [obj(CP["tbl"], img("cg_low.png", 38))])], margin=(mm(1),) * 4),
             cell([para(PP["cellc"], [obj(CP["tbl"], img("cg_high.png", 33))])], margin=(mm(1),) * 4)],
            [cell([para(PP["cellc"], rich("원래 상태로 되돌아오는\n돌림힘이 **우세**", "tbl"))], BF_TBL_SIDE),
             cell([para(PP["cellc"], rich("물체를 쓰러뜨리는\n돌림힘이 **우세**", "tbl"))], BF_TBL_SIDE)]]
    return para(PP["tbl"], [obj(CP["tbl"], table(rows, [w, COL_W - w], BF_TBL, row_heights=[mm(7), mm(15), mm(10)]))])


def example_table():
    w = COL_W // 3
    ws = [w, w, COL_W - 2 * w]
    hd = lambda s_: cell([para(PP["cellc"], [t(CP["tblw"], s_)])], BF_TBL_HEAD, margin=(mm(1),) * 4)
    ph = lambda s_: cell([para(PP["cellc"], [obj(CP["tbl"], img(s_, 26))])], margin=(mm(0.5),) * 4)
    tx = lambda s_: cell([para(PP["cellj"], rich(s_, "tbl"))], vert="TOP", margin=(mm(1.5), mm(1.5), mm(1.2), mm(1.2)))
    rows = [[hd("원뿔 구조물"), hd("사다리차"), hd("초고층 건물")],
            [ph("ex_cone.png"), ph("ex_ladder.png"), ph("ex_tower.png")],
            [tx("아래쪽 바닥면이 넓어 쉽게 넘어지지 않는다."), tx("지지대를 펼쳐 세워 바닥이 넓어지는 효과를 낸다."),
             tx("바닥으로 갈수록 넓어지는 구조로 안정성을 높인다.")]]
    return para(PP["tblK"], [t(CP["noteb"], "생활 속 예")]) + para(PP["tbl"], [obj(CP["tbl"], table(rows, ws, BF_TBL, row_heights=[mm(6.5), mm(19), mm(14)]))])


def restore_table():
    w = COL_W // 2
    hd = lambda s_: cell([para(PP["cellc"], [t(CP["tblw"], s_)])], BF_TBL_HEAD, margin=(mm(1),) * 4)
    rows = [[hd("오뚝이"), hd("제자리로 돌아오는 추")],
            [cell([para(PP["cellc"], [obj(CP["tbl"], img("roly.png", 37))])], margin=(mm(1),) * 4),
             cell([para(PP["cellc"], [obj(CP["tbl"], img("pendulum.png", 37))])], margin=(mm(1),) * 4)],
            [cell([para(PP["cellj"], rich(s_, "tbl")) for s_ in [
                "평형 상태에서는 무게 중심이 받침점을 지나는 연직선 위에 있다.",
                "옆으로 넘어지면 무게 중심이 높아지고, 받침점이 회전축이 된다.",
                "→ 중력에 의한 돌림힘이 원래 상태로 되돌리는 방향으로 작용한다."]], vert="TOP",
                  margin=(mm(1.5), mm(1.5), mm(1.2), mm(1.2))),
             cell([para(PP["cellj"], rich(s_, "tbl")) for s_ in [
                 "평형 상태에서는 양쪽 추의 중력에 의한 돌림힘의 합이 0이다.",
                 "한쪽을 누르면 받침점에서 두 추까지의 수평 거리가 달라진다.",
                 "→ 원래 상태로 되돌아가려는 방향으로 돌림힘이 작용한다."]], vert="TOP",
                  margin=(mm(1.5), mm(1.5), mm(1.2), mm(1.2)))]]
    return para(PP["tbl"], [obj(CP["tbl"], table(rows, [w, COL_W - w], BF_TBL, row_heights=[mm(6.5), mm(17), mm(22)]))])


def ship_table():
    w0 = mm(26)
    w1 = COL_W - w0
    tx = lambda lines: cell([para(PP["cell"], rich(s_, "tbl")) for s_ in lines], vert="CENTER",
                            margin=(mm(2), mm(1.5), mm(1.2), mm(1.2)))
    rows = [[cell([para(PP["cellc"], [obj(CP["tbl"], img("ship_low.png", 21))]),
                   para(PP["cellc"], [t(CP["tblb"], "무게 중심이 낮은 경우")])], margin=(mm(1),) * 4),
             tx(["무게 중심 ↓ → 중력의 작용선이 **안쪽**, 부력의 작용선이 바깥쪽",
                 "∴ **원래 상태로 되돌리려는** 돌림힘이 작용 → 안정"])],
            [cell([para(PP["cellc"], [obj(CP["tbl"], img("ship_high.png", 21))]),
                   para(PP["cellc"], [t(CP["tblb"], "무게 중심이 높은 경우")])], margin=(mm(1),) * 4),
             tx(["무게 중심 ↑ → 중력의 작용선이 **바깥쪽**, 부력의 작용선이 안쪽",
                 "∴ **배를 넘어뜨리려는** 돌림힘이 작용 → 불안정"])]]
    return para(PP["tbl"], [obj(CP["tbl"], table(rows, [w0, w1], BF_TBL, row_heights=[mm(28), mm(28)]))])


def answers():
    A = []
    items = [
        ("01 힘", [
            "2 kg 물체 : $a = -1 rm m/s ^{2}$ 이므로 2초 후 속도 $v = 5 + (-1) TIMES 2 = 3 rm m/s$",
        ]),
        ("02 돌림힘", [
            "회전 팔의 영향 : $tau _1 < tau _2$ (회전 팔이 길수록 돌림힘이 크다.)",
            "힘의 방향의 영향 : $0 < rF sin theta < rF$ ($theta$ 가 90°에 가까울수록 돌림힘이 크다.)",
            "지레 : $a > b$ (힘을 주는 쪽의 팔이 길수록 작은 힘으로 들 수 있다.)",
        ]),
        ("03 물체의 평형", [
            "시소 : $m_A = 30 rm kg$, $m_B = 60 rm kg$, $F_A = 300 rm N$, $F_B = 600 rm N$ ($because ~ F = mg$)",
            "$r_A = 2 rm m$, $r_B = r$  →  $tau _A = 600 rm N CDOT m$, $tau _B = 600r$ 이므로 $r = 1 rm m$",
            "타워 크레인 : $tau _A = F_M r_1 = Mgr_1$ ,  $tau _B = F_m r_2 = mgr_2$  →  $Mr_1 = mr_2$",
        ]),
        ("08", [
            "힘 : 아래 방향 = 물체 30 N + 막대 $10m$ N,  위 방향(수직 항력) = $(30 + 10m)$ N",
            "받침대 기준 : 시계 방향 $0.5 TIMES 10m$ N·m = 시계 반대 방향 $1 TIMES 30$ N·m  $therefore ~ m = 6 rm kg$",
            "ㄱ. (○) 30 N × 1 m = 30 N·m    ㄴ. (×) $5m$ N·m    ㄷ. (×) $m = 6 rm kg$    **정답 : ㄱ**",
        ]),
        ("09", [
            "막대 중심 기준 : $0.3 TIMES 10m = 0.1 TIMES 10 + 0.2(15 + 10m)$  $therefore ~ m = 4 rm kg$",
            "줄 기준 : 시계 방향 $0.1 TIMES 10m$ = 시계 반대 방향 $0.2 TIMES 5 + 0.3 TIMES 10$  → 같은 결과",
            "ㄱ. (○) 40 N    ㄴ. (×) 장력 = 5 + 10 + 40 = 55 N    ㄷ. (×) 추 1 N·m ≠ 물체 12 N·m    **정답 : ㄱ**",
        ]),
    ]
    for head, lines in items:
        A.append(h2("■", head))
        for ln in lines:
            A.append(bul(ln))
    return A


# ================================================================== 빌드
def main():
    # 수식 크기 일괄 계산을 위해 먼저 본문을 한 번 구성
    body_paras = body()
    first = para(PP["body"], [
        f'<hp:run charPrIDRef="{CP["base"]}">'
        + sec_pr(PAGE_W, PAGE_H, (ML, MR, mm(12), mm(10), mm(11), mm(10)), cols=2, col_gap=COL_GAP,
                 col_line=("0.12 mm", LINE), header_footer=header_footer())
        + "</hp:run>"])
    for k in ("h1", "h2", "h3", "kicker", "figk", "tblK"):
        layout.KEEP_NEXT.add(PP[k])
    col_h = PAGE_H - mm(12) - mm(11) - mm(10) - mm(10) - mm(5)
    sec1, last_col, _ = layout.apply(section_xml([first] + body_paras), H, COL_W, col_h, 2)
    sec0, _, _ = layout.apply(cover(), H, PAGE_W, PAGE_H, 1, body=False)
    print("columns used:", last_col + 1, "pages:", (last_col // 2) + 1)
    header = H.xml(2)
    write_package(OUT, header, [sec0, sec1], IMAGES, title="통합과학 WEEK2 LEVER - 평형과 안정성",
                  preview_text="통합과학 WEEK 2 LEVER 평형과 안정성")
    print("written", OUT, "images", len(IMAGES), "charPr", len(H.char_prs), "paraPr", len(H.para_prs),
          "eq", len(_eq_cache))


if __name__ == "__main__":
    main()
