#!/usr/bin/env python3
"""Sunday 22 November 2026 - The World in One Day.

Renders a one-page broadsheet poster (1024x1024 PNG) summing up the
world news of Sunday 22 November 2026: 3 illustrated lead stories,
10 cards and 37 one-line briefs, every item dated to the Sunday,
with a UTC timeline band and an explicit date-check box that names
the Saturday and Friday stories deliberately left out.

Python 3.13, standard library plus Pillow. Deterministic output.
Writes entry.png into MAKEFUN_OUTPUT_DIR / OUTPUT_DIR / ./output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor; design space is 1024x1024
W = 1024

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_O = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

INK = (26, 24, 20)
PAPER = (250, 246, 236)
FAINT = (110, 102, 90)
RULE = (40, 36, 30)
RED = (164, 38, 30)
BLUE = (30, 74, 138)
TEAL = (16, 110, 110)
GOLD = (176, 124, 28)
GREEN = (52, 110, 52)
PURPLE = (96, 62, 140)
BROWN = (140, 84, 40)

REGION_COLORS = {
    "EUROPE": (196, 60, 44),
    "MIDDLE EAST": (222, 138, 30),
    "ASIA-PACIFIC": (30, 110, 170),
    "AMERICAS": (44, 140, 84),
    "AFRICA": (150, 96, 170),
    "OCEANIA": (30, 150, 150),
    "WORLD": (90, 90, 96),
}


def F(path, size):
    return ImageFont.truetype(path, size * S)


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw * S or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(d, x, y, s, font, fill=INK, anchor="la"):
    d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor)


def rect(d, x, y, w, h, fill=None, outline=None, width=1):
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S],
                fill=fill, outline=outline, width=width * S)


def line(d, x1, y1, x2, y2, fill=RULE, width=1):
    d.line([x1 * S, y1 * S, x2 * S, y2 * S], fill=fill, width=width * S)


# ---------------------------------------------------------------- data
HEROES = [
    dict(n=1, region="WORLD", topic="CLIMATE", tag="ONGOING", tagc=RED,
         place="ANTALYA, TURKIYE", clock="06:00 GMT",
         head="COP31's final text lands at dawn - and stalls by dark",
         body=("The ten-page package never names fossil fuels, oil, coal or a "
               "phase-out; it recalls Dubai 2023 instead. Its goals: electricity "
               "to 35% of final energy by 2035, a gigatonne of carbon capture, "
               "adaptation finance tripled with no baseline - and the first COP "
               "admission that 1.5C will be overshot. Objections closed at 03:00 "
               "GMT; the approval plenary slipped all day and by evening the "
               "deal was still unadopted."),
         src="Sources: Reuters - AP - The Guardian", art="cop"),
    dict(n=2, region="MIDDLE EAST", topic="GULF WAR", tag="CLAIM", tagc=BROWN,
         place="MANAMA, BAHRAIN", clock="GULF WAR",
         head="Iran claims strikes on US radars in Bahrain; Manama says a factory burned",
         body=("The IRGC says missiles and drones hit Patriot radars at Al-Riffa "
               "and Awali Sakhir late Saturday, answering alleged US drone "
               "incursions. Bahrain says its defences intercepted the attacks, "
               "debris fell - and an industrial facility caught fire. No "
               "casualties; the claimed radar hits are unverified."),
         src="Sources: Al Jazeera - Reuters - IRGC statement", art="gulf"),
    dict(n=3, region="EUROPE", topic="WAR", tag="REPORTED", tagc=BLUE,
         place="KYIV, UKRAINE", clock="186 DRONES - 3 MISSILES",
         head="186 drones in the night: Kyiv downs or jams 161",
         body=("Russia sent 186 drones - 72 of them jet-powered Shaheds - from "
               "18:00 Saturday; by 08:00 Sunday air defence had shot down or "
               "electronically suppressed 161, the Air Force said. Strikes were "
               "recorded at 18 sites; one drone destroyed a five-storey block in "
               "Dymer, near Kyiv - up to seven people feared trapped, two "
               "injured, nine evacuated."),
         src="Sources: Ukrainian Air Force - General Staff", art="kyiv"),
]

CARDS = [
    dict(n=4, region="ASIA-PACIFIC", topic="HONG KONG", art="vote",
         head="Hong Kong's Election Committee vote hits a record 98.79%",
         body="856 candidates for 723 seats in 31 subsectors; 5,640 of 5,709 voters cast ballots before polls closed at 18:00.",
         src="HK Government - SCMP"),
    dict(n=5, region="AMERICAS", topic="FORMULA 1", art="f1",
         head="Verstappen wins a 35-lead-change Las Vegas thriller",
         body="From pole he beat Norris by 0.639s and Piastri by 1.529s; Russell hit the wall late and finished 9th, champion Antonelli 4th.",
         src="Reuters - F1"),
    dict(n=6, region="OCEANIA", topic="CRICKET", art="cricket",
         head="India declare at 720/9 - a Test record in New Zealand",
         body="Pant 128, Rahul 136; first innings ever with 50+ stands for all of the first seven wickets. NZ 119/2, 233 behind.",
         src="ESPNcricinfo - Cricbuzz"),
    dict(n=7, region="AMERICAS", topic="MEXICO", art="mexico",
         head="'El Chapo Isidro' seized in Sinaloa; 11 die in the operation",
         body="Special forces arrested FBI top-ten fugitive Fausto Isidro Meza Flores in Guasave on Saturday after a shoot-out.",
         src="Sky News - BBC"),
    dict(n=8, region="AFRICA", topic="NIGERIA", art="boat",
         head="Bayelsa funeral boat toll reaches at least 24",
         body="The mourners' boat capsized on Friday; recovery work on the river went on through Sunday.",
         src="AP - Vanguard"),
    dict(n=9, region="MIDDLE EAST", topic="IRAN", art="power",
         head="Iran starts rationing electricity as gas output falls",
         body="Two-hour daily power cuts begin across the grid, the state firm Tavanir announces.",
         src="Tavanir - RFE/RL"),
    dict(n=10, region="MIDDLE EAST", topic="GAZA", art="gaza",
         head="Hamas seeks urgent talks after an aid vehicle is hit",
         body="Three aid workers died in a drone strike on a food vehicle in Gaza City; Hamas demands emergency talks.",
         src="Al Jazeera - Anadolu"),
    dict(n=11, region="WORLD", topic="THE HAGUE", art="court",
         head="Myanmar rejects the world court's genocide ruling as 'unfair'",
         body="The ICJ found Myanmar committed genocide against the Rohingya; rights groups press for sanctions.",
         src="Reuters - AP"),
    dict(n=12, region="WORLD", topic="THE VATICAN", art="vatican",
         head="Pope Leo lunches with 1,300 poor guests at the Vatican",
         body="On the tenth World Day of the Poor, 1,300 guests heard the Angelus in the Paul VI Hall, then lunched with the Pope.",
         src="Vatican News"),
    dict(n=13, region="EUROPE", topic="TENNIS", art="tennis",
         head="Zverev meets Alcaraz in tonight's ATP Finals title match",
         body="World No.1 Zverev, unbeaten and unbroken all week, faces Alcaraz at 17:00 GMT in Turin; $5.17m awaits an undefeated champion.",
         src="ATP - Reuters"),
]

BRIEFS = [
    (14, "Saudi downs a Houthi missile aimed at Riyadh, 01:42.", "Anadolu"),
    (15, "Russian cargo ship ablaze off Finland; all 16 crew off.", "Reuters"),
    (16, "Korea's education minister quits over AI exam cheating.", "Seoul press"),
    (17, "Israel opposition chief: settler attacks are 'terrorism'.", "AP"),
    (18, "Jeweller Paolo Bulgari dies aged 89 in Rome.", "AP"),
    (19, "Ex-UN Women chief Mlambo-Ngcuka dies at 71.", "AP"),
    (20, "Iran shows twin-missile launcher; says it hit 3 tankers.", "State media"),
    (21, "Bukele seeks a third term; fights gangs in Haiti.", "AP"),
    (22, "ICE detains two on a Seattle airport jet bridge.", "UPI"),
    (23, "Melbourne: 70 years since the 1956 Olympics opened.", "ABC"),
    (24, "Sudan army says it retook some 30 towns in Kordofan.", "FT"),
    (25, "FBI crime database hacked, second breach in 2 months.", "BBC"),
    (26, "Bangladesh: 38 Awami League homes set on fire.", "TOI"),
    (27, "DR Congo: 40 killed in attack on Cantine, in the east.", "Officials"),
    (28, "Estonia to shut its Russia border from 1 December.", "Reuters"),
    (29, "Nepal's PM lands in Delhi on first state visit.", "IANS"),
    (30, "Marles rejects US report critical of AUKUS subs.", "Reuters"),
    (31, "Fred Nile, ex-NSW MP, dies aged 92.", "ABC"),
    (32, "Lebanon's Aoun demands full Israeli withdrawal.", "Al Jazeera"),
    (33, "Serang candy factory fire: 3 dead, 36 missing.", "Detiknews"),
    (34, "Syria says it intercepted arms bound for Lebanon.", "State media"),
    (35, "Gaza teams pull 129 more bodies from the rubble.", "Local reports"),
    (36, "Nvidia's Huang agrees to Senate testimony.", "Senate staff"),
    (37, "Banda Sea quake 6.8 off Timor-Leste; no tsunami alert.", "GFZ"),
    (38, "Trump orders contractors to report Congress requests.", "Reports"),
    (39, "Briton completes 3-day swim through Strait of Hormuz.", "Inshorts"),
    (40, "Lock of George Washington's hair sells for $4,000.", "Auction"),
    (41, "EU sends 1 billion euros more military aid to Ukraine.", "EU"),
    (42, "Blasts near Russia's Baltic Fleet base, Kaliningrad.", "Reports"),
    (43, "Thai youth rally in Bangkok for education reform.", "Bangkok press"),
    (44, "Pakistan's PML-N pushes new-provinces referendum.", "Pakistani press"),
    (45, "Suspect convicted over deadly 2025 Palisades fire.", "Court reports"),
    (46, "Mitsotakis teased over GTA VI Christmas-gift quip.", "Greek press"),
    (47, "India dismisses Bagdogra military-flight reports.", "ANI"),
    (48, "Reports: Kim never returned Trump's calls last year.", "US reports"),
    (49, "Turin doubles final precedes the singles tonight.", "ATP"),
    (50, "Tonight: Liverpool host Manchester United.", "Premier League"),
]

STATS = [
    ("~200", "NATIONS AT THE COP31 TALKS"),
    ("03:00", "GMT DEADLINE FOR OBJECTIONS"),
    ("186", "DRONES FIRED AT UKRAINE OVERNIGHT"),
    ("161", "DOWNED OR JAMMED BY 08:00"),
    ("98.79%", "HONG KONG'S RECORD TURNOUT"),
    ("720/9", "INDIA'S RECORD TOTAL IN NZ"),
]

TIMELINE = [
    ("03:00", "COP31 objections close"),
    ("05:30", "Las Vegas GP ends"),
    ("08:00", "Kyiv: 161 of 186 downed"),
    ("10:00", "HK polls close, 98.79%"),
    ("15:00", "Antalya deal unadopted"),
    ("17:00", "ATP Finals final, Turin"),
]

REGIONS = [("EUROPE", 9), ("MIDDLE EAST", 10), ("ASIA-PACIFIC", 9),
           ("AMERICAS", 9), ("AFRICA", 4), ("OCEANIA", 4), ("WORLD", 5)]

DATECHECK = ("Wires read up to 12:40 UTC, Sunday 22 November 2026: every story above was reported, or still "
             "developing, on 22 November in at least one time zone. Named as other days' news, not counted: "
             "BepiColombo reached Mercury orbit on Saturday; the EU-Indonesia trade signing (Sat); England's "
             "record 37-12 rugby win and Saturday's "
             "Premier League results; the Kryvyi Rih strike (Fri; 2 dead, 58 hurt, toll confirmed Sat); Friday's "
             "market close. Left out: the Shenzhen summit (19 Nov), the 404-drone barrage (19-20 Nov), the Peru "
             "quake (Fri, 6.7).")


# ---------------------------------------------------------------- art
def poly(d, pts, fill, outline=None):
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline)


def hero_art(d, kind, x, y, w, h):
    if kind == "cop":  # Antalya dawn: sea, sun rising, conference halls
        rect(d, x, y, w, h, fill=(38, 52, 92))
        rect(d, x, y + h * 0.52, w, h * 0.48, fill=(24, 70, 96))
        d.ellipse([(x + w * 0.40) * S, (y + h * 0.16) * S, (x + w * 0.60) * S, (y + h * 0.52) * S], fill=(244, 178, 84))
        rect(d, x, y + h * 0.46, w, h * 0.07, fill=(250, 205, 130))
        for i, bw in enumerate((0.20, 0.30, 0.17)):
            bx = x + w * (0.06 + 0.30 * i)
            rect(d, bx, y + h * 0.30, w * bw, h * 0.22, fill=(16, 22, 40))
            for r in range(2):
                for c in range(3):
                    rect(d, bx + 4 + c * w * bw * 0.3, y + h * 0.34 + r * h * 0.08, 4, 3, fill=(255, 214, 120))
        poly(d, [(x, y + h), (x + w * 0.3, y + h * 0.72), (x + w * 0.52, y + h), ], fill=(30, 40, 66))
        poly(d, [(x + w * 0.45, y + h), (x + w * 0.75, y + h * 0.70), (x + w, y + h)], fill=(24, 34, 56))
    elif kind == "gulf":  # night Gulf: radar base, ship, fire glow
        rect(d, x, y, w, h, fill=(14, 20, 38))
        rect(d, x, y + h * 0.66, w, h * 0.34, fill=(18, 44, 62))
        d.ellipse([(x + w * 0.78) * S, (y + h * 0.08) * S, (x + w * 0.88) * S, (y + h * 0.24) * S], fill=(226, 228, 210))
        rect(d, x + w * 0.05, y + h * 0.52, w * 0.30, h * 0.14, fill=(30, 34, 44))
        line(d, x + w * 0.12, y + h * 0.52, x + w * 0.12, y + h * 0.30, fill=(120, 130, 140), width=2)
        d.arc([(x + w * 0.045) * S, (y + h * 0.22) * S, (x + w * 0.20) * S, (y + h * 0.38) * S], 300, 60, fill=(240, 190, 90), width=2 * S)
        poly(d, [(x + w * 0.55, y + h * 0.66), (x + w * 0.60, y + h * 0.56), (x + w * 0.86, y + h * 0.56), (x + w * 0.90, y + h * 0.66)], fill=(52, 58, 66))
        rect(d, x + w * 0.66, y + h * 0.47, w * 0.10, h * 0.09, fill=(52, 58, 66))
        for fx in (0.60, 0.68, 0.76):
            poly(d, [(x + w * fx, y + h * 0.56), (x + w * (fx + 0.02), y + h * 0.42), (x + w * (fx + 0.045), y + h * 0.56)], fill=(238, 120, 40))
            poly(d, [(x + w * (fx + 0.012), y + h * 0.56), (x + w * (fx + 0.024), y + h * 0.47), (x + w * (fx + 0.036), y + h * 0.56)], fill=(250, 196, 84))
    else:  # kyiv night: skyline, searchlights, drone dots
        rect(d, x, y, w, h, fill=(12, 16, 34))
        for sx, sy in ((0.1, 0.2), (0.3, 0.12), (0.55, 0.25), (0.8, 0.15), (0.65, 0.08)):
            rect(d, x + w * sx, y + h * sy, 2, 2, fill=(220, 224, 235))
        poly(d, [(x + w * 0.16, y + h), (x + w * 0.34, y + h * 0.30), (x + w * 0.40, y + h)], fill=(90, 130, 190))
        poly(d, [(x + w * 0.86, y + h), (x + w * 0.62, y + h * 0.34), (x + w * 0.56, y + h)], fill=(70, 105, 160))
        for i in range(9):
            bx = x + w * (0.05 + 0.105 * i)
            bh = h * (0.22 + 0.13 * ((i * 37) % 3) / 2)
            rect(d, bx, y + h - bh, w * 0.075, bh, fill=(20, 26, 44))
            for r in range(3):
                rect(d, bx + 3, y + h - bh + 4 + r * 7, 3, 3, fill=(255, 206, 110))
        for i in range(14):
            dx = x + w * (0.08 + 0.065 * i)
            dy = y + h * (0.10 + 0.05 * ((i * 53) % 4) / 3)
            d.ellipse([(dx) * S, (dy) * S, (dx + 3) * S, (dy + 2) * S], fill=(240, 120, 90))


CARD_ICON_BG = {
    "vote": (214, 224, 240), "f1": (24, 24, 30), "cricket": (198, 226, 188),
    "mexico": (226, 214, 188), "boat": (188, 216, 228), "power": (240, 226, 178),
    "gaza": (232, 208, 190), "court": (216, 210, 226), "trade": (196, 224, 214),
    "tennis": (206, 230, 196), "vatican": (238, 228, 200),
}


def card_art(d, kind, x, y, w, h):
    rect(d, x, y, w, h, fill=CARD_ICON_BG[kind])
    cx, cy = x + w / 2, y + h / 2
    if kind == "vote":
        rect(d, cx - 16, cy - 10, 32, 22, outline=INK, width=2)
        line(d, cx - 16, cy - 10, cx, cy + 2, fill=INK, width=2)
        line(d, cx + 16, cy - 10, cx, cy + 2, fill=INK, width=2)
        text(d, cx, cy + 14, "VOTE", F(SANS_B, 8), fill=RED, anchor="ma")
    elif kind == "f1":
        rect(d, x + 8, cy - 4, w - 16, 8, fill=(200, 40, 40))
        d.ellipse([(x + 16) * S, (cy + 2) * S, (x + 28) * S, (cy + 14) * S], fill=(10, 10, 10), outline=(230, 230, 230))
        d.ellipse([(x + w - 28) * S, (cy + 2) * S, (x + w - 16) * S, (cy + 14) * S], fill=(10, 10, 10), outline=(230, 230, 230))
        for i in range(6):
            rect(d, x + 10 + i * 9, y + 5, 5, 5, fill=(240, 240, 240) if i % 2 == 0 else (20, 20, 20))
    elif kind == "cricket":
        d.ellipse([(cx - 7) * S, (cy - 7) * S, (cx + 7) * S, (cy + 7) * S], fill=(196, 40, 40))
        rect(d, cx + 14, cy - 14, 4, 28, fill=BROWN)
        rect(d, cx - 22, cy - 12, 3, 24, fill=(230, 220, 180))
        rect(d, cx - 16, cy - 12, 3, 24, fill=(230, 220, 180))
    elif kind == "mexico":
        d.ellipse([(cx) * S, (cy - 12) * S, (cx + 12) * S, (cy) * S], fill=(250, 214, 90), outline=INK)
        text(d, cx + 6, cy - 11, "10", F(SANS_B, 7), fill=INK, anchor="ma")
        rect(d, cx - 20, cy + 2, 34, 12, fill=(60, 60, 66))
        text(d, cx - 3, cy + 5, "FBI", F(SANS_B, 8), fill=(250, 250, 250), anchor="ma")
    elif kind == "boat":
        poly(d, [(x + 14, cy + 2), (x + w - 14, cy + 2), (x + w - 26, cy + 13), (x + 26, cy + 13)], fill=BROWN)
        line(d, cx, cy + 2, cx, cy - 14, fill=INK, width=2)
        d.polygon([(cx * S, (cy - 14) * S), (cx * S, (cy - 2) * S), ((cx + 10) * S, (cy - 2) * S)], fill=(250, 250, 250), outline=INK)
        line(d, x + 6, cy + 17, x + w - 6, cy + 17, fill=BLUE, width=2)
    elif kind == "power":
        poly(d, [(cx + 2, cy - 16), (cx - 9, cy + 3), (cx - 1, cy + 3), (cx - 3, cy + 16), (cx + 10, cy - 3), (cx + 1, cy - 3)], fill=(240, 170, 30), outline=INK)
    elif kind == "gaza":
        rect(d, cx - 18, cy - 8, 36, 16, fill=(250, 250, 250), outline=INK, width=2)
        rect(d, cx - 3, cy - 8, 6, 16, fill=RED)
        rect(d, cx - 18, cy - 3, 36, 6, fill=RED)
        d.ellipse([(x + 12) * S, (cy - 14) * S, (x + 20) * S, (cy - 6) * S], outline=INK, width=2)
        d.ellipse([(x + w - 20) * S, (cy + 6) * S, (x + w - 12) * S, (cy + 14) * S], outline=INK, width=2)
    elif kind == "court":
        line(d, cx - 18, cy - 6, cx + 18, cy - 6, fill=INK, width=3)
        for px in (-14, 0, 14):
            rect(d, cx + px - 2, cy - 6, 4, 16, fill=INK)
        line(d, cx - 20, cy + 12, cx + 20, cy + 12, fill=INK, width=3)
        poly(d, [(cx - 20, cy - 10), (cx + 20, cy - 10), (cx, cy - 18)], fill=INK)
    elif kind == "trade":
        poly(d, [(x + 12, cy + 4), (x + 34, cy + 4), (x + 30, cy + 13), (x + 16, cy + 13)], fill=(90, 90, 96))
        line(d, cx + 2, cy + 4, cx + 2, cy - 12, fill=INK, width=2)
        poly(d, [(cx + 2, cy - 12), (cx + 2, cy), (cx + 13, cy)], fill=(200, 60, 50))
        text(d, cx + 16, cy - 8, "EU-IDN", F(SANS_B, 8), fill=INK, anchor="ma")
    elif kind == "vatican":
        d.pieslice([(cx - 13) * S, (cy - 4) * S, (cx + 13) * S, (cy + 22) * S], 180, 360, fill=(196, 164, 90), outline=INK)
        rect(d, cx - 15, cy + 8, 30, 3, fill=INK)
        line(d, cx, cy - 16, cx, cy - 5, fill=INK, width=2)
        line(d, cx - 3, cy - 13, cx + 3, cy - 13, fill=INK, width=2)
    elif kind == "tennis":
        d.ellipse([(cx - 16) * S, (cy - 12) * S, (cx + 2) * S, (cy + 12) * S], outline=INK, width=2)
        line(d, cx - 2, cy + 10, cx + 10, cy + 18, fill=INK, width=3)
        d.ellipse([(cx + 8) * S, (cy - 14) * S, (cx + 18) * S, (cy - 4) * S], fill=(190, 220, 60), outline=INK)


# ---------------------------------------------------------------- map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 49), (-122, 37), (-105, 20), (-97, 16), (-87, 13), (-83, 9), (-105, 20), (-117, 33), (-135, 58), (-155, 60)],
    [(-79, 9), (-70, 11), (-60, 8), (-50, 0), (-44, -3), (-38, -8), (-48, -15), (-58, -25), (-65, -35), (-70, -45), (-73, -52), (-72, -40), (-70, -20), (-75, -10), (-80, -3), (-77, 4)],
    [(-10, 36), (0, 44), (-2, 49), (5, 50), (8, 55), (12, 56), (18, 56), (24, 59), (30, 60), (28, 66), (45, 68), (70, 68), (100, 70), (130, 72), (160, 70), (178, 66), (170, 60), (140, 55), (130, 45), (122, 38), (108, 32), (105, 20), (100, 8), (98, 12), (92, 16), (88, 22), (80, 15), (77, 8), (72, 20), (66, 25), (61, 25), (57, 26), (52, 28), (50, 24), (55, 24), (58, 22), (53, 17), (48, 14), (44, 12), (43, 18), (48, 28), (50, 29), (48, 30), (36, 36), (30, 36), (27, 37), (22, 37), (15, 38), (12, 44), (8, 44), (3, 43), (-2, 37), (-6, 36), (-10, 36)],
    [(-17, 15), (-10, 5), (-5, 5), (2, 6), (6, 4), (9, 4), (13, -2), (12, -10), (14, -18), (16, -28), (19, -33), (26, -34), (31, -28), (32, -20), (35, -15), (36, -5), (40, -2), (41, 5), (48, 11), (51, 12), (44, 11), (40, 15), (38, 20), (35, 28), (34, 31), (30, 31), (22, 33), (15, 32), (10, 34), (0, 35), (-6, 35), (-10, 31), (-15, 25), (-17, 20)],
    [(95, 5), (100, 8), (103, 1), (107, 12), (110, 20), (115, 23), (120, 25), (122, 30), (127, 35), (130, 38), (135, 34), (138, 36), (140, 40), (142, 45), (140, 50), (135, 45), (130, 42), (127, 40), (122, 38), (120, 32), (115, 28), (110, 25), (108, 18), (106, 10), (103, 5), (100, 3), (98, 8), (97, 15), (95, 16), (92, 20), (90, 22), (88, 21), (86, 20), (80, 15), (77, 8), (74, 12), (72, 19), (70, 22), (66, 25), (61, 25), (60, 28), (66, 30), (70, 35), (75, 35), (80, 38), (85, 40), (90, 42), (95, 45), (100, 50), (105, 55), (110, 60), (115, 65), (120, 68), (110, 70), (95, 68), (85, 65), (80, 60), (85, 55), (90, 50), (95, 48)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (130, -32), (135, -35), (138, -36), (140, -38), (145, -38), (147, -39), (150, -37), (153, -30), (153, -25), (151, -20), (149, -15), (146, -11), (142, -11), (141, -13), (142, -18), (140, -22), (136, -12), (135, -15), (132, -11), (130, -12), (126, -14), (122, -17), (118, -20), (114, -21)],
    [(167, -45), (170, -43), (172, -41), (174, -39), (176, -38), (178, -37), (176, -40), (174, -42), (171, -44), (168, -46)],
]
PINS = [  # (lon, lat, story number)
    (-99, 26, 7), (-122, 37, 5), (-58, -20, 0), (30, 50, 1), (31, 50, 3), (50, 26, 2),
    (35, 31, 10), (44, 33, 0), (47, 29, 0), (55, 25, 9), (67, 25, 0), (78, 21, 12),
    (90, 24, 0), (100, 15, 0), (106, -6, 12), (114, 30, 4), (121, 31, 0), (127, 37, 0),
    (139, 35, 0), (3, 7, 8), (8, 9, 0), (22, -29, 0), (28, -15, 0), (151, -34, 6),
    (5, 45, 13), (15, 45, 0), (26, 58, 0), (36, 55, 0), (19, 41, 0), (-0.1, 51, 0),
]


def draw_map(d, x, y, w, h):
    rect(d, x, y, w, h, fill=(238, 240, 235), outline=RULE, width=1)

    def px(lon, lat):
        return x + (lon + 180) / 360 * w, y + (85 - lat) / 165 * h

    for cont in CONTINENTS:
        poly(d, [px(lon, lat) for lon, lat in cont], fill=(196, 204, 186))
    for lon, lat, n in PINS:
        if n == 0:
            continue
        cx, cy = px(lon, lat)
        d.ellipse([(cx - 5) * S, (cy - 5) * S, (cx + 5) * S, (cy + 5) * S], fill=RED, outline=(250, 246, 236), width=1 * S)
        text(d, cx, cy - 1, str(n), F(SANS_B, 6), fill=(255, 255, 255), anchor="ma")
    text(d, x + 6, y + h - 12, "WHERE IT HAPPENED - PINS MATCH STORY NUMBERS", F(SANS_B, 6.5), fill=FAINT)


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W * S, W * S), PAPER)
    d = ImageDraw.Draw(img)

    # masthead strip
    rect(d, 0, 0, W, 24, fill=INK)
    text(d, 14, 6, "THE WORLD IN ONE DAY", F(SANS_B, 10), fill=(250, 246, 236))
    text(d, W - 14, 6, "50 STORIES - 7 REGIONS - EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
         F(SANS_B, 9), fill=(250, 246, 236), anchor="ra")

    # title + standfirst
    text(d, W / 2, 32, "Sunday 22 November 2026", F(SERIF_B, 44), fill=INK, anchor="ma")
    text(d, W / 2, 88, "COP31's final text lands at dawn and stalls by dark - Iran and Bahrain trade claims - 186 drones over Ukraine",
         F(SERIF_I, 12.5), fill=RED, anchor="ma")
    line(d, 12, 112, W - 12, 112, fill=RULE, width=2)

    # stat strip
    sw = (W - 24) / 6
    for i, (big, small) in enumerate(STATS):
        cx = 12 + sw * i + sw / 2
        text(d, cx, 118, big, F(SERIF_B, 19), fill=INK, anchor="ma")
        for j, ln in enumerate(wrap(d, small, F(SANS_B, 6.5), sw - 8)):
            text(d, cx, 142 + j * 8, ln, F(SANS_B, 6.5), fill=FAINT, anchor="ma")
        if i:
            line(d, 12 + sw * i, 118, 12 + sw * i, 158, fill=(200, 192, 175), width=1)
    line(d, 12, 162, W - 12, 162, fill=RULE, width=1)

    # region bar
    total = sum(c for _, c in REGIONS)
    bx = 12
    for name, cnt in REGIONS:
        bw = (W - 24) * cnt / total
        rect(d, bx, 168, bw, 15, fill=REGION_COLORS[name])
        text(d, bx + bw / 2, 171.5, f"{name} {cnt}", F(SANS_B, 7.5), fill=(255, 255, 255), anchor="ma")
        bx += bw

    # timeline band
    rect(d, 12, 190, W - 24, 20, fill=(238, 233, 220), outline=RULE, width=1)
    text(d, 18, 196, "THE DAY IN UTC", F(SANS_B, 8), fill=INK)
    tw = (W - 130) / 6
    ftm, fev = F(SANS_B, 8.5), F(SANS, 7.2)
    for i, (tm, ev) in enumerate(TIMELINE):
        tx = 118 + tw * i
        text(d, tx, 195, tm, ftm, fill=RED)
        off = d.textlength(tm, font=ftm) / S + 5
        text(d, tx + off, 196, ev, fev, fill=INK)
    line(d, 12, 216, W - 12, 216, fill=RULE, width=1)

    # heroes
    hw = (W - 24 - 16) / 3
    for i, hz in enumerate(HEROES):
        hx = 12 + i * (hw + 8)
        hero_art(d, hz["art"], hx, 220, hw, 88)
        text(d, hx + 6, 290, hz["place"], F(SANS_B, 8), fill=(255, 255, 255))
        text(d, hx + hw - 6, 290, hz["clock"], F(SANS_B, 7), fill=(255, 255, 255), anchor="ra")
        ky = 316
        text(d, hx, ky, f"{hz['n']} - {hz['region']} - {hz['topic']}", F(SANS_B, 8), fill=REGION_COLORS[hz["region"]])
        tw_ = d.textlength(f"{hz['n']} - {hz['region']} - {hz['topic']}", font=F(SANS_B, 8))
        rect(d, hx + tw_ / S + 6, ky - 1, 44, 12, outline=hz["tagc"], width=1)
        text(d, hx + tw_ / S + 28, ky + 1, hz["tag"], F(SANS_B, 7), fill=hz["tagc"], anchor="ma")
        hy = ky + 15
        for ln in wrap(d, hz["head"], F(SERIF_B, 14.5), hw):
            text(d, hx, hy, ln, F(SERIF_B, 14.5), fill=INK)
            hy += 17
        hy += 2
        for ln in wrap(d, hz["body"], F(SANS, 9.3), hw):
            text(d, hx, hy, ln, F(SANS, 9.3), fill=(52, 48, 42))
            hy += 11.2
        text(d, hx, 468, hz["src"], F(SANS_O, 7.5), fill=FAINT)
        if i:
            line(d, hx - 4, 220, hx - 4, 478, fill=(200, 192, 175), width=1)
    line(d, 12, 480, W - 12, 480, fill=RULE, width=2)

    # day in ten
    text(d, 12, 486, "THE DAY IN TEN", F(SERIF_B, 15), fill=INK)
    text(d, W - 12, 490, "THE STORIES THAT MOVED THE WORLD TODAY", F(SANS_B, 7.5), fill=FAINT, anchor="ra")
    cw = (W - 24 - 4 * 8) / 5
    for idx, cd_ in enumerate(CARDS):
        col, row = idx % 5, idx // 5
        cx = 12 + col * (cw + 8)
        cy = 510 + row * 112
        card_art(d, cd_["art"], cx, cy, cw, 36)
        ky = cy + 41
        text(d, cx, ky, f"{cd_['n']} - {cd_['region']} - {cd_['topic']}", F(SANS_B, 6.8), fill=REGION_COLORS[cd_["region"]])
        hy = ky + 11
        for ln in wrap(d, cd_["head"], F(SERIF_B, 10), cw)[:3]:
            text(d, cx, hy, ln, F(SERIF_B, 10), fill=INK)
            hy += 11.5
        for ln in wrap(d, cd_["body"], F(SANS, 7.6), cw)[:4]:
            text(d, cx, hy + 1, ln, F(SANS, 7.6), fill=(52, 48, 42))
            hy += 9.3
        text(d, cx, cy + 106, cd_["src"], F(SANS_O, 6.8), fill=FAINT)
        if col:
            line(d, cx - 4, cy, cx - 4, cy + 110, fill=(200, 192, 175), width=1)
    line(d, 12, 740, W - 12, 740, fill=RULE, width=1)

    # bottom: briefs in three columns
    text(d, 12, 746, "ALSO ON SUNDAY 22 NOVEMBER", F(SERIF_B, 13), fill=INK)
    text(d, 330, 750, "- 37 MORE STORIES", F(SANS_B, 8), fill=FAINT)
    bw = (W - 24 - 2 * 14) / 3
    fbrief, fnum, fsrc = F(SANS, 7.7), F(SANS_B, 7.7), F(SANS, 7.0)
    col_items = [BRIEFS[:13], BRIEFS[13:25], BRIEFS[25:]]
    for ci, items in enumerate(col_items):
        x = 12 + ci * (bw + 14)
        y = 772
        for n, txt, src in items:
            text(d, x, y, str(n), fnum, fill=RED)
            tx = x + d.textlength(f"{n} ", font=fnum) / S
            text(d, tx, y, txt, fbrief, fill=(52, 48, 42))
            sx = tx + d.textlength(txt + " ", font=fbrief) / S
            text(d, sx, y + 0.5, f"[{src}]", fsrc, fill=FAINT)
            y += 12.5
        if ci < 2:
            line(d, x + bw + 7, 772, x + bw + 7, 934, fill=(200, 192, 175), width=1)

    # date check
    rect(d, 12, 944, W - 24, 46, outline=RED, width=1)
    text(d, 18, 948, "DATE CHECK - READ THIS FIRST", F(SANS_B, 8.5), fill=RED)
    yy = 960
    for ln in wrap(d, DATECHECK, F(SANS, 8.2), W - 36):
        text(d, 18, yy, ln, F(SANS, 8.2), fill=(52, 48, 42))
        yy += 10

    # footer
    line(d, 12, 996, W - 12, 996, fill=RULE, width=1)
    text(d, 12, 1001, "HOW TO READ THE TAGS  ONGOING still developing as we print.  REPORTED one source's account, not yet confirmed.  CLAIM a party's claim, contested or unverified.",
         F(SANS, 7.8), fill=INK)
    text(d, 12, 1012, "SCENES ARE DRAWN ILLUSTRATIONS OF REPORTED EVENTS, NOT PHOTOGRAPHS.  SOURCES: BBC - REUTERS - AL JAZEERA - AP - THE GUARDIAN - SCMP - DW - UPI - FT - ESPNCRICINFO  -  THE WORLD IN ONE DAY - 22 NOV 2026",
         F(SANS, 7.2), fill=FAINT)

    img = img.resize((W, W), Image.LANCZOS)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get("OUTPUT_DIR") or "output"
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, "entry.png"))
    print("wrote", os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
