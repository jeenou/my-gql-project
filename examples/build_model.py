from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url="http://localhost:3030/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Example query to fetch schema or model info
query = gql("""
    query {
        __schema {
            types {
                name
            }
        }
    }
""")

result = client.execute(query)
print("Schema types:", result)

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
