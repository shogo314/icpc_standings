from pathlib import Path
from bs4 import BeautifulSoup
from itertools import batched
import json
from string import ascii_uppercase


def main():
    IN = Path().joinpath("html", "ICPC 2025 Asia Bangkok Regional.html")
    OUT = Path().joinpath("json", "standings_2025_bangkok.json")
    with IN.open("r") as f:
        text = f.read()
    soup = BeautifulSoup(text, "html.parser")
    table = (
        soup.find("body", class_="static")
        .find("div", class_="container-fluid")
        .find("div", class_="row")
        .find("div", class_="col-12")
    )
    TaskInfo = list(ascii_uppercase[:14])
    ContestData = {
        "UnitTime": "minute",
        "Penalty": 20,
        "Duration": 300,
        "TaskInfo": TaskInfo,
    }
    StandingsData = []
    pre_rank = -1
    for tr in table.find_all("tr"):
        if tr.find_all("td", class_="scoresummary"):
            break
        if tr["class"] == ["scoreheader"]:
            continue
        data = {}
        rank = tr.find("td", class_="scorepl rank").get_text(strip=True)
        try:
            data["Rank"] = int(rank)
            pre_rank = int(rank) + 1
        except:
            data["Rank"] = pre_rank
        Score = int(tr.find("td", class_="scorenc").get_text(strip=True))
        Penalty = int(tr.find("td", class_="scorett").get_text(strip=True))
        data["TotalResult"] = {
            "Score": Score,
            "Penalty": Penalty,
        }
        x = tr.find("td", class_="scoretn cl_FFFFFF").find_all("span")
        data["TeamName"] = x[0].get_text(strip=True)
        data["University"] = x[1].get_text(strip=True)
        TaskResults = {}
        Score_ = 0
        Penalty_ = 0
        for n, problem in zip(TaskInfo, tr.find_all("td")[7:], strict=True):
            if not problem.find_all("a"):
                continue
            assert problem.find("a")["data-problem-id"].startswith(n)
            # print(n, problem)
            tmp = problem.get_text("<span>", strip=True).split("<span>")
            assert len(tmp) in [1, 2]
            if len(tmp) == 2:
                tm = int(tmp[0])
                wa = int(tmp[1].split()[0]) - 1
                TaskResults[n] = {
                    "Elapsed": tm,
                    "Score": 1,
                    "Penalty": wa,
                }
                assert 0 <= tm <= ContestData["Duration"]
                Score_ += 1
                Penalty_ += tm + wa * ContestData["Penalty"]
            else:
                wa = int(tmp[0].split()[0])
                TaskResults[n] = {
                    "Elapsed": 0,
                    "Score": 1,
                    "Penalty": wa,
                }
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
