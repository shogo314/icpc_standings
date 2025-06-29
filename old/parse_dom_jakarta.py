import sys


def bracket_analysis(s: str) -> list[str]:
    ret = []
    t = ""
    for c in s:
        if c == "<":
            if t.strip():
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
    stk = []
    for s in l:
        for tag in ["tr", "td", "span", "a"]:
            if s.startswith("</" + tag):
                assert tag == stk.pop()
                k -= 1
                ret.append((k, s))
                break
            if s.startswith("<" + tag):
                ret.append((k, s))
                k += 1
                stk.append(tag)
                break
        else:
            ret.append((k, s))
    return ret


def to_dict(f: list[tuple[int, str]]) -> dict:
    # problems
    problem_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
    k = 157
    StandingsData = []
    while True:
        if f[k][1].startswith("<tr style="):
            break
        assert f[k][0] == 0 and f[k][1].startswith("<tr")
        d = {}
        k += 1
        assert f[k][1].startswith('<td class="scorepl')
        k += 1
        try:
            d["Rank"] = int(f[k][1])
            k += 1
        except:
            d["Rank"] = 74
        assert f[k] == (1, "</td>")
        k += 1
        assert f[k] == (1, '<td class="scoreaf">')
        k += 6
        assert f[k] == (1, "</td>")
        k += 1
        assert f[k] == (1, '<td class="scoreaf">')
        k += 4
        assert f[k] == (1, "</td>")
        k += 1
        assert f[k][0] == 1 and f[k][1].startswith('<td')
        k += 1
        assert f[k][0] == 2 and f[k][1].startswith("<a")
        k += 1
        assert f[k] == (3, '<span class="forceWidth">')
        k += 1
        if f[k][1].startswith("<span"):
            k += 3
        d["TeamName"] = f[k][1]
        k += 1
        assert f[k] == (3, "</span>")
        k += 1
        assert f[k][0] == 3 and f[k][1].startswith("<span")
        k += 1
        # if f[k][1].startswith('<span class="badge'):
        #     k += 3
        d["University"] = f[k][1]
        k += 1
        assert f[k] == (3, "</span>")
        k += 3
        assert f[k] == (1, '<td class="scorenc">')
        k += 1
        TotalResult = {}
        TotalResult["Score"] = int(f[k][1])
        k += 1
        assert f[k] == (1, "</td>")
        k += 1
        assert f[k] == (1, '<td class="scorett">')
        k += 1
        TotalResult["Penalty"] = int(f[k][1])
        d["TotalResult"] = TotalResult
        k += 1
        assert f[k] == (1, "</td>")
        k += 1
        TaskResults = {}
        for p in problem_list:
            assert f[k] == (1, '<td class="score_cell">')
            k += 1
            if f[k] == (1, "</td>"):
                k += 1
                continue
            assert f[k] == (2, "<a>")
            k += 1
            if f[k] == (3, '<div class="score_incorrect">'):
                k += 1
                assert f[k] == (3, "&nbsp;")
                k += 1
                assert f[k] == (3, "<span>")
                k += 1
                TaskResults[p] = {}
                TaskResults[p]["Elapsed"] = 0
                TaskResults[p]["Score"] = 0
                assert f[k][1].split()[1].startswith("tr")
                TaskResults[p]["Penalty"] = int(f[k][1].split()[0])
            else:
                assert f[k][1].startswith('<div class="score_correct')
                k += 1
                TaskResults[p] = {}
                TaskResults[p]["Elapsed"] = int(f[k][1])
                TaskResults[p]["Score"] = 1
                k += 1
                assert f[k] == (3, "<span>")
                k += 1
                assert f[k][1].split()[1].startswith("tr")
                TaskResults[p]["Penalty"] = int(f[k][1].split()[0]) - 1
            k += 1
            assert f[k] == (3, "</span>")
            k += 1
            assert f[k] == (3, "</div>")
            k += 1
            assert f[k] == (2, "</a>")
            k += 1
            assert f[k] == (1, "</td>")
            k += 1
        k += 1
        d["TaskResults"] = TaskResults
        StandingsData.append(d)
        print(d, file=sys.stderr)
    return {
        "ContestData": {
            "UnitTime": "minute",
            "Penalty": 20,
            "Duration": 5 * 60,
            "TaskInfo": problem_list,
        },
        "StandingsData": StandingsData,
    }
    # return {
    #     "ContestData": {
    #         "UnitTime": "second",
    #         "Penalty": 20 * 60,
    #         "Duration": 3 * 60 * 60,
    #         "TaskInfo": problem_list,
    #     },
    #     "StandingsData": StandingsData,
    # }


def main():
    html_data = ""
    with open("html/The 2024 ICPC Asia Jakarta Regional Contest.html", "r") as f:
        html_data = f.read()
    b = bracket_analysis(html_data)
    formated = depth_analysis(b)
    for x in formated:
        print(x)
    d = to_dict(formated)
    import json

    with open("standings_2024_jakarta.json", "w") as f:
        print(json.dumps(d, ensure_ascii=False), file=f)


if __name__ == "__main__":
    main()
