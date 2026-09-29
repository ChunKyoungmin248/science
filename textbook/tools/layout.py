"""간이 조판기: 문단마다 줄 나눔을 계산해 <hp:linesegarray>를 채운다.

한글은 파일을 열 때 스스로 다시 조판하지만, 저장된 줄 정보가 있으면 다른
뷰어(rhwp 등)도 같은 흐름으로 쪽/단을 나눈다. 글꼴 폭은 Pretendard 실측.
"""
import re
from lxml import etree

import hwpx

HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
HS = "http://www.hancom.co.kr/hwpml/2011/section"
N = {"hp": HP}
q = lambda tag: f"{{{HP}}}{tag}"
OBJ_TAGS = {q(t) for t in ("pic", "equation", "tbl", "rect", "polygon", "ellipse", "line", "container")}
CTRL_TAGS = {q("secPr"), q("ctrl")}


def _obj_size(el):
    sz = el.find("hp:sz", N)
    pos = el.find("hp:pos", N)
    if sz is None:
        return 0, 0, False
    tac = pos is not None and pos.get("treatAsChar") == "1"
    w, h = int(sz.get("width")), int(sz.get("height"))
    om = el.find("hp:outMargin", N)
    if om is not None and tac:
        w += int(om.get("left", 0)) + int(om.get("right", 0))
        h += int(om.get("top", 0)) + int(om.get("bottom", 0))
    return w, h, tac


class Layout:
    def __init__(self, header, col_width, col_height, n_cols=2):
        self.h = header
        self.col_w = col_width
        self.col_h = col_height
        self.n_cols = n_cols

    # ------------------------------------------------------------ items
    def items(self, p):
        """문단 → [(kind, units, width, height, size)] kind: t(글자)/o(개체)/c(조판부호)/br"""
        out = []
        for run in p.findall("hp:run", N):
            size, face, bold = self.h.cp_meta.get(int(run.get("charPrIDRef", 0)), (1000, "Pretendard", False))
            for ch in run:
                if ch.tag in CTRL_TAGS:
                    out.append(("c", 8, 0, 0, size))
                elif ch.tag in OBJ_TAGS:
                    w, hh, tac = _obj_size(ch)
                    out.append(("o", 8, w if tac else 0, hh if tac else 0, size))
                elif ch.tag == q("t"):
                    f = hwpx._font(face, bold, size)
                    segs = [(ch.text or "", None)]
                    for sub in ch:
                        segs.append((None, sub))
                        segs.append((sub.tail or "", None))
                    for text, sub in segs:
                        if sub is not None:
                            if sub.tag == q("lineBreak"):
                                out.append(("br", 1, 0, 0, size))
                            elif sub.tag == q("tab"):
                                out.append(("t", 8, 3 * size, size, size))
                            else:
                                out.append(("t", 1, int(f.getlength(" ") * 10), size, size))
                            continue
                        for word in re.split(r"(?<= )", text):
                            if word:
                                out.append(("t", len(word.encode("utf-16-le")) // 2,
                                            int(f.getlength(word) * 10), size, size))
        return out

    # ------------------------------------------------------------ lines
    def lines(self, p, width):
        pp = self.h.pp_meta.get(int(p.get("paraPrIDRef", 0)),
                                dict(left=0, right=0, indent=0, prev=0, next=0, line=160))
        items = self.items(p)
        base = max([it[4] for it in items if it[0] == "t"] or [items[0][4] if items else 1000])
        lines, cur, cur_w, pos, start = [], [], 0, 0, 0

        def avail(first):
            a = width - pp["left"] - pp["right"]
            if first:
                a -= pp["indent"]
            return max(1500, a)

        for it in items:
            kind, units, w, hh, sz = it
            if kind == "br":
                lines.append((start, cur))
                pos += units
                start, cur, cur_w = pos, [], 0
                continue
            if cur and w > 0 and cur_w + w > avail(not lines):
                # 긴 단어는 글자 단위로 자른다
                lines.append((start, cur))
                start, cur, cur_w = pos, [], 0
            cur.append(it)
            cur_w += w
            pos += units
        lines.append((start, cur))
        out = []
        for i, (st, its) in enumerate(lines):
            tsz = max([x[4] for x in its if x[0] == "t"] or [base])
            oh = max([x[3] for x in its if x[0] == "o"] or [0])
            vs = max(tsz, oh)
            spacing = int(tsz * (pp["line"] - 100) / 100)
            if oh > tsz:
                spacing = int(tsz * max(0, pp["line"] - 100) / 100 * 0.5)
            cs = pp["left"] + (pp["indent"] if i == 0 else 0)
            out.append(dict(textpos=st, vertsize=vs, textheight=vs, baseline=int(vs * 0.85),
                            spacing=spacing, horzpos=max(0, cs), horzsize=avail(i == 0)))
        return out, pp

    @staticmethod
    def write(p, segs):
        old = p.find("hp:linesegarray", N)
        if old is not None:
            p.remove(old)
        arr = etree.SubElement(p, q("linesegarray"))
        for s in segs:
            e = etree.SubElement(arr, q("lineseg"))
            for k in ("textpos", "vertpos", "vertsize", "textheight", "baseline", "spacing", "horzpos", "horzsize"):
                e.set(k, str(s[k]))
            e.set("flags", "393216")

    # ------------------------------------------------------------ sublists (셀·글상자·머리말)
    def flow_sublist(self, sub, width):
        y = 0
        for p in sub.findall("hp:p", N):
            self.nested(p)
            segs, pp = self.lines(p, width)
            y += pp["prev"]
            for s in segs:
                s["vertpos"] = y
                y += s["vertsize"] + s["spacing"]
            y += pp["next"]
            self.write(p, segs)
        return y

    def nested(self, p):
        for tc in p.iter(q("tc")):
            cs = tc.find("hp:cellSz", N)
            cm = tc.find("hp:cellMargin", N)
            w = int(cs.get("width")) - int(cm.get("left")) - int(cm.get("right"))
            sub = tc.find("hp:subList", N)
            if sub.get("_done"):
                continue
            self.flow_sublist(sub, w)
            sub.set("_done", "1")
        for dt in p.iter(q("drawText")):
            rect = dt.getparent()
            sz = rect.find("hp:sz", N)
            tm = dt.find("hp:textMargin", N)
            w = int(sz.get("width")) - int(tm.get("left")) - int(tm.get("right"))
            sub = dt.find("hp:subList", N)
            if sub.get("_done"):
                continue
            self.flow_sublist(sub, w)
            sub.set("_done", "1")
        for tag in ("header", "footer"):
            for hf in p.iter(q(tag)):
                sub = hf.find("hp:subList", N)
                if sub.get("_done"):
                    continue
                self.flow_sublist(sub, int(sub.get("textWidth")))
                sub.set("_done", "1")

    # ------------------------------------------------------------ 본문 흐름(단/쪽 나눔)
    def flow_body(self, sec, report=None):
        paras = sec.findall("hp:p", N)
        infos = []
        for p in paras:
            self.nested(p)
            segs, pp = self.lines(p, self.col_w)
            infos.append((p, segs, pp))
        col, y = 0, 0
        placements = []
        for i, (p, segs, pp) in enumerate(infos):
            if p.get("pageBreak") == "1" and i:
                col = (col // self.n_cols + 1) * self.n_cols
                y = 0
            elif p.get("columnBreak") == "1" and i:
                col += 1
                y = 0
            key = p.get("_keep")
            first_h = segs[0]["vertsize"] + segs[0]["spacing"] if segs else 0
            need = pp["prev"] + first_h
            # 다음 문단과 함께(제목) : 다음 문단 첫 줄(또는 개체)까지 들어가야 함
            j = i
            while j + 1 < len(infos) and self._keep_next(infos[j][2], infos[j][0]):
                nxt = infos[j + 1]
                need += sum(s["vertsize"] + s["spacing"] for s in infos[j][1][1:]) + infos[j][2]["next"]
                need += nxt[2]["prev"] + (nxt[1][0]["vertsize"] + nxt[1][0]["spacing"] if nxt[1] else 0)
                j += 1
            if y > 0 and y + need > self.col_h:
                col += 1
                y = 0
            y += pp["prev"] if y > 0 else 0
            for k, s in enumerate(segs):
                h_ = s["vertsize"] + s["spacing"]
                if y > 0 and y + s["vertsize"] > self.col_h:
                    col += 1
                    y = 0
                s["vertpos"] = y
                y += h_
            y += pp["next"]
            self.write(p, segs)
            placements.append((col, y))
        if report is not None:
            report.extend(placements)
        return col

    def _keep_next(self, pp_meta, p):
        pid = int(p.get("paraPrIDRef", 0))
        return pid in KEEP_NEXT


KEEP_NEXT = set()


def apply(section_xml, header, col_w, col_h, n_cols=2, body=True):
    root = etree.fromstring(section_xml.encode("utf-8"))
    lay = Layout(header, col_w, col_h, n_cols)
    rep = []
    if body:
        last_col = lay.flow_body(root, rep)
    else:
        for p in root.findall("hp:p", N):
            lay.nested(p)
            segs, pp = lay.lines(p, col_w)
            y = 0
            for s in segs:
                s["vertpos"] = y
                y += s["vertsize"] + s["spacing"]
            lay.write(p, segs)
        last_col = 0
    for e in root.iter():
        if "_done" in e.attrib:
            del e.attrib["_done"]
    xml = etree.tostring(root, encoding="unicode")
    return hwpx.XML_DECL + xml, last_col, rep
