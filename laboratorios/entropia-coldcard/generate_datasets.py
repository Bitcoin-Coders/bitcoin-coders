#!/usr/bin/env python3

import argparse
import hashlib
import json
import random
from pathlib import Path


DOMAIN_TAG = b"bitcoin-coders-synthetic-entropy-lab-v1"


def expand_reduced_state(state: int, state_bits: int, output_bytes: int) -> bytes:
    """
    Expande um estado sintético pequeno para uma saída maior.

    Este modelo NÃO representa a implementação da COLDCARD.
    Ele serve apenas para demonstrar que uma saída pode parecer
    aleatória mesmo tendo sido originada de pouco estado interno.
    """
    state_size = max(1, (state_bits + 7) // 8)
    state_bytes = state.to_bytes(state_size, byteorder="big")

    output = bytearray()
    counter = 0

    while len(output) < output_bytes:
        block = hashlib.sha256(
            DOMAIN_TAG
            + state_bits.to_bytes(2, byteorder="big")
            + state_bytes
            + counter.to_bytes(4, byteorder="big")
        ).digest()

        output.extend(block)
        counter += 1

    return bytes(output[:output_bytes])


def generate_uniform_reference(
    output_path: Path,
    sample_count: int,
    sample_bytes: int,
    seed: int,
) -> None:
    """
    Gera uma referência uniforme e reproduzível para comparação estatística.

    random.Random não é usado como gerador criptográfico.
    Aqui ele serve exclusivamente como fonte sintética reproduzível.
    """
    rng = random.Random(seed)

    with output_path.open("wb") as output_file:
        for _ in range(sample_count):
            sample = bytes(rng.getrandbits(8) for _ in range(sample_bytes))
            output_file.write(sample)


def generate_reduced_state(
    output_path: Path,
    sample_count: int,
    sample_bytes: int,
    state_bits: int,
    seed: int,
) -> None:
    rng = random.Random(seed)

    state_space = 1 << state_bits

    with output_path.open("wb") as output_file:
        for _ in range(sample_count):
            state = rng.randrange(state_space)
            sample = expand_reduced_state(
                state=state,
                state_bits=state_bits,
                output_bytes=sample_bytes,
            )
            output_file.write(sample)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera datasets sintéticos para análise de entropia."
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=50_000,
        help="Quantidade de amostras em cada dataset.",
    )

    parser.add_argument(
        "--sample-bytes",
        type=int,
        default=32,
        help="Quantidade de bytes por amostra.",
    )

    parser.add_argument(
        "--state-bits",
        type=int,
        default=20,
        help="Tamanho do estado interno do modelo degradado.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=20260730,
        help="Seed usada somente para reprodutibilidade do experimento.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
        help="Diretório onde os datasets serão armazenados.",
    )

    args = parser.parse_args()

    if args.samples <= 1:
        raise SystemExit("--samples deve ser maior que 1.")

    if args.sample_bytes <= 0:
        raise SystemExit("--sample-bytes deve ser maior que zero.")

    if not 1 <= args.state_bits <= 64:
        raise SystemExit("--state-bits deve estar entre 1 e 64.")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    uniform_path = args.output_dir / "uniform_reference.bin"
    reduced_path = args.output_dir / "reduced_state.bin"

    print("[1/2] Gerando referência uniforme...")
    generate_uniform_reference(
        output_path=uniform_path,
        sample_count=args.samples,
        sample_bytes=args.sample_bytes,
        seed=args.seed,
    )

    print("[2/2] Gerando modelo com estado reduzido...")
    generate_reduced_state(
        output_path=reduced_path,
        sample_count=args.samples,
        sample_bytes=args.sample_bytes,
        state_bits=args.state_bits,
        seed=args.seed ^ 0xC01DC4AD,
    )

    metadata = {
        "experiment": "synthetic entropy reduction",
        "warning": (
            "Modelo sintético. Não representa nem reproduz "
            "o algoritmo real de qualquer hardware wallet."
        ),
        "samples_per_dataset": args.samples,
        "sample_bytes": args.sample_bytes,
        "reduced_state_bits": args.state_bits,
        "uniform_reference_file": str(uniform_path),
        "reduced_state_file": str(reduced_path),
    }

    metadata_path = args.output_dir / "metadata.json"

    with metadata_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)

    print()
    print("Datasets criados:")
    print(f"  {uniform_path}")
    print(f"  {reduced_path}")
    print(f"  {metadata_path}")


if __name__ == "__main__":
    main()
