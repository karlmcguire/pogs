#!/usr/bin/env python3.7

from functools import reduce
import fitz
import json
import os

class Extractor:
    def __init__(self, file):
        self.file = file

    def __get(self, i, j):
        return self.file["blocks"][i]["lines"][j]["spans"][0]["text"]

    def __rap(self, i, j):
        return reduce(lambda x, y: x + y["spans"][0]["text"],
                      self.file["blocks"][i]["lines"][j:], "")

    def positions(self):
        p = []
        for i in range(0, len(self.file["blocks"]) - 11):
            if self.__get(i, 0).strip().find("2019-") == -1:
                continue
            p.append(i)
        return p

    def rows(self, positions):
        r = []
        for i, j in enumerate(positions):
            text = self.__rap(j, 0)
            more = ""
            if i == len(positions) - 1:
                for k in range(j + 1, j + 1 + 3):
                    more += self.__rap(k, 0)
            else:
                for k in range(j + 1, positions[i + 1]):
                    more += self.__rap(k, 0)
            r.append(text + more)
        return r

    def filtered(self, rows):
        f = []
        for row in rows:
            cols = row.split("  ")
            last = len(cols)
            # find the last segment of the incident (description)
            for i, col in enumerate(cols):
                if col.find("DESCRIPTION") != -1:
                    last = i + 1
                    break
            # ignore empty log rows
            if cols[:last][last - 1].find("time period") != -1:
                continue
            f.append(cols[:last])
        return f

    def extract(self):
        return self.filtered(self.rows(self.positions()))

class Incident:
    locations = {
        "atkins",
        "bioinformatics",
        "epic",
        "belk",
        "parking",
        "lot",
        "union",
        "levin",
        "levine",
        "hall",
        "richardson",
        "cameron",
        "student",
        "light",
        "sanford",
        "fretwell",
        "colvard",
        "alumni",
        "lex",
        "lynch",
        "mcenery",
        "mceniry",
        "belk",
        "cri",
        "south",
        "niner",
        "east",
        "van",
        "greek",
        "cone",
        "broadrick/mary",
        "king",
        "foundation",
        "west",
        "early",
        "pps",
        "chhs",
        "woodward",
        "miltimore",
        "phillips",
        "holshouser",
        "pps-walk-in/lynch",
        "nrfc",
        "poplar",
        "mary",
        "hawthorne",
        "north",
        "police",
        "facilities",
        "duke",
        "coe",
        "college",
        "e.",
        "akins",
        "agency",
        "rowe",
        "hawthorn",
        "wallis"
    }

    def __init__(self, data):
        self.number,      rest = self.__get_number(data)
        self.type,        rest = self.__get_type(rest)
        self.location,    rest = self.__get_location(rest)
        self.reported,    rest = self.__get_reported(rest)
        self.secured,     rest = self.__get_secured(rest)
        self.occurred,    rest = self.__get_occurred(rest)
        self.disposition, rest = self.__get_disposition(rest)
        self.description, rest = self.__get_description(rest)

    def __get_number(self, data):
        return (data[1].split("-")[0], 
                data[1:])

    def __get_type(self, data):
        def parse(left, line, i):
            # some types are appended to the report number
            if i == 0:
                left = line[0].split("-")[1]
                left = left[1:] + " " if len(left) > 3 else ""
                line = line[1:]
            # go until we run into the location column
            if i == 12 or line[0].lower() in self.locations: 
                return (left.strip(), line)
            left += line[0] + " "
            line = line[1:]
            return parse(left, line, i + 1)
        return parse("", data, 0)

    def __get_location(self, data):
        def is_date(word):
            return len(word.split("/")) >= 3
        def parse(left, line, i):
            # go until we run into the date reported column
            if i == 10 or is_date(line[0].lower()):
                return (left.strip(), line)
            left += line[0] + " "
            line = line[1:]
            return parse(left, line, i + 1)
        return parse("", data, 0)

    def __get_reported(self, data):
        def parse(left, line, i):
            # 04/22/2019 04/22/2019 at 04:03
            if len(line[0].split("/")) == 3:
                if len(line[1].split("/")) == 3:
                    left += line[0] + " "
                    line = line[1:]
                    return (left.strip(), line)
            # 03/08/2019 06:30 and
            # 04/23/2019 at 11:39
            if len(line[0].split(":")) == 2:
                left += line[0] + " "
                line = line[1:]
                return (left.strip(), line)
            # at most (date) at (time)
            if i == 3:
                return (left.strip(), line)
            left += line[0] + " "
            line = line[1:]
            return parse(left, line, i + 1)
        return parse("", data, 0)

    def __get_secured(self, data):
        def parse(left, line, i):
            # some have the word "at" and some don't (wack)
            if len(line[0].split(":")) == 2:
                left += line[0] + " "
                line = line[1:]
                return (left.strip(), line)
            # go until occurred statement
            if i == 3 or line[0].find("Occurred") != -1:
                return (left.strip(), line)
            left += line[0] + " "
            line = line[1:]
            return parse(left, line, i + 1)
        return parse("", data, 0)

    def __get_occurred(self, data):
        def parse(left, line, i):
            # go until the disposition
            if i == 10 or (line[0].split("/")[0] == "Open" or
                           line[0].split("/")[0] == "Closed"):
                return (left.strip(), line)
            left += line[0] + " "
            line = line[1:]
            return parse(left, line, i + 1)
        return parse("", data, 0)

    def __get_disposition(self, data):
        def parse(left, line, i):
            # go until INCIDENT DESCRIPTION (next line)
            if i == 5 or line[0] == "INCIDENT":
                return (left.strip(), line)
            left += line[0] + " "
            line = line[1:]
            return parse(left, line, i + 1)
        return parse("", data, 0)

    def __get_description(self, data):
        def parse(left, line, i):
            # we read the entire description
            if len(line) == 0:
                return (left.strip(), line)
            # ignore the INCIDENT DESCRIPTION words
            if line[0] == "INCIDENT":
                line = line[2:]
            left += line[0] + " "
            line = line[1:]
            return parse(left, line, i + 1)
        return parse("", data, 0)


pref = "./pdfs/"

# iterate through every pdf and extract the incidents
for path in os.listdir(pref):
    file = fitz.open(pref + path)
    for i in range(0, file.pageCount):
        page = file.loadPage(i).getText("dict")
        for raw in Extractor(page).extract():
            incident = Incident((" ").join(raw).split(" "))
            print(path, incident.type)
