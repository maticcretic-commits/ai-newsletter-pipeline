import json
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / "workflows" / "ai-newsletter-pipeline.json"


def load():
    with open(WORKFLOW) as f:
        return json.load(f)


def test_valid_json():
    data = load()
    assert isinstance(data, dict)


def test_nodes_non_empty_with_unique_names_and_ids():
    data = load()
    nodes = data["nodes"]
    assert len(nodes) > 0
    names = [n["name"] for n in nodes]
    ids = [n["id"] for n in nodes]
    assert len(set(names)) == len(names), "duplicate node names"
    assert len(set(ids)) == len(ids), "duplicate node ids"


def test_every_node_has_type_position_parameters():
    data = load()
    for n in data["nodes"]:
        assert n.get("type"), f"node {n.get('name')} missing type"
        assert n.get("position"), f"node {n.get('name')} missing position"
        assert "parameters" in n, f"node {n.get('name')} missing parameters"


def test_connections_reference_existing_nodes():
    data = load()
    names = {n["name"] for n in data["nodes"]}
    conns = data["connections"]
    assert conns, "connections object is empty"
    for source, outputs in conns.items():
        assert source in names, f"connection source '{source}' not a node"
        for branch in outputs.get("main", []):
            for target in branch:
                assert target["node"] in names, (
                    f"connection target '{target['node']}' not a node"
                )


def test_schedule_trigger_present():
    data = load()
    triggers = [n for n in data["nodes"] if n["type"] == "n8n-nodes-base.scheduleTrigger"]
    assert triggers, "no schedule trigger node found"
    # at least one branch of the schedule trigger feeds an RSS node
    conns = data["connections"]
    sched = triggers[0]["name"]
    targets = [t["node"] for branch in conns.get(sched, {}).get("main", []) for t in branch]
    assert any("RSS" in t.upper() for t in targets), "schedule trigger not wired to an RSS node"


def test_pipeline_chain_complete():
    data = load()
    names = {n["name"] for n in data["nodes"]}
    required = {
        "Weekly Schedule",
        "RSS Feed — Tech",
        "RSS Feed — AI News",
        "Merge Feeds",
        "AI Summarise Items",
        "AI Rewrite Newsletter",
        "Build HTML Email",
        "Send Newsletter",
        "Log Success",
    }
    assert required.issubset(names), f"missing nodes: {required - names}"


def test_no_hardcoded_secrets():
    raw = WORKFLOW.read_text()
    assert "sk-" not in raw, "looks like a hardcoded OpenAI key"
    lowered = raw.lower()
    assert '"password"' not in lowered, "looks like a hardcoded password"
    # credentials must be referenced by name only
    data = load()
    for n in data["nodes"]:
        for cred_name, cred in (n.get("credentials") or {}).items():
            assert cred.get("id") is None, (
                f"node '{n['name']}' pins a credential id"
            )


def test_env_example_has_placeholders():
    env_file = Path(__file__).resolve().parents[1] / "workflows" / "starter-config.env.example"
    text = env_file.read_text()
    for key in ["RSS_FEEDS", "OPENAI_MODEL", "NEWSLETTER_FROM", "NEWSLETTER_TO"]:
        assert key in text, f"{key} missing from env example"
    assert "sk-" not in text
