"""손필기 도식을 깔끔한 벡터 그림(PNG)으로 다시 그린다."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
for f in font_manager.findSystemFonts():
    if "Pretendard" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Pretendard"
plt.rcParams["mathtext.fontset"] = "stix"

RED = "#C8242B"
BLUE = "#1F6FB5"
INK = "#1F1F1F"
BOX = "#E9D3A8"
BOXE = "#A9844E"
GRAY = "#8A8A8A"


def arrow(ax, p, q, c=RED, lw=2.6, ms=16):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms,
                                 color=c, lw=lw, shrinkA=0, shrinkB=0))


def new(w, h):
    fig = plt.figure(figsize=(w, h), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w * 10)
    ax.set_ylim(0, h * 10)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", dpi=300, transparent=False, facecolor="white")
    plt.close(fig)


# 1) 2 kg 물체 예제
fig, ax = new(3.4, 1.35)
ax.plot([1, 33], [2.5, 2.5], color=INK, lw=1.6)
ax.add_patch(Rectangle((13, 2.5), 7, 5.2, fc=BOX, ec=BOXE, lw=1.4))
ax.text(16.5, 5.1, "2 kg", ha="center", va="center", fontsize=10, color=INK)
arrow(ax, (13, 5.1), (4.5, 5.1), RED)
ax.text(8.6, 6.2, "2 N", ha="center", fontsize=10, color=RED, fontweight="bold")
arrow(ax, (14, 10.2), (24, 10.2), BLUE, lw=2)
ax.text(25, 10.2, "5 m/s", va="center", fontsize=10, color=BLUE, fontweight="bold")
ax.text(1.5, 9.8, "2 s 동안", fontsize=9.5, color=INK)
save(fig, "draw_box2kg.png")

# 2) 지레
fig, ax = new(3.9, 1.7)
y = 8.5
ax.add_patch(Rectangle((3, y), 30, 0.8, fc="#D9B98A", ec=BOXE, lw=1))
ax.add_patch(Polygon([(22.5, y), (20.5, y - 4.2), (24.5, y - 4.2)], fc="#BFBFBF", ec=GRAY, lw=1))
ax.plot([17, 29], [y - 4.2, y - 4.2], color=GRAY, lw=1.2)
ax.text(22.5, y - 6.2, "받침점", ha="center", fontsize=9, color=INK)
arrow(ax, (3.4, y), (3.4, y - 5.5), RED)
ax.text(4.3, y - 5.3, r"$F$", fontsize=13, color=RED)
ax.add_patch(Rectangle((29.5, y + 0.8), 3.4, 3.0, fc=BOX, ec=BOXE, lw=1.2))
ax.text(31.2, y + 2.3, r"$m$", ha="center", va="center", fontsize=12, color=INK)
arrow(ax, (31.2, y), (31.2, y - 5.5), BLUE)
ax.text(32.0, y - 5.3, r"$w=mg$", fontsize=11, color=BLUE)
for (x0, x1, lab) in [(3.4, 22.5, r"$a$"), (22.5, 31.2, r"$b$")]:
    ax.annotate("", (x0, y + 5.3), (x1, y + 5.3),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
    ax.plot([x0, x0], [y + 1, y + 6], color=GRAY, lw=0.8, ls=(0, (2, 2)))
    ax.plot([x1, x1], [y + 1, y + 6], color=GRAY, lw=0.8, ls=(0, (2, 2)))
    ax.text((x0 + x1) / 2, y + 6.1, lab, ha="center", fontsize=13, color=INK)
save(fig, "draw_lever.png")


def box3d(ax, x, y, w, h, dx, dy, fc="#F3E6D3", ec="#8C5A2B"):
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fc=fc, ec=ec, lw=1.3))
    ax.add_patch(Polygon([(x, y + h), (x + w, y + h), (x + w + dx, y + h + dy), (x + dx, y + h + dy)], fc="#EAD7BC", ec=ec, lw=1.3))
    ax.add_patch(Polygon([(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h)], fc="#DCC4A2", ec=ec, lw=1.3))


# 3) 같은 작용선 (ex1)
fig, ax = new(3.4, 2.3)
box3d(ax, 8, 5, 16, 9, 6, 4)
cx, cy = 19, 11.5
ax.plot([cx, cx], [1.5, 22], color=RED, lw=1.2)
ax.plot([cx - 7, cx + 7], [cy - 7, cy + 7], color=RED, lw=1.2, ls=(0, (4, 3)))
arrow(ax, (cx, cy), (2.5, cy), BLUE, lw=2.2)
arrow(ax, (cx, cy), (32, cy), BLUE, lw=2.2)
ax.plot([cx], [cy], "o", color=INK, ms=4)
ax.text(1.5, cy + 1.3, r"$F_1$", fontsize=13, color=BLUE)
ax.text(30.5, cy + 1.3, r"$F_2$", fontsize=13, color=BLUE)
ax.text(cx + 7.4, cy + 7.2, "회전축", fontsize=9.5, color=RED)
save(fig, "draw_same_line.png")

# 4) 작용선이 다른 경우 (ex2)
fig, ax = new(3.0, 3.1)
box3d(ax, 10, 4, 8, 17, 4, 3.5)
cx, cy = 16, 13.5
ax.plot([cx, cx], [1, 29], color=RED, lw=1.2)
ax.plot([cx - 9, cx + 9], [cy - 8, cy + 8], color=RED, lw=1.2, ls=(0, (4, 3)))
arrow(ax, (cx, 18.5), (3, 18.5), BLUE, lw=2.2)
arrow(ax, (cx, 8.5), (28, 8.5), BLUE, lw=2.2)
ax.text(2, 19.8, r"$F_1$", fontsize=13, color=BLUE)
ax.text(26.5, 9.8, r"$F_2$", fontsize=13, color=BLUE)
ax.annotate("", (cx + 0.2, 16.8), (cx + 0.2, cy), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9))
ax.text(cx + 0.8, 14.7, r"$r_1$", fontsize=11, color=INK)
ax.annotate("", (cx - 0.2, 10.2), (cx - 0.2, cy), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9))
ax.text(cx - 3.3, 11.0, r"$r_2$", fontsize=11, color=INK)
ax.text(cx + 9.2, cy + 8, "회전축", fontsize=9.5, color=RED)
save(fig, "draw_diff_line.png")

# 5) 수직항력 (수평면, 빗면)
fig, ax = new(3.6, 1.9)
ax.plot([1, 14], [5, 5], color=INK, lw=1.5)
ax.add_patch(Rectangle((4.5, 5), 6, 4, fc=BOX, ec=BOXE, lw=1.2))
arrow(ax, (7.5, 9), (7.5, 15), BLUE)
ax.text(8.2, 13.5, r"$N$", fontsize=13, color=BLUE)
arrow(ax, (7.5, 7), (7.5, 1.2), RED)
ax.text(8.2, 1.5, r"$mg$", fontsize=12, color=RED)
import math
th = math.radians(30)
ox, oy = 17, 2
L = 18
ax.plot([ox, ox + L * math.cos(th)], [oy, oy + L * math.sin(th)], color=INK, lw=1.5)
ax.plot([ox, ox + L * math.cos(th)], [oy, oy], color=INK, lw=1.2)
ax.text(ox + 3.4, oy + 0.4, r"$\theta$", fontsize=11, color=INK)
u = (math.cos(th), math.sin(th)); n = (-math.sin(th), math.cos(th))
bx, by = ox + 9 * u[0], oy + 9 * u[1]
w, h = 5.5, 3.8
pts = [(bx, by), (bx + w * u[0], by + w * u[1]), (bx + w * u[0] + h * n[0], by + w * u[1] + h * n[1]), (bx + h * n[0], by + h * n[1])]
ax.add_patch(Polygon(pts, fc=BOX, ec=BOXE, lw=1.2))
cx, cy = bx + w / 2 * u[0] + h / 2 * n[0], by + w / 2 * u[1] + h / 2 * n[1]
g = 6.0
arrow(ax, (cx, cy), (cx, cy - g), RED)
ax.text(cx + 0.5, cy - g - 0.3, r"$mg$", fontsize=11, color=RED)
c = g * math.cos(th); s = g * math.sin(th)
arrow(ax, (cx, cy), (cx - n[0] * c, cy - n[1] * c), RED, lw=1.5, ms=11)
arrow(ax, (cx, cy), (cx - u[0] * s, cy - u[1] * s), RED, lw=1.5, ms=11)
ax.text(cx - n[0] * c + 1.2, cy - n[1] * c - 0.4, r"$mg\cos\theta$", fontsize=9, color=RED)
ax.text(cx - u[0] * s - 7.8, cy - u[1] * s - 0.6, r"$mg\sin\theta$", fontsize=9, color=RED)
arrow(ax, (cx + n[0] * h / 2, cy + n[1] * h / 2), (cx + n[0] * (h / 2 + c), cy + n[1] * (h / 2 + c)), BLUE)
ax.text(cx + n[0] * (h / 2 + c) + 0.6, cy + n[1] * (h / 2 + c) - 0.8, r"  $N=mg\cos\theta$", fontsize=9.5, color=BLUE)
save(fig, "draw_normal.png")
print("ok")
