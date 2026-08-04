#!/usr/bin/env python3

import argparse
import json
import math
import zlib
from pathlib import Path

import numpy as np


PREFIX_LENGTHS = [8, 16, 24, 32, 40, 48, 56, 64]


def load_samples(path: Path, sample_bytes: int) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)

    if data.size == 0:
        raise ValueError(f"Arquivo vazio: {path}")

    if data.size % sample_bytes != 0:
        raise ValueError(
            f"O arquivo possui {data.size} bytes, "
            f"valor incompatível com registros de {sample_bytes} bytes."
        )

    return data.reshape((-1, sample_bytes))


def shannon_entropy(counts: np.ndarray) -> float:
    total = counts.sum()

    if total == 0:
        return 0.0

    probabilities = counts[counts > 0] / total
    return float(-np.sum(probabilities * np.log2(probabilities)))


def min_entropy_from_counts(counts: np.ndarray) -> float:
    total = counts.sum()

    if total == 0:
        return 0.0

    maximum_probability = counts.max() / total
    return float(-math.log2(maximum_probability))


def row_view(samples: np.ndarray) -> np.ndarray:
    contiguous = np.ascontiguousarray(samples)
    row_size = contiguous.dtype.itemsize * contiguous.shape[1]

    return contiguous.view(
        np.dtype((np.void, row_size))
    ).reshape(-1)


def prefix_unique_count(samples: np.ndarray, prefix_bits: int) -> int:
    prefix_bytes = (prefix_bits + 7) // 8
    prefixes = samples[:, :prefix_bytes].copy()

    remaining_bits = prefix_bits % 8

    if remaining_bits:
        mask = (0xFF << (8 - remaining_bits)) & 0xFF
        prefixes[:, -1] &= mask

    return int(np.unique(row_view(prefixes)).size)


def analyze_samples(samples: np.ndarray) -> dict:
    sample_count, sample_bytes = samples.shape
    flat_bytes = samples.reshape(-1)

    global_byte_counts = np.bincount(flat_bytes, minlength=256)

    position_entropies = []
    position_min_entropies = []

    for position in range(sample_bytes):
        counts = np.bincount(samples[:, position], minlength=256)
        position_entropies.append(shannon_entropy(counts))
        position_min_entropies.append(min_entropy_from_counts(counts))

    bits = np.unpackbits(samples, axis=1)
    flat_bits = bits.reshape(-1)

    ones = int(flat_bits.sum())
    total_bits = int(flat_bits.size)
    zeros = total_bits - ones

    ones_rate = ones / total_bits
    monobit_z_score = (ones - zeros) / math.sqrt(total_bits)

    if flat_bytes.size > 1:
        first = flat_bytes[:-1].astype(np.float64)
        second = flat_bytes[1:].astype(np.float64)

        serial_correlation = float(np.corrcoef(first, second)[0, 1])
    else:
        serial_correlation = 0.0

    unique_rows, counts = np.unique(
        row_view(samples),
        return_counts=True,
    )

    unique_samples = int(unique_rows.size)
    duplicated_values = int(np.count_nonzero(counts > 1))
    repeated_observations = int(sample_count - unique_samples)
    maximum_multiplicity = int(counts.max())

    collision_pairs = int(
        np.sum(counts.astype(np.int64) * (counts.astype(np.int64) - 1) // 2)
    )

    if collision_pairs > 0:
        effective_state_space = (
            sample_count * (sample_count - 1)
        ) / (2 * collision_pairs)

        estimated_effective_bits = math.log2(effective_state_space)
    else:
        effective_state_space = None
        estimated_effective_bits = None

    if sample_count > 1:
        consecutive_xor = np.bitwise_xor(samples[1:], samples[:-1])
        hamming_distances = np.unpackbits(
            consecutive_xor,
            axis=1,
        ).sum(axis=1)

        hamming_summary = {
            "mean": float(hamming_distances.mean()),
            "standard_deviation": float(hamming_distances.std()),
            "minimum": int(hamming_distances.min()),
            "maximum": int(hamming_distances.max()),
        }
    else:
        hamming_summary = {
            "mean": None,
            "standard_deviation": None,
            "minimum": None,
            "maximum": None,
        }

    raw_bytes = samples.tobytes()
    compressed_bytes = zlib.compress(raw_bytes, level=9)

    prefix_results = {}

    for prefix_bits in PREFIX_LENGTHS:
        if prefix_bits <= sample_bytes * 8:
            unique_prefixes = prefix_unique_count(samples, prefix_bits)

            prefix_results[str(prefix_bits)] = {
                "unique": unique_prefixes,
                "duplicate_observations": sample_count - unique_prefixes,
                "unique_fraction": unique_prefixes / sample_count,
            }

    bit_one_rate_by_position = bits.mean(axis=0)

    report = {
        "sample_count": sample_count,
        "sample_bytes": sample_bytes,
        "sample_bits": sample_bytes * 8,
        "global_byte_shannon_entropy": shannon_entropy(global_byte_counts),
        "byte_entropy_by_position": {
            "mean": float(np.mean(position_entropies)),
            "minimum": float(np.min(position_entropies)),
            "maximum": float(np.max(position_entropies)),
        },
        "byte_min_entropy_by_position": {
            "mean": float(np.mean(position_min_entropies)),
            "minimum": float(np.min(position_min_entropies)),
            "maximum": float(np.max(position_min_entropies)),
        },
        "bit_statistics": {
            "total_bits": total_bits,
            "ones": ones,
            "zeros": zeros,
            "ones_rate": ones_rate,
            "monobit_z_score": monobit_z_score,
            "maximum_position_bias": float(
                np.max(np.abs(bit_one_rate_by_position - 0.5))
            ),
        },
        "serial_byte_correlation": serial_correlation,
        "compression": {
            "original_bytes": len(raw_bytes),
            "compressed_bytes": len(compressed_bytes),
            "compression_ratio": len(compressed_bytes) / len(raw_bytes),
        },
        "collisions": {
            "unique_samples": unique_samples,
            "duplicated_values": duplicated_values,
            "repeated_observations": repeated_observations,
            "collision_pairs": collision_pairs,
            "maximum_multiplicity": maximum_multiplicity,
            "estimated_effective_state_space": effective_state_space,
            "estimated_effective_bits": estimated_effective_bits,
        },
        "consecutive_hamming_distance": hamming_summary,
        "prefixes": prefix_results,
    }

    return report


def print_summary(path: Path, report: dict) -> None:
    collisions = report["collisions"]

    print()
    print("=" * 72)
    print(path)
    print("=" * 72)

    print(f"Amostras:                 {report['sample_count']}")
    print(f"Bytes por amostra:        {report['sample_bytes']}")

    print(
        "Entropia global/byte:     "
        f"{report['global_byte_shannon_entropy']:.6f} bits"
    )

    print(
        "Proporção de bits 1:      "
        f"{report['bit_statistics']['ones_rate']:.6f}"
    )

    print(
        "Correlação serial:        "
        f"{report['serial_byte_correlation']:.6f}"
    )

    print(
        "Razão após compressão:    "
        f"{report['compression']['compression_ratio']:.6f}"
    )

    print(f"Amostras únicas:          {collisions['unique_samples']}")
    print(f"Observações repetidas:    {collisions['repeated_observations']}")
    print(f"Pares de colisão:         {collisions['collision_pairs']}")
    print(f"Maior multiplicidade:     {collisions['maximum_multiplicity']}")

    if collisions["estimated_effective_bits"] is not None:
        print(
            "Estado efetivo estimado: "
            f"{collisions['estimated_effective_bits']:.2f} bits"
        )
    else:
        print("Estado efetivo estimado: sem colisões suficientes")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analisa propriedades estatísticas de amostras binárias."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Arquivo binário contendo amostras concatenadas.",
    )

    parser.add_argument(
        "--sample-bytes",
        type=int,
        default=32,
        help="Quantidade de bytes por amostra.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Arquivo JSON onde o relatório será salvo.",
    )

    args = parser.parse_args()

    samples = load_samples(args.input, args.sample_bytes)
    report = analyze_samples(samples)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as output_file:
        json.dump(report, output_file, indent=2, ensure_ascii=False)

    print_summary(args.input, report)
    print()
    print(f"Relatório salvo em {args.output}")


if __name__ == "__main__":
    main()
