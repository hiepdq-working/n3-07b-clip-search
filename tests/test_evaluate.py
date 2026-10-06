import pandas as pd

from evaluate import final_labels


def J(rows):
    return pd.DataFrame(rows, columns=["query_id", "name", "judge", "rel"])


def test_agreement_and_disagreement():
    j = J([
        ["T01", "a", "an", 1], ["T01", "a", "binh", 1],
        ["T01", "b", "an", 1], ["T01", "b", "binh", 0],
        ["T01", "c", "an", 0], ["T01", "c", "binh", 0],
        ["T01", "d", "an", 0], ["T01", "d", "binh", 1],
    ])
    final, kappas, dis = final_labels(j)
    rel = final.set_index("name").rel.to_dict()
    assert rel == {"a": 1, "b": 0, "c": 0, "d": 0}          # lệch -> sai
    assert sorted(dis.name) == ["b", "d"]
    assert kappas.iloc[0].agree_pct == 50.0


def test_adjudication_overrides():
    j = J([["T01", "b", "an", 1], ["T01", "b", "binh", 0]])
    adj = pd.DataFrame([["T01", "b", 1]], columns=["query_id", "name", "rel"])
    final, _, dis = final_labels(j, adj)
    assert final.rel.tolist() == [1]
    assert dis.empty


def test_last_save_wins():
    j = J([["T01", "a", "an", 0], ["T01", "a", "an", 1], ["T01", "a", "binh", 1]])
    final, _, dis = final_labels(j)
    assert final.rel.tolist() == [1] and dis.empty
