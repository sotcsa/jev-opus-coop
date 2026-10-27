# jev-opus-coop

A legegyszerűbb példa arra, hogyan működik együtt a **Jev** (TypeSafe AI döntési modellje) és a **Claude Opus 5.5**:
a Jev dönt, az Opus gondolkodik, a kód végrehajt, az ember jóváhagy.

```
üzenet ──► Jev (1 hívás: típus + veszélyes?)
             ├─ veszélyes          ──► [EMBER] jóváhagyás kell
             ├─ egyszerű, biztos   ──► [KÓD]   kész válasz, Opus nélkül
             └─ nehéz / bizonytalan ─► [OPUS]  Opus 5.5 megoldja
```

## Futtatás

```bash
pip install -r requirements.txt
export TYPESAFE_API_KEY=...
export ANTHROPIC_API_KEY=...
python jev_opus.py "Írj egy Python függvényt, ami eldönti, hogy egy szám prím-e"
```

Kulcsok nélkül, ál-szerverekkel is kipróbálható:

```bash
python tests/demo_mock.py
```

## Mit érdemes tudni

- Egy Jev hívás több döntést ad (itt egy Choice és egy Noul), mindegyikhez confidence-t. A küszöbök (0,85 és 0,5) kiinduló értékek, saját példákon érdemes hangolni.
- Az Opus hívás `fallbacks="default"`-ot használ: ha az Opus elutasít egy kérést, a szerver másik modellel próbálja újra. Ha nem kell, a `betas` és a `fallbacks` sor törölhető.
- A Jev közvetlen API-ja még várólistás; elérhető OpenRouteren, Vercel AI Gatewayen és Cloudflare AI-n keresztül is.
