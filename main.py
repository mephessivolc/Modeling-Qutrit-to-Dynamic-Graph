from __future__ import annotations

"""
Toy model híbrido para caminhos mínimos em grafos dinâmicos com qutrits.

O script implementa:
1. Representação ternária de arestas: 0=ausente, 1=ativa, 2=restrita.
2. Preparação de snapshots em um registrador de qutrits com PennyLane.
3. Decodificação do snapshot a partir de qml.probs.
4. Projeção do grafo admissível (apenas arestas ativas).
5. Consulta clássica de caminho mínimo via Dijkstra.
6. Baseline clássico-oráculo para comparação de correção.
7. Métricas simples de concordância e relatório representacional.

Requisitos:
    pip install pennylane numpy

Observação:
    Este toy model re-prepara o snapshot completo a cada atualização.
    Isso é intencional: a meta é validar a modelagem, não otimizar o circuito.
"""

from dataclasses import dataclass
from math import inf, isclose
import heapq
from typing import Any, Iterable, Sequence

import numpy as np

try:
    import pennylane as qml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PennyLane não está instalado. Execute: pip install pennylane"
    ) from exc

Vertex = Any
Edge = tuple[Vertex, Vertex]

STATE_LABELS = {
    0: "ausente",
    1: "ativa",
    2: "restrita",
}


@dataclass(frozen=True)
class Update:
    """Atualização de uma única aresta para um novo estado ternário."""

    edge: Edge
    new_state: int
    description: str = ""

    def __post_init__(self) -> None:
        if self.new_state not in (0, 1, 2):
            raise ValueError("new_state deve pertencer a {0, 1, 2}.")


class HybridQutritShortestPath:
    """
    Toy model híbrido com qutrits para shortest path dinâmico.

    Parâmetros
    ----------
    vertices:
        Lista de vértices do grafo.
    edges:
        Universo fixo E* de arestas candidatas. A ordem define o mapeamento fio<->aresta.
    weights:
        Dicionário de pesos por aresta.
    initial_sigma:
        Vetor inicial com estados ternários na mesma ordem de `edges`.
    source, target:
        Vértices de consulta do caminho mínimo.
    directed:
        Se False, cada aresta é tratada como bidirecional na consulta clássica.
    measure_probabilities:
        Se True, usa qml.probs para decodificar o snapshot. Se False, usa qml.state.
    """

    def __init__(
        self,
        vertices: Sequence[Vertex],
        edges: Sequence[Edge],
        weights: dict[Edge, float],
        initial_sigma: Sequence[int],
        source: Vertex,
        target: Vertex,
        *,
        directed: bool = True,
        measure_probabilities: bool = True,
    ) -> None:
        self.vertices = list(vertices)
        self.edges = list(edges)
        self.weights = dict(weights)
        self.source = source
        self.target = target
        self.directed = directed
        self.measure_probabilities = measure_probabilities

        if len(initial_sigma) != len(self.edges):
            raise ValueError("initial_sigma deve ter o mesmo tamanho de edges.")
        if any(state not in (0, 1, 2) for state in initial_sigma):
            raise ValueError("Todos os estados em initial_sigma devem pertencer a {0,1,2}.")

        self.num_edges = len(self.edges)
        self.edge_to_index = {edge: i for i, edge in enumerate(self.edges)}
        self.initial_sigma = np.asarray(initial_sigma, dtype=int)

        self._validate_weights()
        self.dev = qml.device("default.qutrit", wires=self.num_edges)
        self._build_qnodes()

    def _validate_weights(self) -> None:
        missing = [e for e in self.edges if e not in self.weights]
        if missing:
            raise ValueError(f"Pesos ausentes para as arestas: {missing}")
        non_positive = [e for e, w in self.weights.items() if w <= 0]
        if non_positive:
            raise ValueError(f"Todos os pesos devem ser positivos. Arestas inválidas: {non_positive}")

    def _prepare_basis_state(self, snapshot: np.ndarray) -> None:
        wires = list(range(self.num_edges))
        if hasattr(qml, "QutritBasisState"):
            qml.QutritBasisState(snapshot, wires=wires)
        else:  # compatibilidade com versões antigas
            qml.QutritBasisStatePreparation(snapshot, wires=wires)

    def _build_qnodes(self) -> None:
        @qml.qnode(self.dev)
        def probs_qnode(snapshot: np.ndarray):
            self._prepare_basis_state(snapshot)
            return qml.probs(wires=range(self.num_edges))

        @qml.qnode(self.dev)
        def state_qnode(snapshot: np.ndarray):
            self._prepare_basis_state(snapshot)
            return qml.state()

        self._probs_qnode = probs_qnode
        self._state_qnode = state_qnode

    def prepare_snapshot(self, snapshot: Sequence[int]) -> np.ndarray:
        """Executa o circuito e retorna probs ou statevector."""
        snapshot_arr = np.asarray(snapshot, dtype=int)
        self._validate_snapshot(snapshot_arr)
        if self.measure_probabilities:
            return np.asarray(self._probs_qnode(snapshot_arr))
        return np.asarray(self._state_qnode(snapshot_arr))

    def _validate_snapshot(self, snapshot: np.ndarray) -> None:
        if snapshot.shape != (self.num_edges,):
            raise ValueError(f"Snapshot deve ter shape ({self.num_edges},), recebeu {snapshot.shape}.")
        if any(s not in (0, 1, 2) for s in snapshot):
            raise ValueError("Snapshot contém estado fora de {0,1,2}.")

    def decode_snapshot(self, measurement: np.ndarray) -> np.ndarray:
        """
        Decodifica o snapshot a partir de probs ou do statevector.

        Para um estado de base preparado exatamente, a maior probabilidade/amplitude
        identifica o índice correspondente ao snapshot ternário.
        """
        if self.measure_probabilities:
            index = int(np.argmax(measurement))
            peak = float(measurement[index])
            if peak < 0.999999:
                print(
                    f"[aviso] A distribuição não é estritamente determinística (pico={peak:.6f}). "
                    "A decodificação usa argmax."
                )
        else:
            probs = np.abs(measurement) ** 2
            index = int(np.argmax(probs))
            peak = float(probs[index])
            if peak < 0.999999:
                print(
                    f"[aviso] O statevector não é estritamente de base (pico={peak:.6f}). "
                    "A decodificação usa argmax."
                )

        return self._base10_to_base3_digits(index, self.num_edges)

    @staticmethod
    def _base10_to_base3_digits(index: int, width: int) -> np.ndarray:
        digits = np.zeros(width, dtype=int)
        for pos in range(width - 1, -1, -1):
            digits[pos] = index % 3
            index //= 3
        return digits

    def project_admissible_edges(self, snapshot: Sequence[int]) -> list[Edge]:
        snapshot_arr = np.asarray(snapshot, dtype=int)
        return [edge for edge, state in zip(self.edges, snapshot_arr, strict=True) if state == 1]

    def build_adjacency(self, admissible_edges: Iterable[Edge]) -> dict[Vertex, list[tuple[Vertex, float]]]:
        adjacency: dict[Vertex, list[tuple[Vertex, float]]] = {v: [] for v in self.vertices}
        for u, v in admissible_edges:
            weight = self.weights[(u, v)]
            adjacency[u].append((v, weight))
            if not self.directed:
                adjacency[v].append((u, weight))
        return adjacency

    def dijkstra(self, admissible_edges: Iterable[Edge]) -> tuple[float, list[Vertex]]:
        adjacency = self.build_adjacency(admissible_edges)
        source, target = self.source, self.target

        dist = {v: inf for v in self.vertices}
        prev: dict[Vertex, Vertex | None] = {v: None for v in self.vertices}
        dist[source] = 0.0
        heap: list[tuple[float, Vertex]] = [(0.0, source)]

        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist > dist[u]:
                continue
            if u == target:
                break
            for v, w in adjacency.get(u, []):
                alt = current_dist + w
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(heap, (alt, v))

        if dist[target] == inf:
            return inf, []

        path: list[Vertex] = []
        cur: Vertex | None = target
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return dist[target], path

    def apply_update(self, snapshot: Sequence[int], update: Update) -> np.ndarray:
        snapshot_arr = np.asarray(snapshot, dtype=int).copy()
        if update.edge not in self.edge_to_index:
            raise KeyError(f"Aresta {update.edge} não pertence a E*.")
        idx = self.edge_to_index[update.edge]
        snapshot_arr[idx] = update.new_state
        return snapshot_arr

    def run_hybrid(self, updates: Sequence[Update]) -> list[dict[str, Any]]:
        """Executa o toy model híbrido do instante 0 até após a última atualização."""
        results: list[dict[str, Any]] = []
        snapshot = self.initial_sigma.copy()

        for step in range(len(updates) + 1):
            measurement = self.prepare_snapshot(snapshot)
            decoded = self.decode_snapshot(measurement)
            admissible = self.project_admissible_edges(decoded)
            distance, path = self.dijkstra(admissible)
            results.append(
                {
                    "step": step,
                    "snapshot": snapshot.copy(),
                    "decoded": decoded,
                    "admissible_edges": admissible,
                    "distance": distance,
                    "path": path,
                }
            )
            if step < len(updates):
                snapshot = self.apply_update(snapshot, updates[step])
        return results

    def run_classical_oracle(self, updates: Sequence[Update]) -> list[dict[str, Any]]:
        """Baseline clássico: aplica as mesmas atualizações e recomputa do zero."""
        results: list[dict[str, Any]] = []
        snapshot = self.initial_sigma.copy()

        for step in range(len(updates) + 1):
            admissible = self.project_admissible_edges(snapshot)
            distance, path = self.dijkstra(admissible)
            results.append(
                {
                    "step": step,
                    "snapshot": snapshot.copy(),
                    "admissible_edges": admissible,
                    "distance": distance,
                    "path": path,
                }
            )
            if step < len(updates):
                snapshot = self.apply_update(snapshot, updates[step])
        return results

    def evaluate(self, updates: Sequence[Update]) -> dict[str, Any]:
        hybrid = self.run_hybrid(updates)
        classical = self.run_classical_oracle(updates)

        distance_matches = 0
        path_matches = 0
        comparable_paths = 0
        all_rows: list[dict[str, Any]] = []

        for q_row, c_row in zip(hybrid, classical, strict=True):
            q_dist = q_row["distance"]
            c_dist = c_row["distance"]
            dist_equal = (q_dist == inf and c_dist == inf) or isclose(q_dist, c_dist, rel_tol=1e-12, abs_tol=1e-12)
            if dist_equal:
                distance_matches += 1

            q_path = q_row["path"]
            c_path = c_row["path"]
            path_equal = q_path == c_path
            if q_path or c_path:
                comparable_paths += 1
                if path_equal:
                    path_matches += 1

            all_rows.append(
                {
                    "step": q_row["step"],
                    "snapshot": q_row["snapshot"].tolist(),
                    "decoded": q_row["decoded"].tolist(),
                    "distance_qutrit": q_dist,
                    "distance_classical": c_dist,
                    "distance_match": dist_equal,
                    "path_qutrit": q_path,
                    "path_classical": c_path,
                    "path_match": path_equal,
                }
            )

        total_steps = len(hybrid)
        return {
            "hybrid": hybrid,
            "classical": classical,
            "rows": all_rows,
            "distance_accuracy": distance_matches / total_steps,
            "path_accuracy": (path_matches / comparable_paths) if comparable_paths else 1.0,
            "num_steps": total_steps,
            "representation_report": self.representation_report(),
        }

    def representation_report(self) -> dict[str, int]:
        """Comparação representacional simples por aresta e no registrador inteiro."""
        n = self.num_edges
        return {
            "num_edges": n,
            "qutrit_units": n,
            "one_hot_bits": 3 * n,
            "compact_binary_bits": 2 * n,
            "invalid_compact_codes_per_edge": 1,
            "valid_codes_per_edge": 3,
            "all_compact_codes_per_edge": 4,
        }

    def print_trace(self, evaluation: dict[str, Any]) -> None:
        print("=" * 80)
        print("Traço do toy model híbrido vs. baseline clássico")
        print("=" * 80)
        for row in evaluation["rows"]:
            snapshot = row["snapshot"]
            labels = [STATE_LABELS[s] for s in snapshot]
            dist_q = row["distance_qutrit"]
            dist_c = row["distance_classical"]
            path_q = row["path_qutrit"] or "sem caminho"
            path_c = row["path_classical"] or "sem caminho"
            print(f"step={row['step']:>2} | sigma={snapshot} | estados={labels}")
            print(f"       qutrit : dist={dist_q} | caminho={path_q}")
            print(f"       classic: dist={dist_c} | caminho={path_c}")
            print(f"       match? distance={row['distance_match']} | path={row['path_match']}")
        print("-" * 80)
        print(f"distance_accuracy = {evaluation['distance_accuracy']:.3f}")
        print(f"path_accuracy     = {evaluation['path_accuracy']:.3f}")
        print(f"representation    = {evaluation['representation_report']}")


def demo_instance() -> tuple[HybridQutritShortestPath, list[Update]]:
    """Instância pequena coerente com o exemplo do artigo."""
    vertices = ["s", "a", "b", "c", "t"]
    edges = [
        ("s", "a"),
        ("a", "c"),
        ("c", "t"),
        ("s", "b"),
        ("b", "t"),
        ("a", "t"),
    ]
    weights = {
        ("s", "a"): 1.0,
        ("a", "c"): 2.0,
        ("c", "t"): 2.0,
        ("s", "b"): 2.0,
        ("b", "t"): 2.0,
        ("a", "t"): 4.0,
    }
    # sigma0 = (1,1,1,1,0,2)
    initial_sigma = [1, 1, 1, 1, 0, 2]

    model = HybridQutritShortestPath(
        vertices=vertices,
        edges=edges,
        weights=weights,
        initial_sigma=initial_sigma,
        source="s",
        target="t",
        directed=True,
        measure_probabilities=True,
    )

    updates = [
        Update(("b", "t"), 1, "ativa (b,t), abrindo rota curta"),
        Update(("a", "c"), 2, "restringe (a,c), bloqueando rota anterior"),
        Update(("a", "t"), 1, "ativa ligação direta (a,t)"),
        Update(("s", "b"), 0, "remove (s,b)"),
    ]
    return model, updates


def main() -> None:
    model, updates = demo_instance()
    evaluation = model.evaluate(updates)
    model.print_trace(evaluation)


if __name__ == "__main__":
    main()
