# Modeling Qutrit to Dynamic Graph

This repository presents an academic proof-of-concept for the modeling of **shortest paths in classical dynamic graphs** through **qutrit-based state encoding** implemented with PennyLane.

The project accompanies the research proposal:

> **Shortest Path Modeling in Dynamic Graphs with Qutrit Encoding**

Its central objective is not to claim quantum speedup, but to investigate whether a **multi-state quantum representation** can provide a coherent and formally adequate description for dynamic graph problems whose edge states are not naturally binary.

---

## Research context

The repository is situated at the intersection of:

- **dynamic graph algorithms**, especially in the fully dynamic setting;
- **quantum information with higher-dimensional systems**;
- **hybrid quantum-classical modeling**;
- **conceptual and methodological validation** through simulation.

In the proposed framework, **qudits** are treated as the general conceptual structure for multi-valued state encoding, while **qutrits** constitute the minimal operational instance adopted for the present proof-of-concept.

---

## Objective

The repository implements and documents a toy hybrid model for **dynamic shortest-path queries** in graphs subject to edge insertions, removals, and state changes.

The specific goals are:

1. to formalize a ternary state model for graph edges;
2. to encode such states directly in qutrits;
3. to reconstruct admissible graph snapshots from the encoded representation;
4. to compare the resulting shortest-path outputs against a classical baseline;
5. to assess the representational adequacy of qutrit encoding with respect to binary alternatives.

---

## Formal model

Let $E^\star \subseteq V \times V$ be a fixed universe of candidate edges.  
The dynamic graph state is described by the function

$$
\sigma_t : E^\star \to \{0,1,2\},
$$

with the interpretation

$$
\sigma_t(e)=
\begin{cases}
0, & \text{if } e \text{ is absent}, \\
1, & \text{if } e \text{ is active}, \\
2, & \text{if } e \text{ is restricted}.
\end{cases}
$$

The qutrit encoding is defined by

$$
\phi(\sigma_t(e))=
\begin{cases}
\ket{0}, & \sigma_t(e)=0,\\
\ket{1}, & \sigma_t(e)=1,\\
\ket{2}, & \sigma_t(e)=2.
\end{cases}
$$

The global graph snapshot is represented by

$$
\ket{\Sigma_t} = \bigotimes_{e \in E^\star} \ket{\sigma_t(e)}.
$$

Only active edges are projected into the admissible graph:

$$
G_t^{\mathrm{adm}} = (V, E_t^{\mathrm{adm}})
$$

with

$$
E_t^{\mathrm{adm}} = \{ e \in E^\star : \sigma_t(e)=1 \}.
$$

Shortest-path queries are then evaluated classically on $G_t^{\mathrm{adm}}$.

---

## Conceptual contribution

The main conceptual contribution of this repository lies in the direct correspondence between the **logical domain of the problem** and the **state space used for encoding**.

In standard binary encodings, a ternary variable often requires one of the following:

- auxiliary variables,
- additional constraints,
- invalid codewords.

In contrast, the qutrit-based model preserves the ternary domain of the edge state directly. This makes the proposed encoding especially suitable for problems in which the distinction between **absent**, **active**, and **restricted** edges must remain explicit throughout the dynamic evolution of the graph.

More broadly, the repository supports the interpretation that **higher-dimensional quantum systems may serve as natural representational tools** for discrete optimization and graph-theoretic models with non-binary semantics.

---

## Toy model and validation strategy

The implementation follows a hybrid workflow:

1. **state update**  
   the current edge-state vector is updated after each dynamic event;

2. **qutrit snapshot preparation**  
   the new graph configuration is encoded as a qutrit register;

3. **projection of the admissible graph**  
   only edges in the active state are considered for shortest-path queries;

4. **classical shortest-path computation**  
   a classical solver, such as Dijkstra, is applied to the reconstructed admissible graph;

5. **comparison with a classical oracle baseline**  
   the same sequence of updates is evaluated classically, and the outputs are compared.

The principal validation criterion is the agreement between the hybrid model and the classical baseline in terms of:

- shortest-path distance,
- shortest-path route, when unique,
- consistency under repeated updates.

---

## Interpretation of results

The results obtained in small-scale experiments should be interpreted as evidence of:

- **correctness** on the tested instances;
- **dynamic consistency** under state transitions;
- **representational adequacy** for ternary edge states.

They should **not** be interpreted as evidence of:

- quantum speedup,
- asymptotic performance improvement,
- superiority over classical dynamic shortest-path algorithms,
- hardware-level advantage.

The scope of the repository is therefore **methodological and conceptual**, not competitive benchmarking.

---

## Computational environment

The project supports multiple execution modes:

### Local Python environment

The core implementation can be executed directly in a local Python environment with PennyLane and NumPy installed.

Typical requirements include:

- Python 3.10+
- `pennylane`
- `numpy`

Install dependencies with:

```bash
pip install pennylane numpy
```

or, if provided:

```bash
pip install -r requirements.txt
```

### Docker support

The repository also includes a **Docker** configuration in order to provide a reproducible execution environment.

This allows the project to be run inside an isolated container, which is useful for:

- dependency consistency,
- reproducibility of experiments,
- easier setup across different machines,
- controlled execution of the hybrid toy model.

### Docker Compose support

In addition, the repository includes a **Docker Compose** configuration to orchestrate containers.  
This makes it possible to standardize the execution workflow and, when needed, coordinate multiple services associated with experimentation, development, or documentation.

Typical use cases include:

- running the main application container;
- mounting local source files into the container environment;
- isolating runtime dependencies;
- simplifying command execution and environment setup.

If the repository includes the expected files, the project can typically be started with commands such as:

```bash
docker compose up --build
```

or

```bash
docker-compose up --build
```

depending on the local Docker installation.

---

## Running the project

A typical execution of the toy model may be performed with:

```bash
python main.py
```

Expected output may include:

- the current dynamic state vector `sigma`;
- the semantic interpretation of each edge state;
- shortest-path results from the qutrit-based model;
- shortest-path results from the classical baseline;
- accuracy values for distance and path agreement;
- representational statistics comparing qutrit and binary encodings.

---

## Representative metrics

Typical reported metrics include:

- `distance_accuracy`
- `path_accuracy`
- number of candidate edges
- qutrit units required
- one-hot binary cost
- compact binary cost
- number of invalid compact binary codes

These values help illustrate the central methodological claim of the project: **qutrit encoding can represent ternary graph states more directly than standard binary alternatives**.

---

## Repository structure

A possible repository organization is:

```text
.
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── main.py
```

Adjust this section to reflect the actual file tree of the repository.

---

## Limitations

This repository does not implement a full quantum algorithm for fully dynamic shortest paths.  
It also does not provide:

- quantum complexity analysis,
- large-scale empirical benchmarking,
- execution on real quantum hardware,
- claims of algorithmic advantage.

Its primary value lies in offering a clear, reproducible, and formally motivated framework for studying **multi-state quantum representations of dynamic graph problems**.

---

## Future directions

Natural extensions of this work include:

- scaling the experiments to larger graph instances;
- considering longer update sequences;
- introducing qudits with dimension $d > 3$;
- incorporating richer edge-state semantics;
- extending the approach to other dynamic graph problems, such as connectivity, matching, or maintenance of components;
- investigating local qutrit update operators instead of full snapshot re-preparation.

---

## Citation

If you use this repository in academic work, please cite the corresponding paper, manuscript, or repository record.

Suggested BibTeX entry:

```bibtex
@misc{modeling_qutrit_dynamic_graph,
  title={Shortest Path Modeling in Dynamic Graphs with Qutrit Encoding},
  author={Caface, Clovis and Ramos, Diogo and Freitas, Gisele},
  url={https://github.com/mephessivolc/Modeling-Qutrit-to-Dynamic-Graph/tree/main},
  year={2026},
  note={GitHub repository}
}
```

---

## License

This repository is distributed under the terms of the **MIT License**.

For the full license text, see the [LICENSE](LICENSE) file.

---

## Author

Repository maintained by **Clovis Caface**.