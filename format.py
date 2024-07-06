import sys


def bracket_analysis(s: str) -> list[str]:
    ret = []
    t = ""
    for c in s:
        if c == "<":
            if t:
                ret.append(t.strip())
            t = "<"
        elif c == ">":
            t += ">"
            ret.append(t.strip())
            t = ""
        else:
            t += c
    return ret


def depth_analysis(l: list[str]) -> list[tuple[int, str]]:
    ret: list[tuple[int, str]] = []
    k = 0
    for s in l:
        if s.startswith("</div"):
            k -= 1
        elif s.startswith("<div"):
            ret.append((k, s))
            k += 1
        else:
            ret.append((k, s))
    return ret


def to_dict(f: list[tuple[int, str]]) -> dict:
    assert f[0] == (0, '<div class="standard-standings">')
    assert f[1] == (1, '<div class="standings-section">')
    assert f[2] == (2, '<div class="team-row legend">')
    assert f[3] == (3, '<div class="team-col team-mark">')
    assert f[4] == (3, '<div class="team-col team-rank">')
    assert f[5] == (4, "#")
    assert f[6] == (3, '<div class="team-col team-score">')
    assert f[7] == (4, "Solved")
    assert f[8] == (3, '<div class="team-col team-name">')
    assert f[9] == (4, "Team/University")
    assert f[10] == (3, '<div class="team-problems">')
    k = 11
    # problems
    problem_list = []
    while True:
        if f[k] != (4, '<div class="team-col team-problem">'):
            break
        assert f[k] == (4, '<div class="team-col team-problem">')
        k += 3
        assert f[k][0] == 6 and not f[k][1].startswith("<")
        problem_list.append(f[k][1])
        k += 1
        assert f[k] == (6, "</span>")
        k += 1
        assert f[k] == (6, '<span class="team-problem-flag">')
        k += 2
        assert f[k] == (6, "</i>")
        k += 1
        assert f[k] == (6, "</span>")
        k += 1
    assert f[k] == (1, '<div class="standings-section">')
    k += 1
    assert f[k] == (1, '<div class="standings-section">')
    k += 1
    assert f[k] == (2, "<div>")
    k += 1
    StandingsData = []
    rank_flag = True
    rank_cnt = 1
    while True:
        if k >= len(f):
            break
        d = {}
        assert f[k][0] == 3 and f[k][1].startswith("<div data-key=")
        k += 1
        assert f[k][0] == 4 and f[k][1].startswith('<div class="team-row  "')
        k += 1
        assert f[k] == (5, '<div class="team-left">')
        k += 5
        assert f[k] == (5, '<div class="team-col team-rank">')
        k += 2
        if f[k][1] == "-":
            rank_flag = False
            d["Rank"] = rank_cnt
        else:
            assert rank_flag
            d["Rank"] = int(f[k][1])
            rank_cnt += 1
        k += 5
        assert f[k] == (5, '<div class="team-right">')
        k += 1
        assert f[k] == (6, '<div class="team-col team-score">')
        k += 2
        assert f[k] == (7, '<div class="team-colored-col-fg">')
        k += 1
        TotalResult = {}
        TotalResult["Score"] = int(f[k][1])
        k += 3
        assert f[k][0] == 8 and f[k][1].startswith("(") and f[k][1].endswith(")")
        TotalResult["Penalty"] = int(f[k][1][1:-1])
        d["TotalResult"] = TotalResult
        k += 2
        assert f[k] == (6, '<div class="team-col team-name">')
        k += 2
        d["TeamName"] = f[k][1]
        k += 4
        d["University"] = f[k][1]
        k += 7
        assert f[k] == (6, '<div class="team-problems">')
        k += 1
        TaskResults = {}
        for p in problem_list:
            assert f[k] == (7, '<div class="team-col team-problem">')
            k += 1
            if f[k] == (8, '<div class="team-colored-col-bg bg-solved">') or f[k] == (
                8,
                '<div class="team-colored-col-bg bg-solved-first">',
            ):
                k += 1
                assert f[k] == (8, '<div class="team-colored-col-fg">')
                k += 2
                TaskResults[p] = {}
                tt = list(map(int, f[k][1].split(":")))
                tt.reverse()
                while len(tt) > 1:
                    ttt = tt.pop() * 60
                    tt[-1] += ttt
                TaskResults[p]["Elapsed"] = tt[0]
                TaskResults[p]["Score"] = 1
                k += 3
                if f[k] == (9, "<span>"):
                    k += 1
                    assert f[k][1].startswith("(+") and f[k][1].endswith(")")
                    TaskResults[p]["Penalty"] = int(f[k][1][2:-1])
                    k += 4
                else:
                    TaskResults[p]["Penalty"] = 0
                    k += 3
            elif f[k] == (8, '<div class="team-colored-col-bg bg-rejected">'):
                k += 1
                assert f[k] == (8, '<div class="team-colored-col-fg">')
                k += 2
                TaskResults[p] = {}
                assert f[k] == (9, "-")
                TaskResults[p]["Elapsed"] = 0
                TaskResults[p]["Score"] = 0
                k += 3
                assert f[k][1].startswith("(+") and f[k][1].endswith(")")
                TaskResults[p]["Penalty"] = int(f[k][1][2:-1])
                k += 3
            elif f[k] == (8, '<div class="team-colored-col-bg bg-unattempted">'):
                k += 1
                assert f[k] == (8, '<div class="team-colored-col-fg">')
                k += 2
                assert f[k] == (9, "-")
                k += 5
            else:
                print("err", f[k], file=sys.stderr)
                assert False
        d["TaskResults"] = TaskResults
        StandingsData.append(d)
    # return {
    #     "ContestData": {
    #         "UnitTime": "minute",
    #         "Penalty": 20,
    #         "Duration": 5 * 60,
    #         "TaskInfo": problem_list,
    #     },
    #     "StandingsData": StandingsData,
    # }
    return {
        "ContestData": {
            "UnitTime": "second",
            "Penalty": 20 * 60,
            "Duration": 3 * 60 * 60,
            "TaskInfo": problem_list,
        },
        "StandingsData": StandingsData,
    }


def main():
    html_data = ""
    with open("html/ICPC 2024 国内予選.html", "r") as f:
        html_data = f.read()
    formated = depth_analysis(bracket_analysis(html_data))
    d = to_dict(formated)
    import json

    with open("standings_2024_domestic.json", "w") as f:
        print(json.dumps(d), file=f)


if __name__ == "__main__":
    main()
