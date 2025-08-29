from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json

transport = RequestsHTTPTransport(
    url="http://localhost:3030/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

with open('model_data.json', 'r') as f:
    data = json.load(f)

# Example mutation to create input data setup

mutation = gql("""
mutation CreateInputDataSetup {
    createInputDataSetup(setupUpdate: {
        useMarketBids: true,
        useReserves: false,
        useReserveRealisation: false,
        useNodeDummyVariables: false,
        useRampDummyVariables: false,
        commonTimesteps: 0,
        commonScenarioName: "default",
        nodeDummyVariableCost: 0.0,
        rampDummyVariableCost: 0.0
    }) {
        errors {
            field
            message
        }
    }
}
""")

result = client.execute(mutation)
print("CreateInputDataSetup result:", result)

# Query the model after creating input data setup
model_query = gql("""
query {
    model {
        inputData {
            setup {
                reserveRealisation
                useMarketBids
                useReserves
                commonTimeSteps
                useNodeDummyVariables
                useRampDummyVariables
                nodeDummyVariableCost
                rampDummyVariableCost
            }
        }
    }
}
""")

model_result = client.execute(model_query)
print("Model data:", model_result)

nodes = data.get('nodes', [])

for node in nodes:
    mutation = gql(f"""
    mutation {{
        createNode(node: {{
            name: "{node['name']}",
            isCommodity: {str(node['isCommodity']).lower()},
            isMarket: {str(node['isMarket']).lower()},
            isRes: {str(node['isRes']).lower()},
            cost: [],
            inflow: []
        }}) {{
            errors {{
                field
                message
            }}
        }}
    }}
    """)
    result = client.execute(mutation)
    print(f"CreateNode result for {node['name']}:", result)

processes = data.get('processes', [])
for process in processes:
    add_process_mutation = gql(f"""
    mutation CreateProcess {{
        createProcess(process: {{
            name: "{process['name']}",
            conversion: {process['conversion']},
            isCfFix: {str(process['isCfFix']).lower()},
            isOnline: {str(process['isOnline']).lower()},
            isRes: {str(process['isRes']).lower()},
            eff: {process['eff']},
            loadMin: {process['loadMin']},
            loadMax: {process['loadMax']},
            startCost: {process['startCost']},
            minOnline: {process['minOnline']},
            maxOnline: {process['maxOnline']},
            minOffline: {process['minOffline']},
            maxOffline: {process['maxOffline']},
            initialState: {str(process['initialState']).lower()},
            isScenarioIndependent: {str(process['isScenarioIndependent']).lower()},
            cf: [],
            effTs: []
        }}) {{
            errors {{
                field
                message
            }}
        }}
    }}
    """)
    add_process_result = client.execute(add_process_mutation)
    print(f"CreateProcess result for {process['name']}:", add_process_result)

node_groups = data.get('node_groups', [])

for node_group in node_groups:
    mutation = gql(f"""
    mutation {{
        createNodeGroup(name: "{node_group['name']}") {{
            message
        }}
    }}
    """)
    result = client.execute(mutation)
    print(f"CreateNodeGroup result for {node_group['name']}:", result)

process_groups = data.get('process_groups', [])
for process_group in process_groups:
    mutation = gql(f"""
    mutation {{
        createProcessGroup(name: "{process_group['name']}") {{
            message
        }}
    }}
    """)
    result = client.execute(mutation)
    print(f"CreateProcessGroup result for {process_group['name']}:", result)

# Example mutation to add a scenario
add_scenario_mutation = gql("""
mutation CreateScenario {
    createScenario(name: "ExampleScenario", weight: 1.0) {
        message
    }
}
""")
add_scenario_result = client.execute(add_scenario_mutation)
print("CreateScenario result:", add_scenario_result)

# Example mutation to add a market to the model
add_market_mutation = gql("""
mutation CreateMarket {
    createMarket(market: {
        name: "ExampleMarket",
        mType: ENERGY,
        node: "ExampleNode",
        processGroup: "ExampleProcessGroup",
        direction: UP,
        realisation: [],
        reserveType: "ReserveType",
        isBid: true,
        isLimited: false,
        minBid: 0.0,
        maxBid: 100.0,
        fee: 0.0,
        price: [
        {
        scenario: "ExampleScenario",
        constant: 50.0
        }],
        upPrice: [{
        scenario: "ExampleScenario",
        constant: 51.0
        }],
        downPrice: [{
        scenario: "ExampleScenario",
        constant: 49.0
        }],
        reserveActivationPrice: []
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_market_result = client.execute(add_market_mutation)
print("CreateMarket result:", add_market_result)

# Example mutation to add a risk to the model
add_risk_mutation = gql("""
mutation CreateRisk {
    createRisk(risk: {
        parameter: "HighDemandSpike",
        value: 0.15
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_risk_result = client.execute(add_risk_mutation)
print("CreateRisk result:", add_risk_result)
# Example mutation to add a node diffusion to the model
add_nodediffusion_mutation = gql("""
mutation CreateNodeDiffusion {
    createNodeDiffusion(newDiffusion: {
        fromNode: "ExampleNode",
        toNode: "ExampleNode2",
        coefficient: [
            { scenario: "ExampleScenario", constant: 0.5 }
        ]
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_nodediffusion_result = client.execute(add_nodediffusion_mutation)
print("CreateNodeDiffusion result:", add_nodediffusion_result)
# Example mutation to add a node delay to the model
add_nodedelay_mutation = gql("""
mutation CreateNodeDelay {
    createNodeDelay(delay: {
        fromNode: "ExampleNode",
        toNode: "ExampleNode2",
        delay: 2.5,
        minDelayFlow: 0.0,
        maxDelayFlow: 10.0
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_nodedelay_result = client.execute(add_nodedelay_mutation)
print("CreateNodeDelay result:", add_nodedelay_result)
# Example mutation to create node history
add_node_history_mutation = gql("""
mutation CreateNodeHistory {
    createNodeHistory(nodeName: "ExampleNode") {
        errors {
            field
            message
        }
    }
}
""")

add_node_history_result = client.execute(add_node_history_mutation)
print("CreateNodeHistory result:", add_node_history_result)
# Example mutation to create a generic constraint
add_genconstraint_mutation = gql("""
mutation CreateGenConstraint {
    createGenConstraint(constraint: {
        name: "ExampleGenConstraint",
        gcType: LESS_THAN,
        isSetpoint: false,
        penalty: 100.0,
        constant: [
            { scenario: "ExampleScenario", constant: 50.0 }
        ]
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_genconstraint_result = client.execute(add_genconstraint_mutation)
print("CreateGenConstraint result:", add_genconstraint_result)

# Example mutation to create a reserve type
add_reservetype_mutation = gql("""
mutation CreateReserveType {
    createReserveType(reserveType: {
        name: "ExampleReserveType",
        rampRate: 1.5
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_reservetype_result = client.execute(add_reservetype_mutation)
print("CreateReserveType result:", add_reservetype_result)

# Example mutation to create an inflow block
add_inflowblock_mutation = gql("""
mutation CreateInflowBlock {
    createInflowBlock(inflowBlock: {
        name: "ExampleInflowBlock",
        node: "ExampleNode",
        data: [
            { scenario: "ExampleScenario", constant: 42.0 }
        ]
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_inflowblock_result = client.execute(add_inflowblock_mutation)
print("CreateInflowBlock result:", add_inflowblock_result)

