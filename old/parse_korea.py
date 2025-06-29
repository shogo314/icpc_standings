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
        if s.startswith("</tr"):
            assert "tr" == stk.pop()
            k -= 1
            ret.append((k, s))
        elif s.startswith("<tr"):
            ret.append((k, s))
            k += 1
            stk.append("tr")
        elif s.startswith("</td"):
            assert "td" == stk.pop()
            k -= 1
            ret.append((k, s))
        elif s.startswith("<td"):
            ret.append((k, s))
            k += 1
            stk.append("td")
        elif s.startswith("</div"):
            assert "div" == stk.pop()
            k -= 1
            ret.append((k, s))
        elif s.startswith("<div"):
            ret.append((k, s))
            k += 1
            stk.append("div")
        elif s.startswith("</span"):
            assert "span" == stk.pop()
            k -= 1
            ret.append((k, s))
        elif s.startswith("<span"):
            ret.append((k, s))
            k += 1
            stk.append("span")
        elif s.startswith("</a"):
            assert "a" == stk.pop()
            k -= 1
            ret.append((k, s))
        elif s.startswith("<a"):
            ret.append((k, s))
            k += 1
            stk.append("a")
        else:
            ret.append((k, s))
        print(ret[-1])
    return ret


def to_dict(f: list[tuple[int, str]]) -> dict:
    # problems
    problem_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    k = 1
    StandingsData = []
    while True:
        if not f[k][1].startswith('<div id="team-'):
            break
        assert f[k][0] == 1 and f[k][1].startswith('<div id="team-')
        d = {}
        TotalResult = {}
        k += 1
        assert f[k][0] == 2 and f[k][1].startswith('<span class="')
        k += 1
        TotalResult["Score"] = int(f[k][1])
        k += 1
        assert f[k] == (2, "</span>")
        k += 1
        assert f[k][0] == 2 and f[k][1].startswith('<span class="')
        k += 1
        d["Rank"] = int(f[k][1])
        k += 1
        assert f[k] == (2, "</span>")
        k += 1
        assert f[k] == (2, '<span class="team-penalty">')
        k += 1
        TotalResult["Penalty"] = int(f[k][1])
        d["TotalResult"] = TotalResult
        k += 1
        assert f[k] == (2, "</span>")
        k += 1
        assert f[k] == (2, '<div class="results">')
        k += 1

        TaskResults = {}
        for p in problem_list:
            assert f[k][0] == 3 and f[k][1].startswith(
                '<span class="problem-result problem-'
            )
            if f[k][1][len('<span class="problem-result problem-x ') :].strip().startswith(
                "solved"
            ):
                TaskResults[p] = {}
                TaskResults[p]["Score"] = 1
                tmp = f[k][1][: -len(' min." data-balloon-pos="down">')].split()[-1]
                TaskResults[p]["Elapsed"] = int(tmp)
                k += 1
                assert f[k] == (4, '<b class="problem-result-text">')
                k += 1
                if f[k] == (4, "</b>"):
                    TaskResults[p]["Penalty"] = 0
                else:
                    TaskResults[p]["Penalty"] = int(f[k][1][1:])
                    k += 1
                assert f[k] == (4, "</b>")
                k += 1
                assert f[k] == (3, "</span>")
                k += 1
            elif f[k][1][len('<span class="problem-result problem-x ') :].strip().startswith(
                "failed"
            ):
                TaskResults[p] = {}
                TaskResults[p]["Score"] = 0
                TaskResults[p]["Elapsed"] = 0
                k += 1
                assert f[k] == (4, '<b class="problem-result-text">')
                k += 1
                TaskResults[p]["Penalty"] = int(f[k][1][1:])
                k += 1
                assert f[k] == (4, "</b>")
                k += 1
                assert f[k] == (3, "</span>")
                k += 1
            else:
                # TaskResults[p] = {}
                # TaskResults[p]["Score"] = 0
                # TaskResults[p]["Elapsed"] = 0
                k += 1
                assert f[k] == (4, '<b class="problem-result-text">')
                # TaskResults[p]["Penalty"] = 0
                k += 1
                assert f[k] == (4, "</b>")
                k += 1
                assert f[k] == (3, "</span>")
                k += 1
        assert f[k] == (2, "</div>")
        k += 1
        assert f[k] == (2, '<div class="balloons">')
        k += 1
        assert f[k] == (2, "</div>")
        k += 1
        assert f[k] == (2, '<div class="team-title">')
        k += 1
        assert f[k] == (3, '<span class="team-name">')
        k += 1
        d["TeamName"] = f[k][1]
        k += 1
        assert f[k] == (3, "</span>")
        k += 1
        assert f[k] == (3, '<span class="team-represents">')
        k += 1
        d["University"] = f[k][1]
        k += 1
        assert f[k] == (3, "</span>")
        k += 1
        assert f[k] == (2, "</div>")
        k += 1
        assert f[k] == (2, '<div class="clear">')
        k += 1
        assert f[k] == (2, "</div>")
        k += 1
        assert f[k] == (1, "</div>")
        k += 1
        d["TaskResults"] = TaskResults
        StandingsData.append(d)
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
    with open("html/The 2023 ICPC Asia Seoul Regional Contest.html", "r") as f:
        html_data = f.read()
    b = bracket_analysis(html_data)
    formated = depth_analysis(b)
    for x in formated:
        print(x)
    d = to_dict(formated)
    import json

    with open("json/standings_2023_seoul.json", "w") as f:
        print(json.dumps(d, ensure_ascii=False), file=f)


if __name__ == "__main__":
    main()
