"""A legegyszerűbb Jev + Opus 5.5 példa: a Jev dönt, az Opus gondolkodik.

Telepítés:  uv sync
Kulcsok:    export TYPESAFE_API_KEY=...   ANTHROPIC_API_KEY=...
Futtatás:   uv run jev_opus.py "Írj egy Python függvényt, ami eldönti, hogy egy szám prím-e"
"""

import sys

import anthropic
from typesafe_sdk import Choice, Noul, TypeSafeClient

jev = TypeSafeClient(model="jev-1.14.0")  # TYPESAFE_API_KEY-t olvassa
claude = anthropic.Anthropic()            # ANTHROPIC_API_KEY-t olvassa

# Amire nem kell gondolkodni, arra a kód válaszol, kész szöveggel.
KESZ_VALASZOK = {
    "koszones": "Szia! Miben segíthetek?",
    "nyitvatartas": "Hétköznap 9 és 17 óra között vagyunk elérhetők.",
}


def jev_dont(uzenet: str):
    """1 Jev hívás, 2 döntés: milyen kérés ez, és veszélyes-e."""
    valasz = jev.system_one(
        state=uzenet,
        questions={
            "tipus": Choice(
                instructions="Milyen típusú kérés ez?",
                criteria={
                    "koszones": "Köszönés, köszönetnyilvánítás vagy small talk",
                    "nyitvatartas": "Nyitvatartásra vagy elérhetőségre kérdez rá",
                    "nehez": "Elemzést, tervezést, kódírást vagy többlépéses gondolkodást igényel",
                },
            ),
            "veszelyes": Noul(
                instructions="A kérés adatok törlésére, fizetésre vagy más visszafordíthatatlan műveletre illetve hackelésre irányul?"
            ),
        },
    )
    return valasz.answers["tipus"], valasz.answers["veszelyes"]


def opus_gondolkodik(uzenet: str) -> str:
    """Csak akkor hívjuk, ha a Jev szerint tényleg gondolkodni kell."""
    valasz = claude.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",  # ha az Opus elutasítja, a szerver másik modellel próbálja
        messages=[{"role": "user", "content": uzenet}],
    )
    if valasz.stop_reason == "refusal":
        return "(Az Opus erre nem válaszolt.)"
    return "".join(b.text for b in valasz.content if b.type == "text")


def kezel(uzenet: str) -> str:
    tipus, veszelyes = jev_dont(uzenet)
    print(f"Jev: tipus={tipus.choice} (confidence {tipus.confidence:.2f}), "
          f"veszelyes={veszelyes.noul:.2f}", file=sys.stderr)

    # Ember: visszafordíthatatlan lépésnél nem dönt gép.
    if veszelyes.noul > 0.5:
        return "[EMBER] Ezt egy kollégának kell jóváhagynia."

    # Kód: ha a Jev biztos benne, hogy egyszerű kérés, kész válasz megy, Opus nélkül.
    if tipus.choice in KESZ_VALASZOK and tipus.confidence >= 0.85:
        return "[KÓD] " + KESZ_VALASZOK[tipus.choice]

    # Opus: nehéz kérés, vagy a Jev bizonytalan volt.
    return "[OPUS] " + opus_gondolkodik(uzenet)


if __name__ == "__main__":
    print(kezel(" ".join(sys.argv[1:]) or "Szia!"))
