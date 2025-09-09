from pathlib import Path
from bs4 import BeautifulSoup
import json


def main():
    IN = Path().joinpath("html", "ICPC 2025 World Finals.html")
    OUT = Path().joinpath("json", "standings_2025_world_finals.json")
    with IN.open("r") as f:
        text = f.read()
    soup = BeautifulSoup(text, "html.parser")
    table = soup.find("body").find("table").find("tbody")
    TaskInfo = []
    for i in table.find("tr").find_all("th")[4:-1]:
        TaskInfo.append(i.get_text(strip=True))
    ContestData = {
        "UnitTime": "minute",
        "Penalty": 20,
        "Duration": 300,
        "TaskInfo": TaskInfo,
    }
    StandingsData = []
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if not cols:
            continue
        if not cols[0].get_text(strip=True):
            continue
        data = {}
        data["Rank"] = int(cols[0].get_text(strip=True))
        data["University"] = " ".join(cols[1].get_text(strip=True).split()[1:])
        Score = int(cols[2].get_text(strip=True))
        Penalty = int(cols[3].get_text(strip=True))
        data["TotalResult"] = {
            "Score": Score,
            "Penalty": Penalty,
        }
        TaskResults = {}
        Score_ = 0
        Penalty_ = 0
        for p, d in zip(TaskInfo, cols[4:-1]):
            if "yes" in d["class"] or "firstYes" in d["class"]:
                wa, tm = map(int, d.get_text(strip=True).split("/"))
                wa -= 1
                TaskResults[p] = {
                    "Elapsed": tm,
                    "Score": 1,
                    "Penalty": wa,
                }
                Score_ += 1
                Penalty_ += tm + wa * ContestData["Penalty"]
            elif "no" in d["class"]:
                wa = int(d.get_text(strip=True).split("/")[0])
                TaskResults[p] = {
                    "Elapsed": tm,
                    "Score": 1,
                    "Penalty": wa,
                }
            else:
                assert d.get_text(strip=True) == "0/--"
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
