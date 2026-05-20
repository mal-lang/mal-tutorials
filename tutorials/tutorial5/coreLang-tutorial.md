# coreLang Tutorial — Modeling a Real Infrastructure Step‑by‑Step

This tutorial introduces [**coreLang**](https://github.com/mal-lang/coreLang), a [MAL](https://mal-lang.org/) (Meta Attack Language)
domain specific language for modeling IT systems and analyzing attacks. After a short chapter on how
the language works, you will incrementally build a realistic model of an infrastructure.

## Chapter 1 — MAL and coreLang basics

### 1.1 coreLang and its definitions

coreLang is a MAL language that captures the abstract IT domain: applications, hardware, networks, data, identities, credentials, vulnerabilities, etc. It is general enough to describe most modern IT infrastructures (cloud, on‑prem, hybrid, microservices, IoT) at a meaningful abstraction.

The language is split across several `.mal` files that can be found in the (coreLang repository)[https://github.com/mal-lang/coreLang/tree/master/src/main/mal]

The current (`1.0.0`) version includes the following files:

| File                   | Description                                                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `ComputeResources.mal` | Defines hosts, applications and software products; use to model machines, VMs, containers and where applications run.                |
| `Networking.mal`       | Models networks, connection rules and routing/firewalls; use for subnets, ACLs and allowed traffic flows.                            |
| `DataResources.mal`    | Defines information and data assets; use to model databases, files and sensitive data storage.                                       |
| `IAM.mal`              | Identity and access types: identities, groups, privileges and credentials; model users, service accounts and permission assignments. |
| `User.mal`             | Human actors and user-related attributes; model people and social engineering targets.                                               |
| `Vulnerability.mal`    | Templates for software and hardware vulnerabilities and their exploitation steps; use to model CVEs and exploitability.              |

The entry point is `main.mal` which includes `coreLang.mal`, which in turn includes all
the files above. Therefore, when importing a language in the [MALGUI](https://github.com/mal-lang/mal-gui) to create the model via GUI, this file can be used as an import.

### 1.2 Useful MAL language concepts in coreLang

When you read a `.mal` file, start by looking for five things: how assets are grouped, how a type is defined, how attack steps flow, how defenses are attached, and how assets are linked together. The snippets below show a few example of how to read `.mal` files that define coreLang.

1. **`category`** is the top-level category for related assets.

   From `ComputeResources.mal`:

   ```mal
   category ComputeResources {
   }
   ```

   Here the file defines one category, `ComputeResources`, and all assets in that file belong to it.

2. **`asset`** defines a thing you can model, and `extends` lets it reuse behavior from a parent asset using inheritence.

   From `ComputeResources.mal`:

   ```mal
   asset SoftwareProduct extends Information
   ```

   Here `SoftwareProduct` is an asset, and `extends Information` means it inherits the behavior that `Information` already provides. In this case, `Information` is definied in the `DataResources.mal` file.

3. **Attack steps** describe what an attacker can do to or through an asset.

   From `Vulnerability.mal`:

   ```mal
   | attemptAbuse @hidden
     ->  abuse

   & abuse
     ->  attemptExploit

   | exploit
     ->  impact
   ```

   Read the symbols like this: `|` means the step can continue when one parent path succeeds, `&` means all required parent paths must succeed, `@hidden` means the step should be excluded from visualization, and `->` lists the next steps that become available. In this example, the attacker first tries to abuse the vulnerability, then exploit it, and finally reach the impact.

   A more concrete step from `ComputeResources.mal` looks like this:

   ```mal
   asset Hardware
   | fullAccess {C,I,A}
     ->  sysExecutedApps.fullAccess,
         hostedData.attemptRead,
         hostedData.attemptWrite,
         deny,
         attemptSpreadWormThroughRemovableMedia
   ```

   Read it as: once the attacker reaches `Hardware.fullAccess`, that success propagates to the linked applications and data. The `{C,I,A}` tag tells you the step affects confidentiality, integrity, and availability, while each item after `->` is a child step that becomes reachable next.

4. **`#`** introduces a defense that can block or make a step harder.

   From `Vulnerability.mal`:

   In coreLang, a defense usually points at the step it protects.

   An example from `Vulnerability.mal` is:

   ```mal
   # networkAccessRequired @suppress [Disabled]
     user info: "Network access is required to abuse the vulnerability."
     ->  networkAccessAchieved,
         softwareProduct.softApplications.softwareProductVulnerabilityNetworkAccessAchieved
   ```

   Here the `#` means the vulnerability is protected by a requirement. If the defense is enabled, the attacker must satisfy the condition before being able to access the next attack steps.

5. **`associations { ... }`** connect assets to each other with named roles.

   From `DataResources.mal`:

```mal
Data [containedData] * <-- AppContainment --> * [containingApp] Application
```

This means a `Data` asset is contained in an `Application`, and the role names become the fields you use in Python (`data.containingApp`, `application.containedData`). The cardinalities tell you that one side can connect to many on the other side.

Essentially, the asset tells you what is being modeled, the attack-step symbols tell you how compromise the asset, the defense syntax tells you what must be true first, and the association syntax tells you how the state of each assets can influence another.

More definitions can be found in the [MAL Syntax page](https://github.com/mal-lang/mal-specification/wiki/MAL-Syntax).

### 1.3 How to work with coreLang in practice

coreLang is the language definition, but the actual modeling workflow usually happens with the support of a variety of MAL tools. Please refer to each repository for instruction on how to install them and their prerequisites.

[MAL Toolbox](https://github.com/mal-lang/mal-toolbox) is a collection of Python modules. Use it when you want to load a language, create a model, add assets and associations, and generate an attack graph from that model. This is the best option when you want the workflow to be repeatable and when you want to build the model step by step in Python code.

[MAL Simulator](https://github.com/mal-lang/mal-simulator) takes the attack graph and runs a simulation on it. That is where attacker and defender agents act on the graph.

If you want to watch the simulation visually, [MAL Sim GUI](https://github.com/mal-lang/malsim-gui) can connect to the simulator and display the simulation as it unfolds.

[MAL GUI](https://github.com/mal-lang/mal-gui) is the visual option. It is useful when you want to explore a model without writing Python first. You can load a language, drag assets into the canvas, create associations visually, and inspect how the attack paths change as the model becomes more complete.

A typical modelling workflow looks like this:

1. Load the coreLang language definition.
2. Create an instance model in Python or in the GUI.
3. Add the assets, associations, entry points, and defenses that describe the scenario.
4. Generate an attack graph from the model.
5. Run a MAL simulation on that attack graph.
6. Inspect the result, either in the console or in MAL Sim GUI, then refine the model and run it again.

## Chapter 2 — Modelling exercise

There cannot be one scenario that will cover everything that the coreLang has to offer and of course, the detail and scope of each model can very greatly. In this tutorial we try to provide a somewhat realistic (even though small) infrastructure to showcase the coreLang capabilities and support tools.

We will not use the [MAL GUI](https://github.com/mal-lang/mal-gui) in this case, but instead we will create the model in code.
We will though, show the simulation on the [MAL Sim GUI](https://github.com/mal-lang/malsim-gui) so that we can more easily show the attack paths.

You are modeling the IT infrastructure of **The Company**, a small company with a customer-facing web service. The layout is the following: one
internet-facing application behind a firewall, a backend app server, and a database on a separate internal network.

TODO: put a draw.io graph here.

```
                            ┌──────────────────────────┐
  Internet ─── Firewall ──▶│  DMZ                     │
                            │  WebApp                  │
                            └────────────┬─────────────┘
                                        │
                           ┌────────────▼─────────────┐
                           │  InternalNet             │
                           │  AppServer               │
                           │  Database ──▶ CustomerData│
                           └──────────────────────────┘
```
