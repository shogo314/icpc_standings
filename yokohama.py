from pathlib import Path
from bs4 import BeautifulSoup
import json


def main():
    IN = Path().joinpath("html", "ICPC 2025 国内予選.html")
    OUT = Path().joinpath("standings_2025_domestic.json")
    with IN.open("r") as f:
        text = f.read()
    soup = BeautifulSoup(text, "html.parser")
    standard_standings = (
        soup.find("body")
        .find("div", id="root")
        .find("div")
        .find("div", class_="container", style="position: relative;")
        .find("div", class_="standard-standings")
    )
    standings = standard_standings.find_all("div", class_="standings-section")
    assert len(standings) == 4
    TaskInfo = []
    for problem in (
        standings[0]
        .find("div", class_="team-row")
        .find("div", class_="team-problems")
        .find_all("div", class_="team-problem")
    ):
        TaskInfo.append(problem.get_text(strip=True))
    ContestData = {
        "UnitTime": "second",
        "Penalty": 1200,
        "Duration": 18000,
        "TaskInfo": TaskInfo,
    }
    ContestData = {
        "UnitTime": "minute",
        "Penalty": 20,
        "Duration": 300,
        "TaskInfo": TaskInfo,
    }
    standing = standings[2].find("div")
    StandingsData = []
    for row in standing.find_all("div", class_="team-row"):
        data = {}
        rank = int(row.find("div", class_="team-rank").get_text(strip=True))
        data["Rank"] = rank
        right = row.find("div", class_="team-right")
        score = list(right.find("div", class_="team-score").find("div", class_="team-colored-col-fg").stripped_strings)
        assert score[1].startswith("(") and score[1].endswith(")")
        Score = int(score[0])
        Penalty = int(score[1][1:-1])
        data["TotalResult"] = {
            "Score": Score,
            "Penalty": Penalty,
        }
        name = list(right.find("div", class_="team-name").stripped_strings)
        data["TeamName"] = name[0]
        data["University"] = name[1]
        problems = right.find("div", class_="team-problems")
        TaskResults = {}
        Score_ = 0
        Penalty_ = 0
        for n, problem in zip(TaskInfo, problems.find_all("div", class_="team-col team-problem"), strict=True):
            # print(problem)
            bg = problem.find("div", class_="team-colored-col-bg").get("class", [])[1]
            assert bg.startswith("bg-")
            if bg == "bg-solved":
                tm, wa = list(problem.find("div", class_="team-colored-col-fg").stripped_strings)
                tm = tm.split(":")
                assert len(tm) == 2
                tm = int(tm[0]) * 60 + int(tm[1])
                if wa == "-":
                    wa = 0
                else:
                    assert wa.startswith("(+") and wa.endswith(")")
                    wa = int(wa[2:-1])
                TaskResults[n] = {
                    "Elapsed": tm,
                    "Score": 1,
                    "Penalty": wa,
                }
                assert 0 <= tm <= ContestData["Duration"]
                Score_ += 1
                Penalty_ += tm + wa * ContestData["Penalty"]
            elif bg == "bg-rejected":
                tm, wa = list(problem.find("div", class_="team-colored-col-fg").stripped_strings)
                assert wa.startswith("(+") and wa.endswith(")")
                wa = int(wa[2:-1])
                TaskResults[n] = {
                    "Elapsed": 0,
                    "Score": 0,
                    "Penalty": wa,
                }
            elif bg == "bg-unattempted":
                pass
            else:
                assert False, f"unknown status {bg}"
        data["TaskResults"] = TaskResults
        StandingsData.append(data)
        assert Penalty == Penalty_
        assert Score == Score_
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
