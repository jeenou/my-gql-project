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
    createNodeGroup(name: "ExampleProcessGroup") {
        message
    }
}
""")
add_node_group_result = client.execute(add_node_group_mutation)
print("CreateNodeGroup result:", add_node_group_result)

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
        reserveType: "ReserveType",
        isBid: true,
        isLimited: false,
        minBid: 0.0,
        maxBid: 100.0,
        fee: 0.0,
        price: [],
        upPrice: [],
        downPrice: [],
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
