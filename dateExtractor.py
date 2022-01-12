import re
import string

# Predefined strings.
numbers = "(^a(?=\s)|eins|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|elf|zwölf|dreizehn|vierzehn|fünfzehn|sechzehn|siebzehn|achtzehn|neunzehn|zwanzig|dreißig|vierzig|fünfzig|sechzig|siebzig|ahtsig|neunzig|hundert|tausend)"
day = "(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag|Sonnabend)"
week_day = "(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)"
month = "(januar|februar|märz|marz|april|mai|juni|juli|august|september|oktober|november|dezember)"
dmy = "(Jahr|Tag|woche|wochenende|Monat)"
rel_day = "(heute|gestern|Morgen|heute Abend|Tonit)"
exp1 = "(Vor|nach|früher|später|vor)"
exp2 = "(Dies|nächste|letzte)"
iso = "\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+"
year = "((?<=\s)\d{4}|^\d{4})"
regxp1 = "((\d+|(" + numbers + "[-\s]?)+) " + dmy + "s? " + exp1 + ")"
regxp2 = "(" + exp2 + " (" + dmy + "|" + week_day + "|" + month + "))"

date = "([012]?[0-9]|3[01])"
regxp3 = "(" + date + " " + month + " " + year + ")"
regxp4 = "(" + month + " " + date + "[th|st|rd]?[,]? " + year + ")"

reg1 = re.compile(regxp1, re.IGNORECASE)
reg2 = re.compile(regxp2, re.IGNORECASE)
reg3 = re.compile(rel_day, re.IGNORECASE)
reg4 = re.compile(iso)
reg5 = re.compile(year)
reg6 = re.compile(regxp3, re.IGNORECASE)
reg7 = re.compile(regxp4, re.IGNORECASE)

def extractDate(text):

    # Initialization
    timex_found = []

    # re.findall() finds all the substring matches, keep only the full
    # matching string. Captures expressions such as 'number of days' ago, etc.
    found = reg1.findall(text)
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # Variations of this thursday, next year, etc
    found = reg2.findall(text)
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # today, tomorrow, etc
    found = reg3.findall(text)
    for timex in found:
        timex_found.append(timex)

    # ISO
    found = reg4.findall(text)
    for timex in found:
        timex_found.append(timex)

    # Dates
    found = reg6.findall(text)
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    found = reg7.findall(text)
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # Year
    found = reg5.findall(text)
    for timex in found:
        timex_found.append(timex)
    # Tag only temporal expressions which haven't been tagged.
    #for timex in timex_found:
    #    text = re.sub(timex + '(?!</TIMEX2>)', '<TIMEX2>' + timex + '</TIMEX2>', text)

    return timex_found