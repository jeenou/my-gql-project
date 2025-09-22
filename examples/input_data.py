from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json
from utilities import prune_nones, pick_keys, normalize_point, normalize_points, normalize_value_inputs

transport = RequestsHTTPTransport(
    url="http://localhost:3030/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

with open('model_data.json', 'r') as f:
    data = json.load(f)

# ---------- CREATE SETUP ----------

create_setup_mut = gql("""
mutation($s: InputDataSetupInput!) {
  createInputDataSetup(setupUpdate: $s) {
    errors { field message }
  }
}
""")

setup_input = prune_nones(data.get("setup", {}))
res = client.execute(create_setup_mut, variable_values={"s": setup_input})
print("CreateInputDataSetup result:", res)


# ---------- NODES ----------
create_node_mutation = gql("""
mutation CreateNode($node: NewNode!) {
  createNode(node: $node) {
    errors { field message }
  }
}
""")

NODE_KEYS = {"name","isCommodity","isMarket","isRes","cost","inflow"}

nodes = data.get('nodes', [])
for raw in nodes:
    node_input = pick_keys(raw, NODE_KEYS)
    # schema requires cost: [ValueInput!]! and inflow: [ForecastValueInput!]!
    node_input.setdefault("cost", [])
    node_input.setdefault("inflow", [])
    node_input = prune_nones(node_input)
    result = client.execute(create_node_mutation, variable_values={"node": node_input})
    print(f"CreateNode result for {raw.get('name')}:", result)

# ---------- NODE STATE ----------
set_node_state_mutation = gql("""
mutation SetNodeState($nodeName: String!, $state: NewState) {
  setNodeState(state: $state, nodeName: $nodeName) {
    errors { field message }
  }
}
""")

node_states = data.get("node_states", [])
for entry in node_states:
    node_name = entry["nodeName"]
    state = entry["state"]

    # GraphQL NewState has no nullables -> ensure all fields are present
    required_fields = [
        "inMax","outMax","stateLossProportional","stateMin","stateMax",
        "initialState","isScenarioIndependent","isTemp","tEConversion","residualValue"
    ]
    missing = [k for k in required_fields if k not in state]
    if missing:
        raise ValueError(f"State for node {node_name!r} missing fields: {', '.join(missing)}")

    res = client.execute(
        set_node_state_mutation,
        variable_values={"nodeName": node_name, "state": state}
    )
    print(f"SetNodeState result for {node_name}:", res)


# ---------- PROCESSES ----------
create_process_mutation = gql("""
mutation CreateProcess($process: NewProcess!) {
  createProcess(process: $process) {
    errors { field message }
  }
}
""")

# Match NewProcess fields in the schema
PROCESS_KEYS = {
    "name","conversion","isCfFix","isOnline","isRes","eff",
    "loadMin","loadMax","startCost","minOnline","maxOnline",
    "minOffline","maxOffline","initialState","isScenarioIndependent",
    "cf","effTs","effOpsFun"
}

# Required *scalar/boolean/enum* fields that must be present (non-null in schema)
REQUIRED_PROCESS_FIELDS = {
    "name","conversion","isCfFix","isOnline","isRes","eff",
    "loadMin","loadMax","startCost","minOnline","maxOnline",
    "minOffline","maxOffline","initialState","isScenarioIndependent"
}

processes = data.get('processes', [])
for raw in processes:
    # Validate: fail fast if any required scalar is missing
    missing = [k for k in REQUIRED_PROCESS_FIELDS if raw.get(k) is None]
    if missing:
        raise ValueError(f"Process {raw.get('name')!r}: missing required fields: {', '.join(missing)}")

    proc_input = pick_keys(raw, PROCESS_KEYS)

    # Non-null list fields -> default to [] if not provided
    proc_input.setdefault("cf", [])
    proc_input.setdefault("effTs", [])
    proc_input.setdefault("effOpsFun", [])

    # Normalize points (no-op if already {'x': float, 'y': float})
    proc_input["effOpsFun"] = normalize_points(proc_input["effOpsFun"])

    # Drop any explicit Nones
    proc_input = prune_nones(proc_input)

    add_process_result = client.execute(
        create_process_mutation,
        variable_values={"process": proc_input}
    )
    print(f"CreateProcess result for {raw.get('name')}:", add_process_result)

# ---------- NODE GROUPS ----------
create_node_group_mutation = gql("""
mutation CreateNodeGroup($name: String!) {
  createNodeGroup(name: $name) { message }
}
""")

node_groups = data.get('node_groups', [])
for ng in node_groups:
    result = client.execute(create_node_group_mutation, variable_values={"name": ng["name"]})
    print(f"CreateNodeGroup result for {ng.get('name')}:", result)

# ---------- PROCESS GROUPS ----------
create_process_group_mutation = gql("""
mutation CreateProcessGroup($name: String!) {
  createProcessGroup(name: $name) { message }
}
""")

process_groups = data.get('process_groups', [])
for pg in process_groups:
    result = client.execute(create_process_group_mutation, variable_values={"name": pg["name"]})
    print(f"CreateProcessGroup result for {pg.get('name')}:", result)

# ---------- SCENARIOS ----------
create_scenario_mutation = gql("""
mutation CreateScenario($name: String!, $weight: Float!) {
  createScenario(name: $name, weight: $weight) { message }
}
""")

scenarios = data.get("scenarios", [{"name": "ExampleScenario", "weight": 1.0}])
for sc in scenarios:
    vars_ = {"name": sc["name"], "weight": float(sc.get("weight", 1.0))}
    add_scenario_result = client.execute(create_scenario_mutation, variable_values=vars_)
    print(f"CreateScenario result for {sc['name']}:", add_scenario_result)

# ---------- MARKETS ----------
create_market_mutation = gql("""
mutation CreateMarket($market: NewMarket!) {
  createMarket(market: $market) { errors { field message } }
}
""")

MARKET_KEYS = {
    "name","mType","node","processGroup","direction",
    "realisation","reserveType","isBid","isLimited",
    "minBid","maxBid","fee","price","upPrice","downPrice","reserveActivationPrice"
}

markets = data.get("markets", [])
for raw in markets:
    mkt = pick_keys(raw, MARKET_KEYS)
    # ensure required lists exist
    mkt.setdefault("realisation", [])
    mkt.setdefault("price", [])
    mkt.setdefault("upPrice", [])
    mkt.setdefault("downPrice", [])
    mkt.setdefault("reserveActivationPrice", [])
    # enums as strings in variables are fine: "ENERGY", "RESERVE", "UP", "RES_UP", ...
    mkt = prune_nones(mkt)
    add_market_result = client.execute(create_market_mutation, variable_values={"market": mkt})
    print(f"CreateMarket result for {raw.get('name')}:", add_market_result)

# ---------- RISKS ----------
create_risk_mutation = gql("""
mutation CreateRisk($risk: NewRisk!) {
  createRisk(risk: $risk) { errors { field message } }
}
""")

RISK_KEYS = {"parameter","value"}

risks = data.get("risk", [])
for raw in risks:
    risk = prune_nones(pick_keys(raw, RISK_KEYS))
    add_risk_result = client.execute(create_risk_mutation, variable_values={"risk": risk})
    print(f"CreateRisk result for {raw.get('parameter')}:", add_risk_result)

# ---------- NODE DIFFUSION ----------
create_node_diffusion_mutation = gql("""
mutation CreateNodeDiffusion($diff: NewNodeDiffusion!) {
  createNodeDiffusion(newDiffusion: $diff) { errors { field message } }
}
""")

NODE_DIFFUSION_KEYS = {"fromNode","toNode","coefficient"}

node_diffusions = data.get("node_diffusions", [])
for raw in node_diffusions:
    diff = pick_keys(raw, NODE_DIFFUSION_KEYS)
    diff.setdefault("coefficient", [])
    diff = prune_nones(diff)
    add_nodediffusion_result = client.execute(
        create_node_diffusion_mutation, variable_values={"diff": diff}
    )
    print(f"CreateNodeDiffusion result {diff.get('fromNode')} -> {diff.get('toNode')}:", add_nodediffusion_result)

# ---------- NODE DELAY ----------
create_node_delay_mutation = gql("""
mutation CreateNodeDelay($delay: NewNodeDelay!) {
  createNodeDelay(delay: $delay) { errors { field message } }
}
""")

NODE_DELAY_KEYS = {"fromNode","toNode","delay","minDelayFlow","maxDelayFlow"}

node_delays = data.get("node_delays", [])
for raw in node_delays:
    dly = prune_nones(pick_keys(raw, NODE_DELAY_KEYS))
    add_nodedelay_result = client.execute(
        create_node_delay_mutation, variable_values={"delay": dly}
    )
    print(f"CreateNodeDelay result {dly.get('fromNode')} -> {dly.get('toNode')}:", add_nodedelay_result)

# ---------- NODE HISTORY (optional steps) ----------
create_node_history_mutation = gql("""
mutation CreateNodeHistory($nodeName: String!) {
  createNodeHistory(nodeName: $nodeName) { errors { field message } }
}
""")

add_history_step_mutation = gql("""
mutation AddStep($nodeName: String!, $step: NewSeries!) {
  addStepToNodeHistory(nodeName: $nodeName, step: $step) { errors { field message } }
}
""")

# Expect entries like:
# { "nodeName": "ExampleNode", "steps": [ { "scenario":"s1", "durations":[{"hours":1,"minutes":0,"seconds":0}], "values":[1.0] } ] }
node_histories = data.get("node_histories", [])
for raw in node_histories:
    node_name = raw["nodeName"]
    res = client.execute(create_node_history_mutation, variable_values={"nodeName": node_name})
    print(f"CreateNodeHistory result for {node_name}:", res)

    for step in raw.get("steps", []):
        step_clean = prune_nones(step)
        res2 = client.execute(add_history_step_mutation, variable_values={"nodeName": node_name, "step": step_clean})
        print(f"AddStepToNodeHistory result for {node_name}:", res2)

# ---------- RESERVE TYPE ----------
create_reserve_type_mutation = gql("""
mutation CreateReserveType($rt: NewReserveType!) {
  createReserveType(reserveType: $rt) { errors { field message } }
}
""")

RESERVE_TYPE_KEYS = {"name","rampRate"}

reserve_types = data.get("reserve_types", [])
for raw in reserve_types:
    rt = prune_nones(pick_keys(raw, RESERVE_TYPE_KEYS))
    add_reservetype_result = client.execute(
        create_reserve_type_mutation, variable_values={"rt": rt}
    )
    print(f"CreateReserveType result for {rt.get('name')}:", add_reservetype_result)

# ---------- INFLOW BLOCK ----------
create_inflow_block_mutation = gql("""
mutation CreateInflowBlock($ib: NewInflowBlock!) {
  createInflowBlock(inflowBlock: $ib) { errors { field message } }
}
""")

INFLOW_BLOCK_KEYS = {"name","node","data"}

inflow_blocks = data.get("inflow_blocks", [])
for raw in inflow_blocks:
    ib = pick_keys(raw, INFLOW_BLOCK_KEYS)
    ib.setdefault("data", [])
    ib = prune_nones(ib)
    add_inflowblock_result = client.execute(
        create_inflow_block_mutation, variable_values={"ib": ib}
    )
    print(f"CreateInflowBlock result for {ib.get('name')}:", add_inflowblock_result)

# ---------- TOPOLOGIES ----------
create_topology_mutation = gql("""
mutation CreateTopology(
  $processName: String!,
  $sourceNodeName: String,
  $sinkNodeName: String,
  $topology: NewTopology!
) {
  createTopology(
    processName: $processName,
    sourceNodeName: $sourceNodeName,
    sinkNodeName: $sinkNodeName,
    topology: $topology
  ) {
    errors { field message }
  }
}
""")

TOPOLOGY_KEYS = {
    "capacity","vomCost","rampUp","rampDown","initialLoad","initialFlow","capTs"
}

topologies = data.get("topologies", [])
for raw in topologies:
    process_name = raw["processName"]
    src = raw.get("sourceNodeName")   # may be None
    sink = raw.get("sinkNodeName")    # may be None

    topo = pick_keys(raw, TOPOLOGY_KEYS)
    topo.setdefault("capTs", [])

    # Ensure capTs is a list of ValueInput objects.
    # Keep only allowed keys and drop Nones; series -> floats.
    cleaned_capts = []
    for v in topo["capTs"]:
        vi = {}
        if "scenario" in v and v["scenario"] is not None:
            vi["scenario"] = v["scenario"]
        if "series" in v and v["series"] is not None:
            vi["series"] = [float(x) for x in v["series"]]
        # optional: include constant only if explicitly provided (non-None)
        if "constant" in v and v["constant"] is not None:
            vi["constant"] = float(v["constant"])
        cleaned_capts.append(vi)

    topo["capTs"] = cleaned_capts
    topo = prune_nones(topo)

    res = client.execute(
        create_topology_mutation,
        variable_values={
            "processName": process_name,
            "sourceNodeName": src,
            "sinkNodeName": sink,
            "topology": topo
        }
    )
    print(f"CreateTopology result for process {process_name} (source={src}, sink={sink}):", res)

    # ---------- GENERIC CONSTRAINT ----------
create_gen_constraint_mutation = gql("""
mutation CreateGenConstraint($constraint: NewGenConstraint!) {
  createGenConstraint(constraint: $constraint) { errors { field message } }
}
""")

create_flow_confactor_mutation = gql("""
mutation CreateFlowConFactor(
  $constraintName: String!,
  $processName: String!,
  $sourceOrSinkNodeName: String!,
  $factor: [ValueInput!]!
) {
  createFlowConFactor(
    constraintName: $constraintName,
    processName: $processName,
    sourceOrSinkNodeName: $sourceOrSinkNodeName,
    factor: $factor
  ) { errors { field message } }
}
""")

create_state_confactor_mutation = gql("""
mutation CreateStateConFactor(
  $constraintName: String!,
  $nodeName: String!,
  $factor: [ValueInput!]!
) {
  createStateConFactor(
    constraintName: $constraintName,
    nodeName: $nodeName,
    factor: $factor
  ) { errors { field message } }
}
""")

create_online_confactor_mutation = gql("""
mutation CreateOnlineConFactor(
  $constraintName: String!,
  $processName: String!,
  $factor: [ValueInput!]!
) {
  createOnlineConFactor(
    constraintName: $constraintName,
    processName: $processName,
    factor: $factor
  ) { errors { field message } }
}
""")

GEN_CONSTRAINT_KEYS = {"name","gcType","isSetpoint","penalty","constant"}

gen_constraints = data.get("gen_constraints", [])
for raw in gen_constraints:
    # 1) create the base constraint
    gc = pick_keys(raw, GEN_CONSTRAINT_KEYS)
    gc.setdefault("constant", [])
    gc["constant"] = normalize_value_inputs(gc["constant"])
    gc = prune_nones(gc)

    add_gc_res = client.execute(
        create_gen_constraint_mutation,
        variable_values={"constraint": gc}
    )
    print(f"CreateGenConstraint result for {raw.get('name')}:", add_gc_res)

    cname = raw["name"]

    # 2) add FLOW factors (if any)
    for ff in raw.get("flow_factors", []):
        factor = normalize_value_inputs(ff.get("factor", []))
        vars_ = {
            "constraintName": cname,
            "processName": ff["processName"],
            "sourceOrSinkNodeName": ff["sourceOrSinkNodeName"],
            "factor": factor
        }
        res = client.execute(create_flow_confactor_mutation, variable_values=vars_)
        print(f"createFlowConFactor {cname} {ff['processName']}->{ff['sourceOrSinkNodeName']}:", res)

    # 3) add STATE factors (if any)
    for sf in raw.get("state_factors", []):
        factor = normalize_value_inputs(sf.get("factor", []))
        vars_ = {
            "constraintName": cname,
            "nodeName": sf["nodeName"],
            "factor": factor
        }
        res = client.execute(create_state_confactor_mutation, variable_values=vars_)
        print(f"createStateConFactor {cname} node={sf['nodeName']}:", res)

    # 4) add ONLINE factors (if any)
    for of in raw.get("online_factors", []):
        factor = normalize_value_inputs(of.get("factor", []))
        vars_ = {
            "constraintName": cname,
            "processName": of["processName"],
            "factor": factor
        }
        res = client.execute(create_online_confactor_mutation, variable_values=vars_)
        print(f"createOnlineConFactor {cname} process={of['processName']}:", res)


