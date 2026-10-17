workspace "service-starter" "Minimal C1/C2 for service-starter — sole source for container views." {

    model {
        user = person "User" "Calls the service."
        system = softwareSystem "service-starter" "Minimal service skeleton." {
            api = container "API" "HTTP API" "Python" "Serves /livez, /readyz and domain routes."
        }
        user -> system "Uses"
        user -> system.api "Calls"
    }

    views {
        systemContext system "SystemContext" {
            include *
            autoLayout
        }
        container system "Containers" {
            include *
            autoLayout
        }
    }
}
