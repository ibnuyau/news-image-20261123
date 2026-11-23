"""World news front page for Monday 23 November 2026.

Draws a 1024x1024 newspaper front page with Python + PIL, following the
front-page layout of the 22 November edition: a navy masthead bar, a large
date title, a red subtitle line, a row of big-number statistics, a coloured
region bar, a UTC timeline, three illustrated lead stories, twelve small
illustrated stories, a dotted world map with a numbered list of more stories,
a date-check box and a footer. Everything is drawn with real text and simple
shapes; there is no network access and no randomness, so running the script
twice writes identical bytes.
"""

import hashlib
import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 26
INK = (28, 28, 28)
NAVY = (23, 33, 66)
RED = (178, 34, 34)
DARKRED = (139, 0, 0)
GREY = (108, 108, 108)
RULE = (196, 196, 196)
PAPER = (252, 250, 244)
CREAM = (246, 242, 232)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    """Split text into lines that fit max_w pixels."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, text, font, x, y, max_w, leading, color=INK, max_lines=None):
    """Draw wrapped text, return the y just below the last line."""
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=font, fill=color)
        y += leading
    return y


def centre(draw, text, font, cx, y, color=INK):
    """Draw text centred on cx, return its width."""
    tw = draw.textlength(text, font=font)
    draw.text((cx - tw / 2, y), text, font=font, fill=color)
    return tw


# ---------------------------------------------------------------- scenes
# Each scene fills the box (x, y, w, h) with a flat colour and draws a few
# simple shapes in it. They are pictograms, not photographs.

def scene_sky(d, x, y, w, h):
    """Night sky with three missile trails and a city silhouette."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 58))
    for sx, sy in ((0.15, 0.25), (0.5, 0.15), (0.82, 0.3)):
        d.ellipse([x + w * sx - 2, y + h * sy - 2,
                   x + w * sx + 2, y + h * sy + 2], fill=(255, 220, 130))
    for i in range(3):
        bx = x + w * (0.12 + i * 0.28)
        bh = h * (0.35 + 0.12 * ((i * 7) % 3))
        d.rectangle([bx, y + h - bh, bx + w * 0.2, y + h], fill=(52, 62, 96))
        for wy in range(2):
            d.rectangle([bx + w * 0.04, y + h - bh + 8 + wy * 16,
                         bx + w * 0.08, y + h - bh + 14 + wy * 16],
                        fill=(255, 210, 110))
    d.line([x + w * 0.7, y + h * 0.2, x + w * 0.55, y + h * 0.55],
           fill=(255, 240, 180), width=3)
    d.line([x + w * 0.85, y + h * 0.35, x + w * 0.72, y + h * 0.6],
           fill=(255, 240, 180), width=3)


def scene_dome(d, x, y, w, h):
    """A capitol dome under a star field."""
    d.rectangle([x, y, x + w, y + h], fill=(28, 54, 96))
    for sx, sy in ((0.12, 0.2), (0.3, 0.12), (0.7, 0.18), (0.88, 0.28)):
        d.ellipse([x + w * sx - 2, y + h * sy - 2,
                   x + w * sx + 2, y + h * sy + 2], fill=(255, 255, 255))
    cx = x + w / 2
    d.rectangle([cx - w * 0.3, y + h * 0.62, cx + w * 0.3, y + h],
                fill=(240, 238, 228))
    d.polygon([(cx - w * 0.22, y + h * 0.62), (cx + w * 0.22, y + h * 0.62),
               (cx, y + h * 0.3)], fill=(240, 238, 228))
    d.rectangle([cx - 3, y + h * 0.22, cx + 3, y + h * 0.3],
                fill=(240, 238, 228))
    d.rectangle([x + w * 0.08, y + h * 0.8, x + w * 0.92, y + h],
                fill=(200, 196, 184))


def scene_chip(d, x, y, w, h):
    """A falling market line over a chip."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 60, 52))
    pts = [(x + w * 0.08, y + h * 0.25), (x + w * 0.3, y + h * 0.35),
           (x + w * 0.5, y + h * 0.3), (x + w * 0.7, y + h * 0.6),
           (x + w * 0.92, y + h * 0.75)]
    d.line(pts, fill=(255, 90, 70), width=4)
    cx, cy = x + w * 0.5, y + h * 0.55
    d.rounded_rectangle([cx - w * 0.16, cy - h * 0.18, cx + w * 0.16,
                         cy + h * 0.18], radius=6,
                        fill=(30, 90, 76), outline=(150, 220, 200), width=2)
    for k in range(3):
        px = cx - w * 0.16 + k * w * 0.16
        d.line([px, cy - h * 0.18, px, cy - h * 0.3], fill=(150, 220, 200),
               width=2)
        d.line([px, cy + h * 0.18, px, cy + h * 0.3], fill=(150, 220, 200),
               width=2)


def scene_flame(d, x, y, w, h):
    """A fire over a factory roofline."""
    d.rectangle([x, y, x + w, y + h], fill=(96, 30, 22))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(52, 52, 52))
    for fx in (0.25, 0.55, 0.8):
        cx = x + w * fx
        d.polygon([(cx - w * 0.07, y + h * 0.66), (cx, y + h * 0.3),
                   (cx + w * 0.07, y + h * 0.66)], fill=(255, 150, 40))
        d.polygon([(cx - w * 0.035, y + h * 0.66), (cx, y + h * 0.45),
                   (cx + w * 0.035, y + h * 0.66)], fill=(255, 220, 90))


def scene_sea(d, x, y, w, h):
    """Waves under a listing ship."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 52, 84))
    d.polygon([(x + w * 0.2, y + h * 0.45), (x + w * 0.8, y + h * 0.55),
               (x + w * 0.75, y + h * 0.7), (x + w * 0.25, y + h * 0.6)],
              fill=(120, 120, 120))
    d.rectangle([x + w * 0.42, y + h * 0.3, x + w * 0.48, y + h * 0.48],
                fill=(120, 120, 120))
    for k in range(3):
        base = y + h * (0.72 + k * 0.09)
        pts = []
        for i in range(13):
            px = x + w * 0.05 + (w * 0.9) * i / 12
            py = base + 3 * math.sin(i * math.pi / 3)
            pts.append((px, py))
        d.line(pts, fill=(140, 190, 230), width=2)


def scene_globe(d, x, y, w, h):
    """A globe on a teal field."""
    d.rectangle([x, y, x + w, y + h], fill=(22, 96, 88))
    cx, cy, r = x + w / 2, y + h / 2, min(w, h) * 0.32
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              outline=(240, 240, 230), width=3)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
              outline=(240, 240, 230), width=2)
    d.line([x + w * 0.18, cy, x + w * 0.82, cy], fill=(240, 240, 230),
           width=2)


# ---------------------------------------------------------------- small icons
# Each draws inside the square (x, y, s) in the given colour.

def ico_quake(d, x, y, s, c):
    cx, cy = x + s / 2, y + s / 2
    pts = [(cx - s * 0.35, cy + s * 0.3), (cx - s * 0.12, cy - s * 0.15),
           (cx + s * 0.05, cy + s * 0.2), (cx + s * 0.18, cy - s * 0.3),
           (cx + s * 0.35, cy + s * 0.1)]
    d.line(pts, fill=c, width=3)


def ico_gavel(d, x, y, s, c):
    d.rectangle([x + s * 0.15, y + s * 0.2, x + s * 0.75, y + s * 0.38],
                outline=c, width=3)
    d.line([x + s * 0.45, y + s * 0.38, x + s * 0.45, y + s * 0.75],
           fill=c, width=3)
    d.line([x + s * 0.2, y + s * 0.78, x + s * 0.7, y + s * 0.78],
           fill=c, width=3)


def ico_robot(d, x, y, s, c):
    d.rounded_rectangle([x + s * 0.18, y + s * 0.22, x + s * 0.82,
                         y + s * 0.78], radius=s * 0.08, outline=c, width=3)
    d.line([x + s * 0.5, y + s * 0.22, x + s * 0.5, y + s * 0.08],
           fill=c, width=3)
    d.ellipse([x + s * 0.45, y + s * 0.02, x + s * 0.55, y + s * 0.12],
              fill=c)
    d.ellipse([x + s * 0.32, y + s * 0.38, x + s * 0.42, y + s * 0.48],
              fill=c)
    d.ellipse([x + s * 0.58, y + s * 0.62, x + s * 0.68, y + s * 0.72],
              fill=c)


def ico_cross(d, x, y, s, c):
    cx, cy = x + s / 2, y + s / 2
    d.ellipse([cx - s * 0.4, cy - s * 0.4, cx + s * 0.4, cy + s * 0.4],
              outline=c, width=3)
    d.rectangle([cx - s * 0.07, cy - s * 0.25, cx + s * 0.07,
                 cy + s * 0.25], fill=c)
    d.rectangle([cx - s * 0.25, cy - s * 0.07, cx + s * 0.25,
                 cy + s * 0.07], fill=c)


def ico_cup(d, x, y, s, c):
    d.polygon([(x + s * 0.2, y + s * 0.25), (x + s * 0.8, y + s * 0.25),
               (x + s * 0.68, y + s * 0.75), (x + s * 0.32, y + s * 0.75)],
              outline=c, width=3)
    d.line([x + s * 0.5, y + s * 0.25, x + s * 0.5, y + s * 0.08],
           fill=c, width=3)
    d.line([x + s * 0.25, y + s * 0.85, x + s * 0.75, y + s * 0.85],
           fill=c, width=3)


def ico_chart(d, x, y, s, c):
    for i, bh in enumerate((0.25, 0.45, 0.3, 0.6)):
        bx = x + s * (0.12 + i * 0.22)
        d.rectangle([bx, y + s * (0.85 - bh), bx + s * 0.14, y + s * 0.85],
                    fill=c)


def ico_ring(d, x, y, s, c):
    cx, cy = x + s / 2, y + s / 2
    d.ellipse([cx - s * 0.32, cy - s * 0.32, cx + s * 0.32, cy + s * 0.32],
              outline=c, width=3)
    d.ellipse([cx - s * 0.1, cy - s * 0.1, cx + s * 0.1, cy + s * 0.1],
              fill=c)


def ico_bolt(d, x, y, s, c):
    d.polygon([(x + s * 0.55, y + s * 0.05), (x + s * 0.3, y + s * 0.55),
               (x + s * 0.48, y + s * 0.55), (x + s * 0.42, y + s * 0.95),
               (x + s * 0.72, y + s * 0.42), (x + s * 0.52, y + s * 0.42)],
              fill=c)


def ico_plane(d, x, y, s, c):
    d.polygon([(x + s * 0.1, y + s * 0.55), (x + s * 0.9, y + s * 0.4),
               (x + s * 0.9, y + s * 0.55), (x + s * 0.5, y + s * 0.62)],
              outline=c, width=2)
    d.polygon([(x + s * 0.45, y + s * 0.55), (x + s * 0.6, y + s * 0.3),
               (x + s * 0.68, y + s * 0.55)], fill=c)


def ico_megaphone(d, x, y, s, c):
    d.polygon([(x + s * 0.12, y + s * 0.42), (x + s * 0.85, y + s * 0.18),
               (x + s * 0.85, y + s * 0.66), (x + s * 0.12, y + s * 0.58)],
              outline=c, width=3)
    d.line([x + s * 0.3, y + s * 0.58, x + s * 0.24, y + s * 0.85],
           fill=c, width=3)


def ico_star(d, x, y, s, c):
    cx, cy = x + s / 2, y + s / 2
    pts = []
    for i in range(10):
        r = s * 0.46 if i % 2 == 0 else s * 0.19
        a = math.pi * i / 5 - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, outline=c, width=2)


def ico_flag(d, x, y, s, c):
    d.rectangle([x + s * 0.1, y + s * 0.15, x + s * 0.9, y + s * 0.85],
                fill=c)
    d.line([x + s * 0.1, y + s * 0.15, x + s * 0.1, y + s * 0.98],
           fill=c, width=3)


def ico_globe(d, x, y, s, c):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=3)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=c,
              width=2)
    d.line([x + s * 0.1, cy, x + s * 0.9, cy], fill=c, width=2)


def ico_flame(d, x, y, s, c):
    cx = x + s / 2
    d.polygon([(cx - s * 0.28, y + s * 0.85), (cx, y + s * 0.08),
               (cx + s * 0.28, y + s * 0.85)], fill=c)
    d.polygon([(cx - s * 0.12, y + s * 0.85), (cx, y + s * 0.4),
               (cx + s * 0.12, y + s * 0.85)], fill=(255, 255, 255))


def ico_sea(d, x, y, s, c):
    for k in range(3):
        base = y + s * (0.25 + k * 0.25)
        pts = []
        for i in range(11):
            px = x + s * 0.05 + (s * 0.9) * i / 10
            py = base + s * 0.05 * math.sin(i * math.pi / 2.5)
            pts.append((px, py))
        d.line(pts, fill=c, width=2)


# ---------------------------------------------------------------- stories
# Every story below was first reported on Monday 23 November 2026.

LEADS = [
    ("RUSSIAN MISSILES IN POLAND", scene_sky,
     "1  WARSAW, POLAND  ·  NATO",
     "NATO meets as Poland confirms Russian missiles",
     "Poland said three objects that fell on its soil were Russian cruise "
     "missiles, and NATO called an emergency meeting for Monday. It is the "
     "sharpest escalation on the alliance's eastern flank in months.",
     "Reuters"),
    ("DEMOCRATS' BIGGEST WIN SINCE 1992", scene_dome,
     "2  WASHINGTON, USA  ·  POLITICS",
     "Democrats take biggest House majority since 1992",
     "Democrats clinched at least 258 House seats after Chuck Hubbard "
     "flipped a North Carolina seat, giving the party its largest House "
     "majority in 21 years and its biggest since 1992.",
     "BBC, Washington Examiner"),
    ("NVIDIA CHIEF STEPS DOWN", scene_chip,
     "3  SANTA CLARA, USA  ·  MARKETS",
     "Nvidia chief steps down as markets plunge",
     "Nvidia chief executive Jensen Huang stepped down as US stocks "
     "plunged and Asian markets stayed on alert. Taiwan banned short "
     "selling at or below the flat price from Monday.",
     "SimpleLife, AFP"),
]

GRID = [
    ("ANTALYA · CLIMATE", "COP31 fallout: UN chief 'deeply disappointed'",
     "UN chief: 'no ambiguity in the science'. COP32 next.",
     ico_globe, (22, 96, 88)),
    ("VANUATU · QUAKE", "M6.5 quake strikes Vanuatu region",
     "M6.5 quake at 02:40 UTC, 598 km deep.",
     ico_quake, (52, 62, 96)),
    ("IOWA · ARMY", "Army to detonate bomb chemicals despite pause",
     "Army to detonate five tons of lead-azide by Tuesday.",
     ico_gavel, (96, 30, 22)),
    ("GENEVA · ARMS", "128 states agree to pursue killer-robot rules",
     "128 states agree to pursue killer-robot rules by 2028.",
     ico_robot, (28, 54, 96)),
    ("UK · HEALTH", "NHS launches largest AI breast-cancer trial",
     "700,000 women invited to join the AI mammogram trial.",
     ico_cross, (16, 60, 52)),
    ("UK · FOOTBALL", "FIFA to confirm UK as 2035 Women's Cup host",
     "FIFA confirms on Monday UK hosts 2035 Women's Cup.",
     ico_cup, (24, 52, 84)),
    ("CIKANDE · FIRE", "Factory-fire search resumes; 24 body bags",
     "Search resumed Monday after 24 body bags recovered.",
     ico_flame, (96, 30, 22)),
    ("FINLAND · SEA", "Russian cargo ship still burning off Finland",
     "Russian cargo ship still burning off Finland after attack.",
     ico_sea, (24, 52, 84)),
    ("LIBYA · SEA", "Drone attack on Russian ship at Libya port",
     "Blast on corvette Merkury blamed on a drone attack.",
     ico_sea, (52, 62, 96)),
    ("TAIWAN · MARKETS", "Taiwan bans short selling as shares slump",
     "Taiwan bans short selling after shares fell 17.5%.",
     ico_chart, (16, 60, 52)),
    ("USA · CELEBRITY", "Miley Cyrus weds drummer Maxx Morando",
     "Miley Cyrus married drummer Maxx Morando in California.",
     ico_ring, (22, 96, 88)),
    ("OHIO · CRIME", "Three killed in Ohio baby-shower shooting",
     "Three killed, one wounded at a baby shower in Ohio.",
     ico_megaphone, (96, 30, 22)),
]

ALSO = [
    "Trump: no rush to strike Iran; hawks urge action.",
    "India and China hold 10-day talks to ease border tensions.",
    "Nepal PM Balen Shah begins his first visit to India.",
    "Myanmar calls ASEAN's decision 'unfair and imbalanced'.",
    "Thousands march in Lisbon as living costs fuel anger.",
    "Delta flights disrupted ahead of Thanksgiving; 30% hit.",
    "Flu hospitalisations at highest early level since 2010.",
    "Kilauea volcano rises to Watch; lava fountains forecast.",
    "Grays Harbor coast faces flooding on Monday morning.",
    "Skubal signs record $450m deal with the New York Mets.",
    "Elderly man rescued after 11 days lost in the Amazon.",
    "No deal on forming a new government in Israel.",
    "Liverpool beat Man United; new boss's nightmare start.",
    "Paolo Bulgari, Italian jeweller, dies aged 89.",
    "Boy, 7, pulled alive from Kyiv rubble hours after a strike.",
    "West Bank settlers torch 12 Palestinian vehicles overnight.",
    "Trump says working with Schumer would be 'difficult'.",
    "Alcaraz wins his first ATP Finals title, beating Zverev.",
    "Marquez wins a record-tying eighth MotoGP title.",
    "US intel chief backs Trump's 'friend' label for Putin.",
    "Bangladesh garment sector lost $428m in 18 days of unrest.",
]

STATS = [
    ("258", "Democrats' House seats"),
    ("3", "Russian missiles in Poland"),
    ("6.5", "Vanuatu quake magnitude"),
    ("$450m", "Skubal's record Mets deal"),
    ("128", "states back killer-robot rules"),
    ("700k", "women in AI cancer trial"),
]

REGIONS = [
    ("EUROPE", 11, (28, 90, 130)),
    ("MIDDLE EAST", 3, (178, 34, 34)),
    ("AMERICAS", 12, (28, 54, 96)),
    ("ASIA-PACIFIC", 6, (196, 130, 30)),
    ("AFRICA", 1, (34, 120, 70)),
    ("OCEANIA", 1, (110, 60, 140)),
    ("WORLD", 2, (90, 90, 90)),
]

TIMELINE = [
    ("00:49", "NHS AI trial"),
    ("01:23", "Democrats clinch House"),
    ("02:40", "Vanuatu quake"),
    ("09:22", "COP31 fails"),
]

# A coarse dotted world map: '#' is land, '.' is ocean.
MAP_ROWS = [
    "................................................",
    "...#####....####......##################........",
    "..########..######..########################....",
    ".##########..#####.##########################...",
    "..#########...###...#######################....",
    "...#######.....#.....##########..#########......",
    "....#####.............########....#######.......",
    ".....###..............#######......#####........",
    "....####....#.........######.......####.........",
    "...#####...###.......#######.......###..........",
    "....###...#####.....########....................",
    ".....#....######....#########...................",
    "..........######.....########..................",
    "...........####.......######...................",
    "............##.........####......####...........",
    "...............................######..........",
    "................................####..........",
    "................................................",
]

# (map column, map row) of the numbered dots for the 15 main stories.
MAP_DOTS = [
    (24, 3), (10, 5), (33, 4), (13, 8), (26, 2), (33, 8),
    (9, 6), (24, 4), (28, 9), (39, 6), (25, 3), (27, 9),
    (38, 6), (11, 5), (12, 6),
]

FOOTER = ("Sources: Reuters, BBC, AP, AFP, The Guardian, Al Jazeera, "
          "The Hindu, Washington Examiner. Every story above was first "
          "reported on Monday 23 November 2026.")
LEGEND = ("CERTAINTY: REPORTED = carried by the day's wires  ·  "
          "CLAIM = one side's account, labelled as such  ·  "
          "FORECAST = still to happen when drawn.")
DATECHECK = ("DATE CHECK  Left out as other days' news: the COP31 collapse "
             "itself (Sun 22 Nov) — only its aftermath is on this page; "
             "the Cikande fire started Sat 21 Nov; the Dymer drone strike "
             "was Sun 22 Nov. Tonight's count: 36 stories.")


# ---------------------------------------------------------------- layout

def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_bar = load(SANS_B, 13)
    f_bar_s = load(SANS, 11)
    f_title = load(SERIF_B, 58)
    f_sub = load(SERIF_I, 17)
    f_stat_n = load(SERIF_B, 26)
    f_stat_l = load(SANS, 10)
    f_reg = load(SANS_B, 12)
    f_time = load(SANS_B, 11)
    f_time_s = load(SANS, 11)
    f_tag = load(SANS_B, 12)
    f_lead_k = load(SANS_B, 11)
    f_lead_h = load(SERIF_B, 19)
    f_lead_b = load(SANS, 12)
    f_gk = load(SANS_B, 10)
    f_gh = load(SERIF_B, 13)
    f_gs = load(SANS, 11)
    f_sec = load(SANS_B, 13)
    f_also = load(SANS, 11)
    f_date = load(SANS_B, 11)
    f_foot = load(SANS, 10)

    # ---- top navy bar
    d.rectangle([0, 0, W, 26], fill=NAVY)
    d.text((MARGIN, 6), "THE WORLD IN ONE DAY", font=f_bar, fill=(255, 255, 255))
    right = "36 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
    rw = d.textlength(right, font=f_bar_s)
    d.text((W - MARGIN - rw, 7), right, font=f_bar_s, fill=(255, 255, 255))

    # ---- big date title
    centre(d, "Monday 23 November 2026", f_title, W / 2, 34, INK)

    # ---- red subtitle line
    sub = ("NATO meets as Poland names Russian missiles  ·  Democrats take "
           "biggest House majority since 1992  ·  Nvidia chief steps down")
    centre(d, sub, f_sub, W / 2, 96, DARKRED)
    d.line([MARGIN, 122, W - MARGIN, 122], fill=INK, width=2)

    # ---- stats row
    col_w = (W - 2 * MARGIN) / 6
    for i, (num, label) in enumerate(STATS):
        cx = MARGIN + col_w * i + col_w / 2
        centre(d, num, f_stat_n, cx, 128, DARKRED)
        centre(d, label, f_stat_l, cx, 158, GREY)
        if i:
            d.line([MARGIN + col_w * i, 130, MARGIN + col_w * i, 168],
                   fill=RULE, width=1)

    # ---- region bar
    total = sum(c for _, c, _ in REGIONS)
    bar_y = 176
    bx = MARGIN
    bar_w = W - 2 * MARGIN
    for name, count, color in REGIONS:
        seg_w = bar_w * count / total
        d.rectangle([bx, bar_y, bx + seg_w, bar_y + 20], fill=color)
        label = "%s %d" % (name, count)
        lw = d.textlength(label, font=f_reg)
        if lw < seg_w - 6:
            d.text((bx + (seg_w - lw) / 2, bar_y + 3), label, font=f_reg,
                   fill=(255, 255, 255))
        else:
            num = str(count)
            nw = d.textlength(num, font=f_reg)
            d.text((bx + (seg_w - nw) / 2, bar_y + 3), num, font=f_reg,
                   fill=(255, 255, 255))
        bx += seg_w

    # ---- UTC timeline
    tl_y = 202
    d.rectangle([0, tl_y, W, tl_y + 16], fill=NAVY)
    d.text((MARGIN, tl_y + 2), "THE DAY IN UTC", font=f_time,
           fill=(255, 220, 130))
    tx = MARGIN + 120
    for t, ev in TIMELINE:
        d.text((tx, tl_y + 2), t, font=f_time, fill=(255, 255, 255))
        tw = d.textlength(t, font=f_time)
        d.text((tx + tw + 5, tl_y + 2), ev, font=f_time_s,
               fill=(220, 220, 220))
        tx += tw + 5 + d.textlength(ev, font=f_time_s) + 18

    return img, d, (f_tag, f_lead_k, f_lead_h, f_lead_b, f_gk, f_gh, f_gs,
                    f_sec, f_also, f_date, f_foot)


def draw_rest(img, d, fonts):
    (f_tag, f_lead_k, f_lead_h, f_lead_b, f_gk, f_gh, f_gs,
     f_sec, f_also, f_date, f_foot) = fonts

    # ---- three lead stories
    lead_top = 226
    lead_w = (W - 2 * MARGIN - 2 * 14) // 3
    lead_h = 246
    for i, (tag, scene, kicker, head, body, src) in enumerate(LEADS):
        x = MARGIN + i * (lead_w + 14)
        # tag bar
        d.rectangle([x, lead_top, x + lead_w, lead_top + 20], fill=DARKRED)
        tw = d.textlength(tag, font=f_tag)
        d.text((x + (lead_w - tw) / 2, lead_top + 3), tag, font=f_tag,
               fill=(255, 255, 255))
        # illustration
        scene(d, x, lead_top + 20, lead_w, 96)
        # kicker + headline + body
        y = lead_top + 122
        d.text((x, y), kicker, font=f_lead_k, fill=DARKRED)
        y += 16
        y = para(d, head, f_lead_h, x, y, lead_w, 22, max_lines=3)
        y = para(d, body, f_lead_b, x, y + 2, lead_w, 15, max_lines=4)
        d.text((x, y + 2), "(" + src + ")", font=f_lead_b, fill=GREY)

    # ---- twelve small stories, two rows of six
    grid_top = lead_top + lead_h + 8
    cell_w = (W - 2 * MARGIN - 5 * 10) // 6
    cell_h = 112
    for i, (kicker, head, summ, icon, banner) in enumerate(GRID):
        col = i % 6
        row = i // 6
        x = MARGIN + col * (cell_w + 10)
        cy = grid_top + row * cell_h
        # small illustration banner
        d.rectangle([x, cy, x + cell_w, cy + 28], fill=banner)
        icon(d, x + cell_w / 2 - 12, cy + 2, 24, (255, 255, 255))
        # number + kicker
        y = cy + 32
        d.text((x, y), "%d  %s" % (i + 4, kicker), font=f_gk, fill=DARKRED)
        y += 12
        y = para(d, head, f_gh, x, y, cell_w, 14, max_lines=2)
        para(d, summ, f_gs, x, y + 1, cell_w, 12, max_lines=2)

    return grid_top + 2 * cell_h + 6


def draw_bottom(img, d, fonts, top):
    (f_tag, f_lead_k, f_lead_h, f_lead_b, f_gk, f_gh, f_gs,
     f_sec, f_also, f_date, f_foot) = fonts

    # ---- world map + also list
    map_x = MARGIN
    map_w = 300
    map_top = top
    d.text((map_x, map_top), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((map_x, map_top), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((map_x + 150, map_top), "pins match story numbers", font=f_foot,
           fill=GREY)
    # dotted map
    rows = len(MAP_ROWS)
    cols = len(MAP_ROWS[0])
    cell = map_w / cols
    my = map_top + 20
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == '#':
                d.ellipse([map_x + c * cell + 1, my + r * cell + 1,
                           map_x + (c + 1) * cell - 1,
                           my + (r + 1) * cell - 1], fill=(120, 120, 120))
    # numbered dots for the 15 main stories
    for n, (mc, mr) in enumerate(MAP_DOTS, start=1):
        cx = map_x + (mc + 0.5) * cell
        cy = my + (mr + 0.5) * cell
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=DARKRED)
        num = str(n)
        nw = d.textlength(num, font=f_foot)
        d.text((cx - nw / 2, cy - 5), num, font=f_foot,
               fill=(255, 255, 255))

    # also list, two columns to the right of the map
    ax = map_x + map_w + 16
    aw = W - MARGIN - ax
    d.text((ax, map_top), "ALSO ON MONDAY 23 NOVEMBER  —  21 MORE STORIES",
           font=f_sec, fill=INK)
    col_w = (aw - 14) // 2
    ay = map_top + 20
    for i, item in enumerate(ALSO):
        col = i % 2
        row = i // 2
        x = ax + col * (col_w + 14)
        y = ay + row * 14
        d.text((x, y), "%d  %s" % (i + 16, item), font=f_also, fill=INK)

    # ---- date check box
    box_top = ay + 11 * 14 + 8
    d.rectangle([MARGIN, box_top, W - MARGIN, box_top + 34],
                outline=DARKRED, width=2)
    lines = wrap(d, DATECHECK, f_date, W - 2 * MARGIN - 16)
    by = box_top + 4
    for line in lines:
        d.text((MARGIN + 8, by), line, font=f_date, fill=INK)
        by += 13

    # ---- footer
    fy = box_top + 34 + 6
    flines = wrap(d, FOOTER, f_foot, W - 2 * MARGIN)
    for line in flines:
        lw = d.textlength(line, font=f_foot)
        d.text(((W - lw) / 2, fy), line, font=f_foot, fill=GREY)
        fy += 12
    llines = wrap(d, LEGEND, f_foot, W - 2 * MARGIN)
    for line in llines:
        lw = d.textlength(line, font=f_foot)
        d.text(((W - lw) / 2, fy), line, font=f_foot, fill=GREY)
        fy += 12

    # ---- bottom navy bar
    d.rectangle([0, H - 22, W, H], fill=NAVY)
    f_bar = load(SANS_B, 12)
    d.text((MARGIN, H - 18), "THE WORLD IN ONE DAY", font=f_bar,
           fill=(255, 255, 255))
    right = "MONDAY 23 NOVEMBER 2026  ·  ONE PAGE"
    rw = d.textlength(right, font=f_bar)
    d.text((W - MARGIN - rw, H - 18), right, font=f_bar,
           fill=(255, 255, 255))
    return fy


def main():
    img, d, fonts = draw_page()
    mid = draw_rest(img, d, fonts)
    bottom = draw_bottom(img, d, fonts, mid)
    img.save("entry.png")
    data = open("entry.png", "rb").read()
    print("size:", img.size, "bottom y:", bottom)
    print("bytes:", len(data))
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
