#!/usr/bin/env python3

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PREFIX_LENGTHS = [8, 16, 24, 32, 40, 48, 56, 64]


def load_samples(path: Path, sample_bytes: int) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)

    if data.size % sample_bytes != 0:
        raise ValueError(
            f"{path} não contém um número inteiro de amostras "
            f"de {sample_bytes} bytes."
        )

    return data.reshape((-1, sample_bytes))


def row_view(samples: np.ndarray) -> np.ndarray:
    contiguous = np.ascontiguousarray(samples)
    row_size = contiguous.dtype.itemsize * contiguous.shape[1]

    return contiguous.view(
        np.dtype((np.void, row_size))
    ).reshape(-1)


def unique_prefix_fraction(
    samples: np.ndarray,
    prefix_bits: int,
) -> float:
    prefix_bytes = (prefix_bits + 7) // 8
    prefixes = samples[:, :prefix_bytes].copy()

    remaining_bits = prefix_bits % 8

    if remaining_bits:
        mask = (0xFF << (8 - remaining_bits)) & 0xFF
        prefixes[:, -1] &= mask

    unique_count = np.unique(row_view(prefixes)).size
    return unique_count / samples.shape[0]


def collision_count(samples: np.ndarray) -> int:
    unique_count = np.unique(row_view(samples)).size
    return int(samples.shape[0] - unique_count)


def hamming_distances(samples: np.ndarray) -> np.ndarray:
    if samples.shape[0] < 2:
        return np.array([], dtype=np.int32)

    differences = np.bitwise_xor(samples[1:], samples[:-1])

    return np.unpackbits(
        differences,
        axis=1,
    ).sum(axis=1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera gráficos comparativos dos datasets."
    )

    parser.add_argument(
        "--uniform",
        type=Path,
        default=Path("data/uniform_reference.bin"),
    )

    parser.add_argument(
        "--reduced",
        type=Path,
        default=Path("data/reduced_state.bin"),
    )

    parser.add_argument(
        "--sample-bytes",
        type=int,
        default=32,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/entropy_comparison.png"),
    )

    args = parser.parse_args()

    uniform = load_samples(args.uniform, args.sample_bytes)
    reduced = load_samples(args.reduced, args.sample_bytes)

    uniform_bits = np.unpackbits(uniform, axis=1)
    reduced_bits = np.unpackbits(reduced, axis=1)

    uniform_bit_rates = uniform_bits.mean(axis=0)
    reduced_bit_rates = reduced_bits.mean(axis=0)

    uniform_hamming = hamming_distances(uniform)
    reduced_hamming = hamming_distances(reduced)

    uniform_prefixes = [
        unique_prefix_fraction(uniform, prefix_bits)
        for prefix_bits in PREFIX_LENGTHS
    ]

    reduced_prefixes = [
        unique_prefix_fraction(reduced, prefix_bits)
        for prefix_bits in PREFIX_LENGTHS
    ]

    uniform_collisions = collision_count(uniform)
    reduced_collisions = collision_count(reduced)

    figure, axes = plt.subplots(
        2,
        2,
        figsize=(14, 9),
        constrained_layout=True,
    )

    bit_positions = np.arange(args.sample_bytes * 8)

    axes[0, 0].plot(
        bit_positions,
        uniform_bit_rates,
        linewidth=1,
        label="Referência uniforme",
    )

    axes[0, 0].plot(
        bit_positions,
        reduced_bit_rates,
        linewidth=1,
        alpha=0.8,
        label="Estado reduzido",
    )

    axes[0, 0].axhline(
        0.5,
        color="black",
        linestyle="--",
        linewidth=1,
    )

    axes[0, 0].set_title("Proporção de bits 1 por posição")
    axes[0, 0].set_xlabel("Posição do bit")
    axes[0, 0].set_ylabel("Proporção de bits 1")
    axes[0, 0].set_ylim(0.47, 0.53)
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.2)

    bins = np.arange(
        0,
        args.sample_bytes * 8 + 2,
        2,
    )

    axes[0, 1].hist(
        uniform_hamming,
        bins=bins,
        density=True,
        alpha=0.6,
        label="Referência uniforme",
    )

    axes[0, 1].hist(
        reduced_hamming,
        bins=bins,
        density=True,
        alpha=0.6,
        label="Estado reduzido",
    )

    axes[0, 1].set_title("Distância de Hamming entre amostras consecutivas")
    axes[0, 1].set_xlabel("Quantidade de bits diferentes")
    axes[0, 1].set_ylabel("Densidade")
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.2)

    axes[1, 0].plot(
        PREFIX_LENGTHS,
        uniform_prefixes,
        marker="o",
        label="Referência uniforme",
    )

    axes[1, 0].plot(
        PREFIX_LENGTHS,
        reduced_prefixes,
        marker="o",
        label="Estado reduzido",
    )

    axes[1, 0].set_title("Fração de prefixos distintos")
    axes[1, 0].set_xlabel("Tamanho do prefixo em bits")
    axes[1, 0].set_ylabel("Prefixos únicos / amostras")
    axes[1, 0].set_ylim(0, 1.05)
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.2)

    labels = ["Referência uniforme", "Estado reduzido"]
    values = [uniform_collisions, reduced_collisions]
    colors = ["#4C78A8", "#F58518"]

    bars = axes[1, 1].bar(
        labels,
        values,
        color=colors,
    )

    axes[1, 1].set_title("Observações duplicadas completas")
    axes[1, 1].set_ylabel("Quantidade")

    for bar, value in zip(bars, values):
        axes[1, 1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,}".replace(",", "."),
            ha="center",
            va="bottom",
        )

    axes[1, 1].grid(axis="y", alpha=0.2)

    figure.suptitle(
        "Saída visualmente aleatória não garante estado interno suficiente",
        fontsize=16,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)

    figure.savefig(
        args.output,
        dpi=180,
        bbox_inches="tight",
    )

    print(f"Gráfico salvo em {args.output}")


if __name__ == "__main__":
    main()
