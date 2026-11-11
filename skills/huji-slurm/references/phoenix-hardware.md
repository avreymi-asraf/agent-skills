# Phoenix & Cinder Hardware

Source: [Phoenix cluster policy](https://wiki.cs.huji.ac.il/wiki/Phoenix_cluster_policy), fetched 2026-10-31. GPU groups exist since 2025-03-18. Every September, nodes older than 7 years move from phoenix to cinder, so this table changes yearly. Check the live state with `sinfo -o '%N %c %m %G'` or `ssinfo`.

CPU column = total (sockets:cores:threads). GPU column = count × type (VRAM, group).

## phoenix

| Nodes | # | CPU | RAM | GPU |
|---|---|---|---|---|
| ampere-01 | 1 | 32 (8:4:1) | 375.7G | 8 a10 (22G, g0) |
| arion-[01-02] | 2 | 128 (2:64:1) | 501.7G | 8 a10 (22G, g0) |
| binky-[01-05] | 5 | 48 (8:6:1) | 501.7G | 8 a5000 (24G, g0) |
| creek-[01-04] | 4 | 72 (2:18:2) | 247.5G | 8 rtx2080 (10G, g0) |
| cyril-01 | 1 | 128 (2:64:1) | 501.7G | 8 a6000 (48G, g4) |
| drape-[01-03] | 3 | 128 (2:64:1) | 501.7G | 8 a5000 (24G, g0) |
| dumfries-004, -010 | 2 | 32 (2:8:2) | 123.5G | 4 rtx2080 (10G, g0) |
| dumfries-[005-006], [008-009] | 4 | 32 (2:8:2) | 123.5G | 3 rtx2080 (10G, g0) |
| dumfries-007 | 1 | 32 (2:8:2) | 123.5G | 1 rtx2080 (10G, g0) |
| epona-[01-02] | 2 | 128 (2:64:1) | 501.6G | 8 a40 (45G, g4) |
| firefoot-[01-07] | 7 | 64 (2:32:1) | 995.6G | 8 l40s (45G, g4) |
| firefoot-[08-17] | 10 | 64 (2:32:1) | 1.5T | 8 l40s (45G, g4) |
| firth-[01-02] | 2 | 40 (2:10:2) | 374.6G | 8 rtx6000 (24G, g0) |
| gringolet-[01-06] | 6 | 128 (2:64:1) | 1.0T | — (CPU only) |
| hasufel-[01-02] | 2 | 64 (2:32:1) | 1.0T | 8 l4 (23G, g0) |
| incitatus-[01-02] | 2 | 64 (2:32:1) | 1.0T | 8 l4 (23G, g0) |
| joey-01 | 1 | 128 (2:64:1) | 1.8T | 8 h200 (140G, g10) |
| khan-[01-02] | 2 | 128 (2:64:1) | 1.1T | 8 rtxpro6000 (96G, g4) |
| wadi-[01-05] | 5 | 128 (2:32:2) | 501.7G | — (CPU only) |

Totals: 62 nodes, 5024 CPUs, 47.53T RAM, 373 GPUs.

## GPU totals by type (phoenix)

| Type | VRAM | Group | Count | `--gres` |
|---|---|---|---|---|
| rtx2080 | 10G | g0 | 53 | `gpu:rtx2080:1` |
| a10 | 22G | g0 | 24 | `gpu:a10:1` |
| l4 | 23G | g0 | 32 | `gpu:l4:1` |
| a5000 | 24G | g0 | 64 | `gpu:a5000:1` |
| rtx6000 | 24G | g0 | 16 | `gpu:rtx6000:1` |
| a40 | 45G | g4 | 16 | `gpu:a40:1` |
| l40s | 45G | g4 | 136 | `gpu:l40s:1` |
| a6000 | 48G | g4 | 8 | `gpu:a6000:1` |
| rtxpro6000 | 96G | g4 | 16 | `gpu:rtxpro6000:1` |
| h200 | 140G | g10 | 8 | `gpu:h200:1` |

Groups: g0 = 189 GPUs (≤ 40G), g4 = 176 (40–100G), g10 = 8 (> 100G). Request a group with `--gres=gg:g4:1`. The type names in the `--gres` column follow the wiki's spelling; confirm with `sinfo -o '%G'`.

Choosing:
- Debug / small eval: any g0 (`gg:g0:1`) — biggest pool, shortest wait.
- 24G is enough (QLoRA ≤ 8B, inference of 7B in bf16): `gg:g0:1`, but rtx2080 (10G) is also in g0. If 10G is too little, ask for a type (`gpu:a5000:1`) — or try `vmem` (unverified with groups).
- 45G class (bf16 LoRA on 8B, 13B QLoRA): `gpu:l40s:1` (136 cards, the deepest g4 pool).
- 96–140G: rtxpro6000 or h200; very few cards, expect long waits.
- bf16 / FlashAttention-2 need Ampere or newer. In g0, **rtx2080 and rtx6000 are Turing (no bf16)**, so a plain `gg:g0:1` may land on one: for bf16 training ask for a type (`gpu:a5000:1`, `gpu:l4:1`, `gpu:a10:1`) or use fp16. All cinder GPUs are pre-Ampere.

## cinder (old nodes, same policy, no GPU groups)

| Nodes | # | CPU | RAM | GPU |
|---|---|---|---|---|
| cb-[06,08,10,14,19] | 5 | 16 (2:4:2) | 60.8G | — |
| cortex-01, [03-05] | 4 | 16 (2:8:1) | 249.8G | 8 m60 (8G) |
| cortex-02 | 1 | 16 (2:8:1) | 249.8G | 6 m60 (8G) |
| cortex-[06-08] | 3 | 24 (2:12:1) | 249.8G | 8 m60 (8G) |
| dumfries-001/002/003 | 3 | 32 (2:8:2) | 123.5G | 4/3/2 rtx2080 (10G) |
| gsm-01 | 1 | 32 (2:8:2) | 249.8G | — |
| gsm-[03-04] | 2 | 32 (2:8:2) | 249.8G | 3 black (6G) |
| lucy-[02-03] | 2 | 48 (2:12:2) | 375.7G | 2 gtx980 (4G) |
| ohm-[54-64] | 11 | 48 (2:12:2) | 245.8G | — |
| oxygen-[01-08] | 8 | 48 (2:12:2) | 247.8G | — |
| sed-[01-04,07-11] | 9 | 20 (2:10:1) | 245.8G | — |
| sm-16 | 1 | 16 (2:4:2) | 185.9G | — |
| sm-[01-04,08] | 5 | 16 (2:4:2) | 44.1G | — |
| sm-[17-18,20] | 3 | 24 (2:6:2) | 59.8G | — |

Totals: 58 nodes, 1780 CPUs, 11.38T RAM, 81 GPUs. Useful for CPU-only work (preprocessing, CPU evals): `sbatch -M cinder ...`.

Other CS clusters named on the wiki (`hm`, `blaise` — ppc64le, `astro`, BioCompute) have their own access rules and are out of scope here.
