import re

def normalize_gpu_name(full_name: str) -> str:
    full_name = re.sub(
        r"(NVIDIA|AMD|Intel|Palit|MSI|ASUS|Gigabyte|Sapphire|PowerColor|Gainward|Zotac|KFA2|Inno3D|GamingPro|GAMING|OC|VENTUS|EAGLE|TUF|STRIX|Dual|Turbo|Phoenix|Fighter|Nitro\+?|Pulse|Challenger|Hellhound|Red Devil|XLR8|JetStream|GameRock|Edition|Ret)",
        "",
        full_name,
        flags=re.I
    )
    full_name = re.sub(r"(\d)(Ti|SUPER|XT|XTX|Ultra)", r"\1 \2", full_name, flags=re.I)
    full_name = full_name.replace("-", " ")
    full_name = re.sub(r"\s+", " ", full_name).strip()

    patterns = [
        r"(GeForce\s+RTX\s+\d{3,4}\s*(Ti|SUPER|Ultra)?)",
        r"(GeForce\s+GTX\s+\d{3,4}\s*(Ti)?)",
        r"(Radeon\s+RX\s+\d{3,4}\s*(XT|XTX)?)",
        r"(Arc\s+A\d{3}\s*(Pro)?)",
    ]

    for p in patterns:
        m = re.search(p, full_name, re.IGNORECASE)
        if m:
            name = m.group(1)
            name = (
                name.replace("ti", "Ti")
                    .replace("super", "SUPER")
                    .replace("xtx", "XTX")
                    .replace("xt", "XT")
                    .replace("ultra", "Ultra")
            )

            name = re.sub(r"\s+", " ", name).strip()

            return name

    return full_name