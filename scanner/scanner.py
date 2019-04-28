#!/usr/bin/env python3.7

from functools import reduce
import fitz
import json
import os

pdfs = "./pdfs/"

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
    def __init__(self, data):
        self.number = self.__get_number(data)

    def __get_number(self, data):
        return data[0].split(" ")[1].split("-")[0]

    def __str__(self):
        return self.number



for path in os.listdir(pdfs):
    file = fitz.open(pdfs + path)
    for i in range(0, file.pageCount):
        page = file.loadPage(i).getText("dict")
        for raw in Extractor(page).extract():
            incident = Incident(raw)
            print(incident.number)
