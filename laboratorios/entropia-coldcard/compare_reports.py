#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def read_report(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as input_file:
        return json.load(input_file)


def format_number(value, digits=6):
    if value is None:
        return "—"

    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")

    return f"{value:.{digits}f}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compara dois relatórios de análise de entropia."
    )

    parser.add_argument(
        "--uniform",
        type=Path,
        default=Path("results/uniform_report.json"),
    )

    parser.add_argument(
        "--reduced",
        type=Path,
        default=Path("results/reduced_report.json"),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/summary.md"),
    )

    args = parser.parse_args()

    uniform = read_report(args.uniform)
    reduced = read_report(args.reduced)

    rows = [
        (
            "Entropia global por byte",
            format_number(uniform["global_byte_shannon_entropy"]),
            format_number(reduced["global_byte_shannon_entropy"]),
        ),
        (
            "Proporção de bits 1",
            format_number(uniform["bit_statistics"]["ones_rate"]),
            format_number(reduced["bit_statistics"]["ones_rate"]),
        ),
        (
            "Correlação serial",
            format_number(uniform["serial_byte_correlation"]),
            format_number(reduced["serial_byte_correlation"]),
        ),
        (
            "Razão após compressão",
            format_number(uniform["compression"]["compression_ratio"]),
            format_number(reduced["compression"]["compression_ratio"]),
        ),
        (
            "Amostras únicas",
            format_number(uniform["collisions"]["unique_samples"]),
            format_number(reduced["collisions"]["unique_samples"]),
        ),
        (
            "Observações repetidas",
            format_number(uniform["collisions"]["repeated_observations"]),
            format_number(reduced["collisions"]["repeated_observations"]),
        ),
        (
            "Pares de colisão",
            format_number(uniform["collisions"]["collision_pairs"]),
            format_number(reduced["collisions"]["collision_pairs"]),
        ),
        (
            "Estado efetivo estimado",
            (
                format_number(
                    uniform["collisions"]["estimated_effective_bits"],
                    digits=2,
                )
                + " bits"
                if uniform["collisions"]["estimated_effective_bits"] is not None
                else "sem colisões"
            ),
            (
                format_number(
                    reduced["collisions"]["estimated_effective_bits"],
                    digits=2,
                )
                + " bits"
                if reduced["collisions"]["estimated_effective_bits"] is not None
                else "sem colisões"
            ),
        ),
    ]

    lines = [
        "| Métrica | Referência uniforme | Estado reduzido |",
        "|---|---:|---:|",
    ]

    for metric, uniform_value, reduced_value in rows:
        lines.append(
            f"| {metric} | {uniform_value} | {reduced_value} |"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(f"Tabela criada em {args.output}")


if __name__ == "__main__":
    main()
