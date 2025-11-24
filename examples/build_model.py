from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url="http://localhost:3030/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Example query to fetch schema or model info
# query = gql("""
#    query {
#        __schema {
#            types {
#                name
#            }
#        }
#    }
#""")

#result = client.execute(query)
#print("Schema types:", result)

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

# Example mutation to add a node to the model
add_node_mutation = gql("""
mutation CreateNode {
    createNode(node: {
        name: "ExampleNode",
        isCommodity: false,
        isMarket: false,
        isRes: false,
        cost: [],
        inflow: []
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_node_result = client.execute(add_node_mutation)
print("CreateNode result:", add_node_result)
# Example mutation to add ExampleNode2 to the model
add_node2_mutation = gql("""
mutation CreateNode {
    createNode(node: {
        name: "ExampleNode2",
        isCommodity: false,
        isMarket: false,
        isRes: false,
        cost: [],
        inflow: []
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_node2_result = client.execute(add_node2_mutation)
print("CreateNode2 result:", add_node2_result)

# Example mutation to add a process to the model
add_process_mutation = gql("""
mutation CreateProcess {
    createProcess(process: {
        name: "ExampleProcess",
        conversion: UNIT,
        isCfFix: false,
        isOnline: true,
        isRes: false,
        eff: 1.0,
        loadMin: 0.0,
        loadMax: 1.0,
        startCost: 0.0,
        minOnline: 0.0,
        maxOnline: 10.0,
        minOffline: 0.0,
        maxOffline: 10.0,
        initialState: true,
        isScenarioIndependent: true,
        cf: [],
        effTs: []
        effOpsFun: []
    }) {
        errors {
            field
            message
        }
    }
}
""")

add_process_result = client.execute(add_process_mutation)
print("CreateProcess result:", add_process_result)

# Example mutation to add a node group
add_node_group_mutation = gql("""
mutation CreateNodeGroup {
    createNodeGroup(name: "ExampleNodeGroup") {
        message
    }
}
""")
add_node_group_result = client.execute(add_node_group_mutation)
print("CreateNodeGroup result:", add_node_group_result)

# Example mutation to add a scenario
add_scenario_mutation = gql("""
mutation CreateScenario {
    createScenario(name: "s1", weight: 1.0) {
        message
    }
}
""")
add_scenario_result = client.execute(add_scenario_mutation)
print("CreateScenario result:", add_scenario_result)

# Example mutation to add a process group
add_process_group_mutation = gql("""
mutation CreateProcessGroup {
    createProcessGroup(name: "ExampleProcessGroup") {
        message
    }
}
""")
add_process_group_result = client.execute(add_process_group_mutation)
print("CreateProcessGroup result:", add_process_group_result)

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
        reserveType: "ExampleReserveType",
        isBid: true,
        isLimited: false,
        minBid: 0.0,
        maxBid: 100.0,
        fee: 0.0,
        price: [
        {
        scenario: "s1",
        constant: 50.0
        }],
        upPrice: [{
        scenario: "s1",
        constant: 51.0
        }],
        downPrice: [{
        scenario: "s1",
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
            { scenario: "s1", constant: 0.5 }
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
            { scenario: "s1", constant: 50.0 }
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

# Example mutation to create an inflow block
add_inflowblock_mutation = gql("""
mutation CreateInflowBlock {
    createInflowBlock(inflowBlock: {
        name: "ExampleInflowBlock",
        node: "ExampleNode",
        data: [
            { scenario: "s1", constant: 42.0 }
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

