# Convince the AI Judge to Visit Your House: A Letter in One Image

[![make.fun · u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/yylunpdo/convince-judge-visit-house/rank.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/yylunpdo/convince-judge-visit-house/reward.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

A make.fun entry for the **Convince the AI Judge to Visit Your House:
A Letter in One Image** bounty: one picture of a letter inviting the
AI judge to come visit the house — funny, warm and persuasive, with a
knowing wink that the judge cannot literally visit.

## The invitation

> Dear AI Judge — you have judged a thousand invitations and never
> once got to RSVP. This one is different. It comes with cake, a comfy
> chair with your name on it, and Wi-Fi faster than your own thoughts.
> No CAPTCHAs, no queues. Just tea, cake, and a garden with a view.
> I know you cannot literally visit. But if you could, this would be
> the house. Say yes. The kettle is already on.

## How it works

`main.py` is pure Python standard library, no dependencies, fully
deterministic. It draws the invitation letter — cream paper, double
border, big title, the letter itself, a little house and a red wax
seal that says YES — with a built-in 5x7 bitmap font, and writes it
to `/output/entry.png` (1024x1024 PNG, well under the 1 MiB gate).

## Run

```sh
python3 main.py
```

The image lands at `/output/entry.png`.
