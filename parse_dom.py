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
        if s.startswith("</tr"):
            k -= 1
        elif s.startswith("<tr"):
            ret.append((k, s))
            k += 1
        else:
            ret.append((k, s))
    return ret


def to_dict(f: list[tuple[int, str]]) -> dict:
    assert f[0] == (0, '<table class="scoreboard center ">')
    assert f[2] == (0, "<colgroup>")
    assert f[4] == (0, '<col id="scorerank">')
    assert f[6] == (0, '<col id="scoreflags">')
    assert f[8] == (0, '<col id="scoreteamname">')
    assert f[10] == (0, "</colgroup>")
    assert f[12] == (0, "<colgroup>")
    assert f[14] == (0, '<col id="scoresolv">')
    assert f[16] == (0, '<col id="scoretotal">')
    assert f[18] == (0, "</colgroup>")
    assert f[20] == (0, "<colgroup>")
    k = 22
    while True:
        if f[k] != (0, '<col class="scoreprob">'):
            break
        assert f[k] == (0, '<col class="scoreprob">')
        k += 2
    assert f[50] == (0, "</colgroup>")
    assert f[52] == (0, "<thead>")
    assert f[54] == (0, '<tr class="scoreheader" data-static="1">')
    assert f[56] == (1, '<th title="rank" scope="col">')
    assert f[57] == (1, "rank")
    assert f[58] == (1, "</th>")
    assert f[60] == (1, '<th title="team name" scope="col" colspan="2">')
    assert f[61] == (1, "team")
    assert f[62] == (1, "</th>")
    assert f[64] == (1, '<th title="# solved / penalty time" colspan="2" scope="col">')
    assert f[65] == (1, "score")
    assert f[66] == (1, "</th>")
    # problems
    k = 68
    problem_list = []
    while True:
        if not (f[k][0] == 1 and f[k][1].startswith('<th title="')):
            break
        assert f[k][0] == 1 and f[k][1].startswith('<th title="')
        k += 2
        assert f[k] == (1, '<a target="_self">')
        k += 2
        assert f[k][0] == 1 and f[k][1].startswith('<span class="badge problem-badge"')
        k += 1
        assert f[k][0] == 1 and f[k][1].startswith("<span")
        k += 1
        problem_list.append(f[k][1])
        k += 1
        assert f[k] == (1, "</span>")
        k += 1
        assert f[k] == (1, "</span>")
        k += 2
        assert f[k] == (1, "</a>")
        k += 2
        assert f[k] == (1, "</th>")
        k += 2
    k += 1
    assert f[k] == (0, "</thead>")
    k += 2
    assert f[k] == (0, "<tbody>")
    k += 2
    StandingsData = []
    rank_flag = True
    rank_cnt = 1
    while True:
        if f[k][1].startswith("<tr style="):
            break
        assert f[k][0] == 0 and f[k][1].startswith("<tr")
        d = {}
        k += 2
        assert f[k] == (1, '<td class="scorepl ">')
        k += 1
        d["Rank"] = int(f[k][1])
        k += 1
        assert f[273] == (1, "</td>")
        k += 2
        assert f[k] == (1, '<td class="scoreaf">')
        k += 2
        assert f[k] == (1, "<a>")
        k += 2
        assert f[k][0] == 1 and f[k][1].startswith("<img loading=")
        k += 2
        assert f[k][0] == 1 and f[k][1].startswith("<span ")
        k += 1
        assert f[k] == (1, "</span>")
        k += 1
        assert f[k] == (1, "</a>")
        k += 2
        assert f[k] == (1, "</td>")
        k += 2
        assert f[k][0] == 1 and f[k][1].startswith("<td")
        k += 2
        assert f[k][0] == 1 and f[k][1].startswith("<a")
        k += 2
        assert f[k][0] == 1 and f[k][1].startswith("<span")
        k += 1
        d["TeamName"] = f[k][1]
        k += 1
        assert f[k] == (1, "</span>")
        k += 2
        assert f[k][0] == 1 and f[k][1].startswith("<span")
        k += 1
        d["University"] = f[k][1]
        k += 1
        assert f[k] == (1, "</span>")
        k += 2
        assert f[k] == (1, "</a>")
        k += 2
        assert f[k] == (1, "</td>")
        k += 2
        assert f[k] == (1, '<td class="scorenc">')
        k += 1
        TotalResult = {}
        TotalResult["Score"] = int(f[k][1])
        k += 1
        assert f[k] == (1, "</td>")
        k += 2
        assert f[k] == (1, '<td class="scorett">')
        k += 1
        TotalResult["Penalty"] = int(f[k][1])
        d["TotalResult"] = TotalResult
        k += 1
        assert f[k] == (1, "</td>")
        k += 2
        TaskResults = {}
        for p in problem_list:
            assert f[k] == (1, '<td class="score_cell">')
            k += 2
            if f[k] == (1, "</td>"):
                k += 2
                continue
            assert f[k] == (1, "<a>")
            k += 2
            if f[k][1] == '<div class="score_incorrect">':
                k += 1
                TaskResults[p] = {}
                TaskResults[p]["Elapsed"] = 0
                TaskResults[p]["Score"] = 0
                assert f[k][1] == "&nbsp;"
                k += 1
                assert f[k][1] == "<span>"
                k += 1
                assert f[k][1].split()[1].startswith("tr")
                TaskResults[p]["Penalty"] = int(f[k][1].split()[0])
            else:
                assert f[k][1].startswith('<div class="score_correct')
                k += 1
                TaskResults[p] = {}
                TaskResults[p]["Elapsed"] = int(f[k][1])
                TaskResults[p]["Score"] = 1
                k += 1
                assert f[k] == (1, "<span>")
                k += 1
                assert f[k][1].split()[1].startswith("tr")
                TaskResults[p]["Penalty"] = int(f[k][1].split()[0]) - 1
            k += 1
            assert f[k] == (1, "</span>")
            k += 2
            assert f[k] == (1, "</div>")
            k += 2
            assert f[k] == (1, "</a>")
            k += 2
            assert f[k] == (1, "</td>")
            k += 2
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
    with open("html/ICPC 2024 Asia Taichung Regional.html", "r") as f:
        html_data = f.read()
    formated = depth_analysis(bracket_analysis(html_data))
    d = to_dict(formated)
    import json

    with open("json/standings_2024_taichung.json", "w") as f:
        print(json.dumps(d, ensure_ascii=False), file=f)


if __name__ == "__main__":
    main()
