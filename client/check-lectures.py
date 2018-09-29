"""
MIT License

Copyright (c) 2018 https://github.com/pragma-once

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import os
import requests


current_version = "0.4"


class Lecture:
    def __init__(self, name: str, last_submitted_date: datetime.datetime, period: datetime.timedelta):
        self.name = name
        self.last_submitted_date = last_submitted_date
        self.period = period
        self.next_date = self.last_submitted_date \
                         + (int((datetime.datetime.now() - self.last_submitted_date) / self.period) * self.period) \
                         + self.period
        if datetime.datetime.now() < self.last_submitted_date:
            self.next_date -= self.period

    def __lt__(self, other):
        return self.next_date < other.next_date


latest_version = current_version
latest_version_link = ""
info_source = "https://kharazmi-lectures-checker.github.io/info/0_2.html"
lecture_filter = []
offline_mode = False
show_lecture_duplicates = False

print("Kharazmi University Lectures Date Checker v" + current_version)

try:
    file = open("check-lectures-files/config.txt", 'r')
    for line in file.readlines():
        try:
            if line[0] == "#":
                continue
            exp = line.split('=')
            if len(exp) != 2:
                continue
            if exp[0].lower() == "info":
                info_source = exp[1]
            if exp[0].lower() == "filter":
                lecture_filter = exp[1].split(';')
            if exp[0].lower() == "offline":
                if exp[1].__contains__('1'):
                    print(exp[1])
                    offline_mode = True
            if exp[0].lower() == "duplicates":
                if exp[1].__contains__('1'):
                    print(exp[1])
                    show_lecture_duplicates = True
        except:
            pass
    file.close()
except FileNotFoundError:
    print()
    print("No config file found. Creating one...")
    if not os.path.exists("check-lectures-files"):
        os.makedirs("check-lectures-files")
    file = open("check-lectures-files/config.txt", 'w+')
    file.write(
        "# This config file is auto-generated.\n"
        "\n"
        "# Each line that STARTS in its first letter with # is a comment.\n"
        "\n"
        "# The following line will define a custom source to check the updates and info:\n"
        "#info=https://example.com/info.html\n"
        "\n"
        "# The following line will only allow the app to show a limited set of lectures:\n"
        "#filter=Computer Networks;Formal Methods in Software Engineering;Software Engineering;Software Testing;\n"
        "\n"
        "# The following line will toggle offline mode, that the app will only read the offline info file:\n"
        "#offline=1\n"
        "\n"
        "# The following line will allow lecture duplicates"
        " (not to show only the lecture presented in the nearest future with the same name)\n"
        "#duplicates=1\n"
    )
    file.close()

while 1:
    print()

    info = None
    if not offline_mode:
        print("Getting online info...")
        try:
            info = requests.get(info_source).text
            offline_info = ""
            try:
                file = open("check-lectures-files/info.txt", 'r')
                offline_info = file.read()
                file.close()
            except FileNotFoundError:
                print("Creating an offline copy...")
                if not os.path.exists("check-lectures-files"):
                    os.makedirs("check-lectures-files")
            if info != offline_info:
                print("Writing an offline copy...")
                file = open("check-lectures-files/info.txt", 'w+')
                file.write(info)
                file.close()
        except:
            print("Couldn't get the info online.")
    if info is None:
        print("Getting offline info...")
        try:
            file = open("check-lectures-files/info.txt", 'r')
            info = file.read()
            file.close()
        except FileNotFoundError:
            print("check-lectures-files/info.txt does not exist. No info has been loaded.")
            info = ""

    info = info.split(';')

    lecture_name = "N/A"
    last_submitted_date = None
    period = None
    lectures = []


    def clear_info():
        global lecture_name
        global last_submitted_date
        global period
        lecture_name = "N/A"
        last_submitted_date = None
        period = None


    def add_info():
        if not (last_submitted_date is None or period is None):
            lectures.append(Lecture(lecture_name, last_submitted_date, period))
            clear_info()


    for block in info:
        exp = block.split('=')
        if len(exp) != 2:
            continue
        if exp[0] == "lecture" or exp[0] == "lecture_name":
            clear_info()
            lecture_name = exp[1]
        if exp[0] == "last_submitted_date":
            try:
                last_submitted_date = datetime.datetime(year=int(exp[1][0:4]),
                                                        month=int(exp[1][5:7]),
                                                        day=int(exp[1][8:10]),
                                                        hour=12)

                last_submitted_date = datetime.datetime(year=int(exp[1][0:4]),
                                                        month=int(exp[1][5:7]),
                                                        day=int(exp[1][8:10]),
                                                        hour=int(exp[1][11:13]))

                last_submitted_date = datetime.datetime(year=int(exp[1][0:4]),
                                                        month=int(exp[1][5:7]),
                                                        day=int(exp[1][8:10]),
                                                        hour=int(exp[1][11:13]),
                                                        minute=int(exp[1][14:16]))
            except:
                pass
            add_info()
        elif exp[0] == "period":
            try:
                period = datetime.timedelta(days=int(exp[1]))
            except:
                pass
            add_info()
        elif exp[0] == "latest_version":
            latest_version = exp[1]
        elif exp[0] == "latest_version_link" or exp[0] == "latest_version_url" or exp[0] == "latest_version_download":
            latest_version_link = exp[1]

    lectures.sort()
    showed_lectures = []
    now = datetime.datetime.now()
    now_rounded = datetime.datetime(year=now.year, month=now.month, day=now.day)
    print()
    for lecture in lectures:
        if len(lecture_filter) > 0:
            if not lecture_filter.__contains__(lecture.name):
                continue

        if not show_lecture_duplicates:
            should_continue = False
            for showed_lecture in showed_lectures:
                if showed_lecture.name == lecture.name:
                    should_continue = True
                    break
            if should_continue:
                continue
            showed_lectures.append(lecture)

        next_date_rounded = datetime.datetime(year=lecture.next_date.year,
                                              month=lecture.next_date.month,
                                              day=lecture.next_date.day)
        if next_date_rounded - now_rounded < datetime.timedelta(days=0):
            relative_date = "This is IMPOSSIBLE! This is a bug! The 'next date' cannot be before now."
        elif next_date_rounded - now_rounded <= datetime.timedelta(days=0):
            relative_date = "Today"
        elif next_date_rounded - now_rounded <= datetime.timedelta(days=1):
            relative_date = "Tomorrow"
        else:
            weeks = int((next_date_rounded - now_rounded).days / 7)
            if (next_date_rounded.weekday() + 2) % 7 < (now_rounded.weekday() + 2) % 7:
                weeks += 1
            if weeks == 0:
                relative_date = "This week"
            elif weeks == 1:
                if now_rounded.weekday() == 4:
                    relative_date = "Coming week"
                else:
                    relative_date = "Next week"
            else:
                relative_date = str(weeks) + " weeks later"

        if lecture.next_date.weekday() == 5: weekday = "Sat"
        elif lecture.next_date.weekday() == 6: weekday = "Sun"
        elif lecture.next_date.weekday() == 0: weekday = "Mon"
        elif lecture.next_date.weekday() == 1: weekday = "Tue"
        elif lecture.next_date.weekday() == 2: weekday = "Wed"
        elif lecture.next_date.weekday() == 3: weekday = "Thu"
        elif lecture.next_date.weekday() == 4: weekday = "Fri"
        else: weekday = "Cool! That's a bug that seems impossible!"

        print("Next " + lecture.name + " lecture will be at: " + weekday + " " + str(lecture.next_date)
              + " (" + relative_date + ")")
    print()

    if current_version != latest_version:
        print()
        print("Current version: " + current_version)
        print("Latest version: " + latest_version)
        print("You can download the latest version from: " + latest_version_link)
        print("Do you want to update to the latest version? (y/*)")
        if input() == "y":
            try:
                open(__file__, 'wb').write(requests.get(latest_version_link).content)
                print("Updated! Please restart the script.")
            except:
                print("Could not get the update.")

    print("Enter r to retry and anything to exit:")

    if input() != 'r':
        break
