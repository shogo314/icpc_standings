from pathlib import Path
from bs4 import BeautifulSoup
import json
from string import ascii_uppercase


def main():
    IN = Path().joinpath("html", "ICPC 2025 Asia Taichung Regional.html")
    OUT = Path().joinpath("json", "standings_2025_taichung.json")
    with IN.open("r") as f:
        text = f.read()
    soup = BeautifulSoup(text, "html.parser")
    table = (
        soup.find("body")
        .find("div", class_="container-fluid")
        .find("div", class_="row")
        .find("div", class_="col-12")
        .find("table")
    )
    TaskInfo = list(ascii_uppercase[: len(table.find_all("col", class_="scoreprob"))])
    ContestData = {
        "UnitTime": "minute",
        "Penalty": 20,
        "Duration": 300,
        "TaskInfo": TaskInfo,
    }
    StandingsData = []
    for row in table.find("tbody").find_all("tr"):
        cols = row.find_all("td")
        data = {}
        Rank = int(cols[1].get_text(strip=True))
        try:
            Score = int(cols[5].get_text(strip=True))
        except:
            break
        Penalty = int(cols[6].get_text(strip=True))
        data["Rank"] = Rank
        data["TotalResult"] = {
            "Score": Score,
            "Penalty": Penalty,
        }
        a = cols[4].find("a")
        data["TeamName"] = a.find("span", class_="forceWidth").get_text(strip=True)
        data["University"] = a.find("span", class_="univ forceWidth").get_text(
            strip=True
        )
        TaskResults = {}
        Score_ = 0
        Penalty_ = 0
        for n, problem in zip(TaskInfo, cols[7:], strict=True):
            if problem.find_all("div", class_="score_correct"):
                tm, wa = (
                    problem.find("div", class_="score_correct")
                    .get_text(strip=True, separator="<span>")
                    .split("<span>")
                )
                tm = int(tm)
                wa = int(wa.split()[0]) - 1
                TaskResults[n] = {
                    "Elapsed": tm,
                    "Score": 1,
                    "Penalty": wa,
                }
                assert 0 <= tm <= ContestData["Duration"]
                Score_ += 1
                Penalty_ += tm + wa * ContestData["Penalty"]
            elif problem.find_all("div", class_="score_incorrect"):
                wa = int(
                    problem.find("div", class_="score_incorrect")
                    .get_text(strip=True)
                    .split()[0]
                )
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
