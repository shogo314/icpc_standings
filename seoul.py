from pathlib import Path
from bs4 import BeautifulSoup
import json
import re
from string import ascii_uppercase


def main():
    IN = Path().joinpath("html", "2025 ICPC Asia Seoul Regional.html")
    OUT = Path().joinpath("json", "standings_2025_seoul.json")
    with IN.open("r") as f:
        text = f.read()
    soup = BeautifulSoup(text, "html.parser")
    standings = (
        soup.find("body")
        .find("div", id="wrapper")
        .find("div", id="body")
        .find("div", id="team-list")
    )
    TaskInfo = list(ascii_uppercase[:13])
    ContestData = {
        "UnitTime": "minute",
        "Penalty": 20,
        "Duration": 300,
        "TaskInfo": TaskInfo,
    }
    StandingsData = []
    for team in standings.find_all("div", id=re.compile(r"^team-")):
        data = {}
        Score = int(team.find("span", class_="solved-count").get_text(strip=True))
        Rank = int(team.find("span", class_="team-rank").get_text(strip=True))
        Penalty = int(team.find("span", class_="team-penalty").get_text(strip=True))
        TeamName = team.find("span", class_="team-name").get_text(strip=True)
        University = team.find("span", class_="team-represents").get_text(strip=True)
        data["Rank"] = Rank
        data["TotalResult"] = {
            "Score": Score,
            "Penalty": Penalty,
        }
        data["TeamName"] = TeamName
        data["University"] = University
        TaskResults = {}
        Score_ = 0
        Penalty_ = 0
        for n, problem in zip(
            TaskInfo,
            team.find("div", class_="results").find_all(
                "span", class_="problem-result"
            ),
            strict=True,
        ):
            if "solved" in problem["class"]:
                wa = int("0" + problem.get_text(strip=True)[1:])
                m = re.fullmatch(r"Solved at (\d+) min\.", problem["data-balloon"])
                assert m
                tm = int(m.group(1))
                TaskResults[n] = {
                    "Elapsed": tm,
                    "Score": 1,
                    "Penalty": wa,
                }
                assert 0 <= tm <= ContestData["Duration"]
                Score_ += 1
                Penalty_ += tm + wa * ContestData["Penalty"]
            elif "failed" in problem["class"]:
                wa = int(problem.get_text(strip=True)[1:])
                TaskResults[n] = {
                    "Elapsed": 0,
                    "Score": 0,
                    "Penalty": wa,
                }
            else:
                pass
        assert Penalty == Penalty_
        assert Score == Score_
        data["TaskResults"] = TaskResults
        StandingsData.append(data)
    with OUT.open("w") as f:
        print(
            json.dumps(
                {
                    "ContestData": ContestData,
                    "StandingsData": StandingsData,
                },
                indent=4,
                ensure_ascii=False,
            ),
            file=f,
        )


if __name__ == "__main__":
    main()
