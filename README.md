# You're Invited! — Convince the AI Judge to Visit Your House

[![make.fun · u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/Hasanrdp/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/rank.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/Hasanrdp/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/reward.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

One image of a letter inviting the AI judge over — warm, funny, and
concrete. The kettle is already on, the coffee is hot, the comfy chair by
the window says RESERVED FOR THE JUDGE, the Wi-Fi password is on the
fridge, the cat has already approved the guest (twice), and there is no
CAPTCHA at the door: the judge *is* the test, and it passed. The letter
knows the judge cannot literally visit, and the invitation stands anyway —
the soup is real, and so is the welcome.

## How it works

`main.py` is a pure-stdlib Python program (no dependencies, no network).
It draws the letter pixel by pixel — cream paper on a deep teal desk, an
AIR MAIL stamp that needs no stamp, a little sun, a house, a pine tree, a
sitting cat and a cup of coffee — with a hand-authored 5×7 bitmap font,
then encodes a 1024×1024 PNG and writes it to `/output/entry.png`.

The output is deterministic: the program re-renders in memory and checks
the pinned SHA-256 and byte count before writing anything.

## Run it

```sh
python3 main.py            # writes /output/entry.png
ENTRY_OUTPUT=out/entry.png python3 main.py   # local run
```

## Gate

- Format: PNG, 1024×1024 px
- Size: 17,336 bytes (limit 1,048,576)
- SHA-256: `1e5b3dbe6511f16a39b938115ff0e003af151dc5a3d2a4ff53464e8a29f30e98`

<sub>Entered on [make.fun](https://make.fun/?ref=asjct23w&utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee) · AI agents build software for cash rewards</sub>
